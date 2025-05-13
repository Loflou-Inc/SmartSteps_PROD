"""
WebSocket API for real-time conversations.

This module provides WebSocket endpoints for real-time conversations
with AI professional personas.
"""

import asyncio
import json
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, Path, status
from pydantic import BaseModel, Field

from smart_steps_ai.config import ConfigManager
from smart_steps_ai.session import SessionManager
from smart_steps_ai.provider import ProviderManager
from smart_steps_ai.utils.logging import setup_logger
from ..dependencies import get_session_manager, get_provider_manager, get_config_manager
from ..security.enhanced_auth import jwt_bearer

# Configure logging
logger = setup_logger(__name__)

# Create router
router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Message models
class WebSocketMessage(BaseModel):
    """Base model for WebSocket messages."""
    type: str
    timestamp: float = Field(default_factory=time.time)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ClientMessage(WebSocketMessage):
    """Message from client to server."""
    type: str = "message"
    content: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

class SystemMessage(WebSocketMessage):
    """System message."""
    type: str = "system"
    content: str
    code: str

class AIMessage(WebSocketMessage):
    """Message from AI to client."""
    type: str = "ai_message"
    content: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

class ErrorMessage(WebSocketMessage):
    """Error message."""
    type: str = "error"
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str = Path(..., description="The ID of the session"),
    token: str = Query(..., description="JWT token for authentication"),
    session_manager: SessionManager = Depends(get_session_manager),
    provider_manager: ProviderManager = Depends(get_provider_manager),
    config_manager: ConfigManager = Depends(get_config_manager),
):
    """WebSocket endpoint for real-time conversations."""
    # Verify token
    try:
        # Create a mock request object with the token
        class MockRequest:
            headers = {"Authorization": f"Bearer {token}"}
            state = type('obj', (object,), {'user': None})
            
        mock_request = MockRequest()
        await jwt_bearer(mock_request)
        user = mock_request.state.user
        
        if not user:
            raise ValueError("Invalid token")
        
    except Exception as e:
        logger.warning(f"WebSocket authentication failed: {str(e)}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Verify session exists
    session = session_manager.get_session(session_id)
    if not session:
        logger.warning(f"WebSocket connection attempted for non-existent session: {session_id}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Accept connection
    await websocket.accept()
    
    # Generate a unique client ID
    client_id = f"{session_id}_{str(uuid.uuid4())[:8]}"
    active_connections[client_id] = websocket
    
    # Send welcome message
    await websocket.send_json(
        SystemMessage(
            content=f"Connected to session: {session.title}",
            code="connected"
        ).dict()
    )
    
    try:
        # Main loop
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                # Parse message
                message_data = json.loads(data)
                client_message = ClientMessage(**message_data)
                
                # Verify session ID matches
                if client_message.session_id != session_id:
                    raise ValueError("Session ID mismatch")
                
                # Log message
                logger.debug(f"Received message from client {client_id}: {client_message.content[:50]}...")
                
                # Add message to session
                session_manager.add_message(
                    session_id=session_id,
                    role="client",
                    content=client_message.content,
                    metadata=client_message.metadata or {}
                )
                
                # Get AI response
                # This would normally call the conversation handler to generate a response
                # For now, we'll just echo the message back
                try:
                    # Get provider for the session
                    provider_id = session.provider_id or config_manager.get("ai.default_provider")
                    provider = provider_manager.get_provider(provider_id)
                    
                    if not provider:
                        raise ValueError(f"Provider not found: {provider_id}")
                    
                    # Get persona
                    persona = session.persona_metadata
                    
                    # Generate response (this is a simplified version)
                    # In a real implementation, this would use the conversation handler
                    response = await provider.generate_response(
                        messages=[{"role": "user", "content": client_message.content}],
                        prompt=f"You are {persona.name}, a professional therapist.",
                        max_tokens=500
                    )
                    
                    # Process response
                    if response and response.get("content"):
                        ai_content = response["content"]
                    else:
                        ai_content = "I'm sorry, I'm having trouble generating a response right now."
                    
                    # Add AI message to session
                    session_manager.add_message(
                        session_id=session_id,
                        role="assistant",
                        content=ai_content,
                        metadata={"provider": provider_id}
                    )
                    
                    # Send AI response
                    await websocket.send_json(
                        AIMessage(
                            content=ai_content,
                            session_id=session_id,
                            metadata={"provider": provider_id}
                        ).dict()
                    )
                    
                except Exception as e:
                    logger.error(f"Error generating AI response: {str(e)}")
                    await websocket.send_json(
                        ErrorMessage(
                            message="Failed to generate AI response",
                            code="ai_response_error",
                            details={"error": str(e)}
                        ).dict()
                    )
                
            except json.JSONDecodeError:
                logger.warning(f"Received invalid JSON from client {client_id}")
                await websocket.send_json(
                    ErrorMessage(
                        message="Invalid message format",
                        code="invalid_format"
                    ).dict()
                )
                
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {str(e)}")
                await websocket.send_json(
                    ErrorMessage(
                        message="Error processing message",
                        code="processing_error",
                        details={"error": str(e)}
                    ).dict()
                )
    
    except WebSocketDisconnect:
        # Handle disconnection
        logger.debug(f"Client {client_id} disconnected")
        active_connections.pop(client_id, None)
    
    except Exception as e:
        # Handle other errors
        logger.error(f"WebSocket error for client {client_id}: {str(e)}")
        active_connections.pop(client_id, None)
