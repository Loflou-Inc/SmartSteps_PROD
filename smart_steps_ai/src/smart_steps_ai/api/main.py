"""
Main entry point for running the Smart Steps AI API server.

This module provides a runnable script for starting the FastAPI server with Uvicorn.
"""

import logging
import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from smart_steps_ai.config import ConfigManager
from smart_steps_ai.utils.logging import setup_logger
from .app import get_application

# Configure logging
logger = setup_logger(__name__)

# Helper function to get config values with defaults
def get_config_value(config, key, default):
    """Get configuration value with default fallback."""
    value = config.get(key)
    return value if value is not None else default

def main():
    """Run the API server."""
    # Load environment variables from .env file
    env_path = Path(os.getcwd()) / ".env"
    if env_path.exists():
        logger.info(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path)
    
    # Load configuration
    config = ConfigManager()
    
    # Get host and port from config or environment variables
    api_host = os.environ.get("API_HOST")
    host = get_config_value(config, "api.host", api_host if api_host else "127.0.0.1")
    
    api_port = os.environ.get("API_PORT")
    port_str = get_config_value(config, "api.port", api_port if api_port else "9500")
    port = int(port_str)
    
    # Get other config values
    reload_enabled = get_config_value(config, "api.auto_reload", True)
    log_level = get_config_value(config, "logging.level", "info").lower()
    workers = get_config_value(config, "api.workers", 1)
    
    # Run the server
    logger.info(f"Starting Smart Steps AI API server on {host}:{port}")
    uvicorn.run(
        "smart_steps_ai.api.app:app",
        host=host,
        port=port,
        reload=reload_enabled,
        log_level=log_level,
        workers=workers
    )

if __name__ == "__main__":
    main()
