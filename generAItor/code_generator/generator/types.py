"""
New types used on the generation process.
"""
from typing import NamedTuple


class TargetData(NamedTuple):
    """
    This is all the data we need to create a new target.
    """

    prompt: str
    output_file: str
