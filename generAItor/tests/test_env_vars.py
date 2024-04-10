"""
Test for the Environments variables.
"""
import os
import platform
import sys
from typing import Dict, Union
from unittest.mock import call

import environs
import pytest
from pytest_mock import MockFixture

from code_generator.commons.env_variables import (
    API_KEY_ENV_NAME,
    DEFAULT_OPENAI_INPUT_PRICE,
    DEFAULT_OPENAI_OUTPUT_PRICE,
    DEFAULT_OPENAI_RETRIES,
    DEFAULT_OPENAI_RETRY_SLEEP_TIME,
    EnvVars,
    get_env_vars,
)
from tests.common_test_helpers import function_import_path, parametrize_wrapper


@pytest.mark.parametrize(argnames="is_frozen", argvalues=[True, False])
@pytest.mark.parametrize(argnames="system", argvalues=["Windows", "Linux"])
@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            # Missing required env API_KEY
            {"mocked_env_vars": {}, "expected_result": "Missing API_KEY"},
            {
                "mocked_env_vars": {"API_KEY": ""},
                "expected_result": "Missing API_KEY",
            },
            # Empty value for API_KEY
            {
                "mocked_env_vars": {"API_KEY": "****"},
                "expected_result": "Missing OPENAI_MODEL",
            },
            # Missing required env OPENAI_MODEL
            {
                "mocked_env_vars": {"API_KEY": "****"},
                "expected_result": "Missing OPENAI_MODEL",
            },
            # Empty value for OPENAI_MODEL
            {
                "mocked_env_vars": {"API_KEY": "****", "OPENAI_MODEL": ""},
                "expected_result": "Missing OPENAI_MODEL",
            },
            # Invalid number of retries
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_RETRIES": "50",
                },
                "expected_result": "Invalid value for OPENAI_RETRIES",
            },
            # Invalid sleep time
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_RETRY_SLEEP_TIME": "50",
                },
                "expected_result": "Invalid value for OPENAI_RETRY_SLEEP_TIME",
            },
            # Invalid Azure-Type
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_API_TYPE": "something",
                },
                "expected_result": "Invalid OPENAI_API_TYPE environment var.",
            },
            # Missing AZURE_API_BASE
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_API_TYPE": "azure",
                },
                "expected_result": "Missing AZURE_API_BASE",
            },
            # Empty AZURE_API_BASE
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_API_TYPE": "azure",
                    "AZURE_API_BASE": "",
                },
                "expected_result": "Missing AZURE_API_BASE",
            },
            # Wrong AZURE_API_BASE (Must be an url)
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_API_TYPE": "azure",
                    "AZURE_API_BASE": "not-an-url",
                },
                "expected_result": "Invalid AZURE_API_BASE environment var. "
                "Must be a valid URL'",
            },
            # Missing AZURE_API_VERSION
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_API_TYPE": "azure",
                    "AZURE_API_BASE": "https://something.com",
                },
                "expected_result": "Missing AZURE_API_VERSION",
            },
            # Empty AZURE_API_VERSION
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_API_TYPE": "azure",
                    "AZURE_API_BASE": "https://something.com",
                    "AZURE_API_VERSION": "",
                },
                "expected_result": "Missing AZURE_API_VERSION",
            },
            # Missing AZURE_DEPLOYMENT_ID
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_API_TYPE": "azure",
                    "AZURE_API_BASE": "https://something.com",
                    "AZURE_API_VERSION": "2023-05-15",
                },
                "expected_result": "Missing AZURE_DEPLOYMENT_ID",
            },
            # Empty AZURE_DEPLOYMENT_ID
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_API_TYPE": "azure",
                    "AZURE_API_BASE": "https://something.com",
                    "AZURE_API_VERSION": "2023-05-15",
                    "AZURE_DEPLOYMENT_ID": "",
                },
                "expected_result": "Missing AZURE_DEPLOYMENT_ID",
            },
            # Negative OPENAI_INPUT_PRICE case
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_INPUT_PRICE": "-0.1",
                },
                "expected_result": "Invalid value for OPENAI_INPUT_PRICE environment var.",
            },
            # Negative OPENAI_OUTPUT_PRICE case
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_OUTPUT_PRICE": "-0.1",
                },
                "expected_result": "Invalid value for OPENAI_OUTPUT_PRICE environment var.",
            },
            # General success case with default values
            {
                "mocked_env_vars": {"API_KEY": "****", "OPENAI_MODEL": "model"},
                "expected_result": EnvVars(
                    api_key="****",
                    openai_model="model",
                    openai_input_price=DEFAULT_OPENAI_INPUT_PRICE,
                    openai_output_price=DEFAULT_OPENAI_OUTPUT_PRICE,
                    openai_retries=DEFAULT_OPENAI_RETRIES,
                    openai_retry_sleep_time=DEFAULT_OPENAI_RETRY_SLEEP_TIME,
                ),
            },
            # Success case with overriden values
            {
                "mocked_env_vars": {
                    "API_KEY": "****",
                    "OPENAI_MODEL": "model",
                    "OPENAI_INPUT_PRICE": "0.001",
                    "OPENAI_OUTPUT_PRICE": "0.002",
                    "OPENAI_RETRIES": "7",
                    "OPENAI_RETRY_SLEEP_TIME": "10",
                    "OPENAI_API_TYPE": "azure",
                    "AZURE_API_BASE": "https://something.com",
                    "AZURE_API_VERSION": "2023-05-15",
                    "AZURE_DEPLOYMENT_ID": "azure-id",
                },
                "expected_result": EnvVars(
                    api_key="****",
                    openai_model="model",
                    openai_input_price=0.001,
                    openai_output_price=0.002,
                    openai_retries=7,
                    openai_retry_sleep_time=10,
                    openai_type="azure",
                    azure_base="https://something.com",
                    azure_version="2023-05-15",
                    azure_deployment_id="azure-id",
                ),
            },
        ]
    )
)
def test_env_vars(
    is_frozen: bool,
    system: str,
    mocked_env_vars: Dict[str, str],
    expected_result: Union[str, EnvVars],
    mocker: MockFixture,
) -> None:
    """
    Tests the env variables in different situations.

    :param is_frozen: A flag to mock the `frozen` env. variable
    used to know if we are running inside a bundled pyinstaller system.
    :param system: The mocked system.
    :param mocked_env_vars: The mocked env variables.
    :param expected_result: The expected result.
    :param mocker: The mocking fixture.
    :return: None.
    """
    mocker.patch(function_import_path(platform.system), return_value=system)
    read_env_function = mocker.patch.object(environs.Env, "read_env")
    mocker.patch.dict(os.environ, mocked_env_vars)
    sys.frozen = is_frozen

    if isinstance(expected_result, str):
        with pytest.raises(EnvironmentError) as e:
            get_env_vars()
        assert expected_result in str(e)
    else:
        result = get_env_vars()
        assert expected_result == result

    if system == "Windows" and is_frozen:
        assert read_env_function.call_args_list[0].kwargs["recurse"] is False
    else:
        assert read_env_function.call_args_list[0] == call()
