"""
Test script for the Smart Steps AI CLI.
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import the CLI application from the local module
from smart_steps_ai.__main__ import app, info

if __name__ == "__main__":
    # Run the info command directly
    print("Running the info command:")
    info()
    
    print("\nCLI successfully tested!")
    print("To run the full CLI, use: python -m smart_steps_ai [COMMAND]")
