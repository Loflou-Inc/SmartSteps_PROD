"""
Comprehensive reporting functionality for the Smart Steps AI module.

Provides functions for generating detailed reports combining
multiple types of analysis across sessions.
"""

from datetime import datetime
from typing import List, Dict, Any

from smart_steps_ai.analysis.insights import (
    generate_session_insights,
    extract_key_themes,
    analyze_sentiment_trends,
    generate_progress_report
)

def generate_comprehensive_report(
    sessions,
    client_name,
    period="all",
    comprehensive=False
) -> Dict[str, Any]:
    """
    Generate a comprehensive report across multiple sessions.
    
    Args:
        sessions: List of session objects to analyze
        client_name: Name of the client
        period: Time period for the report (week, month, all)
        comprehensive: Whether to include all analysis types
        
    Returns:
        Dictionary with comprehensive report data
    """
    # Sort sessions by date
    sessions = sorted(sessions, key=lambda s: s.created_at)
    
    # Basic report data
    report = {
        "client_name": client_name,
        "period": period,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "session_count": len(sessions),
        "first_session_date": sessions[0].created_at if sessions else None,
        "last_session_date": sessions[-1].created_at if sessions else None
    }
    
    # Get progress report
    progress_data = generate_progress_report(sessions)
    report["progress"] = progress_data
    
    # Extract all themes across sessions
    all_themes = []
    for session in sessions:
        themes = extract_key_themes(session, count=3)
        all_themes.extend(themes)
    
    # Combine and deduplicate themes
    theme_scores = {}
    for theme, score in all_themes:
        base_theme = theme.split(" (")[0].lower()
        if base_theme in theme_scores:
            theme_scores[base_theme] = max(theme_scores[base_theme], score)
        else:
            theme_scores[base_theme] = score
    
    # Get top themes
    top_themes = sorted([(t.capitalize(), s) for t, s in theme_scores.items()], key=lambda x: x[1], reverse=True)[:5]
    report["themes"] = [t for t, _ in top_themes]
    
    # Gather recommendations from progress report
    report["recommendations"] = progress_data.get("recommendations", [])
    
    # Gather challenges from progress report
    report["challenges"] = progress_data.get("challenges", [])
    
    # Generate executive summary
    # This would normally use AI to create a cohesive summary
    executive_summary = f"This report analyzes {len(sessions)} therapy sessions with {client_name} "
    
    if report["first_session_date"] and report["last_session_date"]:
        time_span = (report["last_session_date"] - report["first_session_date"]).days
        time_span_str = f"{time_span} days" if time_span > 0 else "the same day"
        executive_summary += f"conducted over {time_span_str}. "
    else:
        executive_summary += ". "
    
    executive_summary += "Key themes identified include " + ", ".join(report["themes"][:3]) + ". "
    executive_summary += progress_data.get("summary", "")
    
    report["executive_summary"] = executive_summary
    
    # Add next steps
    report["next_steps"] = [
        "Schedule follow-up session focusing on identified challenges",
        "Review and adjust coping strategies based on effectiveness",
        "Consider additional therapeutic approaches for areas with limited progress",
        "Evaluate need for supplementary resources or interventions",
        "Plan for regular progress reviews to maintain momentum"
    ]
    
    # If comprehensive, include session-specific insights
    if comprehensive:
        session_insights = []
        for session in sessions:
            insights = generate_session_insights(session)
            
            # Skip sessions with no substantial insights
            if not any(insights.values()):
                continue
                
            session_insights.append({
                "session_id": session.id,
                "date": session.created_at,
                "insights": insights
            })
        
        report["session_insights"] = session_insights
        
        # Add sentiment analysis for recent sessions
        recent_sessions = sessions[-3:] if len(sessions) >= 3 else sessions
        sentiment_data = {}
        
        for session in recent_sessions:
            sentiment = analyze_sentiment_trends(session)
            if sentiment:
                sentiment_data[str(session.id)] = sentiment
        
        if sentiment_data:
            report["sentiment_analysis"] = sentiment_data
    
    return report

def generate_session_report(session) -> Dict[str, Any]:
    """
    Generate a comprehensive report for a single session.
    
    Args:
        session: Session object to analyze
        
    Returns:
        Dictionary with session report data
    """
    # Basic report data
    report = {
        "session_id": session.id,
        "client_name": session.client_name,
        "persona_id": session.persona_id,
        "date": session.created_at.strftime("%Y-%m-%d %H:%M"),
        "status": "Active" if not session.ended_at else "Ended"
    }
    
    # Generate insights
    insights = generate_session_insights(session, detailed=True)
    report["insights"] = insights
    
    # Extract themes
    themes = extract_key_themes(session, count=5)
    report["themes"] = [t for t, _ in themes]
    
    # Analyze sentiment
    sentiment = analyze_sentiment_trends(session)
    if sentiment:
        report["sentiment"] = sentiment
    
    # Generate key observations
    key_observations = []
    if "Key Observations" in insights:
        key_observations.extend(insights["Key Observations"])
    
    # Add interaction details
    if hasattr(session, 'messages') and session.messages:
        message_count = len(session.messages)
        client_messages = sum(1 for msg in session.messages if msg.is_user)
        professional_messages = message_count - client_messages
        
        report["interaction"] = {
            "message_count": message_count,
            "client_messages": client_messages,
            "professional_messages": professional_messages,
            "client_professional_ratio": client_messages / professional_messages if professional_messages > 0 else 0
        }
    
        # Add summary of client concerns
        if "Potential Areas of Focus" in insights:
            report["client_concerns"] = insights["Potential Areas of Focus"]
    
    # Generate recommendations
    report["recommendations"] = [
        "Focus on exploring emotional responses to identified stressors",
        "Develop specific coping strategies for challenging situations",
        "Practice self-reflection between sessions to build awareness",
        "Continue to identify and challenge negative thought patterns"
    ]
    
    # Generate executive summary
    # This would normally use AI to create a cohesive summary
    executive_summary = f"This report analyzes a therapy session with {session.client_name} "
    executive_summary += f"conducted on {session.created_at.strftime('%Y-%m-%d')}. "
    
    if "themes" in report and report["themes"]:
        executive_summary += "Key themes identified include " + ", ".join(report["themes"][:2]) + ". "
    
    if "Key Observations" in insights and insights["Key Observations"]:
        executive_summary += "Notable observations include " + insights["Key Observations"][0] + ". "
    
    executive_summary += "The session was productive and identified important areas for ongoing therapeutic work."
    
    report["executive_summary"] = executive_summary
    
    return report
