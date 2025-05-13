"""
Run the Smart Steps AI API server directly.

This script attempts to start the API server with proper error handling
and suggestions for fixing common issues.
"""

import os
import sys
import traceback
from pathlib import Path

# Add the src directory to the Python path
project_dir = Path(__file__).resolve().parent
src_dir = project_dir / "src"
sys.path.insert(0, str(src_dir))

# Ensure logs directory exists
logs_dir = project_dir / "logs"
logs_dir.mkdir(exist_ok=True)

# Create a config directory if needed
config_dir = project_dir / "config"
config_dir.mkdir(exist_ok=True)

# Check for required dependencies
def check_dependencies():
    """Check for required dependencies and suggest installation if missing."""
    required = [
        "fastapi", "uvicorn", "pydantic", "jwt", "python-jose", 
        "passlib", "python-multipart", "bcrypt", "python-dotenv"
    ]
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Missing required dependencies: {', '.join(missing)}")
        print("Please install missing dependencies:")
        for pkg in missing:
            print(f"  pip install {pkg}")
        print("Or run the install_deps.bat script.")
        return False
    
    return True

# Run the API server
if __name__ == "__main__":
    print("Starting Smart Steps AI API Server...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import and run the main function
    try:
        from smart_steps_ai.api.main import main
        main()
    except ImportError as e:
        print(f"Error importing API module: {e}")
        print("\nThis may be caused by missing dependencies or incorrect Python path.")
        print("Suggestions:")
        print("1. Run install_deps.bat to install missing dependencies")
        print("2. Make sure your virtual environment is activated (if using one)")
        print("3. Check that the 'src' directory is in your Python path")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Error starting API server: {e}")
        traceback.print_exc()
        sys.exit(1)
