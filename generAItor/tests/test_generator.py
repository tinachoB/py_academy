"""
Test for the generator module.
"""
import logging
import os
from typing import List, Optional
from unittest.mock import MagicMock

import pytest
from _pytest.logging import LogCaptureFixture
from pytest_mock import MockFixture

from code_generator.commons import file_helper
from code_generator.commons.code_stats import CodeStatsCounter
from code_generator.config_reader.types import FileTag, Paths, Prompt, Target, ValueTag
from code_generator.generator import generator
from code_generator.generator.types import TargetData
from tests import (
    EXPECTED_FORMATTED_PROMPT,
    GENERATOR_OUTPUT_TEST_DIR,
    PROMPTS_DIRECTORY,
    SCHEMAS_DIRECTORY,
    SOURCES_DIRECTORY,
)
from tests.common_test_helpers import function_import_path, parametrize_wrapper

# A Path NT with paths based on the assets dirs.
_PATHS = Paths(
    prompts=str(PROMPTS_DIRECTORY),
    schemas=str(SCHEMAS_DIRECTORY),
    sources=str(SOURCES_DIRECTORY),
    output="home/some_output_dir",
)

# A Target NT with data based on the assets dirs and files.
_TARGET_HTML = Target(
    generate=True,
    comment="None",
    output="{output}/generated_file.html",
    prompt=Prompt(
        file="{prompts}/address.prompt",
        tags=[
            FileTag(tag="{{source_code}}", file="{sources}/person.html"),
            FileTag(tag="{{source_schema}}", file="{schemas}/person_schema.json"),
            FileTag(tag="{{target_schema}}", file="{schemas}/address_schema.json"),
            ValueTag(tag="{{type}}", value="html"),
        ],
    ),
)


def test__get_target_data_success(
    caplog: LogCaptureFixture,
) -> None:
    """
    Testing the _get_target_data with valid data.

    :param caplog: The capture log fixture.
    :return: None.
    """
    # Calling the function under test
    target_data = generator._get_target_data(target=_TARGET_HTML, paths=_PATHS)

    # Reading the expected generated target
    with open(EXPECTED_FORMATTED_PROMPT) as expected_prompt:
        expected_data = TargetData(
            output_file="home/some_output_dir/generated_file.html", prompt=expected_prompt.read()
        )

    # Checking the result
    assert expected_data == target_data
    assert caplog.messages == []


def test__get_target_data_error(caplog: LogCaptureFixture, mocker: MockFixture) -> None:
    """
    Testing the _get_target_data with an error case.
    The function should return None.

    :param caplog: The capture log fixture.
    :param mocker: The mocking fixture.
    :return: None.
    """

    # Mocking one of the inner functions used by _get_target_data
    # to force an exception.
    mocker.patch(
        function_import_path(file_helper.get_file_content),
        side_effect=FileNotFoundError("File not found"),
    )

    # Calling the function under test
    target_data = generator._get_target_data(target=_TARGET_HTML, paths=_PATHS)

    assert target_data is None
    assert caplog.messages == [
        "Error trying to get target data. Error: File not found - Skipping target..."
    ]


@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            # Invalid file. Must be an error.
            {"file_path": "invalid:path/file.txt", "expected_error": True},
            # Success case.
            {
                "file_path": str(GENERATOR_OUTPUT_TEST_DIR.joinpath("file.txt")),
                "expected_error": False,
            },
        ]
    )
)
def test__create_target_file(
    file_path: str, expected_error: bool, caplog: LogCaptureFixture, mocker: MockFixture
) -> None:
    """
    Testing the _create_target_file function.

    :param file_path: The path to the file to be created.
    :param expected_error: Flag indicating if an error must be triggered.
    :param caplog: The capture log fixture.
    :param mocker: The mocking fixture.
    :return: None.
    """

    # Removing previous files
    if os.path.exists(GENERATOR_OUTPUT_TEST_DIR):
        for file in os.listdir(GENERATOR_OUTPUT_TEST_DIR):
            if not file.startswith("__"):
                os.remove(os.path.join(GENERATOR_OUTPUT_TEST_DIR, file))

    # Mocking an exception
    if expected_error:
        mocker.patch(
            function_import_path(os.makedirs),
            side_effect=FileNotFoundError("Error creating dirs"),
        )

    # Calling the function under test
    mocked_file_content = "*" * 1024
    response = generator._create_target_file(file_path=file_path, content=mocked_file_content)

    # Checking the results
    if expected_error:
        assert not os.path.exists(file_path)
        assert caplog.messages == ["Error creating target file. Error: Error creating dirs"]
        assert response is False
    else:
        with open(file_path, "rt", encoding="utf-8") as file:
            assert mocked_file_content == file.read()
            assert response is True


