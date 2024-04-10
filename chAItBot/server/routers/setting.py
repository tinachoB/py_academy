"""
Knowledge Database routers methods
"""
from fastapi import APIRouter, HTTPException, Query, Response, status, FastAPI, Security
from fastapi.params import Depends
from sqlalchemy.orm import Session, aliased, joinedload

from server.Auth0.VerifyToken import VerifyToken
from server.common.common import create_redis_connection, error_detail, error_response
from server.common.env_variables import RedisEnvVars, get_env_vars
from server.helpers.embeddings_db import EmbeddingsDB
from server.helpers.mysql_helper import get_db
from server.helpers.openai_helper import NumpyArray, OpenAIHelper
from server.models.knowledge_categories_database import KnowledgeBaseCategoriesModel
from server.models.knowledge_database import KnowledgeDataBaseModel
from server.schemas.wrappers.base_response import TResponseDataPost, MessagePost


auth = VerifyToken()  # 👈 Get a new instance

router = APIRouter()

__env_vars = get_env_vars()
__openai_helper = OpenAIHelper(config=__env_vars)
__redis_helper = EmbeddingsDB(config=__env_vars.redis)


@router.post(path="/ResetRedis")
async def upload_database(auth_result: str = Security(auth.verify), db: Session = Depends(get_db)):
    """
    Uploads the knowledge database in redis.
    \f
    :return: a Database response based on the current POST status
    """
    message = MessagePost()
    response = TResponseDataPost(message=message)
    try:
        __redis_helper.delete_knowledge_database()

        query_all = db.query(KnowledgeDataBaseModel)

        for item in query_all:
            concatenated_text = f"{item.Title}: {item.Content}"
            embedding = __openai_helper.encode_text(text=concatenated_text)

            categories = db.query(KnowledgeBaseCategoriesModel).filter_by(KnowledgeBase_Id=item.Id).all()
            category_ids = [category.Category_Id for category in categories]

            __redis_helper.upload_embedding(
                embedding.embeddings.tobytes(), item.Id, concatenated_text,
                category_ids
            )

    except HTTPException as e:
        response.success = False
        raise e
    except Exception as e:
        response.success = False
        raise error_response(detail=str(e))

    return response
