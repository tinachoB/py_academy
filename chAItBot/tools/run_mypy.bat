@echo off
rem Run mypy in check mode to ensure that there are no missing types
rem Will exit non-zero if there are errors or incorrectly formatted python imports.

rem set PYTHONPATH=".:server:${PYTHONPATH+:}${PYTHONPATH:-}"

rem Run on sub-packages within this project
mypy --show-error-codes --exclude=routers -p server
