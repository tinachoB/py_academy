"""
Code Stats class.
"""
import json
import logging
import platform
import subprocess
import sys
from typing import NamedTuple, Optional

LOGGER = logging.getLogger(__name__)


class CodeStats(NamedTuple):
    """
    NT with data about code stats.
    """

    code_lines_count: int
    comments_lines_count: int
    empty_lines_count: int


class CodeStatsCounter:
    """
    Class used to keep count of code statistics.
    """

    def __init__(self) -> None:
        """
        Constructor.
        :return: None
        """
        self.__code_lines_count: int = 0
        self.__comments_lines_count: int = 0
        self.__empty_lines_count: int = 0

    def get_stats(self, file: str) -> Optional[CodeStats]:
        """
        Gets the file code stats.
        :param file: The file we want to get the code stats.
        :return: A NT with the file's stats.
        """
        if self.is_frozen_windows():
            # We need to do this due a bug with the `pygount` library on Windows
            # when we are running this from a bundled installer created with PyInstaller.
            return CodeStats(code_lines_count=0, empty_lines_count=0, comments_lines_count=0)

        try:

            command = f"pygount --format=json {file}"
            result = subprocess.run(command, shell=True, text=True, check=True, capture_output=True)
            if result.returncode == 0:
                counter = json.loads(result.stdout)

                self.__code_lines_count += counter["summary"]["totalSourceCount"]
                self.__comments_lines_count += counter["summary"]["totalDocumentationCount"]
                self.__empty_lines_count += counter["summary"]["totalEmptyCount"]

                return CodeStats(
                    code_lines_count=counter["summary"]["totalSourceCount"],
                    comments_lines_count=counter["summary"]["totalDocumentationCount"],
                    empty_lines_count=counter["summary"]["totalEmptyCount"],
                )

            LOGGER.error(f"Error executing 'pygount'. Error: '{result.stderr}'")
        except Exception as e:
            LOGGER.error(f"Error executing 'pygount'. Exception: {e}")
        return None

    @property
    def stats(self) -> CodeStats:
        """
        Gets the collected stats.
        :return: A NT with the stats collected so far.
        """
        return CodeStats(
            code_lines_count=self.__code_lines_count,
            comments_lines_count=self.__comments_lines_count,
            empty_lines_count=self.__empty_lines_count,
        )

    @staticmethod
    def is_frozen_windows() -> bool:
        """
        Checks if we are running on a frozen environment on windows
        (inside the bundled Pyinstaller).
        :return: True if we are on windows on a frozen env, false otherwise.
        """
        return platform.system() == "Windows" and getattr(sys, "frozen", False)
