"""
Quick test runner script for the Smart Steps AI module.
"""

import os
import sys
import time
from pathlib import Path

# Set environment variables for testing
os.environ["SMART_STEPS_APP_ENVIRONMENT"] = "testing"
os.environ["SMART_STEPS_PROVIDERS_USE_MOCK"] = "true"
os.environ["SMART_STEPS_PROVIDERS_MOCK_ENABLED"] = "true"

# Run the end-to-end tests
print("Running end-to-end tests...")
start_time = time.time()
result = os.system(f"python {Path(__file__).parent / 'test_end_to_end.py'}")
duration = time.time() - start_time

print(f"Tests completed in {duration:.2f} seconds with exit code {result}")
sys.exit(result)
