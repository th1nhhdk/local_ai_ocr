@echo off
setlocal

set "SCRIPTROOT=%~dp0"
set "PYTHON_BIN=%SCRIPTROOT%python\python.exe"

@REM Set HF_HOME to models directory
set "HF_HOME=%SCRIPTROOT%models"

@REM NVIDIA disable
set "CUDA_VISIBLE_DEVICES=-1"
@REM AMD disable
set "ROCR_VISIBLE_DEVICES=-1"
@REM Intel disable
set "GGML_VK_VISIBLE_DEVICES=-1"

echo Starting Local AI OCR (CPU-Only)...
"%PYTHON_BIN%" "%SCRIPTROOT%src\main.py"

endlocal
