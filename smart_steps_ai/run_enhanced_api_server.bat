@echo off
setlocal enabledelayedexpansion

echo ======================================
echo  Smart Steps AI API Server Launcher
echo ======================================
echo.

rem Set the path to the project root directory (where this batch file is located)
set PROJECT_DIR=%~dp0
rem Remove trailing backslash
set PROJECT_DIR=%PROJECT_DIR:~0,-1%

rem Set the PYTHONPATH to include the src directory
set PYTHONPATH=%PROJECT_DIR%\src;%PYTHONPATH%

rem Create logs directory if it doesn't exist
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"

rem Set log file path
set LOG_FILE=%PROJECT_DIR%\logs\api_server_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
rem Clean up log file path (replace spaces and colons)
set LOG_FILE=!LOG_FILE: =0!
set LOG_FILE=!LOG_FILE::=!

echo Starting API server at %time% on %date%
echo Logs will be written to !LOG_FILE!
echo.

rem Check if Python is available
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please ensure Python is installed and in your PATH.
    goto :error
)

rem Check if the main module exists
if not exist "%PROJECT_DIR%\src\smart_steps_ai\api\main.py" (
    echo ERROR: API server module not found at %PROJECT_DIR%\src\smart_steps_ai\api\main.py
    goto :error
)

rem Print startup info
echo Server Details:
echo - Project Directory: %PROJECT_DIR%
echo - Python Path: %PYTHONPATH%
echo - Working Directory: %CD%
echo.
echo Starting API server...
echo.

rem Run the API server with logging
cd "%PROJECT_DIR%"
python -m smart_steps_ai.api.main > "!LOG_FILE!" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: API server exited with error code %ERRORLEVEL%
    echo Check log file for details: !LOG_FILE!
    goto :error
)

echo API server stopped normally.
goto :end

:error
echo.
echo ======================================
echo  SERVER START FAILED
echo ======================================
exit /b 1

:end
echo.
echo ======================================
echo  SERVER STOPPED
echo ======================================
exit /b 0
