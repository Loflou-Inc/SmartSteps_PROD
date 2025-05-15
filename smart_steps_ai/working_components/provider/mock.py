"""Minimal implementation of MockProvider"""

import random
import time
from typing import Dict, List, Optional, Any

from .message import Message, MessageRole
from .interface import AIProvider, ProviderConfig, ProviderResponse

class MockProvider(AIProvider):
    """
    Mock provider for testing.
    
    This class implements a mock AI provider that can be used for testing
    without requiring an actual API connection.
    """

    def __init__(self):
        """Initialize the mock provider."""
        self.config = None
        self.response_templates = {
            "greeting": [
                "Hello! How can I help you today?",
                "Good day. I'm here to assist you.",
                "Hi there! How are you feeling today?",
                "Welcome back. What would you like to talk about today?",
            ],
            "question": [
                "That's an interesting question. {topic}?",
                "I'm curious about your thoughts on {topic}?",
                "Could you tell me more about {topic}?",
                "How do you feel about {topic}?",
            ],
            "reflection": [
                "It sounds like you're feeling {emotion} about {topic}.",
                "I hear that you're experiencing {emotion} when it comes to {topic}.",
                "You seem to have strong feelings about {topic}.",
                "Let's explore why {topic} makes you feel {emotion}.",
            ],
        }
        self._available_models = [
            "mock-basic",
            "mock-advanced",
            "mock-therapist",
            "mock-analyst",
        ]
        
        # Flag for deterministic mode
        self.deterministic_mode = False
        self.simulated_delay = 0.5  # Default delay in seconds

    @property
    def name(self) -> str:
        """Get the name of the provider."""
        return "mock"

    @property
    def available_models(self) -> List[str]:
        """Get the list of available models."""
        return self._available_models

    def initialize(self, config: ProviderConfig) -> bool:
        """
        Initialize the provider with the given configuration.

        Args:
            config (ProviderConfig): Provider configuration

        Returns:
            bool: Success flag
        """
        try:
            # Store the configuration
            self.config = config
            return True
        
        except Exception as e:
            return False

    def generate_response(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """
        Generate a mock response.

        Args:
            messages (List[Message]): List of messages in the conversation
            system_prompt (Optional[str]): System prompt to use (default: None)
            **kwargs: Additional provider-specific parameters

        Returns:
            ProviderResponse: Mock response
        """
        try:
            # Simulate processing time
            if self.simulated_delay > 0:
                time.sleep(self.simulated_delay)
            
            # Generate dynamic response
            response_content = self._generate_mock_response(messages, system_prompt)
            
            # Create provider response
            result = ProviderResponse(
                content=response_content,
                model=self.config.model if self.config else "mock-basic"
            )
            
            return result
        
        except Exception as e:
            return ProviderResponse(
                content=f"I apologize, but I'm unable to respond at the moment. Error: {str(e)}",
                model=self.config.model if self.config else "mock-basic",
                error=f"Mock error: {str(e)}"
            )

    def _generate_mock_response(
        self, messages: List[Message], system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a mock response based on messages and system prompt.

        Args:
            messages (List[Message]): List of messages in the conversation
            system_prompt (Optional[str]): System prompt to use (default: None)

        Returns:
            str: Mock response
        """
        # If no messages, return a greeting
        if not messages:
            return random.choice(self.response_templates["greeting"])
        
        # Get the last message from the client
        last_client_message = None
        for message in reversed(messages):
            if message.role == MessageRole.CLIENT:
                last_client_message = message
                break
        
        if not last_client_message:
            return random.choice(self.response_templates["greeting"])
        
        # Determine the type of response based on the content
        content = last_client_message.content.lower()
        
        # Extract potential topics and emotions
        topics = content.split()
        topic = random.choice(topics) if topics else "that"
        emotions = ["happy", "sad", "confused", "anxious", "hopeful"]
        emotion = random.choice(emotions)
        
        # Simple response generation
        if "?" in content:
            template = random.choice(self.response_templates["question"])
            return template.format(topic=topic)
        else:
            template = random.choice(self.response_templates["reflection"])
            return template.format(topic=topic, emotion=emotion)

    def format_messages(
        self, messages: List[Message], system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Format messages for the mock provider.

        Args:
            messages (List[Message]): List of messages to format
            system_prompt (Optional[str]): System prompt to include (default: None)

        Returns:
            List[Dict[str, Any]]: Formatted messages
        """
        formatted_messages = []
        
        for message in messages:
            # Skip internal messages
            if message.role == MessageRole.INTERNAL:
                continue
            
            # Transform role
            role = self.transform_role(message.role)
            
            # Add the message
            formatted_messages.append({
                "role": role,
                "content": message.content,
            })
        
        return formatted_messages

    def validate_api_key(self) -> bool:
        """
        Validate the API key for the mock provider.

        Returns:
            bool: Always returns True for mock provider
        """
        return True

    def get_token_count(self, text: str) -> int:
        """
        Get a simulated token count for a text.

        Args:
            text (str): Text to count tokens for

        Returns:
            int: Simulated token count (approximately 1 token per 4 characters)
        """
        return len(text) // 4
