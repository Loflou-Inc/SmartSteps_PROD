"""
Authentication endpoints for the Smart Steps AI API.

This module provides API endpoints for user authentication.
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from smart_steps_ai.config import ConfigManager
from ..dependencies import get_config_manager
from ..security.simple_auth import authenticate_user, get_current_user

router = APIRouter()

@router.post(
    "/token", 
    summary="Login and get access token",
    description="Authenticates a user and returns an access token."
)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    config_manager: ConfigManager = Depends(get_config_manager)
):
    """Authenticate user and provide access token."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For testing, we use a simplified token approach - username is the token
    access_token = user["username"]
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get(
    "/me", 
    summary="Get current user",
    description="Returns information about the currently authenticated user."
)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get information about the currently authenticated user."""
    return current_user

@router.post(
    "/logout",
    status_code=200,
    summary="Logout current user",
    description="Logs out the current user."
)
async def logout(response: Response, request: Request):
    """Logout the current user."""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}
