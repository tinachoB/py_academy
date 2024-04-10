"""Uses pathlib to make referencing test assets by path easier."""

import os
from pathlib import Path

TEST_DIRECTORY = Path(os.path.dirname(os.path.abspath(__file__)))

# Assets for config
ASSETS_DIRECTORY = TEST_DIRECTORY.joinpath("assets")

# Zip assets directory
ASSETS_ZIP_DIRECTORY = ASSETS_DIRECTORY.joinpath("zip")

# Config directory
CONFIG_DIRECTORY = ASSETS_DIRECTORY.joinpath("config")

CONFIG_OK = CONFIG_DIRECTORY.joinpath("config_ok.json")
CONFIG_OK_WITH_ROOT = CONFIG_DIRECTORY.joinpath("config_ok_with_root.json")
CONFIG_EXTRA_FIELD = CONFIG_DIRECTORY.joinpath("config_extra_field.json")
CONFIG_PATHS_EXTRA_FIELD = CONFIG_DIRECTORY.joinpath("config_paths_extra_field.json")
CONFIG_PATHS_INVALID_TYPE = CONFIG_DIRECTORY.joinpath("config_paths_invalid_type.json")
CONFIG_PATHS_MISSING_OUTPUT = CONFIG_DIRECTORY.joinpath("config_paths_missing_output.json")
CONFIG_PATHS_MISSING_PATHS = CONFIG_DIRECTORY.joinpath("config_paths_missing_paths.json")
CONFIG_PATHS_MISSING_PROMPTS = CONFIG_DIRECTORY.joinpath("config_paths_missing_prompts.json")
CONFIG_PATHS_MISSING_SCHEMAS = CONFIG_DIRECTORY.joinpath("config_paths_missing_schemas.json")
CONFIG_PATHS_MISSING_SOURCES = CONFIG_DIRECTORY.joinpath("config_paths_missing_sources.json")
CONFIG_PATHS_OUTPUT_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_paths_output_invalid_type.json"
)
CONFIG_PATHS_PROMPTS_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_paths_prompts_invalid_type.json"
)
CONFIG_PATHS_SCHEMAS_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_paths_schemas_invalid_type.json"
)
CONFIG_PATHS_SOURCES_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_paths_sources_invalid_type.json"
)
CONFIG_TARGETS_EMPTY = CONFIG_DIRECTORY.joinpath("config_targets_empty.json")
CONFIG_TARGETS_EXTRA_FIELD = CONFIG_DIRECTORY.joinpath("config_targets_extra_field.json")
CONFIG_TARGETS_MISSING_OUTPUT = CONFIG_DIRECTORY.joinpath("config_targets_missing_output.json")
CONFIG_TARGETS_MISSING_PROMPT = CONFIG_DIRECTORY.joinpath("config_targets_missing_prompt.json")
CONFIG_TARGETS_MISSING_TARGET = CONFIG_DIRECTORY.joinpath("config_targets_missing_target.json")
CONFIG_TARGETS_OUTPUT_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_targets_output_invalid_type.json"
)
CONFIG_TARGETS_PROMPT_EXTRA_FIELD = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_extra_field.json"
)
CONFIG_TARGETS_PROMPT_FILE_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_file_invalid_type.json"
)
CONFIG_TARGETS_PROMPT_MISSING_TAGS = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_missing_tags.json"
)
CONFIG_TARGETS_PROMPT_TAGS_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_invalid_type.json"
)
CONFIG_TARGETS_PROMPT_TAGS_TAG_EXTRA_FIELD = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_tag_extra_field.json"
)
CONFIG_PATHS_OUTPUT_EMPTY = CONFIG_DIRECTORY.joinpath("config_paths_output_empty.json")
CONFIG_PATHS_SOURCES_EMPTY = CONFIG_DIRECTORY.joinpath("config_paths_sources_empty.json")
CONFIG_PATHS_SCHEMAS_EMPTY = CONFIG_DIRECTORY.joinpath("config_paths_schemas_empty.json")
CONFIG_PATHS_PROMPTS_EMPTY = CONFIG_DIRECTORY.joinpath("config_paths_prompts_empty.json")
CONFIG_TARGET_INVALID_TYPE = CONFIG_DIRECTORY.joinpath("config_target_invalid_type.json")
CONFIG_TARGET_OUTPUT_EMPTY = CONFIG_DIRECTORY.joinpath("config_targets_output_empty.json")
CONFIG_TARGETS_PROMPT_FILE_EMPTY = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_file_empty.json"
)
CONFIG_TARGETS_PROMPT_TAGS_TAG_MISSING_TAG = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_tag_missing_tag.json"
)
CONFIG_TARGETS_PROMPT_TAGS_TAG_MISSING_FILE_AND_VALUE = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_tag_missing_file_and_value.json"
)
CONFIG_TARGETS_PROMPT_TAGS_TAG_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_tag_invalid_type.json"
)
CONFIG_TARGETS_PROMPT_TAGS_TAG_EMPTY = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_tag_empty.json"
)
CONFIG_TARGETS_PROMPT_TAGS_FILE_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_file_invalid_type.json"
)
CONFIG_TARGETS_PROMPT_TAGS_FILE_EMPTY = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_file_empty.json"
)
CONFIG_TARGETS_PROMPT_TAGS_VALUE_EMPTY = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_value_empty.json"
)
CONFIG_TARGETS_PROMPT_TAGS_VALUE_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_value_invalid_type.json"
)
CONFIG_TARGETS_PROMPT_TAGS_ITEM_FILE_AND_VALUE = CONFIG_DIRECTORY.joinpath(
    "config_targets_prompt_tags_item_file_and_value.json"
)
CONFIG_INVALID_JSON = CONFIG_DIRECTORY.joinpath("config_invalid_json.json")
CONFIG_COMMENT_INVALID_TYPE = CONFIG_DIRECTORY.joinpath("config_comment_invalid_type.json")
CONFIG_TARGETS_COMMENT_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_targets_comment_invalid_type.json"
)
CONFIG_TARGET_MISSING_GENERATE = CONFIG_DIRECTORY.joinpath("config_target_missing_generate.json")
CONFIG_TARGET_GENERATE_INVALID_TYPE = CONFIG_DIRECTORY.joinpath(
    "config_target_generate_invalid_type.json"
)


# Dirs used to test the generator
GENERATOR_DIRECTORY = ASSETS_DIRECTORY.joinpath("generator")
PROMPTS_DIRECTORY = GENERATOR_DIRECTORY.joinpath("prompts")
SCHEMAS_DIRECTORY = GENERATOR_DIRECTORY.joinpath("schemas")
SOURCES_DIRECTORY = GENERATOR_DIRECTORY.joinpath("sources")
OUTPUT_DIRECTORY = GENERATOR_DIRECTORY.joinpath("output")

EXPECTED_FORMATTED_PROMPT = GENERATOR_DIRECTORY.joinpath("expected_formatted_prompt.prompt")
GENERATOR_OUTPUT_TEST_DIR = GENERATOR_DIRECTORY.joinpath("output")
