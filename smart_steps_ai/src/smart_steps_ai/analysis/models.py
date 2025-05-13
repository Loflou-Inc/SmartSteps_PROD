"""Data models for session analysis."""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ..session.models import SessionMetadata


class InsightCategory(str, Enum):
    """Category of an insight."""

    BEHAVIORAL = "behavioral"
    COGNITIVE = "cognitive"
    EMOTIONAL = "emotional"
    RELATIONAL = "relational"
    GOAL_RELATED = "goal_related"
    STRENGTH = "strength"
    CHALLENGE = "challenge"
    PATTERN = "pattern"
    PROGRESS = "progress"
    STRATEGY = "strategy"
    GENERAL = "general"


class ProgressMetric(BaseModel):
    """A metric for tracking progress."""

    name: str
    description: str
    value: float
    min_value: float = 0.0
    max_value: float = 10.0
    previous_value: Optional[float] = None
    change: Optional[float] = None
    change_percentage: Optional[float] = None
    target_value: Optional[float] = None
    
    def calculate_changes(self) -> None:
        """Calculate the change and change percentage."""
        if self.previous_value is not None:
            self.change = self.value - self.previous_value
            
            if self.previous_value != 0:
                self.change_percentage = (self.change / abs(self.previous_value)) * 100
            else:
                self.change_percentage = None


class Insight(BaseModel):
    """An insight extracted from a session."""

    text: str
    category: InsightCategory
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    relevance: float = Field(default=0.8, ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    related_insights: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)


class ReportFormat(str, Enum):
    """Format of a report."""

    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    CSV = "csv"


class AnalysisResult(BaseModel):
    """Result of a session analysis."""

    session_id: str
    client_name: str
    persona_name: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    # Summary
    summary: str
    
    # Insights
    insights: List[Insight] = Field(default_factory=list)
    
    # Progress metrics
    metrics: List[ProgressMetric] = Field(default_factory=list)
    
    # Key themes
    themes: List[str] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    
    # Next steps
    next_steps: List[str] = Field(default_factory=list)
    
    # Additional data
    session_metadata: Optional[SessionMetadata] = None
    additional_data: Dict[str, str] = Field(default_factory=dict)
