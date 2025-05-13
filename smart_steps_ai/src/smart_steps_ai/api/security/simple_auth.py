"""
Simplified authentication for the Smart Steps AI API.

This module provides a simpler authentication mechanism for the API.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .users.database import fake_users_db

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def get_user_from_db(username: str):
    """Get a user from the database."""
    if username in fake_users_db:
        return fake_users_db[username]
    return None

def authenticate_user(username: str, password: str):
    """Authenticate a user with username and password."""
    user = get_user_from_db(username)
    if not user:
        return False
    if password != user["password"]:  # Simple direct comparison for testing
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from a token."""
    # For testing, we use a simplified token approach
    # In production, use proper JWT validation
    if token == "invalid_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For this simplified version, we assume the token is the username
    user = get_user_from_db(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Check if the current user is an admin."""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
