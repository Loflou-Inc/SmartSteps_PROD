"""Test the AnthropicProvider class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_steps_ai.provider.anthropic import AnthropicProvider
from src.smart_steps_ai.provider.interface import ProviderConfig
from src.smart_steps_ai.session.models import Message, MessageRole


class TestAnthropicProvider(unittest.TestCase):
    """Test the AnthropicProvider class."""

    def setUp(self):
        """Set up the test environment."""
        # Initialize the Anthropic provider
        self.provider = AnthropicProvider()
        
        # Skip if no API key
        if not os.environ.get("ANTHROPIC_API_KEY"):
            self.skipTest("Anthropic API key not available")
        
        # Initialize with configuration
        self.config = ProviderConfig(
            model="claude-3-haiku-20240307",  # Use a smaller, faster model for testing
            max_tokens=100,
            temperature=0.7,
        )
        
        self.initialized = self.provider.initialize(self.config)
        if not self.initialized:
            self.skipTest("Failed to initialize Anthropic provider")

    def test_initialization(self):
        """Test provider initialization."""
        self.assertTrue(self.initialized, "Provider initialization failed")
        self.assertIsNotNone(self.provider.client, "Anthropic client is None")
        self.assertEqual(self.provider.name, "anthropic")
        
        print(f"Initialized Anthropic provider with model: {self.config.model}")

    def test_format_messages(self):
        """Test formatting messages for the Anthropic API."""
        # Create test messages
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            Message(role=MessageRole.CLIENT, content="Hello, how are you?"),
            Message(role=MessageRole.ASSISTANT, content="I'm doing well, thank you. How can I help you today?"),
            Message(role=MessageRole.CLIENT, content="Tell me about the weather."),
            Message(role=MessageRole.INTERNAL, content="This is an internal message that should be skipped."),
        ]
        
        # Format messages
        formatted = self.provider.format_messages(messages)
        
        # Verify formatting
        self.assertEqual(len(formatted), 4, "Should have 4 formatted messages (internal message skipped)")
        
        # Check the roles were transformed correctly
        self.assertEqual(formatted[0]["role"], "system")
        self.assertEqual(formatted[1]["role"], "user")
        self.assertEqual(formatted[2]["role"], "assistant")
        self.assertEqual(formatted[3]["role"], "user")
        
        print(f"Formatted messages: {formatted}")

    def test_token_counting(self):
        """Test token counting."""
        # Test a simple string
        text = "This is a test message to count tokens."
        count = self.provider.get_token_count(text)
        
        # Verify token count
        self.assertGreater(count, 0, "Token count should be greater than 0")
        
        print(f"Token count for '{text}': {count}")

    def test_anthropic_response(self):
        """Test generating a response from the Anthropic API."""
        # Create test messages
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            Message(role=MessageRole.CLIENT, content="What's 2+2?"),
        ]
        
        # Generate a response
        response = self.provider.generate_response(messages)
        
        # Verify response
        self.assertIsNotNone(response, "Response is None")
        self.assertGreater(len(response.content), 0, "Response content is empty")
        self.assertEqual(response.model, self.config.model)
        self.assertIsNone(response.error, "Response has an error")
        
        print(f"Generated response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Token usage: {response.usage}")


if __name__ == "__main__":
    unittest.main()
