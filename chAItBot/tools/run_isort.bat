@echo off

rem Run isort in check mode to ensure that there are not outstanding changes that need to be made.
rem Will exit non-zero if there are errors or incorrectly formatted python imports.

set PYTHONPATH=".:${PYTHONPATH+:}${PYTHONPATH:-}"

rem If this is failing, replace the line with `isort -c -vb` to see verbose output
isort -c .
