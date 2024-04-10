"""
Module for gathering and validating environment variables.
"""
import os
from typing import NamedTuple, Optional

import environs
import validators

# Env variables names
REDIS_HOST_ENV_VAR = "REDIS_HOST"
REDIS_PORT_ENV_VAR = "REDIS_PORT"
REDIS_EMBEDDINGS_DB_ENV_VAR = "REDIS_EMBEDDINGS_DB"
REDIS_HISTORY_DB_ENV_VAR = "REDIS_HISTORY_DB"
REDIS_UNANSWERED_QUESTIONS_DB_ENV_VAR = "REDIS_UNANSWERED_QUESTIONS_DB"
REDIS_PASSWORD_ENV_VAR = "REDIS_PASSWORD"
REDIS_SSL_ENV_VAR = "REDIS_SSL"

# MYSQL related variable names
MYSQL_HOST_ENV_VAR = "MYSQL_HOST"
MYSQL_PORT_ENV_VAR = "MYSQL_PORT"
MYSQL_USER_ENV_VAR = "MYSQL_USER"
MYSQL_PASSWORD_ENV_VAR = "MYSQL_PASSWORD"
MYSQL_DB_NAME_ENV_VAR = "MYSQL_DB_NAME"

OPENAI_API_KEY_ENV_VAR = "OPENAI_API_KEY"
OPENAI_CHAT_MODEL_ENV_VAR = "OPENAI_CHAT_MODEL"
OPENAI_EMBEDDING_MODEL_ENV_VAR = "OPENAI_EMBEDDING_MODEL"
OPENAI_TYPE_ENV_VAR = "OPENAI_TYPE"
OPENAI_RETRIES_ENV_VAR = "OPENAI_RETRIES"
OPENAI_RETRY_SLEEP_TIME_ENV_VAR = "OPENAI_RETRY_SLEEP_TIME"
OPENAI_STATS_ENV_VAR = "OPENAI_STATS"
OPENAI_COMPLETION_INPUT_PRICE_ENV_VAR = "OPENAI_COMPLETION_INPUT_PRICE"
OPENAI_COMPLETION_OUTPUT_PRICE_ENV_VAR = "OPENAI_COMPLETION_OUTPUT_PRICE"
OPENAI_EMBEDDINGS_PRICE_ENV_VAR = "OPENAI_EMBEDDINGS_PRICE"

OPENAI_TEMPERATURE_ENV_VAR = "OPENAI_TEMPERATURE"
OPENAI_TOP_PRIORITY_ENV_VAR = "OPENAI_TOP_PRIORITY"

EMBEDDINGS_PRECISION_FILTER_ENV_VAR = "EMBEDDINGS_PRECISION_FILTER"
EMBEDDINGS_TOP_K_ELEMENTS_ENV_VAR = "EMBEDDINGS_TOP_K_ELEMENTS"

AZURE_API_BASE_ENV_VAR = "AZURE_API_BASE"
AZURE_API_VERSION_ENV_VAR = "AZURE_API_VERSION"

HISTORY_EXPIRATION_TIME_ENV_VAR = "HISTORY_EXPIRATION_TIME"
HISTORY_CACHE_COUNT_ENV_VAR = "HISTORY_CACHE_COUNT"

# Assets
KNOWLEDGE_BASE_PATH_ENV_VAR = "KNOWLEDGE_BASE_PATH"
NO_EMBEDDINGS_KB_DEFAULT_VALUES_PATH_ENV_VAR = "NO_EMBEDDINGS_KB_DEFAULT_VALUES_PATH"
PROMPT_TEMPLATE_PATH_ENV_VAR = "PROMPT_TEMPLATE_PATH"
UNANSWERED_QUESTION_DEFAULT_RESPONSE_PATH_ENV_VAR = "UNANSWERED_QUESTION_DEFAULT_RESPONSE_PATH"


# Default values for Redis
DEFAULT_REDIS_HOST = "localhost"
DEFAULT_REDIS_PORT = 6379
DEFAULT_REDIS_EMBEDDINGS_DB = 0
DEFAULT_REDIS_HISTORY_DB = 1
DEFAULT_UNANSWERED_QUESTIONS_DB = 2
DEFAULT_REDIS_PASSWORD = None
DEFAULT_REDIS_SSL = False


# Default values for MySql
DEFAULT_MYSQL_HOST = "DEFAULT_MYSQL_HOST"
DEFAULT_MYSQL_PORT = 3306
DEFAULT_MYSQL_USER = "DEFAULT_MYSQL_USER"
DEFAULT_MYSQL_PASSWORD = "DEFAULT_MYSQL_PASSWORD"
DEFAULT_MYSQL_DB_NAME = "DEFAULT_MYSQL_DB_NAME"

