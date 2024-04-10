"""Top-level package for code-generator."""
import os
from pathlib import Path

__version__ = "1.0.0"
__program_name__ = "Code Generator"

# Directories
ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Env file
ENV_FILE = ROOT_DIR.joinpath("../.env")
