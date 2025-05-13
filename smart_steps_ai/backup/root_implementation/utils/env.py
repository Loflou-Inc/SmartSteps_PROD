"""
Environment utilities for the Smart Steps AI module.
"""

import os
import dotenv
from typing import Any, Dict, Optional
from pathlib import Path

from .logging import get_logger

# Get logger
logger = get_logger("utils.env")

# Load environment variables from .env file
def load_env(env_file: Optional[str] = None) -> bool:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file: Path to the .env file. If None, looks for .env in the current directory.
        
    Returns:
        True if the .env file was loaded successfully, False otherwise.
    """
    try:
        # Use the specified .env file or look for one in the current directory
        if env_file is None:
            # Look for .env file in the project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_file = os.path.join(project_root, ".env")
        
        # Check if the .env file exists
        if not os.path.exists(env_file):
            logger.warning(f".env file not found: {env_file}")
            return False
        
        # Load the .env file
        result = dotenv.load_dotenv(env_file)
        
        if result:
            logger.debug(f"Loaded environment variables from {env_file}")
        else:
            logger.warning(f"Failed to load environment variables from {env_file}")
        
        return result
    except Exception as e:
        logger.error(f"Error loading environment variables: {e}")
        return False

def get_env(key: str, default: Any = None) -> Any:
    """
    Get an environment variable.
    
    Args:
        key: The environment variable name.
        default: The default value to return if the environment variable is not set.
        
    Returns:
        The environment variable value, or the default if not set.
    """
    value = os.environ.get(key)
    
    if value is None:
        logger.debug(f"Environment variable not found: {key}, returning default: {default}")
        return default
    
    return value

def get_bool_env(key: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable.
    
    Args:
        key: The environment variable name.
        default: The default value to return if the environment variable is not set.
        
    Returns:
        The environment variable value as a boolean, or the default if not set.
    """
    value = get_env(key)
    
    if value is None:
        return default
    
    return value.lower() in ["true", "yes", "1", "t", "y"]

def get_int_env(key: str, default: Optional[int] = None) -> Optional[int]:
    """
    Get an integer environment variable.
    
    Args:
        key: The environment variable name.
        default: The default value to return if the environment variable is not set.
        
    Returns:
        The environment variable value as an integer, or the default if not set.
    """
    value = get_env(key)
    
    if value is None:
        return default
    
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Invalid integer environment variable: {key}={value}")
        return default

def get_float_env(key: str, default: Optional[float] = None) -> Optional[float]:
    """
    Get a float environment variable.
    
    Args:
        key: The environment variable name.
        default: The default value to return if the environment variable is not set.
        
    Returns:
        The environment variable value as a float, or the default if not set.
    """
    value = get_env(key)
    
    if value is None:
        return default
    
    try:
        return float(value)
    except ValueError:
        logger.warning(f"Invalid float environment variable: {key}={value}")
        return default

def get_comma_separated_env(key: str, default: Optional[list] = None) -> Optional[list]:
    """
    Get a comma-separated environment variable as a list.
    
    Args:
        key: The environment variable name.
        default: The default value to return if the environment variable is not set.
        
    Returns:
        The environment variable value as a list, or the default if not set.
    """
    value = get_env(key)
    
    if value is None:
        return default or []
    
    return [item.strip() for item in value.split(",") if item.strip()]

def set_env(key: str, value: Any) -> None:
    """
    Set an environment variable.
    
    Args:
        key: The environment variable name.
        value: The value to set.
    """
    os.environ[key] = str(value)
    logger.debug(f"Set environment variable: {key}={value}")

# Load environment variables on import
load_env()
