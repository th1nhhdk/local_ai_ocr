@echo off
setlocal enabledelayedexpansion

@REM ============================================================
@REM CONFIGURATION
@REM ============================================================
set "SCRIPTROOT=%~dp0"

set "PYTHON_DIR=%SCRIPTROOT%python"
set "PYTHON_VER=3.13.14"
set "PYTHON_ZIP=python-%PYTHON_VER%-embed-amd64.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VER%/%PYTHON_ZIP%"
set "PIP_URL=https://bootstrap.pypa.io/get-pip.py"

set "PYTHON_BIN=%PYTHON_DIR%\python.exe"
set "PYTHON_PTH=%PYTHON_DIR%\python313._pth"

@REM ============================================================
@REM 1. CHECK & INSTALL PYTHON
@REM ============================================================
echo [1/6] Checking Python environment...

if exist "%PYTHON_BIN%" (
    echo - Python found in %PYTHON_DIR%. Skipping download.
) else (
    echo - Python missing or incomplete. Starting download...

    @REM Clean up partial downloads from previous failed runs
    if exist "%PYTHON_ZIP%" (
        echo - Found leftover %PYTHON_ZIP%. Deleting to ensure fresh download...
        del "%PYTHON_ZIP%"
    )

    echo - Downloading Python %PYTHON_VER% Embeddable...
    curl.exe -# -L -o "%PYTHON_ZIP%" "%PYTHON_URL%"
    if !errorlevel! neq 0 goto :ERROR_NETWORK

    echo - Extracting to %PYTHON_DIR%...
    powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
    if !errorlevel! neq 0 goto :ERROR_EXTRACT

    echo - Cleaning up zip file...
    del "%PYTHON_ZIP%"
)

@REM Double check that extraction actually worked
if not exist "%PYTHON_BIN%" goto :ERROR_EXTRACT

@REM ============================================================
@REM 2. CONFIGURE ._pth FILE
@REM ============================================================
echo [2/6] Configuring %PYTHON_PTH%...
@REM This is safe to run repeatedly; it simply replaces the string if found.
powershell -ExecutionPolicy Bypass -Command "(Get-Content '%PYTHON_PTH%') -replace '#import site', 'import site' | Set-Content '%PYTHON_PTH%'"

@REM ============================================================
@REM 3. INSTALL PIP
@REM ============================================================
echo [3/6] Checking for pip...

if exist "%PYTHON_DIR%\Scripts\pip.exe" (
    echo - pip found. Skipping.
) else (
    echo - pip not found.

    @REM Clean up partial get-pip.py
    if exist "get-pip.py" del "get-pip.py"

    echo - Downloading get-pip.py...
    curl.exe -# -L -o get-pip.py "%PIP_URL%"
    if !errorlevel! neq 0 goto :ERROR_NETWORK

    echo - Installing pip...
    "%PYTHON_BIN%" get-pip.py --no-warn-script-location
    if !errorlevel! neq 0 goto :ERROR_PIP

    del "get-pip.py"
)

@REM ============================================================
@REM 4. INSTALL PYTORCH
@REM ============================================================
echo [4/6] Installing PyTorch...
"%PYTHON_BIN%" -m pip install torch==2.12.1 torchvision==0.27.1 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cu130 --no-warn-script-location
if !errorlevel! neq 0 goto :ERROR_PIP

echo - Installing Flash Attention 2 for Python 3.13...
"%PYTHON_BIN%" -m pip install https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.9.25/flash_attn-2.8.3+cu130torch2.12-cp313-cp313-win_amd64.whl --no-warn-script-location
if !errorlevel! neq 0 echo Warning: Failed to install flash-attn wheel. Continuing anyway...

@REM ============================================================
@REM 5. INSTALL REQUIREMENTS
@REM ============================================================
echo [5/6] Installing requirements...
@REM Pip handles partially installed packages automatically.
if exist "%SCRIPTROOT%requirements.txt" (
    "%PYTHON_BIN%" -m pip install -r "%SCRIPTROOT%requirements.txt" --no-warn-script-location
    if !errorlevel! neq 0 goto :ERROR_PIP
) else (
    echo.
    echo FATAL: Cannot find requirements.txt
    pause
    exit /b 1
)

@REM ============================================================
@REM 6. DOWNLOAD MODEL WEIGHTS
@REM ============================================================
echo [6/6] Downloading DeepSeek-OCR-2 Model...

set "MODEL_DIR=%SCRIPTROOT%models"
if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"

set "HF_HOME=%MODEL_DIR%"

echo - Downloading weights from HuggingFace (this might take a while depending on your connection)...
"%PYTHON_DIR%\Scripts\hf.exe" download Dogacel/Universal-DeepSeek-OCR-2
if !errorlevel! neq 0 (
    echo.
    echo FATAL: Model download failed.
    pause
    exit /b 1
)

echo - Model downloaded successfully.

echo.
echo INFO: Environment setup complete.
echo You can now run 'run.cmd' or 'run_cpu-only.cmd'.
echo.
pause
exit /b 0

@REM ============================================================
@REM ERROR HANDLERS
@REM ============================================================
:ERROR_NETWORK
echo.
echo FATAL: Network request failed.
echo Please check your internet connection and try again.
echo.
pause
exit /b 1

:ERROR_EXTRACT
echo.
echo FATAL: Failed to extract Python.
echo The downloaded zip might be corrupt. 
echo The script will delete it automatically on the next run.
echo.
pause
exit /b 1

:ERROR_PIP
echo.
echo FATAL: Pip installation or Package install failed.
echo.
pause
exit /b 1
