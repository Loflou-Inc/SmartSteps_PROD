"""
Persona schema definitions.

This module defines Pydantic models for persona-related API requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

class PersonaBase(BaseModel):
    """Base model for persona data."""
    name: str = Field(..., description="The name of the professional persona")
    role: str = Field(..., description="The professional role of the persona")
    description: str = Field(..., description="A detailed description of the persona")
    expertise: List[str] = Field(..., description="Areas of expertise for the persona")
    traits: List[str] = Field(..., description="Personality traits of the persona")
    voice_style: str = Field(..., description="The communication style of the persona")
    therapeutic_approach: List[str] = Field(..., description="Therapeutic approaches used by the persona")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional persona metadata")

class PersonaCreate(PersonaBase):
    """Model for creating a new persona."""
    pass

class PersonaUpdate(BaseModel):
    """Model for updating an existing persona."""
    name: Optional[str] = Field(None, description="The updated name of the persona")
    description: Optional[str] = Field(None, description="The updated description of the persona")
    expertise: Optional[List[str]] = Field(None, description="Updated areas of expertise")
    traits: Optional[List[str]] = Field(None, description="Updated personality traits")
    voice_style: Optional[str] = Field(None, description="Updated communication style")
    therapeutic_approach: Optional[List[str]] = Field(None, description="Updated therapeutic approaches")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated persona metadata")

class PersonaResponse(PersonaBase):
    """Model for persona response data."""
    id: str = Field(..., description="The unique identifier for the persona")
    created_at: datetime = Field(..., description="The timestamp when the persona was created")
    updated_at: datetime = Field(..., description="The timestamp when the persona was last updated")
    effectiveness: Optional[float] = Field(None, description="The effectiveness rating of the persona (0.0-1.0)")
    session_count: int = Field(..., description="The number of sessions using this persona")
    is_enhanced: bool = Field(..., description="Whether this is an enhanced persona with layered memory")
    
    @classmethod
    def from_persona_model(cls, persona_model):
        """Create a PersonaResponse from a persona model instance."""
        return cls(
            id=persona_model.persona_id,
            name=persona_model.name,
            role=persona_model.role,
            description=persona_model.description,
            expertise=persona_model.expertise,
            traits=persona_model.traits,
            voice_style=persona_model.voice_style,
            therapeutic_approach=persona_model.therapeutic_approach,
            created_at=persona_model.created_at,
            updated_at=persona_model.updated_at,
            effectiveness=persona_model.effectiveness,
            session_count=persona_model.session_count,
            is_enhanced=persona_model.is_enhanced,
            metadata=persona_model.metadata
        )

class PersonaList(BaseModel):
    """Model for a list of personas with pagination information."""
    personas: List[PersonaResponse] = Field(..., description="List of personas")
    total_count: int = Field(..., description="Total number of personas matching the filters")
    limit: int = Field(..., description="Maximum number of personas returned")
    offset: int = Field(..., description="Number of personas skipped")

class PersonaValidation(BaseModel):
    """Model for persona validation results."""
    persona_id: str = Field(..., description="The ID of the validated persona")
    is_valid: bool = Field(..., description="Whether the persona is valid")
    issues: List[str] = Field(..., description="Issues identified during validation")
    warnings: List[str] = Field(..., description="Warnings about potential issues")
    suggestions: List[str] = Field(..., description="Suggestions for improvement")
    validation_date: datetime = Field(..., description="The timestamp when the validation was performed")
