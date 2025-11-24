@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: CONFIGURATION
:: ============================================================
set "PYTHON_VER=3.13.9"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VER%/python-%PYTHON_VER%-embed-amd64.zip"
set "PIP_URL=https://bootstrap.pypa.io/get-pip.py"

set "SCRIPTROOT=%~dp0"
set "WGET=%SCRIPTROOT%bin\wget.exe"
set "PYTHON_DIR=%SCRIPTROOT%python"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
set "PTH_FILE=%PYTHON_DIR%\python313._pth"

set "OLLAMA_DIR=%SCRIPTROOT%ollama"

set "OLLAMA_SETUP_EXE=OllamaSetup.exe"
set "OLLAMA_DOWNLOAD_URL=https://ollama.com/download/OllamaSetup.exe"
set "OLLAMA_LNK_STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Ollama.lnk"
set "OLLAMA_LNK_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Ollama\Ollama.lnk"
set "OLLAMA_BAK_STARTUP=%TEMP%\Ollama_Startup_Backup.lnk"
set "OLLAMA_BAK_MENU=%TEMP%\Ollama_Menu_Backup.lnk"

set "OLLAMA_BIN=%OLLAMA_DIR%\ollama.exe"
set "OLLAMA_HOST=http://127.0.0.1:11435"
set "OLLAMA_MODELS=%SCRIPTROOT%models"

:: ============================================================
:: 1. CHECK & INSTALL PYTHON
:: ============================================================
echo [1/6] Checking Python environment...

if exist "%PYTHON_EXE%" (
    echo - Python found in %PYTHON_DIR%. Skipping download.
) else (
    echo - Python missing or incomplete. Starting download...

    :: Clean up partial downloads from previous failed runs
    if exist "python.zip" (
        echo - Found leftover python.zip. Deleting to ensure fresh download...
        del "python.zip"
    )

    echo - Downloading Python %PYTHON_VER% Embeddable...
    "%WGET%" -q --show-progress -O python.zip "%PYTHON_URL%"
    if !errorlevel! neq 0 goto :ERROR_NETWORK

    echo - Extracting to %PYTHON_DIR%...
    powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path 'python.zip' -DestinationPath '%PYTHON_DIR%' -Force"
    if !errorlevel! neq 0 goto :ERROR_EXTRACT

    echo - Cleaning up zip file...
    del python.zip
)

:: Double check that extraction actually worked
if not exist "%PYTHON_EXE%" goto :ERROR_EXTRACT

:: ============================================================
:: 2. CONFIGURE ._pth FILE
:: ============================================================
echo [2/6] Configuring python313._pth...
:: This is safe to run repeatedly; it simply replaces the string if found.
powershell -ExecutionPolicy Bypass -Command "(Get-Content '%PTH_FILE%') -replace '#import site', 'import site' | Set-Content '%PTH_FILE%'"

:: ============================================================
:: 3. INSTALL PIP
:: ============================================================
echo [3/6] Checking for pip...

if exist "%PYTHON_DIR%\Scripts\pip.exe" (
    echo - pip found. Skipping.
) else (
    echo - pip not found.

    :: Clean up partial get-pip.py
    if exist "get-pip.py" del "get-pip.py"

    echo - Downloading get-pip.py...
    "%WGET%" -q --show-progress -O get-pip.py "%PIP_URL%"
    if !errorlevel! neq 0 goto :ERROR_NETWORK

    echo - Installing pip...
    "%PYTHON_EXE%" get-pip.py --no-warn-script-location
    if !errorlevel! neq 0 goto :ERROR_PIP

    del "get-pip.py"
)

:: ============================================================
:: 4. INSTALL REQUIREMENTS
:: ============================================================
echo [4/6] Installing requirements...
:: Pip handles partially installed packages automatically (idempotent).
if exist "%SCRIPTROOT%requirements.txt" (
    "%PYTHON_EXE%" -m pip install -r "%SCRIPTROOT%requirements.txt" --no-warn-script-location
    if !errorlevel! neq 0 goto :ERROR_PIP
) else (
    echo [ERROR] requirements.txt not found!
    goto :ERROR
)

