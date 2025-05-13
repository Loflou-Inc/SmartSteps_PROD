"""
Conversation management API endpoints.

This module provides endpoints for sending, retrieving, and managing 
conversational messages within therapy sessions.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, Request
from fastapi.responses import JSONResponse

from smart_steps_ai.session import SessionManager
from ..schemas.conversations import (
    MessageCreate,
    MessageResponse,
    MessageList,
    ConversationExport
)
from ..dependencies import get_session_manager, get_conversation_handler, get_current_user, require_scope
from ..errors import NotFoundError, BadRequestError

router = APIRouter()

@router.post(
    "/{session_id}/messages",
    response_model=MessageResponse,
    status_code=201,
    summary="Send a message",
    description="Sends a client message in a therapy session and receives an AI response."
)
async def send_message(
    request: Request,
    session_id: UUID = Path(..., description="The ID of the session"),
    message_data: MessageCreate = Body(...),
    current_user = Depends(get_current_user),
    conversation_handler = Depends(get_conversation_handler),
    _=Depends(require_scope("sessions:write"))
):
    """Send a message in a therapy session and get an AI response."""
    try:
        # Process the message and get response
        response = await conversation_handler.process_message(
            session_id=str(session_id),
            message=message_data.content,
            client_id=message_data.client_id,
            metadata=message_data.metadata
        )
        
        return MessageResponse(
            id=response.message_id,
            session_id=str(session_id),
            sender_type="ai",
            content=response.content,
            timestamp=response.timestamp,
            metadata=response.metadata
        )
    except ValueError as e:
        raise BadRequestError(message=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get(
    "/{session_id}/messages",
    response_model=MessageList,
    summary="Get conversation history",
    description="Retrieves the conversation history for a specific therapy session."
)
async def get_conversation_history(
    request: Request,
    session_id: UUID = Path(..., description="The ID of the session"),
    limit: int = Query(50, description="Maximum number of messages to return"),
    before: Optional[str] = Query(None, description="Only return messages before this message ID"),
    current_user = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    _=Depends(require_scope("sessions:read"))
):
    """Retrieve conversation history for a therapy session."""
    try:
        # Check if session exists
        session = session_manager.get_session(session_id=str(session_id))
        if not session:
            raise NotFoundError(message=f"Session {session_id} not found")
        
        # Get conversation history
        messages = session_manager.get_messages(
            session_id=str(session_id),
            limit=limit,
            before_id=before
        )
        
        # Convert to response model
        message_responses = [
            MessageResponse(
                id=msg.message_id,
                session_id=str(session_id),
                sender_type=msg.sender_type,
                content=msg.content,
                timestamp=msg.timestamp,
                metadata=msg.metadata
            ) for msg in messages
        ]
        
        total_count = session_manager.count_messages(session_id=str(session_id))
        
        return MessageList(
            messages=message_responses,
            total_count=total_count,
            limit=limit
        )
    except ValueError as e:
        raise BadRequestError(message=str(e))
    except Exception as e:
        if isinstance(e, NotFoundError):
            raise
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation history: {str(e)}")

@router.get(
    "/{session_id}/export",
    response_model=ConversationExport,
    summary="Export conversation",
    description="Exports the complete conversation from a therapy session in a structured format."
)
async def export_conversation(
    request: Request,
    session_id: UUID = Path(..., description="The ID of the session to export"),
    format: str = Query("json", description="Export format (json, markdown, text, html)"),
    current_user = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    _=Depends(require_scope("sessions:read"))
):
    """Export conversation in specified format."""
    try:
        # Check if session exists
        session = session_manager.get_session(session_id=str(session_id))
        if not session:
            raise NotFoundError(message=f"Session {session_id} not found")
        
        # Get conversation export based on format
        if format.lower() not in ["json", "markdown", "text", "html"]:
            raise BadRequestError(message=f"Unsupported export format: {format}")
        
        # Get all messages
        messages = session_manager.get_all_messages(session_id=str(session_id))
        
        # Format the export based on requested format
        # This is a simplified implementation - actual formatting would be more complex
        content = ""
        if format.lower() == "json":
            # JSON format is handled by the response model
            pass
        elif format.lower() == "markdown":
            for msg in messages:
                sender = "Client" if msg.sender_type == "client" else "Therapist"
                content += f"## {sender} ({msg.timestamp})\n\n{msg.content}\n\n"
        elif format.lower() == "text":
            for msg in messages:
                sender = "Client" if msg.sender_type == "client" else "Therapist"
                content += f"{sender} ({msg.timestamp}):\n{msg.content}\n\n"
        elif format.lower() == "html":
            content = "<html><body><h1>Session Transcript</h1>"
            for msg in messages:
                sender = "Client" if msg.sender_type == "client" else "Therapist"
                content += f"<div class='{msg.sender_type}-message'><h3>{sender} ({msg.timestamp})</h3><p>{msg.content}</p></div>"
            content += "</body></html>"
        
        # Create the export response
        return ConversationExport(
            session_id=str(session_id),
            title=session.title,
            format=format.lower(),
            content=content,
            message_count=len(messages),
            client_id=session.client_id,
            persona_id=session.persona_id,
            created_at=session.created_at,
            messages=[
                MessageResponse(
                    id=msg.message_id,
                    session_id=str(session_id),
                    sender_type=msg.sender_type,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    metadata=msg.metadata
                ) for msg in messages
            ]
        )
    except ValueError as e:
        raise BadRequestError(message=str(e))
    except Exception as e:
        if isinstance(e, (NotFoundError, BadRequestError)):
            raise
        raise HTTPException(status_code=500, detail=f"Failed to export conversation: {str(e)}")
