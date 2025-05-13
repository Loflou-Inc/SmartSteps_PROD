@echo off
REM Set up environment for OpenAI test

REM Read the API keys from .env file
for /F "tokens=1,2 delims==" %%a in (G:\My Drive\Deftech\SmartSteps\smart_steps_ai\.env) do (
  set %%a=%%b
)

echo API Environment Setup:
echo ---------------------
echo OPENAI_API_KEY=%OPENAI_API_KEY:~0,5%...
echo SMART_STEPS_API_KEY=%SMART_STEPS_API_KEY:~0,5%...
echo.

echo Starting OpenAI Integration Test...
python "G:\My Drive\Deftech\SmartSteps\smart_steps_ai\test_openai_integration.py"
