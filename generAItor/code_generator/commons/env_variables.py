"""
Module for gathering and validating environment variables.
"""
import platform
import sys
from typing import NamedTuple, Optional

import environs
import validators

from code_generator import ENV_FILE

API_KEY_ENV_NAME = "API_KEY"
OPENAI_API_TYPE_ENV_NAME = "OPENAI_API_TYPE"
OPENAI_MODEL_ENV_NAME = "OPENAI_MODEL"
OPENAI_INPUT_PRICE_ENV_NAME = "OPENAI_INPUT_PRICE"
OPENAI_OUTPUT_PRICE_ENV_NAME = "OPENAI_OUTPUT_PRICE"
OPENAI_RETRIES_ENV_NAME = "OPENAI_RETRIES"
OPENAI_RETRY_SLEEP_TIME_ENV_NAME = "OPENAI_RETRY_SLEEP_TIME"
OPENAI_INSTRUCT_MODEL_USE_ENV_NAME = "OPENAI_INSTRUCT_MODEL_USE"

AZURE_API_BASE_ENV_NAME = "AZURE_API_BASE"
AZURE_API_VERSION_ENV_NAME = "AZURE_API_VERSION"
AZURE_DEPLOYMENT_ID_ENV_NAME = "AZURE_DEPLOYMENT_ID"

AZURE_TYPE = "azure"
DEFAULT_OPENAI_RETRIES = 2
DEFAULT_OPENAI_RETRY_SLEEP_TIME = 5  # Secs.
DEFAULT_OPENAI_INSTRUCT_MODEL_USE = False

DEFAULT_OPENAI_INPUT_PRICE = 0.0
DEFAULT_OPENAI_OUTPUT_PRICE = 0.0

MAX_RETRIES = 10
MAX_RETRY_SLEEP_TIME = 30


class EnvVars(NamedTuple):
    """
    Required environment variables.
    """

    api_key: str
    openai_model: str
    openai_type: Optional[str] = None
    azure_base: Optional[str] = None
    azure_version: Optional[str] = None
    azure_deployment_id: Optional[str] = None
    openai_input_price: Optional[float] = DEFAULT_OPENAI_INPUT_PRICE
    openai_output_price: Optional[float] = DEFAULT_OPENAI_OUTPUT_PRICE
    openai_retries: int = DEFAULT_OPENAI_RETRIES
    openai_retry_sleep_time: int = DEFAULT_OPENAI_RETRY_SLEEP_TIME
    openai_instruct_model_use: bool = DEFAULT_OPENAI_INSTRUCT_MODEL_USE


# pylint: disable=too-many-branches


def get_env_vars() -> EnvVars:
    """
    Return a NamedTuple that contains the environment variables required.

    :return: EnvVars typed and validated NamedTuple
    """

    def _is_valid(env_value: str) -> bool:
        return env_value is not None and len(env_value.strip()) != 0

    env = environs.Env()

    if platform.system() == "Windows" and getattr(sys, "frozen", False):
        env.read_env(path=str(ENV_FILE), recurse=False)
    else:
        env.read_env()

    env_vars = EnvVars(
        api_key=env.str(API_KEY_ENV_NAME, default=None),
        openai_model=env.str(OPENAI_MODEL_ENV_NAME, default=None),
        openai_input_price=env.float(
            OPENAI_INPUT_PRICE_ENV_NAME, default=DEFAULT_OPENAI_INPUT_PRICE
        ),
        openai_output_price=env.float(
            OPENAI_OUTPUT_PRICE_ENV_NAME, default=DEFAULT_OPENAI_OUTPUT_PRICE
        ),
        openai_retries=env.int(OPENAI_RETRIES_ENV_NAME, default=DEFAULT_OPENAI_RETRIES),
        openai_retry_sleep_time=env.int(
            OPENAI_RETRY_SLEEP_TIME_ENV_NAME, default=DEFAULT_OPENAI_RETRY_SLEEP_TIME
        ),
        openai_instruct_model_use=env.bool(
            OPENAI_INSTRUCT_MODEL_USE_ENV_NAME, default=DEFAULT_OPENAI_INSTRUCT_MODEL_USE
        ),
        openai_type=env.str(OPENAI_API_TYPE_ENV_NAME, default=None),
        azure_base=env.str(AZURE_API_BASE_ENV_NAME, default=None),
        azure_version=env.str(AZURE_API_VERSION_ENV_NAME, default=None),
        azure_deployment_id=env.str(AZURE_DEPLOYMENT_ID_ENV_NAME, default=None),
    )

    if not _is_valid(env_vars.api_key):
        raise EnvironmentError(f"Missing {API_KEY_ENV_NAME} environment var.")

    if not _is_valid(env_vars.openai_model):
        raise EnvironmentError(f"Missing {OPENAI_MODEL_ENV_NAME} environment var.")

    if env_vars.openai_input_price < 0.0:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_INPUT_PRICE_ENV_NAME} environment var. "
            "It must be a positive number"
        )
    if env_vars.openai_output_price < 0.0:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_OUTPUT_PRICE_ENV_NAME} environment var. "
            "It must be a positive number"
        )

    if env_vars.openai_retries < 0 or env_vars.openai_retries > MAX_RETRIES:
        raise EnvironmentError(
            f"Invalid value for {OPENAI_RETRIES_ENV_NAME} environment var. "
            f"Must be in the range [0, {MAX_RETRIES}]"
        )

    if (
        env_vars.openai_retry_sleep_time < 0
        or env_vars.openai_retry_sleep_time > MAX_RETRY_SLEEP_TIME
    ):
        raise EnvironmentError(
            f"Invalid value for {OPENAI_RETRY_SLEEP_TIME_ENV_NAME} environment var. "
            f"Must be in the range [0, {MAX_RETRY_SLEEP_TIME}]"
        )

    if env_vars.openai_type is not None:
        if env_vars.openai_type != AZURE_TYPE:
            raise EnvironmentError(
                f"Invalid {OPENAI_API_TYPE_ENV_NAME} environment var. "
                f"Must be '{AZURE_TYPE}' if used."
            )
        if not _is_valid(env_vars.azure_base):
            raise EnvironmentError(f"Missing {AZURE_API_BASE_ENV_NAME} environment var.")

        if not validators.url(env_vars.azure_base):
            raise EnvironmentError(
                f"Invalid {AZURE_API_BASE_ENV_NAME} environment var. Must be a valid URL"
            )

        if not _is_valid(env_vars.azure_version):
            raise EnvironmentError(f"Missing {AZURE_API_VERSION_ENV_NAME} environment var.")

        if not _is_valid(env_vars.azure_deployment_id):
            raise EnvironmentError(f"Missing {AZURE_DEPLOYMENT_ID_ENV_NAME} environment var.")

    return env_vars
