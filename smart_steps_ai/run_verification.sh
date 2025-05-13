#!/bin/bash
# =======================================================
# Smart Steps AI End-to-End Verification Script (Linux/macOS)
# =======================================================
# This script runs a complete end-to-end verification of
# the Smart Steps AI system, including API, monitoring,
# and deployment verification.
#
# Usage: ./run_verification.sh [options]
# Options:
#   --clean     Start with a clean environment
#   --docker    Test using Docker containers
#   --help      Show this help message
#
# Author: Smart Steps Team
# Date: May 13, 2025
# =======================================================

# Exit on error
set -e

echo "Smart Steps AI End-to-End Verification"
echo "======================================"

# Parse command line arguments
CLEAN_ENV=0
USE_DOCKER=0
SHOW_HELP=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --clean)
            CLEAN_ENV=1
            shift
            ;;
        --docker)
            USE_DOCKER=1
            shift
            ;;
        --help)
            SHOW_HELP=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            SHOW_HELP=1
            shift
            ;;
    esac
done

if [ $SHOW_HELP -eq 1 ]; then
    echo ""
    echo "Usage: ./run_verification.sh [options]"
    echo "Options:"
    echo "  --clean     Start with a clean environment"
    echo "  --docker    Test using Docker containers"
    echo "  --help      Show this help message"
    echo ""
    exit 0
fi

# Create verification directory
VERIFY_DIR="$(dirname "$0")/verification_results"
mkdir -p "$VERIFY_DIR"
LOG_FILE="$VERIFY_DIR/verification_$(date +%Y%m%d_%H%M%S).log"

# Log start time
echo "Starting verification at $(date)" > "$LOG_FILE"
echo "Environment: $(uname -s)" >> "$LOG_FILE"
echo "Clean environment: $CLEAN_ENV" >> "$LOG_FILE"
echo "Use Docker: $USE_DOCKER" >> "$LOG_FILE"

# Check prerequisites
echo ""
echo "Checking prerequisites..."
echo "Checking prerequisites..." >> "$LOG_FILE"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.9 or later."
    echo "ERROR: Python not found. Please install Python 3.9 or later." >> "$LOG_FILE"
    exit 1
fi

# Check Docker if using Docker mode
if [ $USE_DOCKER -eq 1 ]; then
    if ! command -v docker &> /dev/null; then
        echo "ERROR: Docker not found. Please install Docker or use without --docker flag."
        echo "ERROR: Docker not found. Please install Docker or use without --docker flag." >> "$LOG_FILE"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "ERROR: Docker Compose not found. Please install Docker Compose."
        echo "ERROR: Docker Compose not found. Please install Docker Compose." >> "$LOG_FILE"
        exit 1
    fi
fi

# Environment setup
echo ""
echo "Setting up verification environment..."
echo "Setting up verification environment..." >> "$LOG_FILE"

# Create virtual environment if not using Docker
if [ $USE_DOCKER -eq 0 ]; then
    if [ $CLEAN_ENV -eq 1 ]; then
        if [ -d "venv" ]; then
            echo "Removing existing virtual environment..."
            echo "Removing existing virtual environment..." >> "$LOG_FILE"
            rm -rf venv
        fi
    fi
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        echo "Creating virtual environment..." >> "$LOG_FILE"
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    echo "Activating virtual environment..." >> "$LOG_FILE"
    source venv/bin/activate
    
    echo "Installing dependencies..."
    echo "Installing dependencies..." >> "$LOG_FILE"
    pip install -e . >> "$LOG_FILE" 2>&1
    
    # Create test configuration
    echo "Configuring test environment..."
    echo "Configuring test environment..." >> "$LOG_FILE"
    cp deployment/config/development.env .env >> "$LOG_FILE" 2>&1
fi

# Docker setup if using Docker
if [ $USE_DOCKER -eq 1 ]; then
    echo "Starting Docker containers..."
    echo "Starting Docker containers..." >> "$LOG_FILE"
    
    # Stop any running containers
    docker-compose -f deployment/docker-compose.yml down >> "$LOG_FILE" 2>&1
    
    # Start containers
    docker-compose -f deployment/docker-compose.yml up -d >> "$LOG_FILE" 2>&1
    
    # Wait for services to start
    echo "Waiting for services to initialize..."
    sleep 10
else
    # Start API server
    echo "Starting API server..."
    echo "Starting API server..." >> "$LOG_FILE"
    nohup python run_api_server.py > "$VERIFY_DIR/api_server.log" 2>&1 &
    API_PID=$!
    
    # Start monitoring system
    echo "Starting monitoring system..."
    echo "Starting monitoring system..." >> "$LOG_FILE"
    nohup python deployment/monitoring_system.py start > "$VERIFY_DIR/monitoring.log" 2>&1 &
    MONITORING_PID=$!
    
    # Wait for services to start
    echo "Waiting for services to initialize..."
    sleep 10
fi

# Run verification tests
echo ""
echo "Running verification tests..."
echo "Running verification tests..." >> "$LOG_FILE"

if [ $USE_DOCKER -eq 1 ]; then
    python verify_system.py --all --api-url http://localhost:9500 --username admin --password admin123 >> "$LOG_FILE" 2>&1
else
    python verify_system.py --all >> "$LOG_FILE" 2>&1
fi

VERIFY_RESULT=$?

# Output verification results
if [ $VERIFY_RESULT -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "VERIFICATION SUCCESSFUL!"
    echo "All verification tests passed."
    echo "========================================"
    echo ""
    echo "VERIFICATION SUCCESSFUL!" >> "$LOG_FILE"
else
    echo ""
    echo "========================================"
    echo "VERIFICATION FAILED!"
    echo "Some tests did not pass. See logs for details."
    echo "========================================"
    echo ""
    echo "VERIFICATION FAILED!" >> "$LOG_FILE"
fi

# Cleanup
echo ""
echo "Cleaning up..."
echo "Cleaning up..." >> "$LOG_FILE"

if [ $USE_DOCKER -eq 1 ]; then
    if [ $CLEAN_ENV -eq 1 ]; then
        echo "Stopping Docker containers..."
        echo "Stopping Docker containers..." >> "$LOG_FILE"
        docker-compose -f deployment/docker-compose.yml down >> "$LOG_FILE" 2>&1
    fi
else
    echo "Stopping services..."
    echo "Stopping services..." >> "$LOG_FILE"
    
    # Kill the API server process
    if [ -n "$API_PID" ]; then
        kill -15 $API_PID 2>/dev/null || true
    fi
    
    # Kill the monitoring system process
    if [ -n "$MONITORING_PID" ]; then
        kill -15 $MONITORING_PID 2>/dev/null || true
    fi
    
    # Deactivate virtual environment
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
    fi
fi

echo ""
echo "Verification completed! Logs available at:"
echo "$LOG_FILE"
echo ""

exit $VERIFY_RESULT
