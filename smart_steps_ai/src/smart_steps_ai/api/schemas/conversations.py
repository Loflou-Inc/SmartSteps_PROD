"""
Conversation schema definitions.

This module defines Pydantic models for conversation-related API requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

class MessageBase(BaseModel):
    """Base model for message data."""
    content: str = Field(..., description="The content of the message")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")

class MessageCreate(MessageBase):
    """Model for creating a new message."""
    client_id: str = Field(..., description="The ID of the client sending the message")

class MessageResponse(MessageBase):
    """Model for message response data."""
    id: str = Field(..., description="The unique identifier for the message")
    session_id: str = Field(..., description="The ID of the session this message belongs to")
    sender_type: str = Field(..., description="The type of sender (client or ai)")
    timestamp: datetime = Field(..., description="The timestamp when the message was sent")

class MessageList(BaseModel):
    """Model for a list of messages with pagination information."""
    messages: List[MessageResponse] = Field(..., description="List of messages")
    total_count: int = Field(..., description="Total number of messages in the session")
    limit: int = Field(..., description="Maximum number of messages returned")

class ConversationExport(BaseModel):
    """Model for exporting a complete conversation."""
    session_id: str = Field(..., description="The ID of the session")
    title: str = Field(..., description="The title of the session")
    format: str = Field(..., description="The format of the export (json, markdown, text, html)")
    content: str = Field("", description="The formatted content of the conversation (for non-JSON formats)")
    message_count: int = Field(..., description="The number of messages in the conversation")
    client_id: str = Field(..., description="The ID of the client")
    persona_id: str = Field(..., description="The ID of the professional AI persona")
    created_at: datetime = Field(..., description="The timestamp when the session was created")
    messages: List[MessageResponse] = Field(..., description="The complete list of messages in the conversation")
