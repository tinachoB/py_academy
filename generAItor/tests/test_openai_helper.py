"""
Test for the OpenAIHelper class.
"""
import logging
import time
from typing import Dict, List, Optional

import openai
import pytest
from _pytest.logging import LogCaptureFixture
from openai import ChatCompletion
from pytest_mock import MockFixture

from code_generator.commons.env_variables import EnvVars
from code_generator.commons.openai_helper import OpenAIHelper
from tests.common_test_helpers import function_import_path, parametrize_wrapper

AZURE_ENV_VARS = EnvVars(
    api_key="open-ai-key",
    openai_model="open-ai-model",
    azure_base="azure-base",
    azure_version="azure-version",
    azure_deployment_id="azure-deployment-id",
    openai_type="azure",
)

OPENAI_ENV_VAR = EnvVars(
    api_key="open-ai-key",
    openai_model="open-ai-model",
    azure_base=None,
    azure_version=None,
    azure_deployment_id=None,
    openai_type=None,
)


@pytest.mark.parametrize(argnames="env_vars", argvalues=[OPENAI_ENV_VAR, AZURE_ENV_VARS])
def test_openai_helper_initialization(env_vars: EnvVars) -> None:
    """
    Tests the OpenAIHelper initialization.

    :param env_vars: The env. vars used to initialize the object.
    :return: None.
    """

    helper = OpenAIHelper(env_vars=env_vars)

    assert openai.api_key == env_vars.api_key

    assert helper._openai_model == env_vars.openai_model
    assert helper._engine == env_vars.azure_deployment_id

    assert helper._completion_tokens == 0
    assert helper._prompt_tokens == 0
    assert helper._total_tokens == 0

    if env_vars == AZURE_ENV_VARS:
        assert openai.api_type == env_vars.openai_type
        assert openai.api_base == env_vars.azure_base
        assert openai.api_version == env_vars.azure_version
    else:
        assert openai.api_type == openai.api_type
        assert openai.api_base == openai.api_base
        assert openai.api_version == openai.api_version

    assert helper.stats.prompt_tokens == 0
    assert helper.stats.total_tokens == 0
    assert helper.stats.completion_tokens == 0


def _mock_completion_result(content: str, prompt_tokens: int, completion_token: int):
    return {
        "choices": [
            {"message": {"content": content}},
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_token,
            "total_tokens": prompt_tokens + completion_token,
        },
    }


@pytest.mark.parametrize(argnames="env_vars", argvalues=[OPENAI_ENV_VAR, AZURE_ENV_VARS])
@pytest.mark.parametrize(argnames="show_error_log", argvalues=[True, False])
@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            # Happy path
            {
                "completion_results": [
                    _mock_completion_result(content="text", prompt_tokens=1, completion_token=2)
                ],
                "retries": 1,
                "expected_completion_call_count": 1,
                "expected_sleep_call_count": 0,
                "expected_result": "text",
                "expected_stats": [1, 2, 3],
            },
            # First try failed.
            {
                "completion_results": [
                    ValueError("some error"),
                    _mock_completion_result(content="text", prompt_tokens=1, completion_token=2),
                ],
                "retries": 3,
                "expected_completion_call_count": 2,
                "expected_sleep_call_count": 1,
                "expected_result": "text",
                "expected_stats": [1, 2, 3],
            },
            # One retry, one failed.
            {
                "completion_results": [
                    ValueError("some error"),
                ],
                "retries": 1,
                "expected_completion_call_count": 1,
                "expected_sleep_call_count": 0,
                "expected_result": None,
                "expected_stats": [0, 0, 0],
            },
            # All tries failed.
            {
                "completion_results": [
                    ValueError("some error"),
                    ValueError("some error"),
                    ValueError("some error"),
                ],
                "retries": 3,
                "expected_completion_call_count": 3,
                "expected_sleep_call_count": 2,
                "expected_result": None,
                "expected_stats": [0, 0, 0],
            },
        ]
    )
)
def test_openai_helper_consume(
    env_vars: EnvVars,
    show_error_log: bool,
    completion_results: List[Dict[str, str]],
    retries: int,
    expected_completion_call_count: int,
    expected_sleep_call_count: int,
    expected_result: Optional[str],
    expected_stats: List[int],
    caplog: LogCaptureFixture,
    mocker: MockFixture,
) -> None:
    """
    Testing the `consume` method in different situations.

    :param env_vars: The env vars used to create the object.
    :param show_error_log: Flag used on the method call.
    :param completion_results:  Mocked completion results.
    :param retries: Number of retries.
    :param expected_completion_call_count: Expected completion call count.
    :param expected_sleep_call_count: Expected sleep call count.
    :param expected_result: Expected result.
    :param expected_stats: Expected stats.
    :param caplog: The log capture fixture.
    :param mocker: The mocker fixture.
    :return: None.
    """
    caplog.set_level(level=logging.DEBUG)

    # Mocking the sleep
    sleep_function = mocker.patch(function_import_path(time.sleep))

    # Mocking the OpenAI object
    completion_function = mocker.patch.object(
        ChatCompletion, "create", side_effect=completion_results
    )

    # Creating the helper
    helper = OpenAIHelper(env_vars=env_vars)

    # Calling the function to test
    result = helper.consume(prompt="some prompt", show_error_log=show_error_log, retries=retries)

    # Checking function result
    assert expected_result == result

    # Checking internals calls
    assert completion_function.call_count == expected_completion_call_count

    # Checking internal logs and sleep time
    if any([isinstance(i, Exception) for i in completion_results]):
        assert sleep_function.call_count == expected_sleep_call_count

        if expected_sleep_call_count > 0:
            assert "Waiting 5 secs. to retry..." in caplog.text

        if show_error_log:
            assert "Error: " in caplog.text
        else:
            assert "Error: " not in caplog.text

    # Checking expected stats
    assert helper.stats.prompt_tokens == expected_stats[0]
    assert helper.stats.completion_tokens == expected_stats[1]
    assert helper.stats.total_tokens == expected_stats[2]
