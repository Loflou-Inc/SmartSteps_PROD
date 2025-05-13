#!/usr/bin/env python
"""
Script to run the Smart Steps AI API server.

This script provides a convenient way to start the API server for development
and testing.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from smart_steps_ai.api.main import main

if __name__ == "__main__":
    main()
