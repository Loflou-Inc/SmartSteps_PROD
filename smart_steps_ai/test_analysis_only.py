"""Test script to verify session analysis is working properly."""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set testing environment variables
os.environ["SMART_STEPS_APP_ENVIRONMENT"] = "testing"
os.environ["SMART_STEPS_PROVIDERS_USE_MOCK"] = "true"
os.environ["SMART_STEPS_PROVIDERS_MOCK_ENABLED"] = "true"

# Import the necessary modules
from src.smart_steps_ai.session import SessionManager, MessageRole
from src.smart_steps_ai.analysis import SessionAnalyzer

def test_session_analysis():
    """Test the session analysis functionality."""
    print("Testing session analysis...")
    
    # Create a session manager
    session_manager = SessionManager()
    
    # Create a session
    session = session_manager.create_session(
        client_name="Test Client",
        persona_name="test_persona"
    )
    
    print(f"Created test session: {session.id}")
    
    # Add some messages
    session.add_message(
        role=MessageRole.SYSTEM,
        content="You are a professional therapist."
    )
    
    session.add_message(
        role=MessageRole.ASSISTANT,
        content="Hello! How are you feeling today?"
    )
    
    session.add_message(
        role=MessageRole.CLIENT,
        content="I've been feeling anxious about work lately. I can't seem to focus."
    )
    
    # Save the session
    session_manager.save_session(session)
    print(f"Saved session with {session.messages_count} messages")
    
    # Create an analyzer
    analyzer = SessionAnalyzer(session_manager=session_manager)
    
    # Analyze the session
    print(f"Analyzing session {session.id}...")
    analysis_result = analyzer.analyze_session(session.id)
    
    # Check if analysis was successful
    if analysis_result:
        print("Session analysis successful!")
        print(f"- Summary: {analysis_result.summary[:50]}...")
        print(f"- Insights: {len(analysis_result.insights)}")
        print(f"- Metrics: {len(analysis_result.metrics)}")
        print(f"- Themes: {len(analysis_result.themes)}")
        print(f"- Recommendations: {len(analysis_result.recommendations)}")
        return True
    else:
        print("Session analysis failed!")
        return False

if __name__ == "__main__":
    success = test_session_analysis()
    sys.exit(0 if success else 1)
