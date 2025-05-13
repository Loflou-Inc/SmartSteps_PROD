"""
Analysis API endpoints.

This module provides endpoints for analyzing therapy sessions,
generating insights, and creating reports.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse, HTMLResponse

from smart_steps_ai.session import SessionManager
from smart_steps_ai.analysis import AnalysisManager
from ..schemas.analysis import (
    SessionAnalysisResponse,
    InsightResponse,
    InsightList,
    ReportResponse,
    ProgressResponse
)
from ..security.auth import get_current_user
from ..dependencies import get_session_manager, get_analysis_manager

router = APIRouter()

@router.get(
    "/sessions/{session_id}",
    response_model=SessionAnalysisResponse,
    summary="Analyze session",
    description="Performs a comprehensive analysis of a therapy session."
)
async def analyze_session(
    session_id: UUID = Path(..., description="The ID of the session to analyze"),
    depth: str = Query("standard", description="Analysis depth (basic, standard, deep)"),
    current_user = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    analysis_manager = Depends(get_analysis_manager)
):
    """Analyze a therapy session and generate comprehensive insights."""
    try:
        # Check if session exists
        session = session_manager.get_session(session_id=str(session_id))
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Perform session analysis
        analysis = analysis_manager.analyze_session(
            session_id=str(session_id),
            depth=depth
        )
        
        # Create response
        return SessionAnalysisResponse(
            session_id=str(session_id),
            client_id=session.client_id,
            title=session.title,
            summary=analysis.get("summary", ""),
            key_points=analysis.get("key_points", []),
            themes=analysis.get("themes", []),
            concerns=analysis.get("concerns", []),
            strengths=analysis.get("strengths", []),
            recommendations=analysis.get("recommendations", []),
            sentiment_analysis=analysis.get("sentiment", {}),
            analysis_date=analysis.get("timestamp")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze session: {str(e)}")

@router.get(
    "/insights/client/{client_id}",
    response_model=InsightList,
    summary="Get client insights",
    description="Retrieves insights for a specific client across all therapy sessions."
)
async def get_client_insights(
    client_id: str = Path(..., description="The ID of the client"),
    timeframe: str = Query("all", description="Timeframe for insights (recent, month, year, all)"),
    limit: int = Query(20, description="Maximum number of insights to return"),
    current_user = Depends(get_current_user),
    analysis_manager = Depends(get_analysis_manager)
):
    """Get insights for a specific client across all therapy sessions."""
    try:
        # Get insights for the client
        insights = analysis_manager.get_client_insights(
            client_id=client_id,
            timeframe=timeframe,
            limit=limit
        )
        
        # Create response
        insight_responses = [
            InsightResponse(
                id=insight.get("id"),
                client_id=client_id,
                session_id=insight.get("session_id"),
                type=insight.get("type"),
                content=insight.get("content"),
                confidence=insight.get("confidence", 0.0),
                timestamp=insight.get("timestamp"),
                supporting_evidence=insight.get("evidence", []),
                related_insights=insight.get("related", []),
                actions=insight.get("actions", [])
            ) for insight in insights
        ]
        
        total_count = analysis_manager.count_client_insights(client_id=client_id, timeframe=timeframe)
        
        return InsightList(
            insights=insight_responses,
            total_count=total_count,
            limit=limit,
            client_id=client_id,
            timeframe=timeframe
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve client insights: {str(e)}")

@router.get(
    "/reports/client/{client_id}",
    response_model=ReportResponse,
    summary="Generate client report",
    description="Generates a comprehensive report for a client based on therapy sessions."
)
async def generate_client_report(
    client_id: str = Path(..., description="The ID of the client"),
    format: str = Query("json", description="Report format (json, markdown, html, pdf)"),
    timeframe: str = Query("all", description="Timeframe for report (recent, month, year, all)"),
    template: Optional[str] = Query(None, description="Optional report template name"),
    current_user = Depends(get_current_user),
    analysis_manager = Depends(get_analysis_manager)
):
    """Generate a comprehensive report for a client."""
    try:
        # Generate the report
        report = analysis_manager.generate_client_report(
            client_id=client_id,
            format=format,
            timeframe=timeframe,
            template=template
        )
        
        # Handle different response formats
        if format.lower() == "pdf":
            # For PDF, we would return a binary response
            # This is a placeholder - the actual implementation would depend on how PDFs are generated
            return JSONResponse(
                content={
                    "message": "PDF generation not implemented in this endpoint",
                    "download_url": f"/api/v1/downloads/reports/{report.get('id')}"
                },
                status_code=200
            )
        elif format.lower() == "html":
            # For HTML, return an HTML response
            return HTMLResponse(content=report.get("content", ""))
        else:
            # For JSON and Markdown, use the standard response model
            return ReportResponse(
                id=report.get("id"),
                client_id=client_id,
                title=report.get("title", f"Report for Client {client_id}"),
                format=format.lower(),
                content=report.get("content", ""),
                sections=report.get("sections", []),
                metadata=report.get("metadata", {}),
                created_at=report.get("timestamp"),
                session_count=report.get("session_count", 0),
                timeframe=timeframe
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate client report: {str(e)}")

@router.get(
    "/progress/client/{client_id}",
    response_model=ProgressResponse,
    summary="Get client progress",
    description="Retrieves progress metrics and tracking data for a specific client."
)
async def get_client_progress(
    client_id: str = Path(..., description="The ID of the client"),
    timeframe: str = Query("all", description="Timeframe for progress data (recent, month, year, all)"),
    metrics: List[str] = Query(None, description="Specific metrics to include (defaults to all available)"),
    current_user = Depends(get_current_user),
    analysis_manager = Depends(get_analysis_manager)
):
    """Get progress metrics and tracking data for a client."""
    try:
        # Get progress data for the client
        progress_data = analysis_manager.get_client_progress(
            client_id=client_id,
            timeframe=timeframe,
            metrics=metrics
        )
        
        # Create response
        return ProgressResponse(
            client_id=client_id,
            timeframe=timeframe,
            metrics=progress_data.get("metrics", {}),
            trends=progress_data.get("trends", {}),
            milestones=progress_data.get("milestones", []),
            summary=progress_data.get("summary", ""),
            recommendation=progress_data.get("recommendation", ""),
            session_count=progress_data.get("session_count", 0),
            first_session_date=progress_data.get("first_session"),
            latest_session_date=progress_data.get("latest_session")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve client progress: {str(e)}")

@router.get(
    "/patterns/client/{client_id}",
    response_model=List[InsightResponse],
    summary="Identify client patterns",
    description="Identifies behavioral patterns and recurring themes for a client."
)
async def identify_client_patterns(
    client_id: str = Path(..., description="The ID of the client"),
    depth: str = Query("standard", description="Analysis depth (basic, standard, deep)"),
    limit: int = Query(10, description="Maximum number of patterns to return"),
    current_user = Depends(get_current_user),
    analysis_manager = Depends(get_analysis_manager)
):
    """Identify behavioral patterns and recurring themes for a client."""
    try:
        # Analyze patterns for the client
        patterns = analysis_manager.identify_patterns(
            client_id=client_id,
            depth=depth,
            limit=limit
        )
        
        # Create response
        pattern_responses = [
            InsightResponse(
                id=pattern.get("id"),
                client_id=client_id,
                session_id=None,  # Patterns span across sessions
                type="pattern",
                content=pattern.get("description"),
                confidence=pattern.get("confidence", 0.0),
                timestamp=pattern.get("timestamp"),
                supporting_evidence=pattern.get("evidence", []),
                related_insights=pattern.get("related", []),
                actions=pattern.get("recommendations", [])
            ) for pattern in patterns
        ]
        
        return pattern_responses
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to identify client patterns: {str(e)}")
