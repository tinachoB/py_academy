@echo off
rem Run all code checks to make sure code meets formatting standards.
rem Will exit non-zero if there are errors or improperly formatted code.

set FAILED=

echo Running Pylint
call tools/run_pylint.bat
if errorlevel 1 ( set FAILED=pylint %FAILED% )

echo Running Isort
call tools/run_isort.bat
if errorlevel 1 ( set FAILED=isort %FAILED% )

echo Running Black
call tools/run_black.bat
if errorlevel 1 ( set FAILED=black %FAILED% )

echo Running Mypy
call tools/run_mypy.bat
if errorlevel 1 ( set FAILED=mypy %FAILED% )

if not ["%FAILED%"]==[""] (
  echo Failed: %FAILED%
  exit 1
) else (
    echo Everything is ok
)
