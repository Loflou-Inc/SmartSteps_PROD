@echo off
REM =======================================================
REM Smart Steps AI End-to-End Verification Script (Windows)
REM =======================================================
REM This script runs a complete end-to-end verification of
REM the Smart Steps AI system, including API, monitoring,
REM and deployment verification.
REM
REM Usage: run_verification.bat [options]
REM Options:
REM   --clean     Start with a clean environment
REM   --docker    Test using Docker containers
REM   --help      Show this help message
REM
REM Author: Smart Steps Team
REM Date: May 13, 2025
REM =======================================================

setlocal EnableDelayedExpansion

echo Smart Steps AI End-to-End Verification
echo ======================================

REM Parse command line arguments
set CLEAN_ENV=0
set USE_DOCKER=0
set SHOW_HELP=0

:parse_args
if "%~1"=="" goto :end_parse_args
if /i "%~1"=="--clean" set CLEAN_ENV=1
if /i "%~1"=="--docker" set USE_DOCKER=1
if /i "%~1"=="--help" set SHOW_HELP=1
shift
goto :parse_args
:end_parse_args

if %SHOW_HELP%==1 (
    echo.
    echo Usage: run_verification.bat [options]
    echo Options:
    echo   --clean     Start with a clean environment
    echo   --docker    Test using Docker containers
    echo   --help      Show this help message
    echo.
    exit /b 0
)

REM Create verification directory
set VERIFY_DIR=%~dp0\verification_results
if not exist "%VERIFY_DIR%" mkdir "%VERIFY_DIR%"
set LOG_FILE=%VERIFY_DIR%\verification_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOG_FILE=%LOG_FILE: =0%

REM Log start time
echo Starting verification at %date% %time% > "%LOG_FILE%"
echo Environment: Windows >> "%LOG_FILE%"
echo Clean environment: %CLEAN_ENV% >> "%LOG_FILE%"
echo Use Docker: %USE_DOCKER% >> "%LOG_FILE%"

REM Check prerequisites
echo.
echo Checking prerequisites...
echo Checking prerequisites... >> "%LOG_FILE%"

REM Check Python
python --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Please install Python 3.9 or later.
    echo ERROR: Python not found. Please install Python 3.9 or later. >> "%LOG_FILE%"
    exit /b 1
)

REM Check Docker if using Docker mode
if %USE_DOCKER%==1 (
    docker --version > nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Docker not found. Please install Docker or use without --docker flag.
        echo ERROR: Docker not found. Please install Docker or use without --docker flag. >> "%LOG_FILE%"
        exit /b 1
    )
    
    docker-compose --version > nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Docker Compose not found. Please install Docker Compose.
        echo ERROR: Docker Compose not found. Please install Docker Compose. >> "%LOG_FILE%"
        exit /b 1
    )
)

REM Environment setup
echo.
echo Setting up verification environment...
echo Setting up verification environment... >> "%LOG_FILE%"

REM Create virtual environment if not using Docker
if %USE_DOCKER%==0 (
    if %CLEAN_ENV%==1 (
        if exist venv (
            echo Removing existing virtual environment...
            echo Removing existing virtual environment... >> "%LOG_FILE%"
            rmdir /s /q venv
        )
    )
    
    if not exist venv (
        echo Creating virtual environment...
        echo Creating virtual environment... >> "%LOG_FILE%"
        python -m venv venv
        if %ERRORLEVEL% neq 0 (
            echo ERROR: Failed to create virtual environment.
            echo ERROR: Failed to create virtual environment. >> "%LOG_FILE%"
            exit /b 1
        )
    )
    
    echo Activating virtual environment...
    echo Activating virtual environment... >> "%LOG_FILE%"
    call venv\Scripts\activate
    
    echo Installing dependencies...
    echo Installing dependencies... >> "%LOG_FILE%"
    pip install -e . >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install dependencies.
        echo ERROR: Failed to install dependencies. >> "%LOG_FILE%"
        exit /b 1
    )
    
    REM Create test configuration
    echo Configuring test environment...
    echo Configuring test environment... >> "%LOG_FILE%"
    copy deployment\config\development.env .env /y >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to create test configuration.
        echo ERROR: Failed to create test configuration. >> "%LOG_FILE%"
        exit /b 1
    )
)

