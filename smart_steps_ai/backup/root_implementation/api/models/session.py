"""
Session models for the Smart Steps AI API.

This module defines the data models for session management endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from enum import Enum

from .common import PaginatedResponse


class SessionStatus(str, Enum):
    """Session status options."""
    ACTIVE = "active"
    ENDED = "ended"
    PAUSED = "paused"


class SessionCreate(BaseModel):
    """Session creation request model."""
    persona_id: str = Field(..., description="ID of the persona to use for the session")
    client_name: str = Field(..., description="Name of the client")
    session_type: Optional[str] = Field(None, description="Type of session")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")


class SessionUpdate(BaseModel):
    """Session update request model."""
    client_name: Optional[str] = Field(None, description="Name of the client")
    session_type: Optional[str] = Field(None, description="Type of session")
    status: Optional[SessionStatus] = Field(None, description="Session status")
    summary: Optional[str] = Field(None, description="Session summary")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")


class SessionResponse(BaseModel):
    """Session response model."""
    id: str = Field(..., description="Session ID")
    persona_id: str = Field(..., description="ID of the persona")
    client_name: str = Field(..., description="Name of the client")
    session_type: Optional[str] = Field(None, description="Type of session")
    status: SessionStatus = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Session creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Session update timestamp")
    ended_at: Optional[datetime] = Field(None, description="Session end timestamp")
    summary: Optional[str] = Field(None, description="Session summary")
    message_count: int = Field(0, description="Number of messages in the session")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")

    class Config:
        """Configuration for the model."""
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "persona_id": "therapist",
                "client_name": "John Doe",
                "session_type": "initial_consultation",
                "status": "active",
                "created_at": "2025-05-11T08:00:00Z",
                "updated_at": "2025-05-11T08:30:00Z",
                "ended_at": None,
                "summary": None,
                "message_count": 10,
                "metadata": {
                    "location": "Remote",
                    "platform": "Web"
                }
            }
        }


class SessionList(PaginatedResponse[SessionResponse]):
    """Paginated list of sessions."""
    items: List[SessionResponse] = Field(..., description="List of sessions")
