@echo off
setlocal EnableExtensions EnableDelayedExpansion

set VERSION=v2.2.1
set ARCHIVE_NAME=local_ai_ocr-%VERSION%.zip
set ZIP=7z.exe

where %ZIP% >nul 2>&1
if errorlevel 1 (
    echo FATAL: 7z.exe not found in PATH
    exit /b 1
)

if exist "%ARCHIVE_NAME%" (
    echo Removing existing archive: %ARCHIVE_NAME%
    del /f /q "%ARCHIVE_NAME%"
)

echo Creating %ARCHIVE_NAME%...

%ZIP% a -tzip "%ARCHIVE_NAME%" ^
    "bin\wget.exe" ^
    "demo\" ^
    "src\" ^
    ".gitignore" ^
    "config.toml" ^
    "env_setup.cmd" ^
    "LICENSE" ^
    "README.md" ^
    "README_dev.md" ^
    "README_en.md" ^
    "requirements.txt" ^
    "run.cmd" ^
    "run_cpu-only.cmd" ^
    "run_wlog.cmd" ^
    "run_cpu-only_wlog.cmd" ^
    -xr^^!"bin\.wget-hsts" ^
    -xr^^!"__pycache__" ^
    -xr^^!"*.pyc" ^
    -xr^^!"*.pyo"

if errorlevel 1 (
    echo.
    echo FATAL: make_release failed
    echo.
    pause
    exit /b 1
)

echo.
echo DONE: %ARCHIVE_NAME% created successfully
echo.
endlocal
pause