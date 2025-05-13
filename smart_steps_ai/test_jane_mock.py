"""Simple test for the Jane mock provider."""

import sys
from pathlib import Path

# Add the project root to the Python path
project_dir = Path(r"G:\My Drive\Deftech\SmartSteps\smart_steps_ai")
sys.path.insert(0, str(project_dir))

from src.smart_steps_ai.provider.jane_mock import JaneMockProvider
from src.smart_steps_ai.provider.interface import ProviderConfig, MessageFormat
from src.smart_steps_ai.session.models import Message, MessageRole

def test_jane_mock():
    """Test the Jane mock provider in isolation."""
    print("\n===== Testing Jane Mock Provider =====")
    
    # Create provider
    provider = JaneMockProvider()
    
    # Initialize it
    config = ProviderConfig(
        model="mock-jane",
        max_tokens=500,
        temperature=0.7,
        message_format=MessageFormat.TEXT
    )
    
    provider.initialize(config)
    
    # Define test messages
    test_queries = [
        "Can you tell me about yourself?",
        "Can you tell me about the abuse you suffered as a child?",
        "How did your therapy journey begin?",
        "What was your educational background like?",
        "Tell me about your career and work experience."
    ]
    
    # Test each query
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Create a message list
        messages = [
            Message(
                role=MessageRole.SYSTEM,
                content="You are a professional therapist with a background in trauma."
            ),
            Message(
                role=MessageRole.CLIENT,
                content=query
            )
        ]
        
        # Get a response
        response = provider.generate_response(messages)
        
        # Print response
        print(f"Response: {response.content}")
        print(f"Is first person? {'I ' in response.content or 'my ' in response.content}")
        
    print("\nJane Mock Provider test completed!")

if __name__ == "__main__":
    test_jane_mock()
