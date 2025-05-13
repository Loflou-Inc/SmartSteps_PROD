"""Enhanced validation utilities for the Smart Steps AI module."""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Type, Union, Callable

from pydantic import BaseModel, ValidationError


def validate_schema(
    data: Dict[str, Any], schema: Type[BaseModel]
) -> tuple[bool, Optional[str], Optional[BaseModel]]:
    """
    Validate data against a pydantic schema.

    Args:
        data (Dict[str, Any]): The data to validate
        schema (Type[BaseModel]): The pydantic model to validate against

    Returns:
        tuple[bool, Optional[str], Optional[BaseModel]]: 
            - Success flag
            - Error message (if failed)
            - Validated model instance (if successful)
    """
    try:
        validated_data = schema(**data)
        return True, None, validated_data
    except ValidationError as e:
        return False, str(e), None


def load_json_file(
    file_path: Union[str, Path], schema: Optional[Type[BaseModel]] = None
) -> tuple[bool, Optional[str], Optional[Union[Dict[str, Any], BaseModel]]]:
    """
    Load and optionally validate a JSON file.

    Args:
        file_path (Union[str, Path]): Path to the JSON file
        schema (Optional[Type[BaseModel]]): Pydantic model to validate against (default: None)

    Returns:
        tuple[bool, Optional[str], Optional[Union[Dict[str, Any], BaseModel]]]:
            - Success flag
            - Error message (if failed)
            - Loaded data (if successful)
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False, f"File not found: {path}", None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if schema:
            success, error, validated_data = validate_schema(data, schema)
            if not success:
                return False, f"Validation error: {error}", None
            return True, None, validated_data
        
        return True, None, data
    
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}", None
    
    except Exception as e:
        return False, f"Error loading file: {str(e)}", None


def save_json_file(
    data: Union[Dict[str, Any], BaseModel],
    file_path: Union[str, Path],
    pretty: bool = True,
) -> tuple[bool, Optional[str]]:
    """
    Save data to a JSON file.

    Args:
        data (Union[Dict[str, Any], BaseModel]): Data to save
        file_path (Union[str, Path]): Path where to save the file
        pretty (bool): Whether to format the JSON with indentation (default: True)

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    try:
        path = Path(file_path)
        
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert pydantic model to dict if needed
        if isinstance(data, BaseModel):
            data_dict = data.model_dump()
        else:
            data_dict = data
        
        with open(path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data_dict, f, ensure_ascii=False)
        
        return True, None
    
    except Exception as e:
        return False, f"Error saving file: {str(e)}"


def validate_type(
    value: Any, expected_type: Union[Type, tuple], name: str = "value"
) -> tuple[bool, Optional[str]]:
    """
    Validate that a value is of the expected type.

    Args:
        value (Any): The value to validate
        expected_type (Union[Type, tuple]): The expected type(s)
        name (str): Name of the value for error messages (default: "value")

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    if not isinstance(value, expected_type):
        return False, f"{name} must be of type {expected_type.__name__}, got {type(value).__name__}"
    return True, None


def validate_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    name: str = "value",
) -> tuple[bool, Optional[str]]:
    """
    Validate that a numeric value is within the specified range.

    Args:
        value (Union[int, float]): The value to validate
        min_value (Optional[Union[int, float]]): Minimum allowed value (default: None)
        max_value (Optional[Union[int, float]]): Maximum allowed value (default: None)
        name (str): Name of the value for error messages (default: "value")

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    if not isinstance(value, (int, float)):
        return False, f"{name} must be a number, got {type(value).__name__}"
    
    if min_value is not None and value < min_value:
        return False, f"{name} must be at least {min_value}, got {value}"
    
    if max_value is not None and value > max_value:
        return False, f"{name} must be at most {max_value}, got {value}"
    
    return True, None


def validate_length(
    value: Union[str, list, dict],
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    name: str = "value",
) -> tuple[bool, Optional[str]]:
    """
    Validate that a string, list, or dict has a length within the specified range.

    Args:
        value (Union[str, list, dict]): The value to validate
        min_length (Optional[int]): Minimum allowed length (default: None)
        max_length (Optional[int]): Maximum allowed length (default: None)
        name (str): Name of the value for error messages (default: "value")

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    if not hasattr(value, "__len__"):
        return False, f"{name} must have a length (str, list, dict, etc.), got {type(value).__name__}"
    
    length = len(value)
    
    if min_length is not None and length < min_length:
        return False, f"{name} must have at least {min_length} elements, got {length}"
    
    if max_length is not None and length > max_length:
        return False, f"{name} must have at most {max_length} elements, got {length}"
    
    return True, None


def validate_regex(
    value: str, pattern: Union[str, Pattern], name: str = "value"
) -> tuple[bool, Optional[str]]:
    """
    Validate that a string matches the specified regex pattern.

    Args:
        value (str): The string to validate
        pattern (Union[str, Pattern]): Regex pattern to match against
        name (str): Name of the value for error messages (default: "value")

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    if not isinstance(value, str):
        return False, f"{name} must be a string, got {type(value).__name__}"
    
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
    
    if not pattern.match(value):
        return False, f"{name} does not match the required pattern"
    
    return True, None


