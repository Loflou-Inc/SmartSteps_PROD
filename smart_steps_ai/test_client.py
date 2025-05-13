"""
Test script for the Smart Steps AI Python client library.

This script tests the functionality of the Smart Steps AI Python client library
by connecting to a running API server and making various requests.
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.smart_steps_ai.client import APIClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run the client test."""
    # Create client
    client = APIClient(
        base_url="http://127.0.0.1:9500",
        api_key=os.environ.get("SMART_STEPS_API_KEY"),
    )
    
    # Test health check
    try:
        logger.info("Testing health check...")
        health = client.health_check()
        logger.info(f"Health check result: {health}")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
    
    # Test authentication (if API key is provided)
    if os.environ.get("SMART_STEPS_API_KEY"):
        logger.info("API key provided, testing authenticated endpoints...")
        
        # Test list personas
        try:
            logger.info("Testing list personas...")
            personas = client.list_personas()
            logger.info(f"Found {len(personas.get('personas', []))} personas")
        except Exception as e:
            logger.error(f"List personas failed: {str(e)}")
    else:
        logger.warning("No API key provided. Skipping authenticated endpoints.")
        logger.info("To test authenticated endpoints, set the SMART_STEPS_API_KEY environment variable.")
        
        # Test login (requires username and password)
        try:
            username = input("Enter username for login test: ")
            password = input("Enter password for login test: ")
            
            logger.info("Testing login...")
            login_result = client.login(username, password)
            logger.info(f"Login result: {login_result}")
            
            # Now that we're logged in, test authenticated endpoints
            logger.info("Testing list personas...")
            personas = client.list_personas()
            logger.info(f"Found {len(personas.get('personas', []))} personas")
        except Exception as e:
            logger.error(f"Login and subsequent tests failed: {str(e)}")

if __name__ == "__main__":
    main()