# Default values for Azure
DEFAULT_TYPE = "azure"
DEFAULT_OPENAI_RETRIES = 2
DEFAULT_OPENAI_RETRY_SLEEP_TIME = 5  # Secs.
DEFAULT_HISTORY_EXPIRATION_TIME = 30  # Minutes.
DEFAULT_HISTORY_CACHE_COUNT = 5
DEFAULT_OPENAI_TEMPERATURE = 0.2
DEFAULT_OPENAI_TOP_PRIORITY = 0.01

# Default algorithms constants
DEFAULT_TOP_K_ELEMENTS = 10
DEFAULT_PRECISION_FILTER = 0.8

MIN_TOP_K_ELEMENTS = 1
MAX_TOP_K_ELEMENTS = 10
MIN_PRECISION_FILTER = 0.0
MAX_PRECISION_FILTER = 1.0

# Default value for stats showing
DEFAULT_OPENAI_STATS = True
DEFAULT_OPENAI_PRICE = 0.0

MIN_RETRIES = 0
MAX_RETRIES = 10
MAX_RETRY_SLEEP_TIME = 30


class AlgorithmsEnvVars(NamedTuple):
    embeddings_precision_filter: float
    top_k_elements: int


class RedisEnvVars(NamedTuple):
    host: str
    port: int
    embeddings_db: int
    history_db: int
    unanswered_questions_db: int
    password: Optional[str]
    ssl: bool


class MySqlEnvVars(NamedTuple):
    host: str
    port: int
    user: str
    password: str
    db_name: str


class OpenAIPrices(NamedTuple):
    completion_input: float = DEFAULT_OPENAI_PRICE
    completion_output: float = DEFAULT_OPENAI_PRICE
    embeddings: float = DEFAULT_OPENAI_PRICE


class OpenAIEnvVars(NamedTuple):
    api_key: str
    chat_model: str
    embedding_model: str
    type: Optional[str]
    prices: OpenAIPrices
    retries: int = DEFAULT_OPENAI_RETRIES
    retry_sleep_time: int = DEFAULT_OPENAI_RETRY_SLEEP_TIME
    stats: bool = DEFAULT_OPENAI_STATS
    temperature: float = DEFAULT_OPENAI_TEMPERATURE
    top_priority: float = DEFAULT_OPENAI_TOP_PRIORITY


class AzureEnvVars(NamedTuple):
    api_base: Optional[str] = None
    api_version: Optional[str] = None


class AssetsEnvVars(NamedTuple):
    knowledge_base_path: str
    no_embeddings_kb_default_values_path: str
    prompt_template_path: str
    unanswered_question_default_response_path: str


class EnvVars(NamedTuple):
    """
    Required environment variables.
    """

    redis: RedisEnvVars
    mysql: MySqlEnvVars
    openai: OpenAIEnvVars
    azure: AzureEnvVars
    algorithms: AlgorithmsEnvVars
    assets: AssetsEnvVars
    history_expiration_time: int
    history_cache_count: int


