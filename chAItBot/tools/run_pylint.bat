@echo off

rem Run pylint - make sure python code is correctly styled, is able to check for things that aren't
rem looked for by black.
rem Will exit non-zero if there are errors or incorrectly formatted python code.

rem set PYTHONPATH=".:server:${PYTHONPATH+:}${PYTHONPATH:-}"

pylint server
