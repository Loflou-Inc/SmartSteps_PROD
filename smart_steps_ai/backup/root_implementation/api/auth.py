"""
Authentication for the Smart Steps AI API.

This module provides authentication functionality for the API,
including API key validation and user authentication.
"""

import os
from typing import Optional, Dict, List
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import logging
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel

# Initialize logger
logger = logging.getLogger(__name__)

# API key header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# JWT settings
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "default_secret_key")  # Change in production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours


class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    scopes: List[str] = []


class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: List[str] = []


# Mock user database (replace with actual database in production)
users_db = {
    "admin": User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        disabled=False,
        scopes=["admin"]
    ),
    "user": User(
        username="user",
        email="user@example.com",
        full_name="Regular User",
        disabled=False,
        scopes=["user"]
    )
}


# Mock API keys (replace with secure storage in production)
api_keys = {
    "test_api_key": "user",
    "admin_api_key": "admin"
}


async def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    """
    Validate API key.
    
    Args:
        api_key: API key from request header
        
    Returns:
        Username associated with the API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_keys[api_key]


async def get_current_user(username: str = Depends(get_api_key)) -> User:
    """
    Get current user from API key.
    
    Args:
        username: Username from API key
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user does not exist or is disabled
    """
    if username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    user = users_db[username]
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is disabled",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Token data
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        Decoded token data
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
