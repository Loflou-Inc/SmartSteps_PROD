"""
Persona models for the Smart Steps AI API.

This module defines the data models for persona management endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID

from .common import PaginatedResponse


class PersonaCreate(BaseModel):
    """Persona creation request model."""
    id: str = Field(..., description="ID of the persona")
    name: str = Field(..., description="Name of the persona")
    type: str = Field(..., description="Type of persona")
    background: str = Field(..., description="Background information about the persona")
    education: List[str] = Field(..., description="Education information")
    specialties: List[str] = Field(..., description="Professional specialties")
    approach: str = Field(..., description="Professional approach description")
    theoretical_orientation: Optional[List[str]] = Field(None, description="Theoretical orientations")
    communication_style: Optional[Dict[str, str]] = Field(None, description="Communication style attributes")
    intervention_techniques: Optional[List[str]] = Field(None, description="Intervention techniques")
    response_patterns: Optional[Dict[str, List[str]]] = Field(None, description="Response patterns")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional persona metadata")

    @validator('id')
    def id_valid(cls, v):
        """Validate that ID contains only valid characters."""
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('ID can only contain alphanumeric characters and underscores')
        return v


class PersonaUpdate(BaseModel):
    """Persona update request model."""
    name: Optional[str] = Field(None, description="Name of the persona")
    type: Optional[str] = Field(None, description="Type of persona")
    background: Optional[str] = Field(None, description="Background information about the persona")
    education: Optional[List[str]] = Field(None, description="Education information")
    specialties: Optional[List[str]] = Field(None, description="Professional specialties")
    approach: Optional[str] = Field(None, description="Professional approach description")
    theoretical_orientation: Optional[List[str]] = Field(None, description="Theoretical orientations")
    communication_style: Optional[Dict[str, str]] = Field(None, description="Communication style attributes")
    intervention_techniques: Optional[List[str]] = Field(None, description="Intervention techniques")
    response_patterns: Optional[Dict[str, List[str]]] = Field(None, description="Response patterns")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional persona metadata")


class PersonaResponse(BaseModel):
    """Persona response model."""
    id: str = Field(..., description="ID of the persona")
    name: str = Field(..., description="Name of the persona")
    type: str = Field(..., description="Type of persona")
    background: str = Field(..., description="Background information about the persona")
    education: List[str] = Field(..., description="Education information")
    specialties: List[str] = Field(..., description="Professional specialties")
    approach: str = Field(..., description="Professional approach description")
    theoretical_orientation: Optional[List[str]] = Field(None, description="Theoretical orientations")
    communication_style: Optional[Dict[str, str]] = Field(None, description="Communication style attributes")
    intervention_techniques: Optional[List[str]] = Field(None, description="Intervention techniques")
    response_patterns: Optional[Dict[str, List[str]]] = Field(None, description="Response patterns")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional persona metadata")

    class Config:
        """Configuration for the model."""
        schema_extra = {
            "example": {
                "id": "therapist",
                "name": "Dr. Sarah Thompson",
                "type": "therapist",
                "background": "Dr. Thompson is a licensed clinical psychologist with over 15 years of experience in cognitive behavioral therapy.",
                "education": [
                    "Ph.D. in Clinical Psychology, Stanford University",
                    "M.A. in Psychology, University of California, Berkeley"
                ],
                "specialties": [
                    "Cognitive Behavioral Therapy",
                    "Anxiety Disorders",
                    "Depression",
                    "Trauma"
                ],
                "approach": "Dr. Thompson uses evidence-based cognitive behavioral techniques to help clients identify and change negative thought patterns.",
                "theoretical_orientation": [
                    "Cognitive-Behavioral",
                    "Acceptance and Commitment Therapy",
                    "Mindfulness-Based Cognitive Therapy"
                ],
                "communication_style": {
                    "formality": "moderate",
                    "empathy": "high",
                    "directness": "moderate",
                    "technical_language": "moderate"
                },
                "intervention_techniques": [
                    "Cognitive Restructuring",
                    "Exposure Therapy",
                    "Behavioral Activation",
                    "Mindfulness Practices"
                ],
                "response_patterns": {
                    "greeting": [
                        "Hello [client_name], it's good to see you today.",
                        "Welcome back, [client_name]."
                    ],
                    "exploration": [
                        "Can you tell me more about that?",
                        "How did that make you feel?",
                        "What thoughts were going through your mind at that time?"
                    ]
                },
                "metadata": {
                    "created_at": "2025-05-01T10:00:00Z",
                    "last_updated": "2025-05-10T15:30:00Z"
                }
            }
        }


class PersonaList(PaginatedResponse[PersonaResponse]):
    """Paginated list of personas."""
    items: List[PersonaResponse] = Field(..., description="List of personas")


class KnowledgeAddRequest(BaseModel):
    """Request to add knowledge to a persona."""
    persona_id: str = Field(..., description="ID of the persona")
    document_id: str = Field(..., description="ID of the document")
    content: str = Field(..., description="Document content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")

    @validator('content')
    def content_not_empty(cls, v):
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v


class KnowledgeSearchRequest(BaseModel):
    """Request to search persona knowledge."""
    persona_id: str = Field(..., description="ID of the persona")
    query: str = Field(..., description="Search query")
    limit: Optional[int] = Field(5, description="Maximum number of results")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Filter results by metadata")


class KnowledgeChunk(BaseModel):
    """Knowledge chunk model."""
    chunk_id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    text: str = Field(..., description="Chunk text")
    similarity: float = Field(..., description="Similarity score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Chunk metadata")


class KnowledgeSearchResponse(BaseModel):
    """Knowledge search response model."""
    persona_id: str = Field(..., description="ID of the persona")
    query: str = Field(..., description="Search query")
    results: List[KnowledgeChunk] = Field(..., description="Search results")