REM Docker setup if using Docker
if %USE_DOCKER%==1 (
    echo Starting Docker containers...
    echo Starting Docker containers... >> "%LOG_FILE%"
    
    REM Stop any running containers
    docker-compose -f deployment\docker-compose.yml down >> "%LOG_FILE%" 2>&1
    
    REM Start containers
    docker-compose -f deployment\docker-compose.yml up -d >> "%LOG_FILE%" 2>&1
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to start Docker containers.
        echo ERROR: Failed to start Docker containers. >> "%LOG_FILE%"
        exit /b 1
    )
    
    REM Wait for services to start
    echo Waiting for services to initialize...
    timeout /t 10 /nobreak > nul
) else (
    REM Start API server
    echo Starting API server...
    echo Starting API server... >> "%LOG_FILE%"
    start "Smart Steps API" cmd /c "call venv\Scripts\activate && python run_api_server.py > %VERIFY_DIR%\api_server.log 2>&1"
    
    REM Start monitoring system
    echo Starting monitoring system...
    echo Starting monitoring system... >> "%LOG_FILE%"
    start "Smart Steps Monitoring" cmd /c "call venv\Scripts\activate && python deployment\monitoring_system.py start > %VERIFY_DIR%\monitoring.log 2>&1"
    
    REM Wait for services to start
    echo Waiting for services to initialize...
    timeout /t 10 /nobreak > nul
)

REM Run verification tests
echo.
echo Running verification tests...
echo Running verification tests... >> "%LOG_FILE%"

if %USE_DOCKER%==1 (
    python verify_system.py --all --api-url http://localhost:9500 --username admin --password admin123 >> "%LOG_FILE%" 2>&1
) else (
    python verify_system.py --all >> "%LOG_FILE%" 2>&1
)

set VERIFY_RESULT=%ERRORLEVEL%

REM Output verification results
if %VERIFY_RESULT%==0 (
    echo.
    echo ========================================
    echo VERIFICATION SUCCESSFUL!
    echo All verification tests passed.
    echo ========================================
    echo.
    echo VERIFICATION SUCCESSFUL! >> "%LOG_FILE%"
) else (
    echo.
    echo ========================================
    echo VERIFICATION FAILED!
    echo Some tests did not pass. See logs for details.
    echo ========================================
    echo.
    echo VERIFICATION FAILED! >> "%LOG_FILE%"
)

REM Cleanup
echo.
echo Cleaning up...
echo Cleaning up... >> "%LOG_FILE%"

if %USE_DOCKER%==1 (
    if %CLEAN_ENV%==1 (
        echo Stopping Docker containers...
        echo Stopping Docker containers... >> "%LOG_FILE%"
        docker-compose -f deployment\docker-compose.yml down >> "%LOG_FILE%" 2>&1
    )
) else (
    echo Stopping services...
    echo Stopping services... >> "%LOG_FILE%"
    
    REM Find and kill the API server process
    for /f "tokens=2" %%a in ('tasklist ^| findstr "Smart Steps API"') do (
        taskkill /pid %%a /f > nul 2>&1
    )
    
    REM Find and kill the monitoring system process
    for /f "tokens=2" %%a in ('tasklist ^| findstr "Smart Steps Monitoring"') do (
        taskkill /pid %%a /f > nul 2>&1
    )
    
    REM Deactivate virtual environment
    call venv\Scripts\deactivate
)

echo.
echo Verification completed! Logs available at:
echo %LOG_FILE%
echo.

exit /b %VERIFY_RESULT%
