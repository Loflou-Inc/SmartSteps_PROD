"""
FastAPI application setup for the Smart Steps AI API.

This module configures the FastAPI application, including middleware,
exception handlers, and routers.
"""

import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Global app instance
_app = None

def create_app(config: Optional[Dict[str, Any]] = None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        config: Application configuration
        
    Returns:
        FastAPI application instance
    """
    global _app
    
    # Create FastAPI app
    app = FastAPI(
        title="Smart Steps AI API",
        description="API for the Smart Steps AI Professional Persona module",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, this should be restricted
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Define exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "An internal server error occurred"},
        )
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    # Import and include routers
    from .routers import (
        sessions,
        conversations,
        personas,
        analysis,
    )
    
    app.include_router(sessions.router, prefix="/api/v1")
    app.include_router(conversations.router, prefix="/api/v1")
    app.include_router(personas.router, prefix="/api/v1")
    app.include_router(analysis.router, prefix="/api/v1")
    
    # Store app instance
    _app = app
    
    return app

def get_app() -> FastAPI:
    """
    Get the FastAPI application instance.
    
    Returns:
        FastAPI application instance
    """
    global _app
    if _app is None:
        return create_app()
    return _app
