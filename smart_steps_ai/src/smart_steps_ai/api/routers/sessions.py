"""
Session management API endpoints.

This module provides endpoints for creating, retrieving, updating, and 
deleting therapy sessions in the Smart Steps AI system.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, Request
from fastapi.responses import JSONResponse

from smart_steps_ai.session import SessionManager
from ..schemas.sessions import (
    SessionCreate, 
    SessionResponse, 
    SessionList, 
    SessionUpdate
)
from ..dependencies import get_session_manager, get_current_user, require_scope

router = APIRouter()

@router.post(
    "/", 
    response_model=SessionResponse,
    status_code=201,
    summary="Create a new session",
    description="Creates a new therapy session with the specified parameters."
)
async def create_session(
    request: Request,
    session_data: SessionCreate,
    current_user = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    _=Depends(require_scope("sessions:write"))
):
    """Create a new therapy session."""
    try:
        # Create the session
        session = session_manager.create_session(
            client_id=session_data.client_id,
            persona_id=session_data.persona_id,
            title=session_data.title,
            provider_id=session_data.provider_id,
            metadata=session_data.metadata
        )
        
        return SessionResponse.from_session_model(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get(
    "/", 
    response_model=SessionList,
    summary="List all sessions",
    description="Returns a list of all therapy sessions, with optional filtering."
)
async def list_sessions(
    request: Request,
    client_id: Optional[str] = Query(None, description="Filter sessions by client ID"),
    persona_id: Optional[str] = Query(None, description="Filter sessions by persona ID"),
    limit: int = Query(50, description="Maximum number of sessions to return"),
    offset: int = Query(0, description="Number of sessions to skip"),
    current_user = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    _=Depends(require_scope("sessions:read"))
):
    """List therapy sessions with optional filtering."""
    try:
        # Get sessions with filtering
        sessions = session_manager.list_sessions(
            client_id=client_id,
            persona_id=persona_id,
            limit=limit,
            offset=offset
        )
        
        # Convert to response model
        session_responses = [SessionResponse.from_session_model(s) for s in sessions]
        total_count = session_manager.count_sessions(client_id=client_id, persona_id=persona_id)
        
        return SessionList(
            sessions=session_responses,
            total_count=total_count,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.get(
    "/{session_id}", 
    response_model=SessionResponse,
    summary="Get session details",
    description="Returns detailed information about a specific therapy session."
)
async def get_session(
    request: Request,
    session_id: UUID = Path(..., description="The ID of the session to retrieve"),
    current_user = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    _=Depends(require_scope("sessions:read"))
):
    """Get details for a specific therapy session."""
    try:
        session = session_manager.get_session(session_id=str(session_id))
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return SessionResponse.from_session_model(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Update session",
    description="Updates an existing therapy session with the provided data."
)
async def update_session(
    request: Request,
    session_id: UUID = Path(..., description="The ID of the session to update"),
    session_data: SessionUpdate = Body(...),
    current_user = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    _=Depends(require_scope("sessions:write"))
):
    """Update an existing therapy session."""
    try:
        # Check if session exists
        existing_session = session_manager.get_session(session_id=str(session_id))
        if not existing_session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Update the session
        updated_session = session_manager.update_session(
            session_id=str(session_id),
            title=session_data.title,
            status=session_data.status,
            metadata=session_data.metadata
        )
        
        return SessionResponse.from_session_model(updated_session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

@router.delete(
    "/{session_id}",
    status_code=204,
    summary="Delete session",
    description="Deletes a therapy session and its associated data."
)
async def delete_session(
    request: Request,
    session_id: UUID = Path(..., description="The ID of the session to delete"),
    current_user = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    _=Depends(require_scope("sessions:write"))
):
    """Delete a therapy session."""
    try:
        # Check if session exists
        existing_session = session_manager.get_session(session_id=str(session_id))
        if not existing_session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Delete the session
        session_manager.delete_session(session_id=str(session_id))
        
        return JSONResponse(status_code=204, content={})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