@pytest.mark.parametrize(argnames="chat_response", argvalues=["something", None])
@pytest.mark.parametrize(argnames="create_target_file_response", argvalues=[True, False])
def test__generate_target(
    chat_response: Optional[str], create_target_file_response: bool, mocker: MockFixture
) -> None:
    """
    Testing the _generate_target function.

    :param chat_response: The mocked response from Chat-GPT.
    :param create_target_file_response: The mocked response of the function.
    :param mocker: The mocking fixture.
    :return: None.
    """

    target = TargetData(prompt="Some prompt", output_file="some_file.txt")

    # Mocking the chat assistant
    chat_assistant = MagicMock()
    chat_assistant.consume = MagicMock(return_value=chat_response)

    # Mocking the function to create the target
    crate_target_function = mocker.patch(
        function_import_path(generator._create_target_file),
        return_value=create_target_file_response,
    )

    result = generator._generate_target(
        target=target, chat_assistant=chat_assistant, retries=1, retry_sleep_time=1
    )

    # Checking behavior
    assert crate_target_function.called == (chat_response is not None)
    assert result == (chat_response is not None and create_target_file_response)


@pytest.mark.parametrize(argnames="debug", argvalues=[True, False])
@pytest.mark.parametrize(argnames="stats", argvalues=[True, False])
@pytest.mark.parametrize(argnames="verbose", argvalues=[True, False])
@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            # Nothing to generate
            {"targets": [], "get_target_results": [], "expected_generate_target_call_count": 0},
            # Two targets to generate.
            {
                "targets": [MagicMock(), MagicMock()],
                "get_target_results": [MagicMock(), MagicMock()],
                "expected_generate_target_call_count": 2,
            },
            # Three targets to generate but an error was found trying to get one of them
            {
                "targets": [MagicMock(), MagicMock(), MagicMock()],
                "get_target_results": [MagicMock(), None, MagicMock()],
                "expected_generate_target_call_count": 2,
            },
            # Three targets to generate but an error was found trying to get all of them
            {
                "targets": [MagicMock(), MagicMock(), MagicMock()],
                "get_target_results": [None, None, None],
                "expected_generate_target_call_count": 0,
            },
        ]
    )
)
def test_generate_code(
    debug: bool,
    verbose: bool,
    stats: bool,
    targets: List[MagicMock],
    get_target_results: List[MagicMock],
    expected_generate_target_call_count: int,
    caplog: LogCaptureFixture,
    mocker: MockFixture,
) -> None:
    """
    Testing the generate_code function.

    :param debug: Indicates if debug is on or off.
    :param verbose: Verbosity level.
    :param stats: Indicates if stats must be collected.
    :param targets: The mocked targets.
    :param get_target_results: Mocked values for the _get_target_data function.
    :param expected_generate_target_call_count: Expected call count for the
    _generate_target function.
    :param caplog: The capture log fixture.
    :param mocker: The mocking fixture.
    :return: None.
    """

    caplog.set_level(level=logging.DEBUG)

    # Checking the test params
    assert len(targets) == len(get_target_results), "Check the test parameters."

    # Mocking
    config = MagicMock()
    config.targets = targets

    env_vars = MagicMock()
    env_vars.openai_input_price = 0.003
    env_vars.openai_output_price = 0.004

    # Mocking the inner functions to be called
    get_target_data_function = mocker.patch(
        function_import_path(generator._get_target_data), side_effect=get_target_results
    )
    generate_target_function = mocker.patch(function_import_path(generator._generate_target))

    # Mocking the CodeStats
    get_stats_function = mocker.patch.object(CodeStatsCounter, "get_stats")

    # Calling the function under test
    generator.generate_code(
        config=config, env_vars=env_vars, log=None, debug=debug, verbose=verbose, stats=stats
    )

    # Checking the expected behavior
    assert get_target_data_function.call_count == len(targets)
    assert expected_generate_target_call_count == generate_target_function.call_count

    generated_targets_count = len(list(filter(None, get_target_results)))

    if verbose:
        if generated_targets_count > 0:
            assert "Generated prompt" in caplog.text
        else:
            assert "Generated prompt" not in caplog.text
    else:
        assert "Generated prompt" not in caplog.text

    if generated_targets_count > 0:
        if stats:
            assert get_stats_function.call_count == generated_targets_count

            assert "Code Stats" in caplog.text
            assert "Code lines count" in caplog.text
            assert "Comment lines count" in caplog.text
            assert "Empty lines count" in caplog.text
            assert "OpenAI Stats" in caplog.text
            assert "Prompt" in caplog.text
            assert "Completion" in caplog.text
            assert "Input Charges : USD 0.0000" in caplog.text
            assert "Output Charges: USD 0.0000" in caplog.text
            assert "Total Charges : USD 0.0000" in caplog.text
        else:
            assert not get_stats_function.called
            assert "Code Stats" not in caplog.text
            assert "Code lines count" not in caplog.text
            assert "Comment lines count" not in caplog.text
            assert "Empty lines count" not in caplog.text
            assert "OpenAI Token Stats" not in caplog.text
            assert "Prompt" not in caplog.text
            assert "Completion" not in caplog.text
