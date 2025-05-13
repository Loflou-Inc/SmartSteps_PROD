"""
Session schema definitions.

This module defines Pydantic models for session-related API requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

class SessionBase(BaseModel):
    """Base model for session data."""
    title: str = Field(..., description="The title of the session")
    client_id: str = Field(..., description="The ID of the client")
    persona_id: str = Field(..., description="The ID of the professional AI persona")
    provider_id: Optional[str] = Field(None, description="The ID of the AI provider to use")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")

class SessionCreate(SessionBase):
    """Model for creating a new session."""
    pass

class SessionUpdate(BaseModel):
    """Model for updating an existing session."""
    title: Optional[str] = Field(None, description="The updated title of the session")
    status: Optional[str] = Field(None, description="The updated status of the session")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated session metadata")

class SessionResponse(SessionBase):
    """Model for session response data."""
    id: str = Field(..., description="The unique identifier for the session")
    status: str = Field(..., description="The current status of the session")
    created_at: datetime = Field(..., description="The timestamp when the session was created")
    updated_at: datetime = Field(..., description="The timestamp when the session was last updated")
    message_count: int = Field(..., description="The number of messages in the session")
    duration: Optional[int] = Field(None, description="The duration of the session in seconds")
    
    @classmethod
    def from_session_model(cls, session_model):
        """Create a SessionResponse from a session model instance."""
        return cls(
            id=session_model.session_id,
            title=session_model.title,
            client_id=session_model.client_id,
            persona_id=session_model.persona_id,
            provider_id=session_model.provider_id,
            status=session_model.status,
            created_at=session_model.created_at,
            updated_at=session_model.updated_at,
            message_count=session_model.message_count,
            duration=session_model.duration,
            metadata=session_model.metadata
        )

class SessionList(BaseModel):
    """Model for a list of sessions with pagination information."""
    sessions: List[SessionResponse] = Field(..., description="List of sessions")
    total_count: int = Field(..., description="Total number of sessions matching the filters")
    limit: int = Field(..., description="Maximum number of sessions returned")
    offset: int = Field(..., description="Number of sessions skipped")