def validate_email(email: str) -> tuple[bool, Optional[str]]:
    """
    Validate that a string is a properly formatted email address.

    Args:
        email (str): The email address to validate

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    if not isinstance(email, str):
        return False, f"Email must be a string, got {type(email).__name__}"
    
    # Simple regex for basic email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if not re.match(pattern, email):
        return False, f"Invalid email address: {email}"
    
    return True, None


def validate_date(
    date_str: str, format_str: str = "%Y-%m-%d"
) -> tuple[bool, Optional[str], Optional[datetime]]:
    """
    Validate that a string is a properly formatted date.

    Args:
        date_str (str): The date string to validate
        format_str (str): Expected date format (default: "%Y-%m-%d")

    Returns:
        tuple[bool, Optional[str], Optional[datetime]]:
            - Success flag
            - Error message (if failed)
            - Parsed datetime (if successful)
    """
    if not isinstance(date_str, str):
        return False, f"Date must be a string, got {type(date_str).__name__}", None
    
    try:
        date_obj = datetime.strptime(date_str, format_str)
        return True, None, date_obj
    except ValueError as e:
        return False, f"Invalid date format: {str(e)}", None


def validate_file_exists(
    file_path: Union[str, Path], name: str = "file"
) -> tuple[bool, Optional[str]]:
    """
    Validate that a file exists.

    Args:
        file_path (Union[str, Path]): Path to the file
        name (str): Name of the file for error messages (default: "file")

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    path = Path(file_path)
    
    if not path.exists():
        return False, f"{name} does not exist: {path}"
    
    if not path.is_file():
        return False, f"{name} is not a file: {path}"
    
    return True, None


def validate_directory_exists(
    directory_path: Union[str, Path], name: str = "directory"
) -> tuple[bool, Optional[str]]:
    """
    Validate that a directory exists.

    Args:
        directory_path (Union[str, Path]): Path to the directory
        name (str): Name of the directory for error messages (default: "directory")

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    path = Path(directory_path)
    
    if not path.exists():
        return False, f"{name} does not exist: {path}"
    
    if not path.is_dir():
        return False, f"{name} is not a directory: {path}"
    
    return True, None


def validate_file_extension(
    file_path: Union[str, Path], allowed_extensions: List[str]
) -> tuple[bool, Optional[str]]:
    """
    Validate that a file has an allowed extension.

    Args:
        file_path (Union[str, Path]): Path to the file
        allowed_extensions (List[str]): List of allowed extensions

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    path = Path(file_path)
    
    # Get the lowercase extension without the dot
    extension = path.suffix.lower().lstrip(".")
    
    # Normalize allowed extensions
    normalized_extensions = [ext.lower().lstrip(".") for ext in allowed_extensions]
    
    if extension not in normalized_extensions:
        return False, f"File has invalid extension: {extension}. Allowed: {', '.join(normalized_extensions)}"
    
    return True, None


def validate_with_function(
    value: Any, validator_func: Callable[[Any], bool], error_message: str = "Validation failed"
) -> tuple[bool, Optional[str]]:
    """
    Validate a value using a custom validation function.

    Args:
        value (Any): The value to validate
        validator_func (Callable[[Any], bool]): Function that returns True if valid
        error_message (str): Error message to return if validation fails

    Returns:
        tuple[bool, Optional[str]]:
            - Success flag
            - Error message (if failed)
    """
    try:
        if validator_func(value):
            return True, None
        return False, error_message
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_multiple(
    validators: List[Callable[[], tuple[bool, Optional[str]]]]
) -> tuple[bool, List[str]]:
    """
    Run multiple validators and collect all errors.

    Args:
        validators (List[Callable[[], tuple[bool, Optional[str]]]]): 
            List of validation functions that each return (success, error)

    Returns:
        tuple[bool, List[str]]:
            - Overall success flag
            - List of error messages
    """
    success = True
    errors = []
    
    for validator in validators:
        valid, error = validator()
        if not valid:
            success = False
            if error:
                errors.append(error)
    
    return success, errors
