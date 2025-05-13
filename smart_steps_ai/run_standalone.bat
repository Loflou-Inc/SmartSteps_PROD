@echo off
REM =======================================================
REM Smart Steps AI Standalone Runner (Windows)
REM =======================================================
REM This script runs the Smart Steps AI system in standalone mode.
REM It starts the API server and provides a simple interface
REM for interacting with it.
REM
REM Author: Smart Steps Team
REM Date: May 13, 2025
REM =======================================================

echo Smart Steps AI Standalone Runner
echo ===============================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.9 or later.
    exit /b 1
)

REM Set up environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies if needed
if not exist venv\Lib\site-packages\fastapi (
    echo Installing dependencies...
    pip install -e .
)

REM Run the standalone runner
python standalone_runner.py %*

REM Deactivate virtual environment
call venv\Scripts\deactivate

echo.
echo Smart Steps AI Standalone Runner exited.
