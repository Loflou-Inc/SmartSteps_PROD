#!/bin/bash
# =======================================================
# Smart Steps AI Standalone Runner (Linux/macOS)
# =======================================================
# This script runs the Smart Steps AI system in standalone mode.
# It starts the API server and provides a simple interface
# for interacting with it.
#
# Author: Smart Steps Team
# Date: May 13, 2025
# =======================================================

echo "Smart Steps AI Standalone Runner"
echo "==============================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.9 or later."
    exit 1
fi

# Set up environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -d "venv/lib/python*/site-packages/fastapi" ]; then
    echo "Installing dependencies..."
    pip install -e .
fi

# Run the standalone runner
python standalone_runner.py "$@"

# Deactivate virtual environment
deactivate

echo
echo "Smart Steps AI Standalone Runner exited."
