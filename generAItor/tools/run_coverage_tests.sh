#!/usr/bin/env bash

set -uo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd ${DIR}/..
source ./venv/bin/activate

export PYTHONPATH="./code_generator:./tests${PYTHONPATH+:}${PYTHONPATH:-}"

TEST_MARKED=${1:-all}
if [ "${1:-}" ]; then shift 1; fi

coverage erase # clean up any leftover results
coverage run --concurrency=multiprocessing venv/bin/pytest --doctest-modules -m "not (end_to_end)" "${TEST_MARKED/#all/}" "${PYTEST_EXTRA_ARGS:-}" "$@"

test_res=$?
coverage combine
coverage report --fail-under=80 --skip-covered

cov_res=$?

coverage html
coverage erase

echo "Tests result   : $test_res"
echo "Coverage result: $cov_res"

if [ $test_res -ne 0 ]
then
    echo "Tests are FAILING."
    exit $test_res
fi
