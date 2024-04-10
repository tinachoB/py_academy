"""
Test for the config reader module.
"""
from pathlib import Path

import pytest

from code_generator.config_reader import config_reader
from code_generator.config_reader.types import ConfigData, FileTag, Paths, Prompt, Target, ValueTag
from tests import (
    CONFIG_COMMENT_INVALID_TYPE,
    CONFIG_EXTRA_FIELD,
    CONFIG_INVALID_JSON,
    CONFIG_OK,
    CONFIG_OK_WITH_ROOT,
    CONFIG_PATHS_EXTRA_FIELD,
    CONFIG_PATHS_INVALID_TYPE,
    CONFIG_PATHS_MISSING_OUTPUT,
    CONFIG_PATHS_MISSING_PATHS,
    CONFIG_PATHS_MISSING_PROMPTS,
    CONFIG_PATHS_MISSING_SCHEMAS,
    CONFIG_PATHS_MISSING_SOURCES,
    CONFIG_PATHS_OUTPUT_EMPTY,
    CONFIG_PATHS_OUTPUT_INVALID_TYPE,
    CONFIG_PATHS_PROMPTS_EMPTY,
    CONFIG_PATHS_PROMPTS_INVALID_TYPE,
    CONFIG_PATHS_SCHEMAS_EMPTY,
    CONFIG_PATHS_SCHEMAS_INVALID_TYPE,
    CONFIG_PATHS_SOURCES_EMPTY,
    CONFIG_PATHS_SOURCES_INVALID_TYPE,
    CONFIG_TARGET_GENERATE_INVALID_TYPE,
    CONFIG_TARGET_INVALID_TYPE,
    CONFIG_TARGET_MISSING_GENERATE,
    CONFIG_TARGET_OUTPUT_EMPTY,
    CONFIG_TARGETS_COMMENT_INVALID_TYPE,
    CONFIG_TARGETS_EMPTY,
    CONFIG_TARGETS_EXTRA_FIELD,
    CONFIG_TARGETS_MISSING_OUTPUT,
    CONFIG_TARGETS_MISSING_PROMPT,
    CONFIG_TARGETS_MISSING_TARGET,
    CONFIG_TARGETS_OUTPUT_INVALID_TYPE,
    CONFIG_TARGETS_PROMPT_EXTRA_FIELD,
    CONFIG_TARGETS_PROMPT_FILE_EMPTY,
    CONFIG_TARGETS_PROMPT_FILE_INVALID_TYPE,
    CONFIG_TARGETS_PROMPT_MISSING_TAGS,
    CONFIG_TARGETS_PROMPT_TAGS_FILE_EMPTY,
    CONFIG_TARGETS_PROMPT_TAGS_FILE_INVALID_TYPE,
    CONFIG_TARGETS_PROMPT_TAGS_INVALID_TYPE,
    CONFIG_TARGETS_PROMPT_TAGS_ITEM_FILE_AND_VALUE,
    CONFIG_TARGETS_PROMPT_TAGS_TAG_EMPTY,
    CONFIG_TARGETS_PROMPT_TAGS_TAG_EXTRA_FIELD,
    CONFIG_TARGETS_PROMPT_TAGS_TAG_INVALID_TYPE,
    CONFIG_TARGETS_PROMPT_TAGS_TAG_MISSING_FILE_AND_VALUE,
    CONFIG_TARGETS_PROMPT_TAGS_TAG_MISSING_TAG,
    CONFIG_TARGETS_PROMPT_TAGS_VALUE_EMPTY,
    CONFIG_TARGETS_PROMPT_TAGS_VALUE_INVALID_TYPE,
    OUTPUT_DIRECTORY,
    PROMPTS_DIRECTORY,
    SCHEMAS_DIRECTORY,
    SOURCES_DIRECTORY,
)
from tests.common_test_helpers import parametrize_wrapper

TARGETS = [
    Target(
        comment="Customer SCSS generation",
        generate=True,
        output="{output}/customer.scss",
        prompt=Prompt(
            file="{prompts}/angular.components.prompt",
            tags=[
                FileTag(tag="template_class", file="{sources}/components/employee.scss"),
                FileTag(tag="template_schema", file="{schemas}/employee.json"),
                FileTag(tag="target_schema", file="{schemas}/customers.json"),
                ValueTag(tag="type", value="scss"),
            ],
        ),
    ),
    Target(
        comment="",
        generate=False,
        output="{output}/customer.html",
        prompt=Prompt(
            file="{prompts}/angular.components.prompt",
            tags=[
                FileTag(tag="template_class", file="{sources}/components/employee.html"),
                FileTag(tag="template_schema", file="{schemas}/employee.json"),
                FileTag(tag="target_schema", file="{schemas}/customers.json"),
                ValueTag(tag="type", value="html"),
            ],
        ),
    ),
]

