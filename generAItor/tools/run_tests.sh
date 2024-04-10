#!/usr/bin/env bash

set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd ${DIR}/..
source ./venv/bin/activate

export PYTHONPATH="./code_generator:./tests${PYTHONPATH+:}${PYTHONPATH:-}"

TEST_MARKED=${1:-all}
if [ "${1:-}" ]; then shift 1; fi

echo "run tests: ${TEST_MARKED}; args: ${PYTEST_EXTRA_ARGS:-} $@"

pytest -m "${TEST_MARKED/#all/}" "${PYTEST_EXTRA_ARGS:-}" "$@"
