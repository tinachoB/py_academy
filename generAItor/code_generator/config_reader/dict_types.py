"""
Types used to store config data into a TypedDict
instead of a plain dict.
"""
from typing import List, Optional, TypedDict, Union


class PathsObj(TypedDict):
    sources: str
    prompts: str
    schemas: str
    output: str
    root: Optional[str]


class ValueTagObj(TypedDict):
    tag: str
    value: str


class FileTagObj(TypedDict):
    tag: str
    file: str


class PromptObj(TypedDict):
    file: str
    tags: List[Union[FileTagObj, ValueTagObj]]


class TargetObj(TypedDict):
    output: str
    generate: bool
    prompt: PromptObj
    comment: Optional[str]


class ConfigObjData(TypedDict):
    comment: Optional[str]
    paths: PathsObj
    targets: List[TargetObj]
