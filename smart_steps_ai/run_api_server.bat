@echo off
echo Starting Smart Steps AI API Server...

rem Set the path to the project root directory (where this batch file is located)
set PROJECT_DIR=%~dp0
rem Remove trailing backslash
set PROJECT_DIR=%PROJECT_DIR:~0,-1%

rem Set the PYTHONPATH to include the src directory
set PYTHONPATH=%PROJECT_DIR%\src;%PYTHONPATH%

rem Create logs directory if it doesn't exist
if not exist "%PROJECT_DIR%\logs" mkdir "%PROJECT_DIR%\logs"

rem Run the API server
cd "%PROJECT_DIR%"
python -m smart_steps_ai.api.main

echo API server stopped.
