"""Test script for the enhanced Mock Provider."""

import sys
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import provider components
from src.smart_steps_ai.provider.interface import ProviderConfig, MessageFormat
from src.smart_steps_ai.provider.mock import MockProvider
from src.smart_steps_ai.session.models import Message, MessageRole

def test_mock_provider():
    """Test basic mock provider functionality."""
    print("\n===== Testing Basic Mock Provider =====")
    
    # Create mock provider
    mock_provider = MockProvider()
    
    # Initialize with default configuration
    config = ProviderConfig(
        model="mock-basic",
        max_tokens=500,
        temperature=0.7,
        message_format=MessageFormat.TEXT
    )
    
    mock_provider.initialize(config)
    print(f"Provider name: {mock_provider.name}")
    print(f"Available models: {mock_provider.available_models}")
    
    # Create test messages
    messages = [
        Message(
            role=MessageRole.SYSTEM,
            content="You are a helpful, professional assistant."
        ),
        Message(
            role=MessageRole.CLIENT,
            content="I've been feeling anxious lately. Can you help me understand what might be causing this?"
        )
    ]
    
    # Generate a response
    print("\nGenerating response...")
    start_time = time.time()
    response = mock_provider.generate_response(messages)
    elapsed_time = time.time() - start_time
    
    print(f"Response generated in {elapsed_time:.2f} seconds")
    print(f"Model: {response.model}")
    print(f"Response content: {response.content}")
    
    return True

def test_therapist_mock():
    """Test the therapist-specific mock provider."""
    print("\n===== Testing Therapist Mock Provider =====")
    
    # Create mock provider
    mock_provider = MockProvider()
    
    # Initialize with therapist configuration
    config = ProviderConfig(
        model="mock-therapist",
        max_tokens=500,
        temperature=0.7,
        message_format=MessageFormat.TEXT
    )
    
    mock_provider.initialize(config)
    
    # Create test messages for different scenarios
    test_scenarios = [
        "I've been feeling anxious about work lately.",
        "Why do I keep having these negative thoughts?",
        "I need some advice on dealing with my relationship problems.",
        "I don't know why I feel so sad all the time."
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\nScenario {i+1}: {scenario}")
        
        messages = [
            Message(
                role=MessageRole.SYSTEM,
                content="You are a professional therapist providing support and guidance."
            ),
            Message(
                role=MessageRole.CLIENT,
                content=scenario
            )
        ]
        
        # Generate a response
        response = mock_provider.generate_response(messages)
        print(f"Response: {response.content}")
    
    return True

def test_deterministic_responses():
    """Test deterministic responses for automated testing."""
    print("\n===== Testing Deterministic Responses =====")
    
    # Create mock provider with deterministic mode
    mock_provider = MockProvider()
    
    # Initialize with deterministic configuration
    config = ProviderConfig(
        model="mock-basic",
        max_tokens=500,
        temperature=0.7,
        message_format=MessageFormat.TEXT,
        extra_params={
            "deterministic_mode": True,
            "simulated_delay": 0.1,  # Fast responses for testing
            "deterministic_responses": {
                "specific_pattern": "This is a custom deterministic response for testing."
            }
        }
    )
    
    mock_provider.initialize(config)
    
    # Test built-in deterministic keys
    test_keys = [
        "test_greeting",
        "test_reflection",
        "test_advice",
        "specific_pattern"  # Our custom one
    ]
    
    for key in test_keys:
        print(f"\nTesting deterministic key: {key}")
        
        messages = [
            Message(
                role=MessageRole.SYSTEM,
                content="You are a helpful assistant."
            ),
            Message(
                role=MessageRole.CLIENT,
                content=f"This is a test message containing {key}"
            )
        ]
        
        # Generate a response
        response = mock_provider.generate_response(messages)
        print(f"Response: {response.content}")
    
    # Test error simulation
    print("\nTesting error simulation:")
    
    messages = [
        Message(
            role=MessageRole.SYSTEM,
            content="You are a helpful assistant."
        ),
        Message(
            role=MessageRole.CLIENT,
            content="This is a test message containing test_error"
        )
    ]
    
    # Generate a response
    response = mock_provider.generate_response(messages)
    print(f"Error response: {response.content}")
    print(f"Error metadata: {response.metadata}")
    
    return True

if __name__ == "__main__":
    test_mock_provider()
    test_therapist_mock()
    test_deterministic_responses()
    print("\nAll mock provider tests completed successfully!")
