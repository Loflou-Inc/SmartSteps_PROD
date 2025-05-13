"""Utility functions for the Smart Steps AI module."""

from .logging import get_logger, setup_logger, DEFAULT_LOG_FORMAT, LOG_LEVELS
from .enhanced_logging import StructuredLogger
from .validation import validate_schema, load_json_file, save_json_file
from .enhanced_validation import (
    validate_type, validate_range, validate_length, validate_regex,
    validate_email, validate_date, validate_file_exists,
    validate_directory_exists, validate_file_extension, validate_with_function,
    validate_multiple
)
from .formatting import format_text, format_list_items, truncate_text
from .env import load_dotenv, get_env, get_env_bool, get_env_int, get_env_float, get_env_list
from .security import (
    generate_random_string, hash_password, verify_password,
    encrypt_data, decrypt_data, generate_hmac, verify_hmac,
    sanitize_input, create_rate_limiter, generate_timed_token, verify_timed_token
)

__all__ = [
    # Logging
    'get_logger', 'setup_logger', 'DEFAULT_LOG_FORMAT', 'LOG_LEVELS', 'StructuredLogger',
    
    # Validation
    'validate_schema', 'load_json_file', 'save_json_file',
    'validate_type', 'validate_range', 'validate_length', 'validate_regex',
    'validate_email', 'validate_date', 'validate_file_exists',
    'validate_directory_exists', 'validate_file_extension', 'validate_with_function',
    'validate_multiple',
    
    # Formatting
    'format_text', 'format_list_items', 'truncate_text',
    
    # Environment
    'load_dotenv', 'get_env', 'get_env_bool', 'get_env_int', 'get_env_float', 'get_env_list',
    
    # Security
    'generate_random_string', 'hash_password', 'verify_password',
    'encrypt_data', 'decrypt_data', 'generate_hmac', 'verify_hmac',
    'sanitize_input', 'create_rate_limiter', 'generate_timed_token', 'verify_timed_token'
]