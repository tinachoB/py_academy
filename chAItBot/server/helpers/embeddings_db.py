"""
Helper for Redis
"""
from typing import List, NamedTuple

import redis
from redis.commands.search.field import TagField, VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from server.common.common import create_redis_connection
from server.common.env_variables import RedisEnvVars
from server.common.singleton import Singleton
from server.helpers.openai_helper import NumpyArray, OpenAIHelper

# Index definitions
INDEX_NAME: str = "index"
INDEX_ALREADY_EXISTS_ERROR: str = "Index already exists"

# Doc Prefix
PREFIX: str = "doc"
DOC_PREFIX: str = f"{PREFIX}:"


# Fields on the DB
VALUES_PER_KEY: int = 2  # Two values (paragraph and embeddings)
PARAGRAPH_FIELD_NAME: str = "paragraph"
EMBEDDINGS_FIELD_NAME: str = "embeddings"
CATEGORY_FIELD_NAME: str = "category_id"
SCORE_FIELD_NAME: str = "score"
CATEGORIES_FIELD_NAME: str = "categories"

# Definitions for the Vector (embeddings) field
VECTOR_INDEX_TYPE: str = "HNSW"
VECTOR_TYPE: str = "FLOAT64"
EMBEDDINGS_VECTOR_DIMENSIONS: int = 1536
VECTOR_SIMILARITIES_SEARCH: int = 2
DISTANCE_METRIC: str = "COSINE"

# Schema definition
REDIS_FIELDS_SCHEMA = (
    TagField(PARAGRAPH_FIELD_NAME),
    TextField(CATEGORIES_FIELD_NAME),
    VectorField(
        EMBEDDINGS_FIELD_NAME,
        VECTOR_INDEX_TYPE,
        {
            "TYPE": VECTOR_TYPE,
            "DIM": EMBEDDINGS_VECTOR_DIMENSIONS,
            "DISTANCE_METRIC": DISTANCE_METRIC,
        },
    ),
)

# DB Index Definition
INDEX_DEFINITION = IndexDefinition(prefix=[DOC_PREFIX], index_type=IndexType.HASH)

# Similarities Query
SIMILARITIES_QUERY = (
    Query(f"*=>[KNN $top_elements @{EMBEDDINGS_FIELD_NAME} $vec AS {SCORE_FIELD_NAME}]")
    .sort_by(SCORE_FIELD_NAME)
    .return_fields(PARAGRAPH_FIELD_NAME, SCORE_FIELD_NAME, CATEGORY_FIELD_NAME)
    .dialect(VECTOR_SIMILARITIES_SEARCH)
)


class RedisResult(NamedTuple):
    """
    Redis Named Tuple Result
    """

    ok: bool = True
    message: str = ""
    modified_values: int = 0
    unmodified_values: int = 0


class SimilaritiesResult(NamedTuple):
    """
    A NT with the similarities
    """

    ok: bool = True
    similarities: List[str] = []
    error_message: str = ""


