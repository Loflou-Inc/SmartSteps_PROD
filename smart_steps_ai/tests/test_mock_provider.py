"""Test the MockProvider class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_steps_ai.provider.mock import MockProvider
from src.smart_steps_ai.provider.interface import ProviderConfig
from src.smart_steps_ai.session.models import Message, MessageRole


class TestMockProvider(unittest.TestCase):
    """Test the MockProvider class."""

    def setUp(self):
        """Set up the test environment."""
        # Initialize the mock provider
        self.provider = MockProvider()
        
        # Initialize with configuration
        self.config = ProviderConfig(
            model="mock-basic",
            max_tokens=100,
            temperature=0.7,
        )
        
        self.initialized = self.provider.initialize(self.config)

    def test_initialization(self):
        """Test provider initialization."""
        self.assertTrue(self.initialized, "Provider initialization failed")
        self.assertEqual(self.provider.name, "mock")
        self.assertIsNotNone(self.provider.config, "Provider config is None")
        
        print(f"Initialized mock provider with model: {self.config.model}")

    def test_available_models(self):
        """Test getting available models."""
        models = self.provider.available_models
        
        # Verify models
        self.assertTrue(len(models) > 0, "Provider should have available models")
        self.assertIn("mock-basic", models)
        self.assertIn("mock-therapist", models)
        
        print(f"Available models: {models}")

    def test_response_generation(self):
        """Test generating responses with different message types."""
        # Test with a question
        question_messages = [
            Message(role=MessageRole.CLIENT, content="What do you think about mindfulness?"),
        ]
        
        question_response = self.provider.generate_response(question_messages)
        self.assertIsNotNone(question_response, "Response is None")
        self.assertGreater(len(question_response.content), 0, "Response content is empty")
        
        print(f"Question response: {question_response.content}")
        
        # Test with a feeling statement
        feeling_messages = [
            Message(role=MessageRole.CLIENT, content="I feel anxious about my job interview tomorrow."),
        ]
        
        feeling_response = self.provider.generate_response(feeling_messages)
        self.assertIsNotNone(feeling_response, "Response is None")
        self.assertGreater(len(feeling_response.content), 0, "Response content is empty")
        
        print(f"Feeling response: {feeling_response.content}")
        
        # Test with a request for advice
        advice_messages = [
            Message(role=MessageRole.CLIENT, content="Can you suggest ways to improve my communication skills?"),
        ]
        
        advice_response = self.provider.generate_response(advice_messages)
        self.assertIsNotNone(advice_response, "Response is None")
        self.assertGreater(len(advice_response.content), 0, "Response content is empty")
        
        print(f"Advice response: {advice_response.content}")

    def test_conversation_flow(self):
        """Test a conversation flow with the mock provider."""
        # Create a conversation
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a supportive therapist."),
            Message(role=MessageRole.CLIENT, content="Hello, I'm here for my first session."),
            Message(role=MessageRole.ASSISTANT, content="Welcome! I'm glad you're here. How can I help you today?"),
            Message(role=MessageRole.CLIENT, content="I've been feeling overwhelmed with work lately."),
            Message(role=MessageRole.ASSISTANT, content="I'm sorry to hear that you're feeling overwhelmed. Can you tell me more about what's been happening at work?"),
            Message(role=MessageRole.CLIENT, content="I have too many projects and not enough time."),
        ]
        
        # Generate response
        response = self.provider.generate_response(messages)
        
        # Verify response
        self.assertIsNotNone(response, "Response is None")
        self.assertGreater(len(response.content), 0, "Response content is empty")
        self.assertEqual(response.model, self.config.model)
        
        print(f"Conversation response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Token usage: {response.usage}")

    def test_token_counting(self):
        """Test token counting."""
        # Test a simple string
        text = "This is a test message to count tokens."
        count = self.provider.get_token_count(text)
        
        # Verify token count (should be approximately 1 token per 4 characters)
        expected_count = len(text) // 4
        self.assertEqual(count, expected_count, "Token count should match expected count")
        
        print(f"Token count for '{text}': {count}")


if __name__ == "__main__":
    unittest.main()
