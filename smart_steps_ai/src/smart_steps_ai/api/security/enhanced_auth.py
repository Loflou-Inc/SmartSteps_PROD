"""
Enhanced security middleware for the Smart Steps AI API.

This module implements advanced security features including:
1. Rate limiting to prevent brute force attacks
2. JWT token validation with proper error handling
3. Scope-based authorization
4. Security event logging
"""

import time
from typing import Dict, List, Optional

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
import logging

from smart_steps_ai.config import ConfigManager
from smart_steps_ai.utils.logging import setup_logger

# Configure logging
logger = setup_logger("api.security")

# Load configuration
config = ConfigManager()
api_security = config.get("api.security")
API_SECRET_KEY = api_security.secret_key if api_security and hasattr(api_security, "secret_key") else "development_secret_key"
ALGORITHM = "HS256"

# Rate limiting settings
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100  # maximum requests per window
IP_RATE_LIMITS: Dict[str, List[float]] = {}  # IP -> list of request timestamps


class RateLimitMiddleware:
    """Middleware for API rate limiting."""
    
    async def __call__(self, request: Request, call_next):
        """Process the request with rate limiting."""
        # Skip rate limiting for certain paths
        if request.url.path.startswith("/api/docs") or request.url.path.startswith("/api/redoc"):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Apply rate limiting
        if self._is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Process request
        return await call_next(request)
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if the client IP is rate limited."""
        current_time = time.time()
        
        # Initialize if this is a new IP
        if client_ip not in IP_RATE_LIMITS:
            IP_RATE_LIMITS[client_ip] = []
        
        # Clean up old timestamps
        IP_RATE_LIMITS[client_ip] = [t for t in IP_RATE_LIMITS[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
        
        # Check if rate limit is exceeded
        if len(IP_RATE_LIMITS[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            return True
        
        # Add current request timestamp
        IP_RATE_LIMITS[client_ip].append(current_time)
        return False


class EnhancedJWTBearer(HTTPBearer):
    """Enhanced JWT bearer token authentication with proper error handling."""
    
    def __init__(self, auto_error: bool = True):
        """Initialize with auto error handling."""
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request):
        """Process the request with JWT validation."""
        try:
            credentials = await super().__call__(request)
            
            if credentials:
                # Validate token
                token = credentials.credentials
                payload = self._verify_jwt_token(token)
                
                # Add decoded payload to request state
                request.state.user = payload
                request.state.token = token
                
                # Log successful authentication
                logger.debug(f"Authenticated user: {payload.get('sub', 'unknown')}")
                
                return credentials
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication credentials"
            )
            
        except HTTPException as e:
            # Log authentication failure
            logger.warning(f"Authentication failed: {e.detail}")
            raise
    
    def _verify_jwt_token(self, token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            # Decode token
            payload = jwt.decode(token, API_SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if token has required fields
            if "sub" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            return payload
            
        except JWTError as e:
            # Log detailed error but return generic message
            logger.error(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or token expired"
            )


def verify_scope(required_scope: str):
    """Dependency for verifying user has the required scope."""
    
    async def _verify_scope(request: Request):
        """Verify that the authenticated user has the required scope."""
        # Get user from request state
        user = getattr(request.state, "user", None)
        
        if not user:
            logger.warning("Scope verification failed: No authenticated user")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Get scopes from token
        scopes = user.get("scopes", [])
        
        # Check if required scope is in user's scopes
        if required_scope not in scopes:
            logger.warning(f"Scope verification failed: User {user.get('sub')} missing scope {required_scope}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scope: {required_scope}"
            )
        
        return True
    
    return _verify_scope


# Export components
jwt_bearer = EnhancedJWTBearer()
rate_limit_middleware = RateLimitMiddleware()
