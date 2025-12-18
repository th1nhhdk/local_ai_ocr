@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM CONFIGURATION
REM ============================================================
set "SCRIPTROOT=%~dp0"

set "WGET_BIN=%SCRIPTROOT%bin\wget2.exe"

set "PYTHON_DIR=%SCRIPTROOT%python"
set "PYTHON_VER=3.13.11"
set "PYTHON_ZIP=python-%PYTHON_VER%-embed-amd64.zip"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VER%/%PYTHON_ZIP%"
set "PIP_URL=https://bootstrap.pypa.io/get-pip.py"

set "PYTHON_BIN=%PYTHON_DIR%\python.exe"
set "PYTHON_PTH=%PYTHON_DIR%\python313._pth"

set "OLLAMA_DIR=%SCRIPTROOT%ollama"
set "OLLAMA_VER=v0.13.4"
set "OLLAMA_ZIP=ollama-windows-amd64.zip"
set "OLLAMA_DOWNLOAD_URL=https://github.com/ollama/ollama/releases/download/%OLLAMA_VER%/%OLLAMA_ZIP%"
set "OLLAMA_CHECKSUM_URL=https://github.com/ollama/ollama/releases/download/%OLLAMA_VER%/sha256sum.txt"

set "OLLAMA_BIN=%OLLAMA_DIR%\ollama.exe"
set "OLLAMA_HOST=http://127.0.0.1:11435"
set "OLLAMA_MODELS=%SCRIPTROOT%models"

REM ============================================================
REM 1. CHECK & INSTALL PYTHON
REM ============================================================
echo [1/6] Checking Python environment...

if exist "%PYTHON_BIN%" (
    echo - Python found in %PYTHON_DIR%. Skipping download.
) else (
    echo - Python missing or incomplete. Starting download...

    REM Clean up partial downloads from previous failed runs
    if exist "%PYTHON_ZIP%" (
        echo - Found leftover %PYTHON_ZIP%. Deleting to ensure fresh download...
        del "%PYTHON_ZIP%"
    )

    echo - Downloading Python %PYTHON_VER% Embeddable...
    "%WGET_BIN%" -O "%PYTHON_ZIP%" "%PYTHON_URL%"
    if !errorlevel! neq 0 goto :ERROR_NETWORK

    echo - Extracting to %PYTHON_DIR%...
    powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
    if !errorlevel! neq 0 goto :ERROR_EXTRACT

    echo - Cleaning up zip file...
    del "%PYTHON_ZIP%"
)

REM Double check that extraction actually worked
if not exist "%PYTHON_BIN%" goto :ERROR_EXTRACT

REM ============================================================
REM 2. CONFIGURE ._pth FILE
REM ============================================================
echo [2/6] Configuring %PYTHON_PTH%...
REM This is safe to run repeatedly; it simply replaces the string if found.
powershell -ExecutionPolicy Bypass -Command "(Get-Content '%PYTHON_PTH%') -replace '#import site', 'import site' | Set-Content '%PYTHON_PTH%'"

REM ============================================================
REM 3. INSTALL PIP
REM ============================================================
echo [3/6] Checking for pip...

if exist "%PYTHON_DIR%\Scripts\pip.exe" (
    echo - pip found. Skipping.
) else (
    echo - pip not found.

    REM Clean up partial get-pip.py
    if exist "get-pip.py" del "get-pip.py"

    echo - Downloading get-pip.py...
    "%WGET_BIN%" -O get-pip.py "%PIP_URL%"
    if !errorlevel! neq 0 goto :ERROR_NETWORK

    echo - Installing pip...
    "%PYTHON_BIN%" get-pip.py --no-warn-script-location
    if !errorlevel! neq 0 goto :ERROR_PIP

    del "get-pip.py"
)

REM ============================================================
REM 4. INSTALL REQUIREMENTS
REM ============================================================
echo [4/6] Installing requirements...
REM Pip handles partially installed packages automatically.
if exist "%SCRIPTROOT%requirements.txt" (
    "%PYTHON_BIN%" -m pip install -r "%SCRIPTROOT%requirements.txt" --no-warn-script-location
    if !errorlevel! neq 0 goto :ERROR_PIP
) else (
    echo.
    echo FATAL: Cannot find requirements.txt
    pause
    exit /b 1
)