:: ============================================================
:: 5. DOWNLOAD Ollama
:: ============================================================
echo [5/6] Downloading Ollama...
if exist "%OLLAMA_BIN%" (
    echo - Ollama found in %OLLAMA_DIR%. Skipping download.
) else (
    echo - Downloading %OLLAMA_SETUP_EXE%, this will take a while...

    :: Clean up partial downloads before starting fresh download
    if exist "%OLLAMA_SETUP_EXE%" (
        echo - Found leftover %OLLAMA_SETUP_EXE%. Deleting to ensure fresh download...
        del "%OLLAMA_SETUP_EXE%"
    )

    "%WGET%" -q --show-progress -O "%OLLAMA_SETUP_EXE%" "%OLLAMA_DOWNLOAD_URL%"
    if !errorlevel! neq 0 goto :ERROR_NETWORK

    :: Backup Startup Shortcut if it exists
    if exist "%OLLAMA_LNK_STARTUP%" (
        echo - Backing up existing Ollama Startup shortcut...
        copy /Y "%OLLAMA_LNK_STARTUP%" "%OLLAMA_BAK_STARTUP%" >nul
    )

    :: Backup Start Menu Shortcut if it exists
    if exist "%OLLAMA_LNK_MENU%" (
        echo - Backing up existing Ollama Start Menu shortcut...
        copy /Y "%OLLAMA_LNK_MENU%" "%OLLAMA_BAK_MENU%" >nul
    )

    echo - Installing Ollama to: "%OLLAMA_DIR%"
    start /wait "" "%OLLAMA_SETUP_EXE%" /DIR="%OLLAMA_DIR%" /VERYSILENT /SUPPRESSMSGBOXES /NOICONS /TASKS=""

    if not exist "%OLLAMA_BIN%" goto :ERROR_OLLAMA_INSTALL

    del "%OLLAMA_SETUP_EXE%"

    echo - Sanitizing Ollama installation...
    :: Stop the auto-started process
    taskkill /F /IM "ollama app.exe" >nul 2>&1
    taskkill /F /IM "ollama.exe" >nul 2>&1

    :: Remove from Windows Startup
    if exist "%OLLAMA_LNK_STARTUP%" del "%OLLAMA_LNK_STARTUP%"

    :: Restore original Ollama Startup shortcut if it existed
    if exist "%OLLAMA_BAK_STARTUP%" (
        echo - Restoring original Ollama Startup shortcut...
        move /Y "%OLLAMA_BAK_STARTUP%" "%OLLAMA_LNK_STARTUP%" >nul
    )

    :: Remove the Start Menu Shortcut
    if exist "%OLLAMA_LNK_MENU%" del "%OLLAMA_LNK_MENU%"

    :: Restore original Ollama Start Menu shortcut if it existed
    if exist "%OLLAMA_BAK_MENU%" (
        echo - Restoring original Ollama Start Menu shortcut...
        move /Y "%OLLAMA_BAK_MENU%" "%OLLAMA_LNK_MENU%" >nul
    )

    :: Clean User PATH (Remove Ollama from environment variables)
    powershell -Command "$target='%OLLAMA_DIR%'; $key = 'HKCU:\Environment'; $p = (Get-ItemProperty -Path $key -Name PATH).PATH; $parts = $p -split ';'; $new = ($parts | Where-Object { $_ -ne $target }) -join ';'; Set-ItemProperty -Path $key -Name PATH -Value $new"
)

:: ============================================================
:: 6. DOWNLOAD MODEL
:: ============================================================
echo [6/6] Downloading DeepSeek-OCR Model...

echo Starting Ollama...
start /B "" "%OLLAMA_BIN%" serve >nul 2>&1
timeout /t 3 /nobreak >nul

echo Downloading deepseek-ocr:3b (FP16)...
"%OLLAMA_BIN%" pull deepseek-ocr:3b
if !errorlevel! neq 0 (
    taskkill /F /IM ollama.exe >nul 2>&1
    goto :ERROR_MODEL
)

echo Stopping Ollama...
taskkill /F /IM ollama.exe >nul 2>&1

echo.
echo Environment setup complete.
echo You can now run 'run.bat' or 'run_cpu-only.bat'.
pause
exit /b 0

:: ============================================================
:: ERROR HANDLERS
:: ============================================================
:ERROR_NETWORK
echo.
echo [FATAL ERROR] Network request failed.
echo Please check your internet connection and try again.
pause
exit /b 1

:ERROR_EXTRACT
echo.
echo [FATAL ERROR] Failed to extract Python.
echo The downloaded zip might be corrupt. 
echo The script will delete it automatically on the next run.
pause
exit /b 1

:ERROR_PIP
echo.
echo [FATAL ERROR] Pip installation or Package install failed.
pause
exit /b 1

:ERROR_OLLAMA_INSTALL
echo.
echo [FATAL ERROR] Ollama installation failed.
pause
exit /b 1

:ERROR_MODEL
echo.
echo [FATAL ERROR] Model download failed.
pause
exit /b 1

:ERROR
echo.
echo [FATAL ERROR] An unexpected error occurred.
pause
exit /b 1