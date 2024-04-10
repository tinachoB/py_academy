"""
Helper for logging.
"""
import logging
import sys

import openai

# Log's config
FMT_NOW_DETAILS = "%(asctime)s [%(levelname)5s] %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

logging.basicConfig(
    level=logging.INFO, format=FMT_NOW_DETAILS, datefmt=DATE_FORMAT, stream=sys.stdout
)

logging.getLogger("urllib3.util.retry").setLevel(logging.CRITICAL)
logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)
logging.getLogger("pygount").setLevel(logging.CRITICAL)
openai.util.logger.setLevel(logging.CRITICAL)


def initialize_logger(log: str) -> None:
    """
    Initializes the defined log file
    :param log: Path to a log file.
    :return: None
    """
    if log:
        file_handler = logging.FileHandler(log)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(FMT_NOW_DETAILS))
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