REM ============================================================
REM 5. DOWNLOAD Ollama
REM ============================================================
echo [5/6] Downloading Ollama...
if exist "%OLLAMA_BIN%" (
    echo - Ollama found in %OLLAMA_DIR%. Skipping download.
) else (
    REM Download checksum file
    echo - Downloading checksums...
    "%WGET_BIN%" -O sha256sum.txt "%OLLAMA_CHECKSUM_URL%"
    if !errorlevel! neq 0 goto :ERROR_NETWORK

    REM Extract expected hash
    set "EXPECTED_HASH="
    for /f "tokens=1" %%h in ('findstr "%OLLAMA_ZIP%" sha256sum.txt') do set "EXPECTED_HASH=%%h"

    REM Verify existing zip if present
    if exist "%OLLAMA_ZIP%" (
        if defined EXPECTED_HASH (
            echo - Found %OLLAMA_ZIP%. Verifying checksum...
            set "FILE_HASH="
            for /f "usebackq tokens=*" %%g in (`powershell -Command "(Get-FileHash '%OLLAMA_ZIP%' -Algorithm SHA256).Hash.ToLower()"`) do set "FILE_HASH=%%g"

            if "!FILE_HASH!" neq "!EXPECTED_HASH!" (
                echo - Checksum doesn't match. Deleting corrupted file...
                del "%OLLAMA_ZIP%"
            ) else (
                echo - Checksum verified.
            )
        )
    )

    REM Download if missing
    if not exist "%OLLAMA_ZIP%" (
        echo - Downloading %OLLAMA_ZIP%...
        "%WGET_BIN%" -O "%OLLAMA_ZIP%" "%OLLAMA_DOWNLOAD_URL%"
        if !errorlevel! neq 0 goto :ERROR_NETWORK

        REM Verify downloaded file
        if defined EXPECTED_HASH (
            set "FILE_HASH="
            for /f "usebackq tokens=*" %%g in (`powershell -Command "(Get-FileHash '%OLLAMA_ZIP%' -Algorithm SHA256).Hash.ToLower()"`) do set "FILE_HASH=%%g"
            if "!FILE_HASH!" neq "!EXPECTED_HASH!" (
                echo FATAL: Downloaded file's checksum doesn't match!
                del "%OLLAMA_ZIP%"
                goto :ERROR_NETWORK
            )
        )
    )

    REM Cleanup checksum file
    if exist "sha256sum.txt" del "sha256sum.txt"

    echo - Extracting to %OLLAMA_DIR%...
    powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%OLLAMA_ZIP%' -DestinationPath '%OLLAMA_DIR%' -Force"
    if !errorlevel! neq 0 goto :ERROR_OLLAMA_INSTALL

    REM Clean up zip
    del "%OLLAMA_ZIP%"

    if not exist "%OLLAMA_BIN%" goto :ERROR_OLLAMA_INSTALL
)

REM ============================================================
REM 6. DOWNLOAD MODEL
REM ============================================================
echo [6/6] Downloading DeepSeek-OCR Model...

echo Starting Ollama...
start /B "" "%OLLAMA_BIN%" serve >nul 2>&1
timeout /t 3 /nobreak >nul

echo Downloading deepseek-ocr:3b (FP16)...
"%OLLAMA_BIN%" pull deepseek-ocr:3b
if !errorlevel! neq 0 (
    taskkill /F /IM ollama.exe >nul 2>&1
    echo.
    echo FATAL: Model download failed.
    pause
    exit /b 1
)

echo Stopping Ollama...
taskkill /F /IM ollama.exe >nul 2>&1

echo.
echo INFO: Environment setup complete.
echo You can now run 'run.cmd' or 'run_cpu-only.cmd'.
pause
exit /b 0

REM ============================================================
REM ERROR HANDLERS
REM ============================================================
:ERROR_NETWORK
echo.
echo FATAL: Network request failed.
echo Please check your internet connection and try again.
pause
exit /b 1

:ERROR_EXTRACT
echo.
echo FATAL: Failed to extract Python.
echo The downloaded zip might be corrupt. 
echo The script will delete it automatically on the next run.
pause
exit /b 1

:ERROR_PIP
echo.
echo FATAL: Pip installation or Package install failed.
pause
exit /b 1

:ERROR_OLLAMA_INSTALL
echo.
echo FATAL: Ollama installation failed.
pause
exit /b 1
