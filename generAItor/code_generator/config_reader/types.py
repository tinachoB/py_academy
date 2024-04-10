"""
Config types.
"""
from typing import List, NamedTuple, Optional, Union


class FileTag(NamedTuple):
    """
    FileTag object represented as:
     A tag to be replaced with a file's content:
        e.g.: {"tag": "<tag>", "file": "<file_path>"}
    """

    tag: str
    file: str


class ValueTag(NamedTuple):
    """
    ValueTag object represented as:
     A tag to be replaced with a string value:
        e.g.: {"tag": "<tag>", "value": "<str_value>"}
    """

    tag: str
    value: str


class Prompt(NamedTuple):
    """
    Prompt object represented as:
      A file (where the prompt's content) plus a
      list of information to be deployed based on specific tags:
      e.g.:
      "prompt": {
        "file": "<prompt_file_path>",
        "tags": [
          {"tag": "<tag>", "file": "<file_path>"},
          {"tag": "<tag>", "value": "<str_value>"}
        ]
      }
    """

    file: str
    tags: List[Union[ValueTag, FileTag]]


class Target(NamedTuple):
    """
    Target object represented as:
      An optional target's comment, the output file where
      all information will be placed/built and the specific
      prompt information related.
      e.g.:
      {
        "comment": "<specific target's comment>",
        "generate": true/false,
        "output": "<output_file_path>",
        "prompt": {
          "file": "<prompt_file_path>",
          "tags": [
            {"tag": "<tag>", "file": "<file_path>"},
            {"tag": "<tag>", "value": "<str_value>"}
          ]
        }
      }
    """

    output: str
    generate: bool
    prompt: Prompt
    comment: Optional[str] = ""


class Paths(NamedTuple):
    """
    Paths object represented by:
      All needed/common paths to work with:
      e.g.:
      "paths": {
        "sources": "<sources_path>",
        "prompts": "<prompts_path>",
        "schemas": "<schemas_path>",
        "output": "<output_path>"
      },
    """

    sources: str
    prompts: str
    schemas: str
    output: str
    root: Optional[str] = ""


class ConfigData(NamedTuple):
    """
    ConfigData object represented by:
      The needed paths to work with and a list
      of targets to run the application against:
      e.g.:
        {
          "comment: "some comment (optional)"
          "paths": {
            "sources": "<sources_path>",
            "prompts": "<prompts_path>",
            "schemas": "<schemas_path>",
            "output": "<output_path>"
          },
          "targets": [
            {
              "comment": "<specific target's comment>",
              "output": "<output_file_path>",
              "generate": true/false,
              "prompt": {
                  "file": "<prompt_file_path>",
                    "tags": [
                      {"tag": "<tag>", "file": "<file_path>"},
                      {"tag": "<tag>", "value": "<str_value>"}
                    ]
              }
            }
          ]
        }
    """

    paths: Paths
    targets: List[Target]
    comment: Optional[str] = ""
