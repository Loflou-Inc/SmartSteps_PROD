"""Test the ProviderManager class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_steps_ai.provider import ProviderManager
from src.smart_steps_ai.provider.interface import AIProvider, ProviderConfig
from src.smart_steps_ai.session.models import Message, MessageRole


class TestProviderManager(unittest.TestCase):
    """Test the ProviderManager class."""

    def setUp(self):
        """Set up the test environment."""
        # Initialize the provider manager
        self.provider_manager = ProviderManager()
    
    def test_list_providers(self):
        """Test listing providers."""
        # List providers
        providers = self.provider_manager.list_providers()
        
        # Verify list
        self.assertTrue(len(providers) >= 2, "Provider list should contain at least 2 providers")
        self.assertIn("mock", providers, "Provider list should contain 'mock'")
        self.assertIn("anthropic", providers, "Provider list should contain 'anthropic'")
        
        print(f"Listed providers: {providers}")

    def test_get_mock_provider(self):
        """Test getting the mock provider."""
        # Get the mock provider
        provider = self.provider_manager.get_provider("mock")
        
        # Verify provider
        self.assertIsNotNone(provider, "Mock provider is None")
        self.assertEqual(provider.name, "mock")
        
        # Check available models
        models = provider.available_models
        self.assertTrue(len(models) > 0, "Provider should have available models")
        
        print(f"Got mock provider: {provider.name}")
        print(f"Available models: {models}")

    def test_mock_provider_response(self):
        """Test generating a response from the mock provider."""
        # Get the mock provider
        provider = self.provider_manager.get_provider("mock")
        self.assertIsNotNone(provider, "Mock provider is None")
        
        # Create test messages
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            Message(role=MessageRole.CLIENT, content="Hello, how are you?"),
            Message(role=MessageRole.ASSISTANT, content="I'm doing well, thank you. How can I help you today?"),
            Message(role=MessageRole.CLIENT, content="I'm feeling anxious about my upcoming presentation."),
        ]
        
        # Generate a response
        response = provider.generate_response(messages)
        
        # Verify response
        self.assertIsNotNone(response, "Response is None")
        self.assertGreater(len(response.content), 0, "Response content is empty")
        self.assertEqual(response.model, provider.config.model)
        self.assertIsNone(response.error, "Response has an error")
        
        print(f"Generated response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Token usage: {response.usage}")

    def test_anthropic_provider_initialization(self):
        """Test initializing the Anthropic provider."""
        # Skip if no API key
        if not os.environ.get("ANTHROPIC_API_KEY"):
            self.skipTest("Anthropic API key not available")
        
        # Get the Anthropic provider
        provider = self.provider_manager.get_provider("anthropic")
        
        # Verify provider
        self.assertIsNotNone(provider, "Anthropic provider is None")
        self.assertEqual(provider.name, "anthropic")
        
        # Check available models
        models = provider.available_models
        self.assertTrue(len(models) > 0, "Provider should have available models")
        
        print(f"Got Anthropic provider: {provider.name}")
        print(f"Available models: {models}")


if __name__ == "__main__":
    unittest.main()
