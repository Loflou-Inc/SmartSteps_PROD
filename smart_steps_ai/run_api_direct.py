"""
Direct launcher for the Smart Steps API Server.

This script runs the actual API server with proper error handling.
"""

import os
import sys
import traceback
import importlib.util
from pathlib import Path

# Add the src directory to the Python path
project_dir = Path(__file__).resolve().parent
src_dir = project_dir / "src"
sys.path.insert(0, str(src_dir))

def check_dependencies():
    """Check for required dependencies."""
    required_packages = [
        "fastapi", "uvicorn", "pydantic", 
        "python_jose", "pyjwt", 
        "passlib", "python_multipart", "bcrypt"
    ]
    
    missing = []
    for package in required_packages:
        try:
            # Handle special cases for packages with hyphens
            module_name = package
            if package == "python_jose":
                try:
                    importlib.import_module("jose")
                    print(f"+ {package} installed")
                    continue
                except ImportError:
                    pass
            elif package == "python_multipart":
                try:
                    importlib.import_module("multipart")
                    print(f"+ {package} installed")
                    continue
                except ImportError:
                    pass
            elif package == "pyjwt":
                try:
                    importlib.import_module("jwt")
                    print(f"+ {package} installed")
                    continue
                except ImportError:
                    pass
            
            # Try to import the module
            importlib.import_module(module_name)
            print(f"+ {package} installed")
        except ImportError:
            missing.append(package.replace("_", "-"))
            print(f"- {package} missing")
    
    if missing:
        print("\nMissing dependencies. Install with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Run the Smart Steps API server."""
    print("===== Smart Steps API Server =====")
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    try:
        # Import and run the main module
        print("\nStarting API server...")
        from smart_steps_ai.api.main import main
        main()
    except ImportError as e:
        print(f"\nERROR: Failed to import API module: {e}")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Failed to start API server: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
