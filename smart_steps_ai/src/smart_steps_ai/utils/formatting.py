"""Text formatting utilities for the Smart Steps AI module."""

import re
from string import Template
from typing import Any, Dict, List, Optional, Union


def format_text(
    template: str, variables: Dict[str, Any], fallback: str = "", strip: bool = True
) -> str:
    """
    Format a string template with the provided variables.

    Args:
        template (str): Template string with placeholders
        variables (Dict[str, Any]): Variables to substitute in the template
        fallback (str): Fallback value for missing variables (default: "")
        strip (bool): Whether to strip whitespace from the result (default: True)

    Returns:
        str: Formatted text
    """
    # Handle empty template
    if not template:
        return ""

    # Create a safe variables dictionary with string values
    safe_vars = {k: str(v) if v is not None else fallback for k, v in variables.items()}
    
    # Use string.Template for basic formatting
    result = Template(template).safe_substitute(safe_vars)
    
    # Handle conditional expressions like {{if_condition:true_value|false_value}}
    result = _process_conditional_expressions(result, variables)
    
    # Strip whitespace if requested
    if strip:
        result = result.strip()
    
    return result


def _process_conditional_expressions(
    text: str, variables: Dict[str, Any]
) -> str:
    """
    Process conditional expressions in the format {{if_condition:true_value|false_value}}.

    Args:
        text (str): Text containing conditional expressions
        variables (Dict[str, Any]): Variables for evaluating conditions

    Returns:
        str: Text with processed conditional expressions
    """
    # Pattern to find conditional expressions
    pattern = r"\{\{if_([a-zA-Z0-9_]+):(.*?)\|(.*?)\}\}"
    
    def replace_conditional(match):
        condition_var = match.group(1)
        true_value = match.group(2)
        false_value = match.group(3)
        
        # Check if the condition variable exists and is truthy
        if condition_var in variables and variables[condition_var]:
            return true_value
        return false_value
    
    # Replace all conditional expressions
    return re.sub(pattern, replace_conditional, text)


def format_list_items(items: List[str], separator: str = ", ", last_separator: str = " and ") -> str:
    """
    Format a list of items into a human-readable string.

    Args:
        items (List[str]): List of items to format
        separator (str): Separator between items (default: ", ")
        last_separator (str): Separator before the last item (default: " and ")

    Returns:
        str: Formatted list string
    """
    if not items:
        return ""
    
    if len(items) == 1:
        return items[0]
    
    return separator.join(items[:-1]) + last_separator + items[-1]


def truncate_text(text: str, max_length: int, ellipsis: str = "...") -> str:
    """
    Truncate text to a maximum length, adding ellipsis if needed.

    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        ellipsis (str): Ellipsis string to append (default: "...")

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(ellipsis)] + ellipsis