# pylint: disable=too-many-branches
def get_env_vars() -> EnvVars:
    """
    Return a NamedTuple that contains the environment variables required.

    :return: EnvVars typed and validated NamedTuple
    """

    def _is_valid(env_value: str) -> bool:
        return env_value is not None and len(env_value.strip()) != 0

    env = environs.Env()
    env.read_env()

    env_vars = EnvVars(
        redis=RedisEnvVars(
            host=env.str(REDIS_HOST_ENV_VAR, default=DEFAULT_REDIS_HOST),
            port=env.int(REDIS_PORT_ENV_VAR, default=DEFAULT_REDIS_PORT),
            password=env.str(REDIS_PASSWORD_ENV_VAR, default=DEFAULT_REDIS_PASSWORD),
            embeddings_db=env.str(REDIS_EMBEDDINGS_DB_ENV_VAR, default=DEFAULT_REDIS_EMBEDDINGS_DB),
            history_db=env.str(REDIS_HISTORY_DB_ENV_VAR, default=DEFAULT_REDIS_HISTORY_DB),
            unanswered_questions_db=env.str(
                REDIS_UNANSWERED_QUESTIONS_DB_ENV_VAR, default=DEFAULT_UNANSWERED_QUESTIONS_DB
            ),
            ssl=env.bool(REDIS_SSL_ENV_VAR, default=DEFAULT_REDIS_SSL),
        ),
        mysql=MySqlEnvVars(
            host=env.str(MYSQL_HOST_ENV_VAR, default=DEFAULT_MYSQL_HOST),
            port=env.int(MYSQL_PORT_ENV_VAR, default=DEFAULT_MYSQL_PORT),
            user=env.str(MYSQL_USER_ENV_VAR, default=DEFAULT_MYSQL_USER),
            password=env.str(MYSQL_PASSWORD_ENV_VAR, default=DEFAULT_MYSQL_PASSWORD),
            db_name=env.str(MYSQL_DB_NAME_ENV_VAR, default=DEFAULT_MYSQL_PASSWORD),
        ),
        openai=OpenAIEnvVars(
            api_key=env.str(OPENAI_API_KEY_ENV_VAR, default=None),
            chat_model=env.str(OPENAI_CHAT_MODEL_ENV_VAR, default=None),
            embedding_model=env.str(OPENAI_EMBEDDING_MODEL_ENV_VAR, default=None),
            type=env.str(OPENAI_TYPE_ENV_VAR, default=None),
            retries=env.int(OPENAI_RETRIES_ENV_VAR, default=DEFAULT_OPENAI_RETRIES),
            retry_sleep_time=env.int(
                OPENAI_RETRY_SLEEP_TIME_ENV_VAR, default=DEFAULT_OPENAI_RETRY_SLEEP_TIME
            ),
            stats=env.bool(OPENAI_STATS_ENV_VAR, default=DEFAULT_OPENAI_STATS),
            prices=OpenAIPrices(
                completion_input=env.float(
                    OPENAI_COMPLETION_INPUT_PRICE_ENV_VAR, default=DEFAULT_OPENAI_PRICE
                ),
                completion_output=env.float(
                    OPENAI_COMPLETION_OUTPUT_PRICE_ENV_VAR, default=DEFAULT_OPENAI_PRICE
                ),
                embeddings=env.float(OPENAI_EMBEDDINGS_PRICE_ENV_VAR, default=DEFAULT_OPENAI_PRICE),
            ),
            temperature=env.float(OPENAI_TEMPERATURE_ENV_VAR, default=DEFAULT_OPENAI_TEMPERATURE),
            top_priority=env.float(
                OPENAI_TOP_PRIORITY_ENV_VAR, default=DEFAULT_OPENAI_TOP_PRIORITY
            ),
        ),
        azure=AzureEnvVars(
            api_base=env.str(AZURE_API_BASE_ENV_VAR, default=None),
            api_version=env.str(AZURE_API_VERSION_ENV_VAR, default=None),
        ),
        algorithms=AlgorithmsEnvVars(
            top_k_elements=env.int(
                EMBEDDINGS_TOP_K_ELEMENTS_ENV_VAR, default=DEFAULT_TOP_K_ELEMENTS
            ),
            embeddings_precision_filter=env.float(
                EMBEDDINGS_PRECISION_FILTER_ENV_VAR, default=DEFAULT_PRECISION_FILTER
            ),
        ),
        assets=AssetsEnvVars(
            knowledge_base_path=env.str(KNOWLEDGE_BASE_PATH_ENV_VAR, default=None),
            no_embeddings_kb_default_values_path=env.str(
                NO_EMBEDDINGS_KB_DEFAULT_VALUES_PATH_ENV_VAR, default=None
            ),
            prompt_template_path=env.str(PROMPT_TEMPLATE_PATH_ENV_VAR, default=None),
            unanswered_question_default_response_path=env.str(
                UNANSWERED_QUESTION_DEFAULT_RESPONSE_PATH_ENV_VAR, default=None
            ),
        ),
        history_expiration_time=env.int(
            HISTORY_EXPIRATION_TIME_ENV_VAR, default=DEFAULT_HISTORY_EXPIRATION_TIME
        ),
        history_cache_count=env.int(
            HISTORY_CACHE_COUNT_ENV_VAR, default=DEFAULT_HISTORY_CACHE_COUNT
        ),
    )

    if not _is_valid(env_vars.openai.api_key):
        raise EnvironmentError(f"Missing {OPENAI_API_KEY_ENV_VAR} environment var.")

    if not _is_valid(env_vars.openai.chat_model):
        raise EnvironmentError(f"Missing {OPENAI_CHAT_MODEL_ENV_VAR} environment var.")

    if not _is_valid(env_vars.openai.embedding_model):
        raise EnvironmentError(f"Missing {OPENAI_EMBEDDING_MODEL_ENV_VAR} environment var.")

    if env_vars.openai.retries < MIN_RETRIES or env_vars.openai.retries > MAX_RETRIES:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_RETRIES_ENV_VAR} environment var. "
            f"Must be in the range [{MIN_RETRIES}, {MAX_RETRIES}]"
        )

    if (
        env_vars.algorithms.top_k_elements < MIN_TOP_K_ELEMENTS
        or env_vars.algorithms.top_k_elements > MAX_TOP_K_ELEMENTS
    ):
        raise EnvironmentError(
            f"Invalid value for {EMBEDDINGS_TOP_K_ELEMENTS_ENV_VAR} environment var. "
            f"Must be in the range [{MIN_TOP_K_ELEMENTS}, {MAX_TOP_K_ELEMENTS}]"
        )

    if (
        env_vars.algorithms.embeddings_precision_filter < MIN_PRECISION_FILTER
        or env_vars.algorithms.embeddings_precision_filter > MAX_PRECISION_FILTER
    ):
        raise EnvironmentError(
            f"Invalid value for {EMBEDDINGS_PRECISION_FILTER_ENV_VAR} environment var. "
            f"Must be in the range [{MIN_PRECISION_FILTER:.1f}, {MAX_PRECISION_FILTER:.1f}]"
        )

    if (
        env_vars.openai.retry_sleep_time < 0
        or env_vars.openai.retry_sleep_time > MAX_RETRY_SLEEP_TIME
    ):
        raise EnvironmentError(
            f"Invalid value for {OPENAI_RETRY_SLEEP_TIME_ENV_VAR} environment var. "
            f"Must be in the range [0, {MAX_RETRY_SLEEP_TIME}]"
        )

    if env_vars.openai.prices.completion_input < 0.0:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_COMPLETION_INPUT_PRICE_ENV_VAR} environment var. "
            "It must be a positive number"
        )

    if env_vars.openai.prices.completion_output < 0.0:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_COMPLETION_OUTPUT_PRICE_ENV_VAR} environment var. "
            "It must be a positive number"
        )

    if env_vars.openai.prices.embeddings < 0.0:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_EMBEDDINGS_PRICE_ENV_VAR} environment var. "
            "It must be a positive number"
        )

    if env_vars.openai.temperature < 0.0:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_TEMPERATURE_ENV_VAR} environment var. "
            "It must be a positive number"
        )

    if env_vars.openai.temperature > 1:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_TEMPERATURE_ENV_VAR} environment var. "
            "It must be a value between 0 and 1 "
        )

    if env_vars.openai.top_priority < 0.0:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_TOP_PRIORITY_ENV_VAR} environment var. "
            "It must be a positive number"
        )

    if env_vars.openai.top_priority > 1:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_TOP_PRIORITY_ENV_VAR} environment var. "
            "It must be a value between 0 and 1 "
        )

    if not _is_valid(env_vars.assets.knowledge_base_path) or not os.path.exists(
        env_vars.assets.knowledge_base_path
    ):
        raise EnvironmentError(
            f"Invalid value for {KNOWLEDGE_BASE_PATH_ENV_VAR} environment var. "
            "It must be a valid and existent file path. "
        )

    if not _is_valid(env_vars.assets.no_embeddings_kb_default_values_path) or not os.path.exists(
        env_vars.assets.no_embeddings_kb_default_values_path
    ):
        raise EnvironmentError(
            f"Invalid value for {NO_EMBEDDINGS_KB_DEFAULT_VALUES_PATH_ENV_VAR} environment var. "
            "It must be a valid and existent file path. "
        )

    if not _is_valid(env_vars.assets.prompt_template_path) or not os.path.exists(
        env_vars.assets.prompt_template_path
    ):
        raise EnvironmentError(
            f"Invalid value for {PROMPT_TEMPLATE_PATH_ENV_VAR} environment var. "
            "It must be a valid and existent file path. "
        )

    if not _is_valid(
        env_vars.assets.unanswered_question_default_response_path
    ) or not os.path.exists(env_vars.assets.unanswered_question_default_response_path):
        raise EnvironmentError(
            f"Invalid value for {UNANSWERED_QUESTION_DEFAULT_RESPONSE_PATH_ENV_VAR} environment var. "
            "It must be a valid and existent file path. "
        )

    if env_vars.openai.type is not None:
        if env_vars.openai.type != DEFAULT_TYPE:
            raise EnvironmentError(
                f"Invalid {OPENAI_TYPE_ENV_VAR} environment var. "
                f"Must be '{DEFAULT_TYPE}' if used."
            )
        if not _is_valid(env_vars.azure.api_base):
            raise EnvironmentError(f"Missing {AZURE_API_BASE_ENV_VAR} environment var.")

        if not validators.url(env_vars.azure.api_base):
            raise EnvironmentError(
                f"Invalid {AZURE_API_BASE_ENV_VAR} environment var. Must be a valid URL"
            )

        if not _is_valid(env_vars.azure.api_version):
            raise EnvironmentError(f"Missing {AZURE_API_VERSION_ENV_VAR} environment var.")

    return env_vars
