"""
Text formatting utilities for the Smart Steps AI module.
"""

import re
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

def format_timestamp(timestamp: Optional[float] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a timestamp as a string.
    
    Args:
        timestamp: The timestamp to format, or None for current time.
        format_str: The format string to use.
        
    Returns:
        The formatted timestamp.
    """
    if timestamp is None:
        dt = datetime.now()
    else:
        dt = datetime.fromtimestamp(timestamp)
    
    return dt.strftime(format_str)

def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds as a human-readable string.
    
    Args:
        seconds: The duration in seconds.
        
    Returns:
        A human-readable string representation of the duration.
    """
    # Handle negative durations
    if seconds < 0:
        return "0 seconds"
    
    # Convert to minutes and seconds
    minutes, seconds = divmod(int(seconds), 60)
    
    # Convert to hours and minutes
    hours, minutes = divmod(minutes, 60)
    
    # Format the string
    parts = []
    
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    if seconds > 0 or not parts:
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    return ", ".join(parts)

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated.
    
    Args:
        text: The text to truncate.
        max_length: The maximum length of the truncated text, including the suffix.
        suffix: The suffix to add if the text is truncated.
        
    Returns:
        The truncated text.
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_list(items: List[str], conjunction: str = "and") -> str:
    """
    Format a list of items as a natural language string.
    
    Args:
        items: The list of items to format.
        conjunction: The conjunction to use for the last item.
        
    Returns:
        A natural language string.
    """
    if not items:
        return ""
    
    if len(items) == 1:
        return items[0]
    
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    
    return ", ".join(items[:-1]) + f", {conjunction} {items[-1]}"

def format_json(data: Any, indent: int = 2) -> str:
    """
    Format a JSON-serializable object as a pretty-printed string.
    
    Args:
        data: The data to format.
        indent: The indent level.
        
    Returns:
        A pretty-printed JSON string.
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)

def format_template(template: str, data: Dict[str, Any]) -> str:
    """
    Format a template string with data.
    
    Args:
        template: The template string, with placeholders in the format {{key}}.
        data: The data to use for formatting.
        
    Returns:
        The formatted string.
    """
    # Handle simple replacements
    result = template
    
    # Replace placeholders with values
    for key, value in data.items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    
    # Handle conditional placeholders in the format {{if_condition:true_value|false_value}}
    conditional_pattern = r"{{if_([^:]+):([^|]+)\|([^}]+)}}"
    
    for match in re.finditer(conditional_pattern, template):
        condition_key, true_value, false_value = match.groups()
        
        # Check if the condition is true
        condition_met = False
        if condition_key in data:
            condition_met = bool(data[condition_key])
        
        # Replace the placeholder with the appropriate value
        placeholder = match.group(0)
        replacement = true_value if condition_met else false_value
        result = result.replace(placeholder, replacement)
    
    return result

def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace and converting to lowercase.
    
    Args:
        text: The text to normalize.
        
    Returns:
        The normalized text.
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Convert to lowercase
    text = text.lower()
    
    return text
