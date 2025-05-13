"""Data models for professional personas."""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class PersonalityTraits(BaseModel):
    """Personality traits for a professional persona."""

    empathy: int = Field(default=5, ge=1, le=10)
    analytical: int = Field(default=5, ge=1, le=10)
    patience: int = Field(default=5, ge=1, le=10)
    directness: int = Field(default=5, ge=1, le=10)
    formality: int = Field(default=5, ge=1, le=10)
    warmth: int = Field(default=5, ge=1, le=10)
    curiosity: int = Field(default=5, ge=1, le=10)
    confidence: int = Field(default=5, ge=1, le=10)


class ConversationStyle(BaseModel):
    """Conversation style preferences for a persona."""

    greeting_format: str = "Hello {{client_name}}. How are you today?"
    question_frequency: str = Field(default="medium", pattern="^(low|medium|high)$")
    session_structure: List[str] = []
    typical_phrases: List[str] = []
    closing_format: str = "Thank you for talking with me today."


class AnalysisApproach(BaseModel):
    """Analysis approach for a persona."""

    focuses_on: List[str] = []
    assessment_methods: List[str] = []
    report_style: str = Field(default="balanced", pattern="^(technical|balanced|casual|balanced_professional)$")


class ResponseExample(BaseModel):
    """Example response from a persona."""

    context: str
    client_message: str
    response: str


class PersonaMetadata(BaseModel):
    """Metadata for a professional persona."""

    name: str
    display_name: str
    version: str = "1.0.0"
    description: str


class Persona(BaseModel):
    """Complete professional persona definition."""

    # Metadata
    name: str
    display_name: str
    version: str = "1.0.0"
    description: str

    # Core definition
    system_prompt: str
    personality_traits: PersonalityTraits = Field(default_factory=PersonalityTraits)
    expertise_areas: List[str] = []
    conversation_style: ConversationStyle = Field(default_factory=ConversationStyle)
    analysis_approach: AnalysisApproach = Field(default_factory=AnalysisApproach)
    rules: List[str] = []
    examples: List[ResponseExample] = []
    
    # Provider information
    provider: str = "anthropic"
    model: str = "claude-3-opus-20240229"

    @field_validator("name")
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        """Validate that the name contains only allowed characters."""
        if not v:
            raise ValueError("Name cannot be empty")
        
        if not all(c.isalnum() or c in "_-" for c in v):
            raise ValueError("Name can only contain alphanumeric characters, underscores, and hyphens")
        
        return v

    def to_metadata(self) -> PersonaMetadata:
        """
        Convert to a persona metadata object.

        Returns:
            PersonaMetadata: Metadata object for this persona
        """
        return PersonaMetadata(
            name=self.name,
            display_name=self.display_name,
            version=self.version,
            description=self.description,
        )

    def get_system_prompt(self, additional_context: Optional[str] = None) -> str:
        """
        Get the system prompt for this persona.

        Args:
            additional_context (Optional[str]): Additional context to include in the prompt

        Returns:
            str: System prompt for the AI
        """
        prompt = self.system_prompt
        
        if additional_context:
            prompt = f"{prompt}\n\n{additional_context}"
        
        return prompt
