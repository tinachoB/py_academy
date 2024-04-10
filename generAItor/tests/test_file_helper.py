"""
Test for the file helper module.
"""
import pytest

from code_generator.commons.file_helper import analyze_zip_data, unzip_file
from tests import ASSETS_ZIP_DIRECTORY
from tests.common_test_helpers import parametrize_wrapper


def test_unzip_file() -> None:
    """
    Testing that an existing file is being opened successfully.

    :return: None.
    """
    try:
        zip_file = ASSETS_ZIP_DIRECTORY.joinpath("Test.zip")
        with open(zip_file, "r") as f:
            content = f.buffer
            assert unzip_file(content) is not None
    except Exception as e:
        assert False


@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            {"test_file": "Test.zip", "expected_result": True},
            {"test_file": "Test_bad.zip", "expected_result": False},
        ]
    )
)
def test_analyze_zip_data(test_file: str, expected_result: bool) -> None:
    """
    Testing that an existing file is analyzed appropriately successfully.

    :return: None.
    """
    try:
        zip_file = ASSETS_ZIP_DIRECTORY.joinpath(test_file)
        with open(zip_file, "r") as f:
            content = f.buffer
            assert analyze_zip_data(unzip_file(content)) == expected_result
    except Exception as e:
        assert False
