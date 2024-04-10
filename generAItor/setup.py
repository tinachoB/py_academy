"""Use this file to install code-generator as a module"""
import codecs
import glob
import os
from distutils.core import setup
from typing import List

from setuptools import find_packages


def get_version(relative_path: str) -> str:
    """
    Given a relative path to an `__init__.py` inside a python package, return the version.

    :param relative_path: path to `__init__.py`
    :return: version number
    """
    with codecs.open(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path), "r"
    ) as fp:
        file_content = fp.read()
    for line in file_content.splitlines():
        if line.startswith("__version__"):
            return line.split('"' if '"' in line else "'")[1]
    raise RuntimeError("Unable to find version string.")


def _package_files(directory: str) -> List[str]:
    """
    Recursively walk through a directory structure pulling out all files in that directory
    hierarchy. Used to find package files/data.

    :param directory: a directory to glob
    :return: list of fully qualified paths
    """
    return [
        os.path.join("..", path, filename)
        for (path, directories, filenames) in os.walk(directory)
        for filename in filenames
        if not filename.endswith("pyc")
    ]


def _diagrams_files(diagrams_path: str) -> List[str]:
    """
    Gets a list of diagrams files to add to the package.

    :return: list of the info files.
    """
    return glob.glob(f"{diagrams_path}/*.png")


def _info_files() -> List[str]:
    """
    Gets a list of info files to add to the package.

    :return: list of the info files.
    """
    return glob.glob("*.md")


def prod_dependencies() -> List[str]:
    """
    Pull the dependencies from the requirements' dir
    :return: Each of the newlines, strings of the dependencies
    """
    with open("./requirements/prod.txt", "r") as file:
        return file.read().splitlines()


PACKAGE_NAME = "code_generator"
PACKAGE_DATA = {PACKAGE_NAME: _package_files(PACKAGE_NAME)}

DIAGRAMS = "diagrams"
DIAGRAMS_FILES = _diagrams_files(DIAGRAMS)

INFO = "."
INFO_FILES = _info_files()

setup(
    name=PACKAGE_NAME,
    version=get_version(f"{PACKAGE_NAME}/__init__.py"),
    description="Tool to generate code based on Chat-GPT.",
    author="Gaston Arnau, Martin Boretto",
    author_email="",
    packages=find_packages(**{"exclude": ["tests", "tests.*"]}),
    package_data=PACKAGE_DATA,
    data_files=[(DIAGRAMS, DIAGRAMS_FILES), (INFO, INFO_FILES)],
    install_requires=prod_dependencies(),
    entry_points="""
        [console_scripts]
        code_generator=code_generator.__main__:main
    """,
)
