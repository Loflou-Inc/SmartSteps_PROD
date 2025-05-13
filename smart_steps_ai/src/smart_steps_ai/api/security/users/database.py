"""
User database for the Smart Steps AI API.

This module provides user storage and management for the API.
"""

# Mock user database for development/testing
# In production, this would be replaced with a real user database
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@example.com",
        "password": "password",  # Plain text for testing only
        "disabled": False,
        "role": "admin",
        "scopes": ["sessions:read", "sessions:write", "personas:read", "personas:write", "analysis:read", "analysis:write"]
    },
    "therapist": {
        "username": "therapist",
        "full_name": "Test Therapist",
        "email": "therapist@example.com",
        "password": "password",  # Plain text for testing only
        "disabled": False,
        "role": "therapist",
        "scopes": ["sessions:read", "sessions:write", "personas:read", "analysis:read"]
    },
    "client": {
        "username": "client",
        "full_name": "Test Client",
        "email": "client@example.com",
        "password": "password",  # Plain text for testing only
        "disabled": False,
        "role": "client",
        "scopes": ["sessions:read"]
    }
}
