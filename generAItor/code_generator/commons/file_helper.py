"""
Helper for files management.
"""
import io
import logging
import zipfile
from typing import IO, Dict

from code_generator.config_reader.types import Paths

LOGGER = logging.getLogger(__name__)

_ZIP_FILE_EXPECTED_CONTENT = ["config.json", "output", "prompts", "schemas", "source_code"]


def get_file_content(file: str, paths: Paths) -> str:
    """
    Gets the content of a given file.

    :param file: The file's path.
    :param paths: The configured paths.
    :return: The content of the file.
    """
    file_path = format_file_path(file=file, paths=paths)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def format_file_path(file: str, paths: Paths) -> str:
    """
    Formats file paths based on its configured tags.

    :param file: A string with the path to a file using
    tags to be replaced in the format "{source}/<file>.<ext>"
    :param paths: The values of the tags to replace.
    :return: The formatted path.
    """
    formatted_path = (
        file.replace("{sources}", paths.sources)
        .replace("{prompts}", paths.prompts)
        .replace("{schemas}", paths.schemas)
        .replace("{output}", paths.output)
    )
    if paths.root:
        formatted_path = formatted_path.replace("{root}", paths.root)
    return formatted_path


def _check_structure(extracted_data: Dict[str, bytes]) -> bool:
    """
    Checks if the zip file content contains the expected files.
    :param extracted_data: Zip file content.
    :return: True if the zip file content contains the expected data. False, otherwise.
    """
    for elem in _ZIP_FILE_EXPECTED_CONTENT:
        if elem not in str(extracted_data.keys()):
            LOGGER.error(f"Missing {elem} in zip file")
            return False
    return True


def _check_zip_folders_content(extracted_data: Dict[str, bytes]) -> bool:
    """
    Checks if the zip file content folders are not empty.
    :param extracted_data: Zip file content.
    :return: True if the zip file content folders are not empty. False, otherwise.
    """
    for key, value in extracted_data.items():
        if key.endswith(".json") and value is None:  # pylint: disable=no-else-return
            LOGGER.error(f"{key} file is empty.")
            return False
    data = extracted_data.copy()
    for key in list(data.keys()):
        if key.endswith("/") or key in ["config.json"]:
            data.pop(key)
    for item in _ZIP_FILE_EXPECTED_CONTENT:
        if not any(item in k for k in list(data.keys())) and item not in ["config.json", "output"]:
            LOGGER.error(f"{key} folder is empty.")
            return False
    return True


def unzip_file(zip_file: IO[bytes]) -> Dict[str, bytes]:
    """
    Unzip the file being passed as parameter and return its content
    :param zip_file: Zip file to be checked
    :return: Zip file content.
    """
    zip_content = zip_file.read()
    zip_data = io.BytesIO(zip_content)
    with zipfile.ZipFile(zip_data, "r") as zip_ref:
        # Extract the content in-memory to check if everything is ready to use
        extracted_data = {name: zip_ref.read(name) for name in zip_ref.namelist()}
    return extracted_data


def analyze_zip_data(extracted_data: Dict[str, bytes]) -> bool:
    """
    Checks if the data passed as parameter is not empty and the content is valid.
    :param extracted_data: Data to check.
    :return: True if data is ok to move forward, False otherwise.
    """
    return _check_structure(extracted_data) and _check_zip_folders_content(extracted_data)
