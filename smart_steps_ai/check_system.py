"""
System check script for Smart Steps AI.

This script checks the configuration and gives a detailed report on what needs to be fixed.
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

# Add the src directory to the Python path
project_dir = Path(__file__).resolve().parent
src_dir = project_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Print header
print("\n" + "=" * 80)
print(" Smart Steps AI System Check".center(80))
print("=" * 80 + "\n")

# Check Python version
print(f"Python version: {sys.version}")
if sys.version_info < (3, 8):
    print("⚠️ Warning: Python version should be 3.8 or higher")
else:
    print("✅ Python version OK")

# Check directory structure
print("\nChecking directory structure:")
directories = [
    src_dir,
    project_dir / "config",
    project_dir / "logs"
]
for directory in directories:
    if directory.exists() and directory.is_dir():
        print(f"✅ Directory exists: {directory}")
    else:
        print(f"❌ Directory missing: {directory}")
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  → Created directory: {directory}")
        except Exception as e:
            print(f"  ⚠️ Could not create directory: {e}")

# Check required dependencies
print("\nChecking required dependencies:")
required_packages = {
    "fastapi": "FastAPI",
    "uvicorn": "Uvicorn",
    "pydantic": "Pydantic",
    "jwt": "PyJWT",
    "jose": "python-jose",
    "passlib": "Passlib",
    "dotenv": "python-dotenv",
    "anthropic": "Anthropic",
    "typer": "Typer",
    "rich": "Rich",
    "matplotlib": "Matplotlib",
}

missing_packages = []
for import_name, package_name in required_packages.items():
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {package_name} installed (version: {version})")
    except ImportError:
        print(f"❌ {package_name} not installed")
        missing_packages.append(package_name.lower())

# Check API keys
print("\nChecking API keys:")
api_keys = {
    "OPENAI_API_KEY": "OpenAI API",
    "ANTHROPIC_API_KEY": "Anthropic API",
}
for key, name in api_keys.items():
    if os.environ.get(key):
        print(f"✅ {name} key found in environment")
    else:
        print(f"⚠️ {name} key not found in environment")

# Check if API server can be started
print("\nChecking API server:")

# Check full API
try:
    from smart_steps_ai.api import app
    print("✅ API module can be imported")
except ImportError as e:
    print(f"❌ API module import error: {e}")

# Check simplified API
try:
    from smart_steps_ai.simplified_api import app as simplified_app
    print("✅ Simplified API module can be imported")
except ImportError as e:
    print(f"❌ Simplified API module import error: {e}")

# Summary and recommendations
print("\n" + "=" * 80)
print(" Summary and Recommendations".center(80))
print("=" * 80 + "\n")

if missing_packages:
    print("❌ Missing dependencies:")
    print("   Please install the following packages:")
    for package in missing_packages:
        print(f"   - pip install {package}")
    print("\n   Or run:")
    print("   - install_deps.bat")
else:
    print("✅ All required dependencies are installed")

print("\nRecommended next steps:")
if missing_packages:
    print("1. Install missing dependencies")
    print("2. Run the simplified API server: run_simplified_api.bat")
else:
    print("1. Run the API server: run_api_server.bat")
    print("2. If that fails, try the simplified API: run_simplified_api.bat")

print("3. Check the API documentation at: http://127.0.0.1:8000/docs")
print("4. Configure API keys in your environment (.env file or system environment)")

print("\n" + "=" * 80 + "\n")
