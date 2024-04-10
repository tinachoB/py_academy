"""
Validations for the JSON schema.
"""
from collections import deque
from typing import Union

import jsonschema
from click import BadParameter

# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches


def _validate_types(
    e: jsonschema.ValidationError,
) -> Union[BadParameter, jsonschema.ValidationError]:
    if e.absolute_path == deque(["comment"]):
        return BadParameter("Error: 'comment' must be a string (optional).")
    if e.schema_path == deque(["properties", "targets", "items", "properties", "comment", "type"]):
        return BadParameter("Error: 'targets.items.comment' must be a string (optional).")
    if e.absolute_path == deque(["paths"]):
        return BadParameter("Error: 'paths' must be an object.")
    if e.absolute_path == deque(["targets"]):
        return BadParameter("Error: 'targets' must be an array.")
    if e.absolute_path == deque(["paths", "output"]):
        return BadParameter("Error: 'paths.output' must be a string.")
    if e.absolute_path == deque(["paths", "schemas"]):
        return BadParameter("Error: 'paths.schemas' must be a string.")
    if e.absolute_path == deque(["paths", "prompts"]):
        return BadParameter("Error: 'paths.prompts' must be a string.")
    if e.absolute_path == deque(["paths", "sources"]):
        return BadParameter("Error: 'paths.sources' must be a string.")
    if e.schema_path == deque(["properties", "targets", "items", "properties", "output", "type"]):
        return BadParameter("Error: 'targets.items.output' must be a string.")
    if e.schema_path == deque(["properties", "targets", "items", "properties", "generate", "type"]):
        return BadParameter("Error: 'targets.items.generate' must be a boolean.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "file",
            "type",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.file' must be a string.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "tags",
            "type",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags' must be an array.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "tags",
            "items",
            "properties",
            "tag",
            "type",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags.items.tag' must be a string.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "tags",
            "items",
            "properties",
            "file",
            "type",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags.items.tag.file' must be a string.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "tags",
            "items",
            "properties",
            "value",
            "type",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags.items.tag.value' must be a string.")
    return e


def _validate_required_properties(  # pylint: disable=too-many-return-statements
    e: jsonschema.ValidationError,
) -> Union[BadParameter, jsonschema.ValidationError]:
    if e.message.startswith("'generate'"):
        return BadParameter("Error: 'targets.items.generate' is a required property.")
    if e.message.startswith("'paths'"):
        return BadParameter("Error: 'paths' is a required property.")
    if e.message.startswith("'targets'"):
        return BadParameter("Error: 'targets' is a required array.")
    if e.message.startswith("'schemas'"):
        return BadParameter("Error: 'paths.schemas' is a required property.")
    if e.message.startswith("'sources'"):
        return BadParameter("Error: 'paths.sources' is a required property.")
    if e.message.startswith("'prompts'"):
        return BadParameter("Error: 'paths.prompts' is a required property.")
    if e.message.startswith("'output'"):
        if e.validator_value == ["generate", "output", "prompt"]:
            return BadParameter("Error: 'targets.items.output' is a required property.")
        if e.validator_value == ["sources", "prompts", "schemas", "output"]:
            return BadParameter("Error: 'paths.output' is a required property.")
    if e.schema_path == deque(["properties", "targets", "items", "required"]):
        return BadParameter("Error: 'targets.items.prompt' is a required property.")

    if e.schema_path == deque(
        ["properties", "targets", "items", "properties", "prompt", "required"]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags' is a required array.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "tags",
            "items",
            "required",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags.items.tag' is a required property.")
    if "'file' is a required property" in e.message:
        return BadParameter(
            "Error: 'targets.items.prompt.tags.items.tag' missing 'file' or 'value' property."
        )
    return e


def _validate_min_length(  # pylint: disable=too-many-return-statements
    e: jsonschema.ValidationError,
) -> Union[BadParameter, jsonschema.ValidationError]:
    if e.absolute_path == deque(["paths", "output"]):
        return BadParameter("Error: 'paths.output' cannot be empty.")
    if e.absolute_path == deque(["paths", "sources"]):
        return BadParameter("Error: 'paths.sources' cannot be empty.")
    if e.absolute_path == deque(["paths", "schemas"]):
        return BadParameter("Error: 'paths.schemas' cannot be empty.")
    if e.absolute_path == deque(["paths", "prompts"]):
        return BadParameter("Error: 'paths.prompts' cannot be empty.")
    if e.schema_path == deque(
        ["properties", "targets", "items", "properties", "output", "minLength"]
    ):
        return BadParameter("Error: 'targets.items.output' cannot be empty.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "file",
            "minLength",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.file' cannot be empty.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "tags",
            "items",
            "properties",
            "tag",
            "minLength",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags.items.tag' cannot be empty.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "tags",
            "items",
            "properties",
            "file",
            "minLength",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags.items.tag.file' cannot be empty.")
    if e.schema_path == deque(
        [
            "properties",
            "targets",
            "items",
            "properties",
            "prompt",
            "properties",
            "tags",
            "items",
            "properties",
            "value",
            "minLength",
        ]
    ):
        return BadParameter("Error: 'targets.items.prompt.tags.items.tag.value' cannot be empty.")
    return e


def _validate_min_items(
    e: jsonschema.ValidationError,
) -> Union[BadParameter, jsonschema.ValidationError]:
    if e.absolute_path == deque(["targets"]):
        return BadParameter("Error: 'targets' cannot be an empty array.")
    return e


def _validate_one_of() -> BadParameter:
    return BadParameter(
        "Error: 'targets.items.prompt.tags.items.tag' properties 'file' and 'value' "
        "are mutually exclusive."
    )


def validate(  # pylint: disable=too-many-return-statements
    e: jsonschema.ValidationError,
) -> Union[BadParameter, jsonschema.ValidationError]:
    if e.validator == "additionalProperties":
        if e.schema_path == deque(["additionalProperties"]):
            return BadParameter("Error: Additional properties on config are not allowed.")
        if e.schema_path == deque(["properties", "paths", "additionalProperties"]):
            return BadParameter("Error: Additional properties on 'paths' are not allowed.")
        if e.schema_path == deque(["properties", "targets", "items", "additionalProperties"]):
            return BadParameter("Error: Additional properties on 'targets.items' are not allowed.")
        if e.schema_path == deque(
            [
                "properties",
                "targets",
                "items",
                "properties",
                "prompt",
                "properties",
                "tags",
                "items",
                "additionalProperties",
            ]
        ):
            return BadParameter(
                "Additional properties on 'targets.items.prompt.tags.items.tag' are not allowed"
            )

    if e.validator == "type":
        return _validate_types(e)
    if e.validator == "required":
        return _validate_required_properties(e)
    if e.validator == "minLength":
        return _validate_min_length(e)
    if e.validator == "minItems":
        return _validate_min_items(e)
    if e.validator == "oneOf":
        return _validate_one_of()
    return e
