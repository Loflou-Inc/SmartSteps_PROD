"""
Authentication API endpoints.

This module provides endpoints for user authentication and token management.
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from smart_steps_ai.config import ConfigManager
from ..security.auth import authenticate_user, create_access_token, Token, User, get_current_active_user
from ..dependencies import get_config_manager

router = APIRouter()

@router.post(
    "/token", 
    response_model=Token,
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
    
    # Get token expiration time from config
    access_token_expires_minutes = config_manager.get("api.security.token_expires_minutes", 30)
    access_token_expires = timedelta(minutes=access_token_expires_minutes)
    
    # Create token with user info and scopes
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires,
        config_manager=config_manager
    )
    
    # Set token in HTTP-only cookie for enhanced security
    cookie_secure = config_manager.get("api.security.secure_cookies", False)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=cookie_secure,
        samesite="strict",
        max_age=access_token_expires_minutes * 60
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get(
    "/me", 
    response_model=User,
    summary="Get current user",
    description="Returns information about the currently authenticated user."
)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get information about the currently authenticated user."""
    return current_user

@router.post(
    "/logout",
    status_code=200,
    summary="Logout current user",
    description="Logs out the current user by invalidating their token."
)
async def logout(response: Response, request: Request):
    """Logout the current user."""
    # Clear the access token cookie
    response.delete_cookie(key="access_token")
    
    return {"message": "Successfully logged out"}

