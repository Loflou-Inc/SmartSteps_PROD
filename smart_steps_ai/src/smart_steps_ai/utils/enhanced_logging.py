"""Enhanced logging utilities for the Smart Steps AI module."""

import json
import logging
import os
import sys
import time
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

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
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

# Maximum log file size in bytes (default: 10MB)
DEFAULT_MAX_BYTES = 10 * 1024 * 1024

# Maximum number of backup log files
DEFAULT_BACKUP_COUNT = 5


def get_logger(
    name: str,
    level: Union[str, int] = "info",
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    console: bool = True,
    rotating: bool = False,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    timed_rotating: bool = False,
    when: str = 'midnight',
    encoding: str = "utf-8",
) -> logging.Logger:
    """
    Configure and return a logger with the specified settings.

    Args:
        name (str): The logger name, typically the module name
        level (Union[str, int]): Log level as string or int (default: "info")
        log_file (Optional[Union[str, Path]]): Path to log file (default: None)
        log_format (str): Log format string (default: DEFAULT_LOG_FORMAT)
        console (bool): Whether to log to console (default: True)
        rotating (bool): Whether to use a rotating file handler (default: False)
        max_bytes (int): Maximum file size for rotating handler (default: 10MB)
        backup_count (int): Number of backup files to keep (default: 5)
        timed_rotating (bool): Whether to use a timed rotating handler (default: False)
        when (str): When to rotate for timed rotating handler (default: 'midnight')
        encoding (str): File encoding (default: "utf-8")

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

    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if log_file specified
    if log_file:
        log_path = Path(log_file)
        
        # Create directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Choose the appropriate file handler
        if timed_rotating:
            file_handler = TimedRotatingFileHandler(
                log_path, 
                when=when,
                backupCount=backup_count,
                encoding=encoding
            )
        elif rotating:
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding=encoding
            )
        else:
            file_handler = logging.FileHandler(log_path, encoding=encoding)
            
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def setup_logger(
    name: str,
    level: Union[str, int] = "info",
    log_file: Optional[Union[str, Path]] = None,
    detailed: bool = False,
    rotating: bool = True,
) -> logging.Logger:
    """
    Set up and configure a logger with default settings.
    
    This is a convenience wrapper around get_logger that automatically
    generates a log file path if not specified.
    
    Args:
        name (str): The logger name, typically the module name
        level (Union[str, int]): Log level as string or int (default: "info")
        log_file (Optional[Union[str, Path]]): Path to log file (default: None)
        detailed (bool): Whether to use detailed log format (default: False)
        rotating (bool): Whether to use rotating log files (default: True)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # If log_file is not specified, generate a default one
    if log_file is None:
        log_file = get_default_log_file(name.split('.')[-1])
        
    # Choose the log format
    log_format = DETAILED_LOG_FORMAT if detailed else DEFAULT_LOG_FORMAT
    
    return get_logger(
        name=name, 
        level=level, 
        log_file=log_file,
        log_format=log_format,
        rotating=rotating
    )


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


