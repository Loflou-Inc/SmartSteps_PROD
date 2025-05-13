@echo off
echo Reinstalling Smart Steps AI...
echo.
echo Deactivating virtual environment...
call venv\Scripts\deactivate.bat
echo.
echo Removing old installation...
pip uninstall -y smart_steps_ai
echo.
echo Installing in development mode...
pip install -e .
echo.
echo Installation complete!
echo.
echo You can now run the API server with run_api_server.bat
