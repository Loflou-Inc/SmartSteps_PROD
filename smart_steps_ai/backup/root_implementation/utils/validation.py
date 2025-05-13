"""
Validation utilities for the Smart Steps AI module.
"""

import os
import json
import jsonschema
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from .logging import get_logger

# Get logger
logger = get_logger("utils.validation")

# Persona schema
PERSONA_SCHEMA = {
    "type": "object",
    "required": [
        "name",
        "display_name",
        "version",
        "description",
        "system_prompt"
    ],
    "properties": {
        "name": {
            "type": "string",
            "description": "Unique identifier for the persona"
        },
        "display_name": {
            "type": "string",
            "description": "Human-readable name for the persona"
        },
        "version": {
            "type": "string",
            "description": "Version of the persona definition"
        },
        "description": {
            "type": "string",
            "description": "Brief description of the persona"
        },
        "system_prompt": {
            "type": "string",
            "description": "System prompt to configure the AI model"
        },
        "personality_traits": {
            "type": "object",
            "description": "Personality traits with numeric values"
        },
        "expertise_areas": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Areas of expertise for the persona"
        },
        "conversation_style": {
            "type": "object",
            "description": "Conversation style configuration"
        },
        "analysis_approach": {
            "type": "object",
            "description": "Analysis approach configuration"
        },
        "rules": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Rules that the persona should follow"
        },
        "examples": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "context",
                    "client_message",
                    "response"
                ],
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Context for the example"
                    },
                    "client_message": {
                        "type": "string",
                        "description": "Client message in the example"
                    },
                    "response": {
                        "type": "string",
                        "description": "Persona response in the example"
                    }
                }
            },
            "description": "Example conversations for the persona"
        }
    }
}

def validate_json(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate JSON data against a schema.
    
    Args:
        data: The JSON data to validate.
        schema: The JSON schema to validate against.
        
    Returns:
        A list of validation errors, or an empty list if validation passed.
    """
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    
    # Format the errors
    error_messages = []
    for error in errors:
        if error.path:
            path = ".".join(str(p) for p in error.path)
            error_messages.append(f"{path}: {error.message}")
        else:
            error_messages.append(error.message)
    
    return error_messages

def validate_persona(persona_data: Dict[str, Any]) -> List[str]:
    """
    Validate a persona definition.
    
    Args:
        persona_data: The persona data to validate.
        
    Returns:
        A list of validation errors, or an empty list if validation passed.
    """
    return validate_json(persona_data, PERSONA_SCHEMA)

def validate_persona_file(file_path: str) -> List[str]:
    """
    Validate a persona definition file.
    
    Args:
        file_path: Path to the persona definition file.
        
    Returns:
        A list of validation errors, or an empty list if validation passed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            persona_data = json.load(f)
            return validate_persona(persona_data)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON format: {str(e)}"]
    except Exception as e:
        return [f"Error reading file: {str(e)}"]

def is_valid_session_id(session_id: str) -> bool:
    """
    Check if a session ID is valid.
    
    Args:
        session_id: The session ID to check.
        
    Returns:
        True if the session ID is valid, False otherwise.
    """
    # For now, just check if it's a non-empty string
    return isinstance(session_id, str) and bool(session_id.strip())

def is_valid_client_id(client_id: str) -> bool:
    """
    Check if a client ID is valid.
    
    Args:
        client_id: The client ID to check.
        
    Returns:
        True if the client ID is valid, False otherwise.
    """
    # For now, just check if it's a non-empty string
    return isinstance(client_id, str) and bool(client_id.strip())

def is_valid_session_type(session_type: str) -> bool:
    """
    Check if a session type is valid.
    
    Args:
        session_type: The session type to check.
        
    Returns:
        True if the session type is valid, False otherwise.
    """
    # Valid session types
    valid_types = [
        "therapy",
        "assessment",
        "crisis",
        "followup",
        "initial",
        "coaching",
        "consultation"
    ]
    
    return session_type in valid_types

def is_valid_analysis_type(analysis_type: str) -> bool:
    """
    Check if an analysis type is valid.
    
    Args:
        analysis_type: The analysis type to check.
        
    Returns:
        True if the analysis type is valid, False otherwise.
    """
    # Valid analysis types
    valid_types = [
        "full",
        "brief",
        "insights",
        "progress",
        "patterns",
        "summary"
    ]
    
    return analysis_type in valid_types
