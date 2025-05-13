"""Test script for the analysis module."""

import os
import sys
from pathlib import Path
import datetime
import json

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Now import from src
from src.smart_steps_ai.analysis import (
    SessionAnalyzer, 
    AnalysisResult, 
    InsightCategory, 
    ProgressMetric, 
    Insight,
    ReportFormat,
    VisualizationManager,
    ReportGenerator
)

from src.smart_steps_ai.session.models import Session, Message, MessageRole, SessionState
from src.smart_steps_ai.session import SessionManager
from src.smart_steps_ai.utils import get_logger

logger = get_logger(__name__)

def create_test_session():
    """Create a test session for analysis."""
    # Create a simple test session
    session = Session(
        id="test-session-001",
        client_name="Test Client",
        persona_name="Test Therapist",
        created_at=datetime.datetime.now() - datetime.timedelta(hours=1),
        updated_at=datetime.datetime.now(),
        state=SessionState.COMPLETED,
        tags=["test", "anxiety", "first-session"],
        metadata={
            "session_goals": "Address anxiety and establish rapport",
            "client_focus": "Work-related stress"
        },
        notes="Client responded well to reflective techniques."
    )
    
    # Add some messages
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a professional therapist specializing in cognitive-behavioral therapy."),
        Message(role=MessageRole.PERSONA, content="Hello! Thank you for joining this session today. How are you feeling?"),
        Message(role=MessageRole.CLIENT, content="I've been feeling really anxious about work lately. I can't seem to focus."),
        Message(role=MessageRole.PERSONA, content="I hear that you're experiencing anxiety that's affecting your concentration at work. Can you tell me more about what you're noticing?"),
        Message(role=MessageRole.CLIENT, content="Well, I have these big deadlines coming up, and I keep procrastinating. Then I panic and feel overwhelmed."),
        Message(role=MessageRole.PERSONA, content="That sounds challenging. The cycle of procrastination and panic can be difficult to break. What have you tried so far to manage these feelings?"),
        Message(role=MessageRole.CLIENT, content="I've tried to-do lists, but I still avoid the tasks. Sometimes I just freeze up when I try to start working."),
        Message(role=MessageRole.PERSONA, content="That 'freezing up' sensation is common with anxiety. It sounds like you're experiencing some cognitive blocks when facing these tasks. Let's explore some strategies that might help break this pattern."),
        Message(role=MessageRole.CLIENT, content="I'd like that. I really need to find a way to get past this."),
        Message(role=MessageRole.PERSONA, content="One approach we could consider is breaking tasks down into smaller, more manageable steps. Would you be open to trying that with one of your current projects?"),
        Message(role=MessageRole.CLIENT, content="Yes, I think that could help. I guess part of the problem is that I see the whole project and it feels too big."),
        Message(role=MessageRole.PERSONA, content="That's great insight. Many people feel overwhelmed when looking at the entirety of a large project. Let's practice breaking one down now. What's a project you're currently working on?"),
    ]
    
    for message in messages:
        session.add_message(message)
    
    return session

def test_session_analyzer():
    """Test the SessionAnalyzer functionality."""
    print("\n===== Testing Session Analyzer =====")
    
    # Create a test session
    session = create_test_session()
    session_id = session.id
    
    # Create session manager and save the session
    session_manager = SessionManager()
    session_manager.save_session(session)
    
    # Create session analyzer
    analyzer = SessionAnalyzer(session_manager=session_manager)
    
    # Analyze the session
    print(f"Analyzing session {session_id}...")
    analysis_result = analyzer.analyze_session(session_id)
    
    if analysis_result is None:
        print("Error: Failed to analyze session")
        return False
    
    # Print the analysis results
    print(f"\nAnalysis Results:")
    print(f"Session: {analysis_result.session_id}")
    print(f"Client: {analysis_result.client_name}")
    print(f"Persona: {analysis_result.persona_name}")
    print(f"Timestamp: {analysis_result.timestamp}")
    print(f"\nSummary: {analysis_result.summary}")
    
    if analysis_result.insights:
        print(f"\nInsights ({len(analysis_result.insights)}):")
        for i, insight in enumerate(analysis_result.insights, 1):
            print(f"  {i}. {insight.category.value.capitalize()}: {insight.text} (Confidence: {insight.confidence:.2f})")
    
    if analysis_result.metrics:
        print(f"\nProgress Metrics ({len(analysis_result.metrics)}):")
        for metric in analysis_result.metrics:
            print(f"  {metric.name}: {metric.value:.1f}/{metric.max_value:.1f} - {metric.description}")
            if metric.change is not None:
                change_str = "+" if metric.change > 0 else ""
                print(f"    Change from previous: {change_str}{metric.change:.1f}")
    
    if analysis_result.themes:
        print(f"\nThemes ({len(analysis_result.themes)}):")
        for theme in analysis_result.themes:
            print(f"  - {theme}")
    
    if analysis_result.recommendations:
        print(f"\nRecommendations ({len(analysis_result.recommendations)}):")
        for i, recommendation in enumerate(analysis_result.recommendations, 1):
            print(f"  {i}. {recommendation}")
    
    if analysis_result.next_steps:
        print(f"\nNext Steps ({len(analysis_result.next_steps)}):")
        for i, step in enumerate(analysis_result.next_steps, 1):
            print(f"  {i}. {step}")
    
    return True