class EmbeddingsDB(metaclass=Singleton):
    """
    Class used to wrap the redis actions related to embedding.s
    """

    def __init__(self: "EmbeddingsDB", config: RedisEnvVars) -> None:
        self._redis = create_redis_connection(config=config, db=config.embeddings_db)
        self._create_index()

    def get_similarities(
            self: "EmbeddingsDB",
            text_embeddings: NumpyArray,
            categories: List[int],
            top_elements: int,
            filter_precision: float,
    ) -> SimilaritiesResult:
        """
                Gets a list with paragraphs similar to the input text.
                :param text_embeddings: The embeddings of the text we want to get
                 the similar paragraphs.
                :param categories: A list with the categories to be queried
                :param top_elements: The number of top elements to be returned on the list.
                :param filter_precision: Value used to filter nearest neighbor embeddings.
                :return: A NT with the results.
                """

        def build_categories_filter() -> str:
            return f"@categories:({'|'.join(list(map(str,categories)))})" if categories else "*"

        query = f"{build_categories_filter()}=>[KNN $top_elements @{EMBEDDINGS_FIELD_NAME} $vec AS {SCORE_FIELD_NAME}]"
        try:
            query_result = (
                self._redis.ft(INDEX_NAME)
                .search(
                    Query(query)
                    .sort_by(SCORE_FIELD_NAME)
                    .return_fields(CATEGORIES_FIELD_NAME, PARAGRAPH_FIELD_NAME, SCORE_FIELD_NAME)
                    .dialect(VECTOR_SIMILARITIES_SEARCH),
                    query_params={
                        "top_elements": top_elements,
                        "vec": text_embeddings.tobytes(),  # type: ignore[dict-item]
                    },
                )
                .docs
            )

            return SimilaritiesResult(
                similarities=[
                    result[PARAGRAPH_FIELD_NAME]
                    for result in query_result
                    if float(result[SCORE_FIELD_NAME]) <= 0.3
                ]
            )

        except Exception as e:
            return SimilaritiesResult(ok=False, error_message=str(e))

    def delete_knowledge_database(self: "EmbeddingsDB") -> None:
        """
        Deletes the current Redis DB.
        """
        self._redis.flushdb()
        self._create_index()

    def delete_knowledge_entry(self: "EmbeddingsDB", key: str) -> None:
        """
        Deletes a specific entry from Redis using the provided key.
        """
        self._redis.delete(key)
        self._create_index()

    def upload_knowledge_database(
        self: "EmbeddingsDB", openai_helper: OpenAIHelper, knowledge_base_file: str
    ) -> RedisResult:
        """
        Updates the current Redis DB with all the knowledge base information.
        :param openai_helper: OpenAI helper to encode the text to be embedded.
        :return: A Redis NT Result
        """
        try:
            with open(knowledge_base_file, encoding="utf8") as f:
                paragraphs = f.read().split(";\n")

            pipe = self._redis.pipeline()
            for index, paragraph in enumerate(paragraphs):
                response = openai_helper.encode_text(text=paragraph)
                if response.ok and response.embeddings.any():
                    pipe.hset(
                        name=f"{PREFIX}:{index}",
                        mapping={
                            PARAGRAPH_FIELD_NAME: paragraph,
                            EMBEDDINGS_FIELD_NAME: response.embeddings.tobytes(),
                        },
                    )
            redis_response: List[int] = pipe.execute()
            uploaded_values = sum(redis_response)

            return RedisResult(
                modified_values=uploaded_values,
                unmodified_values=len(redis_response) * VALUES_PER_KEY - uploaded_values,
                message="Knowledge base was uploaded successfully",
            )
        except Exception as e:
            return RedisResult(ok=False, message=str(e))

    def upload_embedding(self: "EmbeddingsDB", embeddings, index, paragraph, categories_id) -> bool:
        """
        Updates the current Redis DB with all the knowledge base information.
        :return: A Redis NT Result
        """
        try:
            pipe = self._redis.pipeline()
            categories_str = ", ".join(map(str, categories_id))

            pipe.hmset(
                name=f"{PREFIX}:{index}",
                mapping={
                    CATEGORIES_FIELD_NAME: categories_str,
                    PARAGRAPH_FIELD_NAME: paragraph,
                    EMBEDDINGS_FIELD_NAME: embeddings,
                },
            )
            pipe.execute()

            return True

        except Exception as e:
            return False

    @property
    def size(self: "EmbeddingsDB") -> int:
        return self._redis.dbsize()

    def _create_index(self: "EmbeddingsDB") -> None:
        try:
            self._redis.ft(INDEX_NAME).create_index(
                fields=REDIS_FIELDS_SCHEMA, definition=INDEX_DEFINITION
            )
        except redis.ResponseError as e:
            if str(e) != INDEX_ALREADY_EXISTS_ERROR:
                raise e
