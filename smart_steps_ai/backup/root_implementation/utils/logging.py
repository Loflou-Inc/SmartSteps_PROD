"""
Logging utilities for the Smart Steps AI module.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Default log directory is in the project root
DEFAULT_LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "logs"
)

# Create the log directory if it doesn't exist
os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)

# Default log file
DEFAULT_LOG_FILE = os.path.join(DEFAULT_LOG_DIR, "smart_steps_ai.log")

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configure root logger
def configure_logging(
    log_file: Optional[str] = None,
    log_level: int = logging.INFO,
    console_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure logging for the Smart Steps AI module.
    
    Args:
        log_file: Path to the log file. Defaults to logs/smart_steps_ai.log in the project root.
        log_level: Log level for the file handler.
        console_level: Log level for the console handler.
        max_bytes: Maximum size of log file before rotation.
        backup_count: Number of backup files to keep.
        
    Returns:
        The configured logger.
    """
    # Use default log file if not specified
    if log_file is None:
        log_file = DEFAULT_LOG_FILE
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("smart_steps_ai")
    logger.setLevel(min(log_level, console_level))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    
    # Create file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Get a logger for a specific module
def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module.
        
    Returns:
        A logger configured for the module.
    """
    return logging.getLogger(f"smart_steps_ai.{module_name}")

# Default logger
logger = get_logger("utils.logging")

# Log uncaught exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Log uncaught exceptions.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set the exception handler
sys.excepthook = handle_exception