def test_report_generation():
    """Test generating reports in different formats."""
    print("\n===== Testing Report Generation =====")
    
    # Create a test session
    session = create_test_session()
    session_id = session.id
    
    # Create session manager and save the session
    session_manager = SessionManager()
    session_manager.save_session(session)
    
    # Create session analyzer
    analyzer = SessionAnalyzer(session_manager=session_manager)
    
    # Analyze the session
    analysis_result = analyzer.analyze_session(session_id)
    
    if analysis_result is None:
        print("Error: Failed to analyze session")
        return False
    
    # Create report generator
    report_generator = ReportGenerator()
    
    # Generate reports in different formats
    formats = [
        ReportFormat.TEXT,
        ReportFormat.MARKDOWN,
        ReportFormat.HTML,
        ReportFormat.JSON,
        ReportFormat.CSV
    ]
    
    # Create an output directory
    output_dir = Path("./output/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate reports
    print(f"Generating reports in {len(formats)} formats...")
    report_paths = report_generator.generate_reports(
        analysis_result=analysis_result,
        formats=formats,
        output_dir=output_dir,
        include_visualizations=True,
        level_of_detail="standard"
    )
    
    # Print the report paths
    print(f"\nGenerated Reports:")
    for format_name, report_path in report_paths.items():
        print(f"  {format_name}: {report_path}")
    
    return True

def test_visualization():
    """Test the visualization functionality."""
    print("\n===== Testing Visualization =====")
    
    # Create visualization manager
    visualization_manager = VisualizationManager()
    
    # Create test metrics
    metrics = [
        {
            "name": "Engagement",
            "description": "Level of client engagement in session",
            "value": 7.5,
            "previous_value": 6.0,
            "target_value": 9.0
        },
        {
            "name": "Anxiety",
            "description": "Reported anxiety level",
            "value": 8.0,
            "previous_value": 9.0,
            "target_value": 5.0
        },
        {
            "name": "Focus",
            "description": "Ability to maintain focus",
            "value": 5.5,
            "previous_value": 4.0,
            "target_value": 7.0
        }
    ]
    
    # Create test insights
    insights = [
        {
            "text": "Client shows patterns of perfectionism when discussing work projects",
            "category": "cognitive",
            "confidence": 0.85
        },
        {
            "text": "Client appears to avoid starting tasks that seem overwhelming",
            "category": "behavioral",
            "confidence": 0.9
        },
        {
            "text": "Client expresses anxiety primarily in physical symptoms like freezing up",
            "category": "emotional",
            "confidence": 0.75
        },
        {
            "text": "Client has insight into the connection between procrastination and anxiety",
            "category": "cognitive",
            "confidence": 0.8
        }
    ]
    
    # Create test themes
    themes = [
        "Work Stress",
        "Procrastination",
        "Perfectionism",
        "Anxiety",
        "Cognitive Blocks"
    ]
    
    # Create output directory
    output_dir = Path("./output/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    print(f"Generating visualizations...")
    
    # Progress chart
    progress_chart = visualization_manager.create_progress_chart(metrics)
    with open(output_dir / "progress_chart.png", "wb") as f:
        import base64
        f.write(base64.b64decode(progress_chart))
    
    # Radar chart
    radar_chart = visualization_manager.create_metrics_radar_chart(metrics)
    with open(output_dir / "radar_chart.png", "wb") as f:
        import base64
        f.write(base64.b64decode(radar_chart))
    
    # Insight category chart
    category_chart = visualization_manager.create_insight_category_chart(insights)
    with open(output_dir / "category_chart.png", "wb") as f:
        import base64
        f.write(base64.b64decode(category_chart))
    
    # Theme pie chart
    theme_chart = visualization_manager.create_theme_pie_chart(themes)
    with open(output_dir / "theme_chart.png", "wb") as f:
        import base64
        f.write(base64.b64decode(theme_chart))
    
    # Confidence distribution chart
    confidence_chart = visualization_manager.create_confidence_distribution_chart(insights)
    with open(output_dir / "confidence_chart.png", "wb") as f:
        import base64
        f.write(base64.b64decode(confidence_chart))
    
    print(f"Visualizations saved to {output_dir}")
    return True

if __name__ == "__main__":
    test_session_analyzer()
    test_report_generation()
    test_visualization()
    print("\nAll analysis module tests completed!")
