"""Extended data models for complex professional personas."""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from .models import Persona, PersonalityTraits, ConversationStyle


class LifeEvent(BaseModel):
    """Significant life event for a professional persona's backstory."""
    
    id: str  # Unique identifier for the event
    title: str  # Brief title of the event
    description: str  # Detailed description
    age: Optional[int] = None  # Age when event occurred
    date: Optional[str] = None  # Date in any format (can be approximate)
    emotional_impact: int = Field(default=5, ge=1, le=10)  # How emotionally significant
    categories: List[str] = []  # Tags like "trauma", "education", "career"
    related_events: List[str] = []  # IDs of related life events
    details: Dict[str, Any] = {}  # Flexible container for specific details


class KnowledgeArea(BaseModel):
    """Knowledge area for a professional persona."""
    
    id: str  # Unique identifier
    name: str  # Name of knowledge area
    description: str  # Description of the knowledge area
    proficiency: int = Field(default=5, ge=1, le=10)  # Level of expertise
    sources: List[str] = []  # Sources of knowledge (education, experience)
    keywords: List[str] = []  # Keywords for searching
    examples: List[str] = []  # Examples of applying this knowledge


class ValueBelief(BaseModel):
    """Core value or belief held by the persona."""
    
    id: str  # Unique identifier
    value: str  # The value or belief
    description: str  # Explanation of the value
    importance: int = Field(default=5, ge=1, le=10)  # How important to identity
    origin: Optional[str] = None  # Where this value came from
    related_values: List[str] = []  # IDs of related values
    influences: List[str] = []  # How this affects behavior


class TherapeuticApproach(BaseModel):
    """Therapeutic approach used by the persona."""
    
    name: str  # Name of approach (e.g., "CBT", "Psychodynamic")
    description: str  # Description of the approach
    proficiency: int = Field(default=5, ge=1, le=10)  # Level of expertise
    core_techniques: List[str] = []  # Key techniques used
    typical_questions: List[str] = []  # Questions commonly asked
    theoretical_foundations: List[str] = []  # Theoretical basis


class CanonicalDetail(BaseModel):
    """Generated canonical detail about the persona's life."""
    
    id: str  # Unique identifier
    detail: str  # The specific detail generated
    context: str  # Original context where generated
    created_at: datetime  # When first generated
    related_event_id: Optional[str] = None  # Related life event if applicable
    categories: List[str] = []  # Categories this detail belongs to
    usage_count: int = 0  # How often it's been referenced
    reference_history: List[str] = []  # When it was referenced


class EnhancedPersona(Persona):
    """Extended professional persona with detailed backstory and knowledge."""
    
    # Core identity extensions
    full_name: str  # Complete name
    birth_date: Optional[str] = None  # Birth date (can be approximate)
    current_age: Optional[int] = None  # Current age
    gender: Optional[str] = None  # Gender identity
    cultural_background: List[str] = []  # Cultural backgrounds
    
    # Life story and experience
    life_events: List[LifeEvent] = []  # Significant life events
    education_history: List[Dict[str, Any]] = []  # Educational background
    professional_history: List[Dict[str, Any]] = []  # Work history
    
    # Knowledge and beliefs
    knowledge_areas: List[KnowledgeArea] = []  # Areas of expertise
    values_and_beliefs: List[ValueBelief] = []  # Core values and beliefs
    therapeutic_approaches: List[TherapeuticApproach] = []  # Clinical approaches
    
    # Generated canonical details (supplementary to life_events)
    canonical_details: List[CanonicalDetail] = []
    
    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True
    
    def get_life_event_by_id(self, event_id: str) -> Optional[LifeEvent]:
        """Retrieve a life event by its ID."""
        for event in self.life_events:
            if event.id == event_id:
                return event
        return None
    
    def get_events_by_category(self, category: str) -> List[LifeEvent]:
        """Get all life events in a specific category."""
        return [event for event in self.life_events if category in event.categories]
    
    def get_canonical_details_by_category(self, category: str) -> List[CanonicalDetail]:
        """Get all canonical details in a specific category."""
        return [detail for detail in self.canonical_details if category in detail.categories]
    
    def add_canonical_detail(self, detail: str, context: str, categories: List[str], 
                            related_event_id: Optional[str] = None) -> CanonicalDetail:
        """Add a new canonical detail to the persona's history."""
        now = datetime.now()
        new_detail = CanonicalDetail(
            id=f"detail_{len(self.canonical_details) + 1}_{now.timestamp()}",
            detail=detail,
            context=context,
            created_at=now,
            related_event_id=related_event_id,
            categories=categories,
            usage_count=1,
            reference_history=[str(now)]
        )
        self.canonical_details.append(new_detail)
        return new_detail
    
    def get_relevant_life_context(self, query: str, max_events: int = 5) -> List[LifeEvent]:
        """
        Get life events relevant to a query.
        
        In a real implementation, this would use embeddings for relevance.
        This is a simplified version based on keyword matching.
        """
        # Simplified implementation - in production would use embeddings
        query_words = set(query.lower().split())
        scored_events = []
        
        for event in self.life_events:
            score = 0
            event_text = f"{event.title} {event.description}".lower()
            
            # Count matching words
            for word in query_words:
                if word in event_text:
                    score += 1
            
            # Add category-based matching
            for category in event.categories:
                if category.lower() in query.lower():
                    score += 2
            
            if score > 0:
                scored_events.append((event, score))
        
        # Sort by relevance score (descending)
        scored_events.sort(key=lambda x: x[1], reverse=True)
        
        # Return top events
        return [event for event, _ in scored_events[:max_events]]
