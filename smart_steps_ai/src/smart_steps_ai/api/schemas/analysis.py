"""
Analysis schema definitions.

This module defines Pydantic models for analysis-related API requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field

class SessionAnalysisResponse(BaseModel):
    """Model for session analysis response data."""
    session_id: str = Field(..., description="The ID of the analyzed session")
    client_id: str = Field(..., description="The ID of the client")
    title: str = Field(..., description="The title of the session")
    summary: str = Field(..., description="A summary of the session")
    key_points: List[str] = Field(..., description="Key points from the session")
    themes: List[str] = Field(..., description="Themes identified in the session")
    concerns: List[str] = Field(..., description="Concerns identified in the session")
    strengths: List[str] = Field(..., description="Client strengths identified in the session")
    recommendations: List[str] = Field(..., description="Recommendations based on the session")
    sentiment_analysis: Dict[str, Any] = Field(..., description="Sentiment analysis results")
    analysis_date: datetime = Field(..., description="The timestamp when the analysis was performed")

class InsightResponse(BaseModel):
    """Model for insight response data."""
    id: str = Field(..., description="The unique identifier for the insight")
    client_id: str = Field(..., description="The ID of the client")
    session_id: Optional[str] = Field(None, description="The ID of the session (if applicable)")
    type: str = Field(..., description="The type of insight")
    content: str = Field(..., description="The content of the insight")
    confidence: float = Field(..., description="The confidence level of the insight (0.0-1.0)")
    timestamp: datetime = Field(..., description="The timestamp when the insight was generated")
    supporting_evidence: List[str] = Field(..., description="Evidence supporting the insight")
    related_insights: List[str] = Field(..., description="Related insight IDs")
    actions: List[str] = Field(..., description="Recommended actions based on the insight")

class InsightList(BaseModel):
    """Model for a list of insights with pagination information."""
    insights: List[InsightResponse] = Field(..., description="List of insights")
    total_count: int = Field(..., description="Total number of insights matching the filters")
    limit: int = Field(..., description="Maximum number of insights returned")
    client_id: str = Field(..., description="The ID of the client")
    timeframe: str = Field(..., description="The timeframe for the insights")

class ReportSection(BaseModel):
    """Model for a section in a report."""
    title: str = Field(..., description="The title of the section")
    content: str = Field(..., description="The content of the section")
    type: str = Field(..., description="The type of the section")
    order: int = Field(..., description="The order of the section in the report")

class ReportResponse(BaseModel):
    """Model for report response data."""
    id: str = Field(..., description="The unique identifier for the report")
    client_id: str = Field(..., description="The ID of the client")
    title: str = Field(..., description="The title of the report")
    format: str = Field(..., description="The format of the report (json, markdown, html, pdf)")
    content: str = Field(..., description="The full content of the report")
    sections: List[ReportSection] = Field(..., description="Sections of the report")
    metadata: Dict[str, Any] = Field(..., description="Additional report metadata")
    created_at: datetime = Field(..., description="The timestamp when the report was generated")
    session_count: int = Field(..., description="The number of sessions included in the report")
    timeframe: str = Field(..., description="The timeframe for the report")

class ProgressMetric(BaseModel):
    """Model for a progress metric."""
    name: str = Field(..., description="The name of the metric")
    value: float = Field(..., description="The current value of the metric")
    baseline: float = Field(..., description="The baseline value of the metric")
    target: Optional[float] = Field(None, description="The target value for the metric")
    change: float = Field(..., description="The change in the metric value")
    change_percentage: float = Field(..., description="The percentage change in the metric value")
    history: List[Dict[str, Any]] = Field(..., description="Historical values of the metric")

class Milestone(BaseModel):
    """Model for a progress milestone."""
    id: str = Field(..., description="The unique identifier for the milestone")
    title: str = Field(..., description="The title of the milestone")
    description: str = Field(..., description="The description of the milestone")
    achieved: bool = Field(..., description="Whether the milestone has been achieved")
    achieved_date: Optional[datetime] = Field(None, description="The date when the milestone was achieved")
    target_date: Optional[datetime] = Field(None, description="The target date for achieving the milestone")
    metrics: List[str] = Field(..., description="Metrics associated with the milestone")

class ProgressResponse(BaseModel):
    """Model for progress response data."""
    client_id: str = Field(..., description="The ID of the client")
    timeframe: str = Field(..., description="The timeframe for the progress data")
    metrics: Dict[str, ProgressMetric] = Field(..., description="Progress metrics")
    trends: Dict[str, Any] = Field(..., description="Trend analysis data")
    milestones: List[Milestone] = Field(..., description="Progress milestones")
    summary: str = Field(..., description="Summary of client progress")
    recommendation: str = Field(..., description="Recommendations based on progress")
    session_count: int = Field(..., description="The number of sessions included in the progress data")
    first_session_date: datetime = Field(..., description="The date of the first session")
    latest_session_date: datetime = Field(..., description="The date of the latest session")