class StructuredLogger:
    """
    Enhanced logger that supports structured logging with additional context.
    
    This class wraps a standard Python logger and adds support for structured
    logging with consistent context, performance metrics, and exception details.
    """
    
    def __init__(
        self, 
        name: str,
        level: Union[str, int] = "info",
        log_file: Optional[Union[str, Path]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the structured logger.
        
        Args:
            name (str): The logger name
            level (Union[str, int]): Log level as string or int (default: "info")
            log_file (Optional[Union[str, Path]]): Path to log file (default: None)
            context (Optional[Dict[str, Any]]): Default context to include in all logs
        """
        self.logger = setup_logger(name, level, log_file, detailed=True)
        self.context = context or {}
        self.timers = {}
    
    def _format_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a message with context.
        
        Args:
            message (str): The log message
            context (Optional[Dict[str, Any]]): Additional context for this message
            
        Returns:
            str: Formatted message with context
        """
        # Combine default context with message-specific context
        combined_context = {**self.context}
        if context:
            combined_context.update(context)
            
        # Return message as is if no context
        if not combined_context:
            return message
            
        # Format context as JSON
        try:
            context_str = json.dumps(combined_context)
        except Exception:
            context_str = str(combined_context)
            
        return f"{message} - Context: {context_str}"
    
    def add_context(self, key: str, value: Any) -> None:
        """
        Add a key-value pair to the default context.
        
        Args:
            key (str): Context key
            value (Any): Context value
        """
        self.context[key] = value
        
    def remove_context(self, key: str) -> None:
        """
        Remove a key from the default context.
        
        Args:
            key (str): Context key to remove
        """
        if key in self.context:
            del self.context[key]
            
    def clear_context(self) -> None:
        """Clear all default context."""
        self.context.clear()
        
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a debug message.
        
        Args:
            message (str): The log message
            context (Optional[Dict[str, Any]]): Additional context for this message
        """
        self.logger.debug(self._format_message(message, context))
        
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an info message.
        
        Args:
            message (str): The log message
            context (Optional[Dict[str, Any]]): Additional context for this message
        """
        self.logger.info(self._format_message(message, context))
        
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning message.
        
        Args:
            message (str): The log message
            context (Optional[Dict[str, Any]]): Additional context for this message
        """
        self.logger.warning(self._format_message(message, context))
        
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """
        Log an error message.
        
        Args:
            message (str): The log message
            context (Optional[Dict[str, Any]]): Additional context for this message
            exc_info (bool): Whether to include exception info (default: False)
        """
        self.logger.error(self._format_message(message, context), exc_info=exc_info)
        
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = True) -> None:
        """
        Log a critical message.
        
        Args:
            message (str): The log message
            context (Optional[Dict[str, Any]]): Additional context for this message
            exc_info (bool): Whether to include exception info (default: True)
        """
        self.logger.critical(self._format_message(message, context), exc_info=exc_info)
        
    def exception(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an exception message with traceback.
        
        Args:
            message (str): The log message
            context (Optional[Dict[str, Any]]): Additional context for this message
        """
        # Add exception details to context
        exc_type, exc_value, exc_traceback = sys.exc_info()
        exc_context = {
            "exception_type": exc_type.__name__ if exc_type else "Unknown",
            "exception_message": str(exc_value) if exc_value else "Unknown",
            "traceback": traceback.format_exc()
        }
        
        # Combine with provided context
        combined_context = context.copy() if context else {}
        combined_context.update(exc_context)
        
        self.logger.error(self._format_message(message, combined_context))
        
    def start_timer(self, name: str) -> None:
        """
        Start a timer for performance measurement.
        
        Args:
            name (str): Timer name
        """
        self.timers[name] = time.time()
        
    def stop_timer(self, name: str, level: str = "debug") -> float:
        """
        Stop a timer and log the elapsed time.
        
        Args:
            name (str): Timer name
            level (str): Log level (default: "debug")
            
        Returns:
            float: Elapsed time in seconds
        """
        if name not in self.timers:
            self.warning(f"Timer '{name}' does not exist")
            return 0.0
            
        start_time = self.timers.pop(name)
        elapsed = time.time() - start_time
        
        # Log at the appropriate level
        log_method = getattr(self, level, self.debug)
        log_method(f"Timer '{name}' completed in {elapsed:.6f} seconds")
        
        return elapsed
        
    def log_performance(
        self, operation: str, elapsed: float, success: bool = True, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log performance metrics for an operation.
        
        Args:
            operation (str): Operation name
            elapsed (float): Elapsed time in seconds
            success (bool): Whether the operation was successful (default: True)
            details (Optional[Dict[str, Any]]): Additional details about the operation
        """
        performance_context = {
            "operation": operation,
            "elapsed_seconds": round(elapsed, 6),
            "success": success
        }
        
        if details:
            performance_context.update(details)
            
        log_level = "info" if success else "warning"
        getattr(self, log_level)(
            f"Performance: {operation} took {elapsed:.6f} seconds", 
            context=performance_context
        )
