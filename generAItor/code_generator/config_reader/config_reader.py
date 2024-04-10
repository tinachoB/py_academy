"""
Reader for the config file.
"""
import json
import logging
import os
from typing import List, Optional, Union

import jsonschema
from click import BadParameter
from jsonschema.validators import Draft202012Validator

from code_generator.commons.file_helper import format_file_path, get_file_content
from code_generator.config_reader import CONFIG_SCHEMA, schema_validations
from code_generator.config_reader.dict_types import (
    ConfigObjData,
    FileTagObj,
    TargetObj,
    ValueTagObj,
)
from code_generator.config_reader.types import ConfigData, FileTag, Paths, Prompt, Target, ValueTag

LOGGER = logging.getLogger(__name__)

_SOURCE_FILE_TAG = "source_code"


def _read_config(config_file: str) -> ConfigObjData:
    """
    Reads the config file.
    :return: The content of the file converted into a dict.
    """
    try:
        with open(config_file, "r") as file:
            json_data: ConfigObjData = json.load(file)
            schema_dir = os.path.dirname(CONFIG_SCHEMA)
            with open(CONFIG_SCHEMA, "r") as schema:
                json_schema = json.load(schema)
                resolver = jsonschema.RefResolver(f"file:///{schema_dir}/", None)
                validator = jsonschema.validators.extend(Draft202012Validator)
                jsonschema.validate(
                    instance=json_data, schema=json_schema, cls=validator, resolver=resolver
                )
                return json_data
    except FileNotFoundError as e:
        raise BadParameter("Error: Config file not found.") from e
    except json.JSONDecodeError as e:
        raise BadParameter(f"Error: Invalid JSON. {e.msg}") from e
    except jsonschema.ValidationError as e:
        raise schema_validations.validate(e) from e


def _check_path_existence(file_path: str) -> Optional[str]:
    """
    Checks if a file truly exists or not and adds
    an error if it's not.
    :param file_path: File to check.
    :return: Str error message if there is any.
    """
    if not os.path.exists(file_path):
        return f"The specific {file_path} file does not exist"
    return None


def _check_tag_files(target: Target, paths: Paths) -> Optional[str]:
    """
    Checks the existence of the specific tag's information except for the
    '{{source_code}}' one. This will be checked in execution time in the
    generator.py file, _get_target_data method.
    :param target: Target object to check
    :param paths: Values to fill the entire prompt file path
    :return: Str error message if there is any.
    """
    # List to concatenate all errors and show them, if exist any, at once
    error_msg: Optional[str] = None
    # Tag's files
    for tag in target.prompt.tags:
        if isinstance(tag, FileTag):
            if _SOURCE_FILE_TAG not in tag.tag:
                # Skipping source_code checking here because it'll be checked during
                # code generation to allow dynamic generated files to be used as source
                # code files in further targets
                error_msg = _check_path_existence(file_path=format_file_path(tag.file, paths))
    return error_msg


def _validate_config_paths(config_data: ConfigData, paths: Paths) -> List[str]:
    """
    Checks all config file paths existence.
    :param config_data: Config object to iterate and look for path existence.
    :param paths: Paths values
    :return: List of errors, if any.
    """
    # List to concatenate all errors and show them, if exist any, at once
    error_list: List[Union[None, str]] = []

    # Paths
    if config_data.paths.root != "":
        error_list.append(
            _check_path_existence(file_path=format_file_path(config_data.paths.root, paths))
        )
    error_list.append(
        _check_path_existence(file_path=format_file_path(config_data.paths.sources, paths))
    )
    error_list.append(
        _check_path_existence(file_path=format_file_path(config_data.paths.prompts, paths))
    )
    error_list.append(
        _check_path_existence(file_path=format_file_path(config_data.paths.schemas, paths))
    )
    error_list.append(
        _check_path_existence(file_path=format_file_path(config_data.paths.output, paths))
    )

    # Target's prompt files
    for target in config_data.targets:
        error_list.append(
            _check_path_existence(file_path=format_file_path(target.prompt.file, paths))
        )
        # Tag's files (check everything except '{{source_code}}' tag
        error_list.append(_check_tag_files(target=target, paths=paths))
    # Return only the error list str without None values
    return list(filter(None, error_list))


def _validate_prompt_tags(prompt: Prompt, paths: Paths) -> List[str]:
    """
    Checks that the prompt file content and tags listed match appropriately
    :param prompt: Prompt object check
    :param paths: Values to fill the entire prompt file path
    :return: List of errors, if any.
    """
    # List to concatenate all errors and show them, if exist any, at once
    error_list: List[Union[None, str]] = []

    file_path_error = _check_path_existence(file_path=format_file_path(prompt.file, paths))
    if file_path_error is not None:
        error_list.append(file_path_error)
    else:
        prompt_file_content = get_file_content(file=prompt.file, paths=paths)
        for tag in prompt.tags:
            if tag.tag not in prompt_file_content:
                error_list.append(f"The tag: {tag.tag} does not exist in the {prompt.file} content")

    # Return only the error list str without None values
    return list(filter(None, error_list))


def _convert_config_data(config: ConfigObjData) -> ConfigData:
    """
    Converts the JSON data from the config file into a NT representation.
    :param config: The JSON data to be converted.
    :return: A NT with all the config data.
    """

    def _get_tag(tag: Union[FileTagObj, ValueTagObj]) -> Union[ValueTag, FileTag]:
        if "file" in tag:
            return FileTag(file=tag["file"], tag=tag["tag"])  # type: ignore[typeddict-item]
        return ValueTag(value=tag["value"], tag=tag["tag"])

    def _get_target(target: TargetObj) -> Target:
        return Target(
            comment=target.get("comment", ""),
            generate=target["generate"],
            output=target["output"],
            prompt=Prompt(
                file=target["prompt"]["file"],
                tags=[_get_tag(tag) for tag in target["prompt"]["tags"]],
            ),
        )

    return ConfigData(
        comment=config.get("comment", ""),
        paths=Paths(
            root=str(config["paths"].get("root", "")),
            sources=str(config["paths"]["sources"]),
            prompts=str(config["paths"]["prompts"]),
            schemas=config["paths"]["schemas"],
            output=config["paths"]["output"],
        ),
        targets=[_get_target(target) for target in config["targets"]],
    )


def _validate_config_data(config_data: ConfigData) -> None:
    """
    Validates the data in the config file.
    :param config_data: The data to be validated. It represents the entire config file info.
    :return: None.
    :raise: A BadParameter exception if invalid data is found.
    """
    # List to concatenate all errors and show them, if exist any, at once
    error_list = _validate_config_paths(config_data, config_data.paths)

    # Prompt file content and tags checking
    for target in config_data.targets:
        error_list += _validate_prompt_tags(target.prompt, config_data.paths)

    if len(error_list) > 0:
        raise BadParameter("\n".join(error_list))


def get_config(config_file: str) -> ConfigData:
    """
    Get the config data.
    :return: The content of the file converted into a dict.
    :raise: A BadParameter exception if something goes wrong.
    """
    try:
        config_json_data = _read_config(config_file=config_file)
        config_data = _convert_config_data(config_json_data)
        _validate_config_data(config_data)
        return config_data
    except Exception as config_error:
        raise BadParameter(config_error) from config_error
