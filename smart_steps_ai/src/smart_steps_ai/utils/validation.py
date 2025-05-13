"""Validation utilities for the Smart Steps AI module."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

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
