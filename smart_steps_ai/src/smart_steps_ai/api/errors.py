"""
API exception handling module.

This module provides custom exception classes and exception handlers
for the Smart Steps AI API.
"""

from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from smart_steps_ai.utils.logging import setup_logger

# Configure logging
logger = setup_logger(__name__)

class APIError(Exception):
    """Base class for API errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        error_code: str = "internal_error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the API error."""
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class BadRequestError(APIError):
    """Error for bad requests."""
    
    def __init__(
        self, 
        message: str = "Bad request", 
        error_code: str = "bad_request",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the bad request error."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST, error_code, details)


class AuthenticationError(APIError):
    """Error for authentication failures."""
    
    def __init__(
        self, 
        message: str = "Authentication failed", 
        error_code: str = "authentication_failed",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the authentication error."""
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, error_code, details)


class AuthorizationError(APIError):
    """Error for authorization failures."""
    
    def __init__(
        self, 
        message: str = "Insufficient permissions", 
        error_code: str = "insufficient_permissions",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the authorization error."""
        super().__init__(message, status.HTTP_403_FORBIDDEN, error_code, details)


class NotFoundError(APIError):
    """Error for not found resources."""
    
    def __init__(
        self, 
        message: str = "Resource not found", 
        error_code: str = "not_found",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the not found error."""
        super().__init__(message, status.HTTP_404_NOT_FOUND, error_code, details)


class RateLimitError(APIError):
    """Error for rate limiting."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        error_code: str = "rate_limit_exceeded",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the rate limit error."""
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS, error_code, details)


class ValidationError(APIError):
    """Error for validation failures."""
    
    def __init__(
        self, 
        message: str = "Validation failed", 
        error_code: str = "validation_failed",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the validation error."""
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, error_code, details)


class ServerError(APIError):
    """Error for server errors."""
    
    def __init__(
        self, 
        message: str = "Internal server error", 
        error_code: str = "internal_server_error",
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the server error."""
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, error_code, details)


# Exception handlers
async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handle API errors."""
    # Log the error
    logger.error(f"API error: {exc.error_code} - {exc.message}")
    
    # Prepare the response
    content = {
        "error": True,
        "message": exc.message,
        "error_code": exc.error_code,
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method,
    }
    
    # Add details if available
    if exc.details:
        content["details"] = exc.details
    
    # Add request ID if available
    if hasattr(request.state, "request_id"):
        content["request_id"] = request.state.request_id
    
    return JSONResponse(status_code=exc.status_code, content=content)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTPExceptions."""
    # Map HTTP exceptions to our API errors
    error_code = f"http_{exc.status_code}"
    message = exc.detail
    
    # Log the error
    logger.error(f"HTTP exception: {error_code} - {message}")
    
    # Prepare the response
    content = {
        "error": True,
        "message": message,
        "error_code": error_code,
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method,
    }
    
    # Add request ID if available
    if hasattr(request.state, "request_id"):
        content["request_id"] = request.state.request_id
    
    return JSONResponse(status_code=exc.status_code, content=content)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    # Extract validation errors
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(x) for x in error["loc"])
        errors.append({
            "location": loc,
            "message": error["msg"],
            "type": error["type"],
        })
    
    # Log the error
    logger.error(f"Validation error: {len(errors)} errors")
    
    # Prepare the response
    content = {
        "error": True,
        "message": "Validation failed",
        "error_code": "validation_error",
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "path": request.url.path,
        "method": request.method,
        "details": {
            "errors": errors
        }
    }
    
    # Add request ID if available
    if hasattr(request.state, "request_id"):
        content["request_id"] = request.state.request_id
    
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=content)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unhandled exceptions."""
    # Log the error
    logger.exception(f"Unhandled exception: {str(exc)}")
    
    # Prepare the response
    content = {
        "error": True,
        "message": "An unexpected error occurred",
        "error_code": "internal_server_error",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "path": request.url.path,
        "method": request.method,
    }
    
    # Add request ID if available
    if hasattr(request.state, "request_id"):
        content["request_id"] = request.state.request_id
    
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the FastAPI application."""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
