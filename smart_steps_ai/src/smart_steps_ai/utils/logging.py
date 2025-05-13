"""Logging utilities for the Smart Steps AI module."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

# Define log levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

# Configure default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_logger(
    name: str,
    level: Union[str, int] = "info",
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
) -> logging.Logger:
    """
    Configure and return a logger with the specified settings.

    Args:
        name (str): The logger name, typically the module name
        level (Union[str, int]): Log level as string or int (default: "info")
        log_file (Optional[Union[str, Path]]): Path to log file (default: None)
        log_format (str): Log format string (default: DEFAULT_LOG_FORMAT)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Convert string level to int if needed
    if isinstance(level, str):
        level = LOG_LEVELS.get(level.lower(), logging.INFO)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if log_file specified
    if log_file:
        log_path = Path(log_file)
        
        # Create directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def setup_logger(
    name: str,
    level: Union[str, int] = "info",
    log_file: Optional[Union[str, Path]] = None,
) -> logging.Logger:
    """
    Set up and configure a logger with default settings.
    
    This is a convenience wrapper around get_logger that automatically
    generates a log file path if not specified.
    
    Args:
        name (str): The logger name, typically the module name
        level (Union[str, int]): Log level as string or int (default: "info")
        log_file (Optional[Union[str, Path]]): Path to log file (default: None)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # If log_file is not specified, generate a default one
    if log_file is None:
        log_file = get_default_log_file(name.split('.')[-1])
        
    return get_logger(name, level, log_file)


def get_default_log_file(module_name: str) -> Path:
    """
    Generate a default log file path based on the module name and current date.

    Args:
        module_name (str): The module name to include in the log file name

    Returns:
        Path: The generated log file path
    """
    # Get the base log directory from the package structure
    log_dir = Path(__file__).parent.parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with date
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_{module_name}.log"
    
    return log_dir / filename
