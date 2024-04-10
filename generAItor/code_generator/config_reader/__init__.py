# Directories
import os
from pathlib import Path

CONFIG_READER_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Config Schema File
CONFIG_SCHEMA = CONFIG_READER_DIR.joinpath("config.schema")
