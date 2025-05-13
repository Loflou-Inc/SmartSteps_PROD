"""Environment variable utilities for the Smart Steps AI module."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from dotenv import load_dotenv as _load_dotenv


def load_dotenv(env_file: Optional[Union[str, Path]] = None) -> bool:
    """
    Load environment variables from a .env file.

    Args:
        env_file (Optional[Union[str, Path]]): Path to .env file (default: None)
            If None, looks for .env in the current directory and parent directories

    Returns:
        bool: True if .env file was loaded, False otherwise
    """
    if env_file:
        return _load_dotenv(env_file)
    
    # Try to find .env in the project root
    current_dir = Path.cwd()
    
    # Check current directory
    env_path = current_dir / ".env"
    if env_path.exists():
        return _load_dotenv(env_path)
    
    # Check parent directories up to 3 levels
    for _ in range(3):
        current_dir = current_dir.parent
        env_path = current_dir / ".env"
        if env_path.exists():
            return _load_dotenv(env_path)
    
    return False


def get_env(
    key: str,
    default: Optional[Any] = None,
    required: bool = False,
    env_dict: Optional[Dict[str, str]] = None,
) -> Any:
    """
    Get an environment variable.

    Args:
        key (str): Environment variable key
        default (Optional[Any]): Default value if not found (default: None)
        required (bool): Whether the variable is required (default: False)
        env_dict (Optional[Dict[str, str]]): Dictionary to use instead of os.environ (default: None)

    Returns:
        Any: Environment variable value or default

    Raises:
        ValueError: If required=True and the variable is not found
    """
    env = env_dict or os.environ
    
    value = env.get(key)
    
    if value is None:
        if required:
            raise ValueError(f"Required environment variable '{key}' not found")
        return default
    
    return value


def get_env_bool(
    key: str, default: bool = False, required: bool = False
) -> bool:
    """
    Get a boolean environment variable.

    Args:
        key (str): Environment variable key
        default (bool): Default value if not found (default: False)
        required (bool): Whether the variable is required (default: False)

    Returns:
        bool: Boolean value of the environment variable

    Raises:
        ValueError: If required=True and the variable is not found
    """
    value = get_env(key, None, required)
    
    if value is None:
        return default
    
    # Convert various string representations to boolean
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "y", "on", "t")
    
    # Convert other types
    return bool(value)


def get_env_int(
    key: str, default: Optional[int] = None, required: bool = False
) -> Optional[int]:
    """
    Get an integer environment variable.

    Args:
        key (str): Environment variable key
        default (Optional[int]): Default value if not found (default: None)
        required (bool): Whether the variable is required (default: False)

    Returns:
        Optional[int]: Integer value of the environment variable

    Raises:
        ValueError: If required=True and the variable is not found or if the value cannot be converted to int
    """
    value = get_env(key, None, required)
    
    if value is None:
        return default
    
    try:
        return int(value)
    except (ValueError, TypeError):
        if required:
            raise ValueError(f"Environment variable '{key}' is not a valid integer: {value}")
        return default


def get_env_float(
    key: str, default: Optional[float] = None, required: bool = False
) -> Optional[float]:
    """
    Get a float environment variable.

    Args:
        key (str): Environment variable key
        default (Optional[float]): Default value if not found (default: None)
        required (bool): Whether the variable is required (default: False)

    Returns:
        Optional[float]: Float value of the environment variable

    Raises:
        ValueError: If required=True and the variable is not found or if the value cannot be converted to float
    """
    value = get_env(key, None, required)
    
    if value is None:
        return default
    
    try:
        return float(value)
    except (ValueError, TypeError):
        if required:
            raise ValueError(f"Environment variable '{key}' is not a valid float: {value}")
        return default


def get_env_list(
    key: str,
    default: Optional[list] = None,
    required: bool = False,
    separator: str = ",",
) -> list:
    """
    Get a list environment variable (comma-separated by default).

    Args:
        key (str): Environment variable key
        default (Optional[list]): Default value if not found (default: None)
        required (bool): Whether the variable is required (default: False)
        separator (str): Separator character (default: ",")

    Returns:
        list: List value of the environment variable

    Raises:
        ValueError: If required=True and the variable is not found
    """
    value = get_env(key, None, required)
    
    if value is None:
        return default or []
    
    if not value:
        return []
    
    return [item.strip() for item in value.split(separator)]
