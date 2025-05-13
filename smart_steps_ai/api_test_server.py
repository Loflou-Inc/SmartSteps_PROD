"""
Simple test server for the API validation.

This script starts a simplified FastAPI server to test the API components.
"""

import sys
import os
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_dir))

from fastapi import FastAPI, Depends, HTTPException, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Define models
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: str
    scopes: List[str] = []

class PersonaResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    expertise_areas: List[str]
    effectiveness: float
    created_at: datetime
    session_count: int
    
class PersonaList(BaseModel):
    personas: List[PersonaResponse]
    total_count: int
    
class SessionResponse(BaseModel):
    id: str
    title: str
    client_id: str
    persona_id: str
    status: str
    created_at: datetime
    message_count: int
    
class SessionList(BaseModel):
    sessions: List[SessionResponse]
    total_count: int
    
class MessageResponse(BaseModel):
    id: str
    session_id: str
    sender_type: str
    content: str
    timestamp: datetime

class MessageCreate(BaseModel):
    content: str
    client_id: str
    metadata: Optional[Dict[str, Any]] = None

# Create app
app = FastAPI(title="Smart Steps API Test")

# Add a simple CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated data
USERS = {
    "admin": {
        "username": "admin",
        "full_name": "Administrator",
        "role": "admin",
        "scopes": ["sessions:read", "sessions:write", "personas:read", "personas:write"]
    },
    "therapist": {
        "username": "therapist",
        "full_name": "Test Therapist",
        "role": "therapist",
        "scopes": ["sessions:read", "sessions:write", "personas:read"]
    }
}

PERSONAS = [
    {
        "id": str(uuid.uuid4()),
        "name": "jane",
        "display_name": "Dr. Jane",
        "description": "Experienced therapist specializing in trauma recovery",
        "expertise_areas": ["trauma", "anxiety", "depression"],
        "effectiveness": 0.92,
        "created_at": datetime.now(),
        "session_count": 15
    },
    {
        "id": str(uuid.uuid4()),
        "name": "mark",
        "display_name": "Dr. Mark",
        "description": "Cognitive behavioral therapist focusing on addiction recovery",
        "expertise_areas": ["addiction", "CBT", "recovery"],
        "effectiveness": 0.89,
        "created_at": datetime.now(),
        "session_count": 8
    }
]

SESSIONS = [
    {
        "id": str(uuid.uuid4()),
        "title": "Initial Assessment",
        "client_id": "client-001",
        "persona_id": PERSONAS[0]["id"],
        "status": "completed",
        "created_at": datetime.now(),
        "message_count": 24
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Follow-up Session",
        "client_id": "client-001",
        "persona_id": PERSONAS[0]["id"],
        "status": "active",
        "created_at": datetime.now(),
        "message_count": 12
    }
]

# Simple authentication
def get_current_user(token: str = Query(..., description="Access token")):
    """Simulated authentication."""
    if token == "test_token":
        return USERS["admin"]
    if token == "therapist_token":
        return USERS["therapist"]
    raise HTTPException(status_code=401, detail="Invalid token")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Smart Steps API Test Server"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": os.environ.get("START_TIME", "unknown")}

# Authentication endpoints
@app.post("/api/v1/auth/token", response_model=TokenResponse)
async def login_for_access_token(username: str = Body(...), password: str = Body(...)):
    """Simulated login."""
    if username in USERS and password == "password":
        token = "test_token" if username == "admin" else "therapist_token"
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Get current user info."""
    return current_user

# Persona endpoints
@app.get("/api/v1/personas", response_model=PersonaList)
async def list_personas(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, description="Maximum number of personas to return"),
    offset: int = Query(0, description="Number of personas to skip"),
):
    """List all personas."""
    return {
        "personas": PERSONAS[offset:offset+limit],
        "total_count": len(PERSONAS)
    }

@app.get("/api/v1/personas/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str = Path(..., description="The ID of the persona to retrieve"),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific persona."""
    for persona in PERSONAS:
        if persona["id"] == persona_id:
            return persona
    raise HTTPException(status_code=404, detail="Persona not found")

# Session endpoints
@app.get("/api/v1/sessions", response_model=SessionList)
async def list_sessions(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, description="Maximum number of sessions to return"),
    offset: int = Query(0, description="Number of sessions to skip"),
):
    """List all sessions."""
    return {
        "sessions": SESSIONS[offset:offset+limit],
        "total_count": len(SESSIONS)
    }

@app.get("/api/v1/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str = Path(..., description="The ID of the session to retrieve"),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific session."""
    for session in SESSIONS:
        if session["id"] == session_id:
            return session
    raise HTTPException(status_code=404, detail="Session not found")

# Conversation endpoints
@app.post("/api/v1/conversations/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: str = Path(..., description="The ID of the session"),
    message_data: MessageCreate = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """Send a message in a session."""
    # Check if session exists
    session = None
    for s in SESSIONS:
        if s["id"] == session_id:
            session = s
            break
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Simulate processing and AI response
    return {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "sender_type": "assistant",
        "content": f"This is a simulated response to: {message_data.content[:50]}...",
        "timestamp": datetime.now()
    }

# Start the server
if __name__ == "__main__":
    import uvicorn
    print("Starting test API server...")
    os.environ["START_TIME"] = str(os.path.getmtime(__file__))
    uvicorn.run(app, host="127.0.0.1", port=9001)
