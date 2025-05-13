"""
Main FastAPI application definition for Smart Steps AI.

This module configures the FastAPI application with all routes, middleware,
and dependencies for the Smart Steps AI Professional Persona REST API.
"""

import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse

from smart_steps_ai.config import ConfigManager
from smart_steps_ai.utils.logging import setup_logger

# Configure logging
logger = setup_logger(__name__)

# Initialize configuration
config = ConfigManager()

# Helper function to get config values with defaults
def get_config(key, default):
    """Get configuration value with default fallback."""
    value = config.get(key)
    return value if value is not None else default

# Create FastAPI application
app = FastAPI(
    title="Smart Steps AI API",
    description="REST API for Smart Steps AI Professional Persona system",
    version="0.1.0",
    docs_url=None,  # We'll configure custom docs later
    redoc_url=None,  # We'll configure custom docs later
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_config("api.cors.origins", ["*"]),
    allow_credentials=get_config("api.cors.allow_credentials", True),
    allow_methods=get_config("api.cors.allow_methods", ["*"]),
    allow_headers=get_config("api.cors.allow_headers", ["*"]),
)

# Add rate limiting middleware
try:
    from .security.enhanced_auth import rate_limit_middleware
    
    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        return await rate_limit_middleware(request, call_next)
    
    logger.info("Rate limiting middleware enabled")
except ImportError as e:
    logger.warning(f"Could not enable rate limiting middleware: {e}")

# Add security logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log API requests and responses."""
    # Generate a unique request ID
    request_id = str(time.time())
    request.state.request_id = request_id
    
    # Log the request
    logger.debug(f"Request [{request_id}]: {request.method} {request.url.path}")
    
    # Process the request
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log the response
    logger.debug(f"Response [{request_id}]: {response.status_code} (took {process_time:.4f}s)")
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    return response

# Mount static files
try:
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        logger.info(f"Static files mounted at /static from {static_dir}")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Import and include routers 
# These imports are placed here to avoid circular dependencies
try:
    from .routers import sessions, conversations, analysis, personas, simple_auth as auth, sync, websocket, monitoring

    # API version prefix
    API_V1_PREFIX = "/api/v1"

    # Add routers to application
    app.include_router(auth.router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
    app.include_router(sessions.router, prefix=f"{API_V1_PREFIX}/sessions", tags=["Sessions"])
    app.include_router(conversations.router, prefix=f"{API_V1_PREFIX}/conversations", tags=["Conversations"])
    app.include_router(analysis.router, prefix=f"{API_V1_PREFIX}/analysis", tags=["Analysis"])
    app.include_router(personas.router, prefix=f"{API_V1_PREFIX}/personas", tags=["Personas"])
    app.include_router(sync.router, prefix=f"{API_V1_PREFIX}/sync", tags=["Synchronization"])
    app.include_router(websocket.router, prefix=f"{API_V1_PREFIX}/ws", tags=["WebSocket"])
    app.include_router(monitoring.router, tags=["Monitoring"])
except ImportError as e:
    logger.error(f"Error importing routers: {e}")
    # Add a basic router for health check
    from fastapi import APIRouter
    health_router = APIRouter()
    
    @health_router.get("/health")
    async def health_check():
        return {"status": "ok", "routers_loaded": False, "error": str(e)}
    
    app.include_router(health_router)

# Custom OpenAPI and documentation
try:
    from .docs import custom_openapi
    
    @app.get("/api/docs", include_in_schema=False)
    async def get_documentation():
        return get_swagger_ui_html(
            openapi_url="/api/openapi.json",
            title="Smart Steps AI API Documentation",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
        )

    @app.get("/api/redoc", include_in_schema=False)
    async def get_redoc_documentation():
        return get_redoc_html(
            openapi_url="/api/openapi.json",
            title="Smart Steps AI API Documentation",
        )

    @app.get("/api/openapi.json", include_in_schema=False)
    async def get_open_api_endpoint():
        return custom_openapi(app)
        
except ImportError as e:
    logger.warning(f"Could not load custom OpenAPI documentation: {e}")
    
    @app.get("/api/docs", include_in_schema=False)
    async def get_documentation():
        return get_swagger_ui_html(
            openapi_url="/api/openapi.json",
            title="Smart Steps AI API Documentation",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
        )

    @app.get("/api/redoc", include_in_schema=False)
    async def get_redoc_documentation():
        return get_redoc_html(
            openapi_url="/api/openapi.json",
            title="Smart Steps AI API Documentation",
        )

    @app.get("/api/openapi.json", include_in_schema=False)
    async def get_open_api_endpoint():
        return get_openapi(
            title="Smart Steps AI API",
            version="0.1.0",
            description="REST API for Smart Steps AI Professional Persona system",
            routes=app.routes,
        )

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint that provides API information and redirects to documentation."""
    return {
        "message": "Smart Steps AI API",
        "version": "0.1.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "static_docs": "/static/docs/index.html"
    }

# Serve the static docs directly
@app.get("/docs", include_in_schema=False)
async def get_static_docs():
    """Serve the static documentation page."""
    return RedirectResponse(url="/static/docs/index.html")

# Add a health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": os.environ.get("START_TIME", "unknown")
    }

# Application startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Perform tasks when the API server starts."""
    logger.info("Starting Smart Steps AI API server")
    # Record start time
    os.environ["START_TIME"] = str(time.time())
    # Additional startup tasks (database connections, etc.) can be added here

@app.on_event("shutdown")
async def shutdown_event():
    """Perform cleanup tasks when the API server shuts down."""
    logger.info("Shutting down Smart Steps AI API server")
    # Additional shutdown tasks (closing connections, etc.) can be added here

# Set up exception handlers
try:
    from .errors import setup_exception_handlers
    setup_exception_handlers(app)
    logger.info("Custom exception handlers configured")
except ImportError as e:
    logger.warning(f"Could not configure custom exception handlers: {e}")

def get_application() -> FastAPI:
    """Return the configured FastAPI application.
    
    This function is used by ASGI servers (like uvicorn) to access the application.
    """
    return app
