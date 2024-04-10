"""
Tests for the CodeStats class
"""
import json
import subprocess
from typing import Dict, List, Optional, Union

import pytest
from pytest_mock import MockFixture

from code_generator.commons.code_stats import CodeStats, CodeStatsCounter
from tests.common_test_helpers import function_import_path, parametrize_wrapper


def _create_pygount_response(code_lines: int, empty_lines: int, comment_lines: int) -> str:
    """
    Helper to create a std with a mocked result for the `pygount` command.

    :param code_lines: The number of lines of codes.
    :param empty_lines: The number of empty lines.
    :param comment_lines: The number of comment lines.
    :return: A json string.
    """
    return json.dumps(
        {
            "summary": {
                "totalSourceCount": code_lines,
                "totalDocumentationCount": comment_lines,
                "totalEmptyCount": empty_lines,
            }
        }
    )


@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            # All process calls were ok
            {
                "process_mocked_result": [
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout=_create_pygount_response(
                            code_lines=10, empty_lines=0, comment_lines=5
                        ),
                        stderr="",
                    ),
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout=_create_pygount_response(
                            code_lines=50, empty_lines=5, comment_lines=10
                        ),
                        stderr="",
                    ),
                ],
                "expected_results": [
                    CodeStats(code_lines_count=10, empty_lines_count=0, comments_lines_count=5),
                    CodeStats(code_lines_count=50, empty_lines_count=5, comments_lines_count=10),
                ],
                "expected_final_count": CodeStats(
                    code_lines_count=60, empty_lines_count=5, comments_lines_count=15
                ),
            },
            # One of the process call return a non-zero exit code.
            {
                "process_mocked_result": [
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=1,  # <<<< Error
                        stdout="",
                        stderr="some error here",
                    ),
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout=_create_pygount_response(
                            code_lines=50, empty_lines=5, comment_lines=10
                        ),
                        stderr="",
                    ),
                ],
                "expected_results": [
                    None,
                    CodeStats(code_lines_count=50, empty_lines_count=5, comments_lines_count=10),
                ],
                "expected_final_count": CodeStats(
                    code_lines_count=50, empty_lines_count=5, comments_lines_count=10
                ),
            },
            # One of the process call throws an exception
            {
                "process_mocked_result": [
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout=_create_pygount_response(
                            code_lines=10, empty_lines=0, comment_lines=5
                        ),
                        stderr="",
                    ),
                    ValueError("some error"),
                    subprocess.CompletedProcess(
                        args=[],
                        returncode=0,
                        stdout=_create_pygount_response(
                            code_lines=50, empty_lines=5, comment_lines=10
                        ),
                        stderr="",
                    ),
                ],
                "expected_results": [
                    CodeStats(code_lines_count=10, empty_lines_count=0, comments_lines_count=5),
                    None,
                    CodeStats(code_lines_count=50, empty_lines_count=5, comments_lines_count=10),
                ],
                "expected_final_count": CodeStats(
                    code_lines_count=60, empty_lines_count=5, comments_lines_count=15
                ),
            },
            # All the process calls throw exceptions
            {
                "process_mocked_result": [
                    ValueError("some error"),
                    ValueError("some error"),
                    ValueError("some error"),
                ],
                "expected_results": [None, None, None],
                "expected_final_count": CodeStats(
                    code_lines_count=0, empty_lines_count=0, comments_lines_count=0
                ),
            },
        ]
    )
)
def test_code_stats(
    process_mocked_result: List[Union[Exception, subprocess.CompletedProcess]],
    expected_results: List[Optional[CodeStats]],
    expected_final_count: CodeStats,
    mocker: MockFixture,
) -> None:
    """
    Tests the CodeStatsCounter in different scenarios.

    :param process_mocked_result: The mocked results for the process execution.
    :param expected_results: The expected result for the get_stats function call.
    :param expected_final_count: The expected final count.
    :param mocker: The mocker fixture.
    :return: None
    """

    counter = CodeStatsCounter()

    # Checking initial behavior
    assert counter.stats.code_lines_count == 0
    assert counter.stats.empty_lines_count == 0
    assert counter.stats.comments_lines_count == 0

    mocker.patch(
        function_import_path(subprocess.run),
        side_effect=process_mocked_result,
    )

    # Testing the get_stats function
    for i in range(len(process_mocked_result)):
        result = counter.get_stats(file="some-file.txt")
        assert result == expected_results[i]

    # Checking the final count
    assert counter.stats == expected_final_count
