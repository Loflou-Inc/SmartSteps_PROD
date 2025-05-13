"""
API server verification tool.

This script checks that all components needed for the API server are
properly installed and configured.
"""

import os
import sys
import importlib
import pkg_resources
from pathlib import Path

# Add the src directory to the Python path
project_dir = Path(__file__).resolve().parent
src_dir = project_dir / "src"
sys.path.insert(0, str(src_dir))

def check_python_version():
    """Check if the Python version is compatible."""
    print(f"Checking Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ is required, but you have {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_required_packages():
    """Check if all required packages are installed."""
    print(f"\nChecking required packages...")
    required = [
        "fastapi", "uvicorn", "pydantic", "jose", "python-jose", 
        "passlib", "python-multipart", "bcrypt", "python-dotenv"
    ]
    
    missing = []
    all_packages = {pkg.key for pkg in pkg_resources.working_set}
    
    for pkg in required:
        pkg_name = pkg.replace("-", "_")
        try:
            importlib.import_module(pkg_name)
            print(f"✅ {pkg} is installed")
        except ImportError:
            try:
                # Try alternate import name
                if pkg_name == "jose":
                    importlib.import_module("python_jose")
                    print(f"✅ {pkg} is installed (as python-jose)")
                    continue
                if pkg_name == "python_jose":
                    importlib.import_module("jose")
                    print(f"✅ {pkg} is installed (as jose)")
                    continue
                
                # Check if it's installed but just can't be imported
                if pkg.replace("-", "_") in all_packages or pkg in all_packages:
                    print(f"⚠️ {pkg} is installed but cannot be imported")
                else:
                    raise ImportError()
            except ImportError:
                missing.append(pkg)
                print(f"❌ {pkg} is missing")
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install them with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    print(f"\nAll required packages are installed.")
    return True

def check_api_modules():
    """Check if all API modules are present."""
    print(f"\nChecking API modules...")
    required_modules = [
        "smart_steps_ai.api.app",
        "smart_steps_ai.api.main",
        "smart_steps_ai.api.dependencies",
        "smart_steps_ai.api.routers.auth",
        "smart_steps_ai.api.routers.sessions",
        "smart_steps_ai.api.routers.personas",
        "smart_steps_ai.api.routers.conversations",
        "smart_steps_ai.api.security.auth",
    ]
    
    missing = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} is present")
        except ImportError as e:
            missing.append(module)
            print(f"❌ {module} is missing: {e}")
    
    if missing:
        print(f"\nMissing modules: {', '.join(missing)}")
        return False
    
    print(f"\nAll required API modules are present.")
    return True

def check_environment():
    """Check if environment variables are configured."""
    print(f"\nChecking environment configuration...")
    
    # Check .env file
    env_path = project_dir / ".env"
    if not env_path.exists():
        print(f"⚠️ .env file not found at {env_path}")
        template_path = project_dir / ".env.template"
        if template_path.exists():
            print(f"   You can create one based on {template_path}")
    else:
        print(f"✅ .env file found at {env_path}")
    
    # Check key environment variables
    important_vars = [
        "API_HOST", "API_PORT", "API_SECRET_KEY", 
        "API_TOKEN_EXPIRES_MINUTES", "API_DEBUG"
    ]
    
    for var in important_vars:
        if var in os.environ:
            print(f"✅ Environment variable {var} is set")
        else:
            print(f"⚠️ Environment variable {var} is not set (will use default)")
    
    return True

def check_api_server():
    """Perform all checks for the API server."""
    print("====================================")
    print(" Smart Steps AI API Server Checker")
    print("====================================\n")
    
    python_ok = check_python_version()
    packages_ok = check_required_packages()
    modules_ok = check_api_modules()
    env_ok = check_environment()
    
    print("\n====================================")
    if all([python_ok, packages_ok, modules_ok, env_ok]):
        print("✅ All checks passed! The API server is ready to run.")
        print("   Run the server with: run_api_server.bat")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues before running the server.")
        return False

if __name__ == "__main__":
    success = check_api_server()
    sys.exit(0 if success else 1)
