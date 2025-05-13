#!/usr/bin/env python
"""
Clean up the Smart Steps AI project directory by removing temporary files,
outdated documentation, and redundant files created during debugging.

This script will remove files that don't belong in the repository.
"""

import os
import sys
import shutil
from pathlib import Path

# Base path to project
BASE_PATH = Path("G:/My Drive/Deftech/SmartSteps/smart_steps_ai")

# Files to remove (relative to base path)
FILES_TO_REMOVE = [
    # Temporary debug files we created
    "improved_api_test.py",
    "fixed_api_test.py",
    "api_routing_diagnostic.py",
    "working_api_test.py", 
    "generate_test_token.py",
    "api_test_token.txt",
    "final_api_test.py",
    "debug_jwt.py",
    "debug_token.txt",
    "run_api_test_server.bat",
    "debug_token_test.py",
    "run_fixed_api_server.bat",
    "fixed_server_test.py",
    
    # Outdated documentation files
    "API_TEST_SUMMARY.md",
    "API_DEBUGGING_REPORT.md",
    "API_DEBUG_RESULTS.md",
    
    # Backup files we created during debugging
    "src/smart_steps_ai/api/dependencies.py.fixed",
    "src/smart_steps_ai/api/dependencies.py.bak",
    
    # Duplicate or redundant scripts
    "CLEANUP_REPORT.md",
    "CLEANUP_SUMMARY.md",
]

def remove_files():
    """Remove the specified files."""
    print("The following files will be removed:")
    
    # Remove the files
    for file_path in FILES_TO_REMOVE:
        full_path = BASE_PATH / file_path
        if full_path.exists():
            try:
                if full_path.is_file():
                    os.remove(full_path)
                elif full_path.is_dir():
                    shutil.rmtree(full_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {str(e)}")
    
    print("\nCleanup completed.")

if __name__ == "__main__":
    remove_files()
