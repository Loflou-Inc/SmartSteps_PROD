"""
Simplified API server for Smart Steps AI.

This script creates a basic FastAPI application with minimal routes
to demonstrate the Smart Steps AI API.
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_dir = Path(r"G:\My Drive\Deftech\SmartSteps\smart_steps_ai")
src_dir = project_dir / "src"
sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict, Any, Optional
from datetime import datetime

# Create a simple FastAPI app
app = FastAPI(
    title="Smart Steps AI API",
    description="Simplified API for Smart Steps AI Professional Persona system",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data
personas = [
    {
        "id": "dr-morgan-hayes",
        "name": "Dr. Morgan Hayes",
        "title": "CBT Therapist", 
        "specialization": "Cognitive Behavioral Therapy",
        "experience_years": 15,
    },
    {
        "id": "dr-alex-rivera",
        "name": "Dr. Alex Rivera",
        "title": "Behavioral Analyst",
        "specialization": "Applied Behavioral Analysis",
        "experience_years": 12,
    }
]

sessions = [
    {
        "id": "session-001",
        "client_id": "client-001",
        "client_name": "John Doe",
        "persona_id": "dr-morgan-hayes",
        "status": "active",
        "created_at": "2025-05-01T10:00:00Z",
        "updated_at": "2025-05-11T15:30:00Z",
        "message_count": 24
    }
]

# Routes
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Smart Steps AI API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/api/v1/personas")
async def get_personas():
    """Get all available personas."""
    return {"items": personas}

@app.get("/api/v1/personas/{persona_id}")
async def get_persona(persona_id: str):
    """Get a specific persona by ID."""
    for persona in personas:
        if persona["id"] == persona_id:
            return persona
    raise HTTPException(status_code=404, detail="Persona not found")

@app.get("/api/v1/sessions")
async def get_sessions():
    """Get all sessions."""
    return {"items": sessions}

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session by ID."""
    for session in sessions:
        if session["id"] == session_id:
            return session
    raise HTTPException(status_code=404, detail="Session not found")

# Run the server
if __name__ == "__main__":
    print("Starting Simplified Smart Steps AI API Server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
