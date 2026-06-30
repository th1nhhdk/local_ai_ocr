@echo off
setlocal

set "SCRIPTROOT=%~dp0"
set "PYTHON_BIN=%SCRIPTROOT%python\python.exe"

@REM Set HF_HOME to models directory
set "HF_HOME=%SCRIPTROOT%models"

echo Starting Local AI OCR...
"%PYTHON_BIN%" "%SCRIPTROOT%src\main.py"

endlocal
