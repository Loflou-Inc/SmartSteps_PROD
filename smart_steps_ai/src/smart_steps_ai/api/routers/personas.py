"""
Persona management API endpoints.

This module provides endpoints for creating, retrieving, updating, and 
managing AI professional personas in the Smart Steps system.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, File, UploadFile
from fastapi.responses import JSONResponse

from smart_steps_ai.persona import PersonaManager
from ..schemas.personas import (
    PersonaCreate,
    PersonaResponse,
    PersonaList,
    PersonaUpdate,
    PersonaValidation
)
from ..security.auth import get_current_user
from ..dependencies import get_persona_manager

router = APIRouter()

@router.post(
    "/", 
    response_model=PersonaResponse,
    status_code=201,
    summary="Create a new persona",
    description="Creates a new AI professional persona with the specified parameters."
)
async def create_persona(
    persona_data: PersonaCreate,
    current_user = Depends(get_current_user),
    persona_manager: PersonaManager = Depends(get_persona_manager)
):
    """Create a new AI professional persona."""
    try:
        # Create the persona
        persona = persona_manager.create_persona(
            name=persona_data.name,
            role=persona_data.role,
            description=persona_data.description,
            expertise=persona_data.expertise,
            traits=persona_data.traits,
            voice_style=persona_data.voice_style,
            therapeutic_approach=persona_data.therapeutic_approach,
            metadata=persona_data.metadata
        )
        
        return PersonaResponse.from_persona_model(persona)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create persona: {str(e)}")

@router.get(
    "/", 
    response_model=PersonaList,
    summary="List all personas",
    description="Returns a list of all available AI professional personas."
)
async def list_personas(
    role: Optional[str] = Query(None, description="Filter personas by role"),
    expertise: Optional[str] = Query(None, description="Filter personas by expertise area"),
    limit: int = Query(50, description="Maximum number of personas to return"),
    offset: int = Query(0, description="Number of personas to skip"),
    current_user = Depends(get_current_user),
    persona_manager: PersonaManager = Depends(get_persona_manager)
):
    """List AI professional personas with optional filtering."""
    try:
        # Get personas with filtering
        personas = persona_manager.list_personas(
            role=role,
            expertise=expertise,
            limit=limit,
            offset=offset
        )
        
        # Convert to response model
        persona_responses = [PersonaResponse.from_persona_model(p) for p in personas]
        total_count = persona_manager.count_personas(role=role, expertise=expertise)
        
        return PersonaList(
            personas=persona_responses,
            total_count=total_count,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list personas: {str(e)}")

@router.get(
    "/{persona_id}", 
    response_model=PersonaResponse,
    summary="Get persona details",
    description="Returns detailed information about a specific AI professional persona."
)
async def get_persona(
    persona_id: str = Path(..., description="The ID of the persona to retrieve"),
    current_user = Depends(get_current_user),
    persona_manager: PersonaManager = Depends(get_persona_manager)
):
    """Get details for a specific AI professional persona."""
    try:
        persona = persona_manager.get_persona(persona_id=persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
        
        return PersonaResponse.from_persona_model(persona)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve persona: {str(e)}")

@router.patch(
    "/{persona_id}",
    response_model=PersonaResponse,
    summary="Update persona",
    description="Updates an existing AI professional persona with the provided data."
)
async def update_persona(
    persona_id: str = Path(..., description="The ID of the persona to update"),
    persona_data: PersonaUpdate = Body(...),
    current_user = Depends(get_current_user),
    persona_manager: PersonaManager = Depends(get_persona_manager)
):
    """Update an existing AI professional persona."""
    try:
        # Check if persona exists
        existing_persona = persona_manager.get_persona(persona_id=persona_id)
        if not existing_persona:
            raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
        
        # Update the persona
        updated_persona = persona_manager.update_persona(
            persona_id=persona_id,
            name=persona_data.name,
            description=persona_data.description,
            expertise=persona_data.expertise,
            traits=persona_data.traits,
            voice_style=persona_data.voice_style,
            therapeutic_approach=persona_data.therapeutic_approach,
            metadata=persona_data.metadata
        )
        
        return PersonaResponse.from_persona_model(updated_persona)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update persona: {str(e)}")

@router.delete(
    "/{persona_id}",
    status_code=204,
    summary="Delete persona",
    description="Deletes an AI professional persona."
)
async def delete_persona(
    persona_id: str = Path(..., description="The ID of the persona to delete"),
    current_user = Depends(get_current_user),
    persona_manager: PersonaManager = Depends(get_persona_manager)
):
    """Delete an AI professional persona."""
    try:
        # Check if persona exists
        existing_persona = persona_manager.get_persona(persona_id=persona_id)
        if not existing_persona:
            raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
        
        # Delete the persona
        persona_manager.delete_persona(persona_id=persona_id)
        
        return JSONResponse(status_code=204, content={})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete persona: {str(e)}")

@router.post(
    "/{persona_id}/validate",
    response_model=PersonaValidation,
    summary="Validate persona",
    description="Validates an AI professional persona and returns any issues."
)
async def validate_persona(
    persona_id: str = Path(..., description="The ID of the persona to validate"),
    current_user = Depends(get_current_user),
    persona_manager: PersonaManager = Depends(get_persona_manager)
):
    """Validate an AI professional persona."""
    try:
        # Check if persona exists
        existing_persona = persona_manager.get_persona(persona_id=persona_id)
        if not existing_persona:
            raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
        
        # Validate the persona
        validation_result = persona_manager.validate_persona(persona_id=persona_id)
        
        # Create response
        return PersonaValidation(
            persona_id=persona_id,
            is_valid=validation_result.get("is_valid", False),
            issues=validation_result.get("issues", []),
            warnings=validation_result.get("warnings", []),
            suggestions=validation_result.get("suggestions", []),
            validation_date=validation_result.get("timestamp")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate persona: {str(e)}")

@router.post(
    "/import",
    response_model=PersonaResponse,
    status_code=201,
    summary="Import persona",
    description="Imports an AI professional persona from a JSON file."
)
async def import_persona(
    file: UploadFile = File(..., description="JSON file containing persona data"),
    current_user = Depends(get_current_user),
    persona_manager: PersonaManager = Depends(get_persona_manager)
):
    """Import an AI professional persona from a JSON file."""
    try:
        # Read the file content
        file_content = await file.read()
        
        # Import the persona
        persona = persona_manager.import_persona(file_content=file_content)
        
        return PersonaResponse.from_persona_model(persona)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import persona: {str(e)}")

@router.get(
    "/{persona_id}/export",
    summary="Export persona",
    description="Exports an AI professional persona to a JSON file."
)
async def export_persona(
    persona_id: str = Path(..., description="The ID of the persona to export"),
    format: str = Query("json", description="Export format (json)"),
    current_user = Depends(get_current_user),
    persona_manager: PersonaManager = Depends(get_persona_manager)
):
    """Export an AI professional persona to a JSON file."""
    try:
        # Check if persona exists
        existing_persona = persona_manager.get_persona(persona_id=persona_id)
        if not existing_persona:
            raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
        
        # Export the persona
        export_data = persona_manager.export_persona(persona_id=persona_id, format=format)
        
        # Create filename
        filename = f"{existing_persona.name.replace(' ', '_').lower()}_persona.json"
        
        # Return the file as a download
        return JSONResponse(
            content=export_data,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export persona: {str(e)}")
