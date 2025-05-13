"""
Authentication and authorization components for the Smart Steps AI API.

This module provides functions and middleware for handling user authentication
and authorization in the API.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from smart_steps_ai.config import ConfigManager
from ..dependencies import get_config_manager

# Define models for authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    role: str
    scopes: list = []

# Set up OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Mock user database for development/testing
# In production, this would be replaced with a real user database
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$8N.5UVEpMmwXt6LzMJsRMu2S5DVZ8BVKpO/Y.nWr4.3PFbVntDq86",  # "password"
        "disabled": False,
        "role": "admin",
        "scopes": ["sessions:read", "sessions:write", "personas:read", "personas:write", "analysis:read", "analysis:write"]
    },
    "therapist": {
        "username": "therapist",
        "full_name": "Test Therapist",
        "email": "therapist@example.com",
        "hashed_password": "$2b$12$8N.5UVEpMmwXt6LzMJsRMu2S5DVZ8BVKpO/Y.nWr4.3PFbVntDq86",  # "password"
        "disabled": False,
        "role": "therapist",
        "scopes": ["sessions:read", "sessions:write", "personas:read", "analysis:read"]
    },
    "client": {
        "username": "client",
        "full_name": "Test Client",
        "email": "client@example.com",
        "hashed_password": "$2b$12$8N.5UVEpMmwXt6LzMJsRMu2S5DVZ8BVKpO/Y.nWr4.3PFbVntDq86",  # "password"
        "disabled": False,
        "role": "client",
        "scopes": ["sessions:read"]
    }
}

def get_user(username: str):
    """Get a user from the database."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return User(**user_dict)
    return None

def verify_password(plain_password: str, hashed_password: str):
    """Verify a password against a hash."""
    # In a real implementation, this would use a proper password hashing library
    # such as bcrypt or passlib to securely verify passwords
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    """Authenticate a user with username and password."""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, fake_users_db[username]["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, config_manager=None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if config_manager is None:
        config_manager = ConfigManager()
    
    # Get secret key from environment
    secret_key = os.environ.get("API_SECRET_KEY", "development_secret_key")
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)  # Default 30 minutes
    
    to_encode.update({"exp": expire})
    
    # Create JWT token
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), config_manager=Depends(get_config_manager)):
    """Get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Get secret key from environment
        secret_key = os.environ.get("API_SECRET_KEY", "development_secret_key")
        
        # Decode JWT token
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username, scopes=payload.get("scopes", []))
    except InvalidTokenError:
        raise credentials_exception
    
    # Get user
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    
    # Check if user is disabled
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """Get the current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
