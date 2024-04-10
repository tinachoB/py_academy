"""
Tests to actually generate some new code from a python source file.
"""
import logging
import os.path
import subprocess
import sys

import pytest
from _pytest.logging import LogCaptureFixture

from code_generator.commons.env_variables import get_env_vars
from code_generator.config_reader.types import ConfigData, FileTag, Paths, Prompt, Target
from code_generator.generator.generator import generate_code
from tests import OUTPUT_DIRECTORY, PROMPTS_DIRECTORY, SCHEMAS_DIRECTORY, SOURCES_DIRECTORY

_CONFIG = ConfigData(
    paths=Paths(
        prompts=str(PROMPTS_DIRECTORY),
        schemas=str(SCHEMAS_DIRECTORY),
        sources=str(SOURCES_DIRECTORY),
        output=str(OUTPUT_DIRECTORY),
    ),
    targets=[
        Target(
            generate=True,
            output="{output}/item.py",
            prompt=Prompt(
                file="{prompts}/python_item.prompt",
                tags=[
                    FileTag(tag="{{source_code}}", file="{sources}/person.py"),
                    FileTag(tag="{{source_schema}}", file="{schemas}/python_person_schema.json"),
                    FileTag(tag="{{target_schema}}", file="{schemas}/python_item_schema.json"),
                ],
            ),
        ),
        Target(
            generate=True,
            output="{output}/test_item.py",
            prompt=Prompt(
                file="{prompts}/python_item_tests.prompt",
                tags=[
                    FileTag(tag="{{source_tests}}", file="{sources}/person_tests.py"),
                    FileTag(tag="{{source_class}}", file="{sources}/person.py"),
                    FileTag(tag="{{target_class}}", file="{output}/item.py"),
                ],
            ),
        ),
    ],
)


@pytest.mark.end_to_end
def test_solution(caplog: LogCaptureFixture) -> None:
    """
    Testing the end-to-end process to generate an item.py and
    test_item.py files.

    :param caplog: The log capture fixture.
    :return: None.
    """
    caplog.set_level(level=logging.DEBUG)

    # Removing previous files
    if os.path.exists(OUTPUT_DIRECTORY):
        for file in os.listdir(OUTPUT_DIRECTORY):
            if not file.startswith("__"):
                os.remove(os.path.join(OUTPUT_DIRECTORY, file))

    try:
        # Generating the Item.py and its tests from Person.py
        generate_code(
            config=_CONFIG,
            env_vars=get_env_vars(),
            log=str(OUTPUT_DIRECTORY.joinpath("log.txt")),
            debug=True,
            stats=True,
        )

        # Checking the generated item.py
        if not os.path.exists(OUTPUT_DIRECTORY.joinpath("item.py")):
            pytest.fail("Error creating item.py")

        # Checking the generated test_item.py
        if not os.path.exists(OUTPUT_DIRECTORY.joinpath("test_item.py")):
            pytest.fail("Error creating test_item.py")

        # Running the generated tests
        return_code = pytest.main([str(OUTPUT_DIRECTORY.joinpath("test_item.py"))])

        # Checking the tests' results
        if return_code != 0:
            pytest.fail(f"Test test_item.py FAILED!")

    except Exception as e:
        pytest.fail(f"Error: {str(e)}")
