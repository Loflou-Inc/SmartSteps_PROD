# Run server from src implementation
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from smart_steps_ai.api.main import main

if __name__ == "__main__":
    print("Starting Smart Steps AI API Server from src implementation...")
    main()
