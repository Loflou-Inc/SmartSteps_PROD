"""
Script to read the last part of the errors log file.
"""

import os
from pathlib import Path

# Get the errors log file
log_dir = Path("G:/My Drive/Deftech/SmartSteps/smart_steps_ai/logs")
error_log = log_dir / "2025-05-12_errors.log"

# Read the last 200 lines
with open(error_log, "r") as f:
    lines = f.readlines()
    last_lines = lines[-200:]

# Print the last lines
for line in last_lines:
    print(line.strip())
