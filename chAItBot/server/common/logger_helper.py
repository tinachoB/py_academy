"""
Helper for logging.
"""
import logging
from logging.handlers import RotatingFileHandler

import openai

logging.getLogger("urllib3.util.retry").setLevel(logging.CRITICAL)
logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)
openai.util.logger.setLevel(logging.CRITICAL)


# Log's config
__FMT_NOW_DETAILS = "%(asctime)s [%(levelname)5s] %(message)s"
__DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
__LOG_NAME = "server.log"
__MAX_BYTES = 10 * 1024 * 1024
__BACKUP_COUNT = 1

__file_handler = RotatingFileHandler(
    filename=__LOG_NAME, maxBytes=__MAX_BYTES, backupCount=__BACKUP_COUNT
)
__file_handler.setLevel(logging.DEBUG)
__file_handler.setFormatter(logging.Formatter(__FMT_NOW_DETAILS))

logging.basicConfig(
    handlers=[__file_handler], level=logging.INFO, format=__FMT_NOW_DETAILS, datefmt=__DATE_FORMAT
)

LOGGER = logging.getLogger()
