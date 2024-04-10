@echo off
set PYTHONPATH="./server:./test${PYTHONPATH+:}${PYTHONPATH:-}"

isort .
