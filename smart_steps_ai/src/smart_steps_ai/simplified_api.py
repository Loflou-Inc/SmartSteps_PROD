"""
Simplified API server for Smart Steps AI.

This module provides a minimal FastAPI server that handles Smart Steps AI interactions.
"""

import asyncio
import importlib.util
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Smart Steps AI API (Simplified)",
    description="Simplified API for Smart Steps AI Professional Persona",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "api": "simplified"}

# Main API entry point that runs when this module is executed
if __name__ == "__main__":
    logger.info("Starting Simplified Smart Steps AI API Server...")
    uvicorn.run(
        "simplified_api:app",
        host="127.0.0.1",
        port=9500,  # Changed from 8000 to 9500
        reload=True,
    )