PATH_WITH_ROOT = Paths(
    root="home/code-generation",
    sources="{root}/frontend",
    prompts="{root}/prompts",
    schemas="{root}/schemas",
    output="{root}/output",
)

PATH_WITHOUT_ROOT = Paths(
    root="",
    sources="home/code-generation/frontend",
    prompts="home/code-generation/prompts",
    schemas="home/code-generation/schemas",
    output="home/code-generation/output",
)

EXPECTED_CONFIG_OK_WITH_ROOT = ConfigData(
    comment="This is well formed config file.", paths=PATH_WITH_ROOT, targets=TARGETS
)

EXPECTED_CONFIG_OK_WITHOUT_ROOT = ConfigData(
    comment="This is well formed config file.", paths=PATH_WITHOUT_ROOT, targets=TARGETS
)


#
# ConfigData NP to test the config data internal validation
#

CONFIG_INTERNAL_VALIDATION_FILE_OK = ConfigData(
    comment="This is well formed config file.",
    paths=Paths(
        sources=str(SOURCES_DIRECTORY),
        prompts=str(PROMPTS_DIRECTORY),
        schemas=str(SCHEMAS_DIRECTORY),
        output=str(OUTPUT_DIRECTORY),
    ),
    targets=[
        Target(
            comment="Customer SCSS generation",
            generate=True,
            output="{output}/address.html",
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
    ],
)


@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            {"config": "invalid file", "error": "Config file not found."},
            {"config": CONFIG_INVALID_JSON, "error": "Invalid JSON."},
            {
                "config": CONFIG_COMMENT_INVALID_TYPE,
                "error": "'comment' must be a string (optional)",
            },
            {
                "config": CONFIG_EXTRA_FIELD,
                "error": "Additional properties on config are not allowed",
            },
            {
                "config": CONFIG_PATHS_EXTRA_FIELD,
                "error": "Additional properties on 'paths' are not allowed",
            },
            {"config": CONFIG_PATHS_INVALID_TYPE, "error": "'paths' must be an object."},
            {
                "config": CONFIG_PATHS_OUTPUT_INVALID_TYPE,
                "error": "'paths.output' must be a string.",
            },
            {
                "config": CONFIG_PATHS_PROMPTS_INVALID_TYPE,
                "error": "'paths.prompts' must be a string.",
            },
            {
                "config": CONFIG_PATHS_SCHEMAS_INVALID_TYPE,
                "error": "'paths.schemas' must be a string.",
            },
            {
                "config": CONFIG_PATHS_SOURCES_INVALID_TYPE,
                "error": "'paths.sources' must be a string.",
            },
            {"config": CONFIG_PATHS_MISSING_PATHS, "error": "'paths' is a required property."},
            {
                "config": CONFIG_PATHS_MISSING_OUTPUT,
                "error": "'paths.output' is a required property.",
            },
            {
                "config": CONFIG_PATHS_MISSING_PROMPTS,
                "error": "'paths.prompts' is a required property.",
            },
            {
                "config": CONFIG_PATHS_MISSING_SCHEMAS,
                "error": "'paths.schemas' is a required property.",
            },
            {
                "config": CONFIG_PATHS_MISSING_SOURCES,
                "error": "'paths.sources' is a required property.",
            },
            {"config": CONFIG_PATHS_OUTPUT_EMPTY, "error": "'paths.output' cannot be empty."},
            {"config": CONFIG_PATHS_SOURCES_EMPTY, "error": "'paths.sources' cannot be empty."},
            {"config": CONFIG_PATHS_SCHEMAS_EMPTY, "error": "'paths.schemas' cannot be empty."},
            {"config": CONFIG_PATHS_PROMPTS_EMPTY, "error": "'paths.prompts' cannot be empty."},
            {"config": CONFIG_TARGETS_MISSING_TARGET, "error": "'targets' is a required array."},
            {"config": CONFIG_TARGET_INVALID_TYPE, "error": "'targets' must be an array."},
            {"config": CONFIG_TARGETS_EMPTY, "error": "'targets' cannot be an empty array."},
            {
                "config": CONFIG_TARGETS_EXTRA_FIELD,
                "error": "Additional properties on 'targets.items' are not allowed",
            },
            {
                "config": CONFIG_TARGETS_COMMENT_INVALID_TYPE,
                "error": "'targets.items.comment' must be a string (optional).",
            },
            {
                "config": CONFIG_TARGETS_MISSING_OUTPUT,
                "error": "'targets.items.output' is a required property.",
            },
            {
                "config": CONFIG_TARGETS_OUTPUT_INVALID_TYPE,
                "error": "'targets.items.output' must be a string.",
            },
            {
                "config": CONFIG_TARGET_OUTPUT_EMPTY,
                "error": "'targets.items.output' cannot be empty.",
            },
            {
                "config": CONFIG_TARGETS_MISSING_PROMPT,
                "error": "'targets.items.prompt' is a required property.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_EXTRA_FIELD,
                "error": "Additional properties are not allowed",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_FILE_INVALID_TYPE,
                "error": "'targets.items.prompt.file' must be a string.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_FILE_EMPTY,
                "error": "targets.items.prompt.file' cannot be empty.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_MISSING_TAGS,
                "error": "targets.items.prompt.tags' is a required array.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_INVALID_TYPE,
                "error": "targets.items.prompt.tags' must be an array.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_TAG_EXTRA_FIELD,
                "error": "Additional properties on 'targets.items.prompt.tags.items.tag' are not allowed",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_TAG_MISSING_TAG,
                "error": "'targets.items.prompt.tags.items.tag' is a required property.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_TAG_MISSING_FILE_AND_VALUE,
                "error": "'targets.items.prompt.tags.items.tag' missing 'file' or 'value' property.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_TAG_INVALID_TYPE,
                "error": "'targets.items.prompt.tags.items.tag' must be a string.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_TAG_EMPTY,
                "error": "'targets.items.prompt.tags.items.tag' cannot be empty.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_FILE_INVALID_TYPE,
                "error": "'targets.items.prompt.tags.items.tag.file' must be a string.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_FILE_EMPTY,
                "error": "'targets.items.prompt.tags.items.tag.file' cannot be empty.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_VALUE_INVALID_TYPE,
                "error": "'targets.items.prompt.tags.items.tag.value' must be a string.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_VALUE_EMPTY,
                "error": "'targets.items.prompt.tags.items.tag.value' cannot be empty.",
            },
            {
                "config": CONFIG_TARGETS_PROMPT_TAGS_ITEM_FILE_AND_VALUE,
                "error": "'targets.items.prompt.tags.items.tag' properties 'file' and 'value' are mutually exclusive.",
            },
            {
                "config": CONFIG_TARGET_MISSING_GENERATE,
                "error": "'targets.items.generate' is a required property.",
            },
            {
                "config": CONFIG_TARGET_GENERATE_INVALID_TYPE,
                "error": "'targets.items.generate' must be a boolean.",
            },
        ]
    )
)
def test__read_config_invalid_cases(config: Path, error: str) -> None:
    """
    Testing all the malformed config.json.

    :param config: The config to check.
    :param error: The expected error.
    :return: None.
    """
    with pytest.raises(Exception) as e:
        config_reader._read_config(str(config))
    assert error in str(e)


@pytest.mark.parametrize(
    **parametrize_wrapper(
        [
            {"config": CONFIG_OK, "expected_result": EXPECTED_CONFIG_OK_WITHOUT_ROOT},
            {
                "config": CONFIG_OK_WITH_ROOT,
                "expected_result": EXPECTED_CONFIG_OK_WITH_ROOT,
            },
        ]
    )
)
def test__read_config_success_case(config: Path, expected_result: ConfigData) -> None:
    """
    Testing a well-formed config file.

    :param config: The path of the config to be tested.
    :return: None.
    """
    config_data = config_reader._read_config(str(config))
    result = config_reader._convert_config_data(config_data)

    assert expected_result == result


def test__read_config_internal_data_success_case() -> None:
    """
    Testing a well-formed, with valid paths, config file.

    :return: None.
    """
    try:
        config_reader._validate_config_data(CONFIG_INTERNAL_VALIDATION_FILE_OK)
    except Exception as e:
        assert False
