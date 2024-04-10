#!/usr/bin/env bash

# Run mypy in check mode to ensure that there are no missing types
# Will exit non-zero if there are errors or incorrectly formatted python imports.

set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd ${DIR}/..
source ./venv/bin/activate

export PYTHONPATH=".:code_generator:${PYTHONPATH+:}${PYTHONPATH:-}"

mypy --show-error-codes -p code_generator  # Run on sub-packages within this project

