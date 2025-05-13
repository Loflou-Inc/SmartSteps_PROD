"""
Message models for the Smart Steps AI API.

This module defines the data models for conversation messages endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from enum import Enum

from .common import PaginatedResponse


class SpeakerType(str, Enum):
    """Speaker type options."""
    CLIENT = "client"
    PERSONA = "persona"
    SYSTEM = "system"


class MessageCreate(BaseModel):
    """Message creation request model."""
    session_id: str = Field(..., description="ID of the session")
    speaker: SpeakerType = Field(..., description="Speaker type")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")

    @validator('content')
    def content_not_empty(cls, v):
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v


class MessageResponse(BaseModel):
    """Message response model."""
    id: str = Field(..., description="Message ID")
    session_id: str = Field(..., description="ID of the session")
    speaker: SpeakerType = Field(..., description="Speaker type")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Message creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")

    class Config:
        """Configuration for the model."""
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "speaker": "client",
                "content": "Hello, I'm here for my appointment.",
                "created_at": "2025-05-11T08:00:00Z",
                "metadata": {
                    "tone": "neutral",
                    "emotion": "calm"
                }
            }
        }


class MessageList(PaginatedResponse[MessageResponse]):
    """Paginated list of messages."""
    items: List[MessageResponse] = Field(..., description="List of messages")


class ConversationRequest(BaseModel):
    """Conversation request model for generating responses."""
    session_id: str = Field(..., description="ID of the session")
    message: str = Field(..., description="User message content")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the conversation")

    @validator('message')
    def message_not_empty(cls, v):
        """Validate that message is not empty."""
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v


class ConversationResponse(BaseModel):
    """Conversation response model with generated response."""
    session_id: str = Field(..., description="ID of the session")
    user_message: MessageResponse = Field(..., description="User message")
    response: MessageResponse = Field(..., description="Generated response")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context from the conversation")
