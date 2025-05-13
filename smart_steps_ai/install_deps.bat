@echo off
echo Installing Smart Steps AI Module dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    exit /b %errorlevel%
)
echo Dependencies installed successfully!
