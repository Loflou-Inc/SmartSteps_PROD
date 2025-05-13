"""
Security utility functions for the Smart Steps AI API.

This module provides utility functions for security-related tasks like
rate limiting, input sanitization, and content security.
"""

import re
import time
from typing import Dict, List, Optional

from fastapi import HTTPException, Request, status

# Simple in-memory rate limiter
# In production, this would be replaced with a more robust solution like Redis
class RateLimiter:
    """Simple in-memory rate limiter for API endpoints."""
    
    def __init__(self, requests_per_minute: int = 60):
        """Initialize the rate limiter.
        
        Args:
            requests_per_minute: Maximum number of requests allowed per minute.
        """
        self.requests_per_minute = requests_per_minute
        self.request_records: Dict[str, List[float]] = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if a request is allowed for a client.
        
        Args:
            client_id: Identifier for the client (e.g., IP address).
            
        Returns:
            bool: True if the request is allowed, False otherwise.
        """
        current_time = time.time()
        time_window = 60.0  # 1 minute window
        
        # Initialize client record if not exists
        if client_id not in self.request_records:
            self.request_records[client_id] = []
        
        # Remove old requests
        self.request_records[client_id] = [
            timestamp for timestamp in self.request_records[client_id]
            if current_time - timestamp < time_window
        ]
        
        # Check if allowed
        if len(self.request_records[client_id]) >= self.requests_per_minute:
            return False
        
        # Add new request
        self.request_records[client_id].append(current_time)
        return True

# Input sanitization functions
def sanitize_input(text: str) -> str:
    """Sanitize input text to prevent injection attacks.
    
    Args:
        text: Input text to sanitize.
        
    Returns:
        str: Sanitized text.
    """
    # Remove potentially dangerous characters
    if text is None:
        return ""
    
    # Basic sanitization - in production, use a proper sanitization library
    sanitized = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    sanitized = re.sub(r'<.*?>', '', sanitized)
    return sanitized

def sanitize_json_input(data: dict) -> dict:
    """Recursively sanitize strings in a JSON-like structure.
    
    Args:
        data: Dictionary to sanitize.
        
    Returns:
        dict: Sanitized dictionary.
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = sanitize_input(value)
        elif isinstance(value, dict):
            result[key] = sanitize_json_input(value)
        elif isinstance(value, list):
            result[key] = [
                sanitize_json_input(item) if isinstance(item, dict)
                else sanitize_input(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result

# Rate limiting middleware
async def rate_limit_middleware(request: Request, limiter: RateLimiter):
    """Middleware for rate limiting API requests.
    
    Args:
        request: FastAPI request object.
        limiter: RateLimiter instance.
        
    Raises:
        HTTPException: If the rate limit is exceeded.
    """
    # Get client identifier (IP address in this simple implementation)
    client_id = request.client.host if request.client else "unknown"
    
    # Check if allowed
    if not limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
