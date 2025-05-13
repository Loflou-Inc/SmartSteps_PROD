"""Mock provider for testing AI integration."""

import datetime
import json
import random
import re
import time
from typing import Dict, List, Optional, Union, Any

from ..utils import get_logger
from .interface import AIProvider, MessageFormat, ProviderConfig, ProviderResponse
from ..session.models import Message, MessageRole


class MockProvider(AIProvider):
    """
    Mock provider for testing.
    
    This class implements a mock AI provider that can be used for testing
    without requiring an actual API connection.
    """

    def __init__(self):
        """Initialize the mock provider."""
        self.logger = get_logger(__name__)
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
            "advice": [
                "Have you considered trying {suggestion}?",
                "Many people find that {suggestion} helps with this kind of situation.",
                "One approach might be to {suggestion}.",
                "In my experience, {suggestion} can be effective.",
            ],
            "validation": [
                "That's completely understandable.",
                "Your feelings are valid.",
                "I can see why you would feel that way.",
                "That sounds challenging.",
            ],
            "therapeutic": [
                "I wonder if there's a connection between {topic1} and {topic2} in your experience?",
                "How do these feelings about {topic1} relate to other areas of your life?",
                "What patterns have you noticed about when these {emotion} feelings come up?",
                "Let's explore how your past experiences with {topic1} might be influencing your current situation.",
                "Have you noticed any triggers that tend to precede these feelings of {emotion}?"
            ],
            "cbt_reframing": [
                "What evidence do you have that supports this thought about {topic1}? What evidence contradicts it?",
                "Is there another way to look at the situation with {topic1} that might be more balanced?",
                "How would you advise a friend who was thinking about {topic1} in this way?",
                "What are some alternative explanations for what happened with {topic1}?",
                "Is this thought about {topic1} helping you or holding you back?"
            ],
            "summarization": [
                "Let me make sure I understand. You're saying that {topic1} has led to feelings of {emotion}, and you're wondering about {topic2}.",
                "So far we've talked about {topic1} and how it relates to your feelings of {emotion}. Would you like to explore {topic2} as well?",
                "I hear you saying that {topic1} has been difficult. You've tried {suggestion}, but you're still feeling {emotion}.",
                "From what you've shared, it seems like {topic1} is a significant source of {emotion} for you right now."
            ],
        }
        self._available_models = [
            "mock-basic",
            "mock-advanced",
            "mock-therapist",
            "mock-analyst",
        ]
        
        # Key-response mappings for deterministic testing
        self.deterministic_responses = {
            "test_greeting": "This is a deterministic test greeting response.",
            "test_reflection": "This is a deterministic test reflection response.",
            "test_advice": "This is a deterministic test advice response.",
            "test_error": "ERROR: This is a simulated error response for testing.",
        }
        
        # Flag for deterministic mode
        self.deterministic_mode = False
        self.simulated_delay = 0.5  # Default delay in seconds
        self.error_rate = 0.0  # Probability of simulated errors

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
            
            # Extract mock-specific configuration from extra_params
            if hasattr(config, "extra_params"):
                # Set deterministic mode if specified
                if "deterministic_mode" in config.extra_params:
                    self.deterministic_mode = config.extra_params["deterministic_mode"]
                
                # Set simulated delay if specified
                if "simulated_delay" in config.extra_params:
                    self.simulated_delay = config.extra_params["simulated_delay"]
                
                # Set error rate if specified
                if "error_rate" in config.extra_params:
                    self.error_rate = config.extra_params["error_rate"]
                
                # Add any custom deterministic responses
                if "deterministic_responses" in config.extra_params:
                    self.deterministic_responses.update(config.extra_params["deterministic_responses"])
            
            # Set persona-specific behavior based on model
            if config.model == "mock-therapist":
                # Increase therapeutic responses for therapist model
                self._set_therapist_behavior()
            elif config.model == "mock-analyst":
                # Set more analytical responses
                self._set_analyst_behavior()
            
            self.logger.info(f"Initialized mock provider with model: {config.model}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize mock provider: {str(e)}")
            return False
            
    def _set_therapist_behavior(self):
        """Configure the mock provider for therapist-like responses."""
        # Add more therapeutic templates or adjust weights here
        self.therapeutic_focus = True
        
    def _set_analyst_behavior(self):
        """Configure the mock provider for analyst-like responses."""
        # Add more analytical templates or adjust weights here
        self.therapeutic_focus = False

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
            # Override config settings with any kwargs
            deterministic_mode = kwargs.get("deterministic_mode", self.deterministic_mode)
            simulated_delay = kwargs.get("simulated_delay", self.simulated_delay)
            error_rate = kwargs.get("error_rate", self.error_rate)
            
            # Simulate processing time
            if simulated_delay > 0:
                time.sleep(simulated_delay)
            
            # Simulate random errors if specified
            if error_rate > 0 and random.random() < error_rate:
                raise Exception("Simulated random error for testing")
            
            # Check for deterministic mode with a specific key
            if deterministic_mode and messages and messages[-1].role == MessageRole.CLIENT:
                last_message = messages[-1].content
                
                # Check for deterministic response keys
                for key, response in self.deterministic_responses.items():
                    if key in last_message:
                        # If "error" is in the key, simulate an error
                        if "error" in key.lower():
                            raise Exception(response)
                        
                        response_content = response
                        self.logger.debug(f"Using deterministic response for key: {key}")
                        break
                else:
                    # No deterministic key found, generate dynamic response
                    response_content = self._generate_mock_response(messages, system_prompt)
            else:
                # Generate dynamic response
                response_content = self._generate_mock_response(messages, system_prompt)
            
            # Calculate mock usage
            input_tokens = sum(len(msg.content) // 4 for msg in messages)
            output_tokens = len(response_content) // 4
            
            # Create provider response
            result = ProviderResponse(
                content=response_content,
                raw_response={
                    "model": self.config.model,
                    "content": response_content,
                    "finish_reason": "stop",
                },
                model=self.config.model,
                finish_reason="stop",
                usage={
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                },
                latency_ms=int(simulated_delay * 1000),
                request_id=f"mock-{datetime.datetime.now().timestamp()}",
                metadata={
                    "provider": self.name,
                    "model": self.config.model,
                    "deterministic_mode": deterministic_mode,
                    "tokens_input": input_tokens,
                    "tokens_output": output_tokens,
                }
            )
            
            self.logger.debug(f"Generated mock response: {response_content[:50]}...")
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to generate mock response: {str(e)}")
            return ProviderResponse(
                content=f"I apologize, but I'm unable to respond at the moment. Error: {str(e)}",
                model=self.config.model,
                error=f"Mock error: {str(e)}",
                metadata={
                    "provider": self.name,
                    "model": self.config.model,
                    "error": str(e),
                }
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
        topics = self._extract_topics(content)
        emotions = self._extract_emotions(content)
        
        # Ensure we have at least something to work with
        topic1 = random.choice(topics) if topics else "that"
        topic2 = random.choice([t for t in topics if t != topic1]) if len(topics) > 1 else "it"
        emotion = random.choice(emotions) if emotions else "concerned"
        suggestion = self._generate_suggestion(topic1)
        
        # For the therapist model, incorporate more therapeutic responses
        if hasattr(self, 'therapeutic_focus') and self.therapeutic_focus:
            response_types = []
            
            # Analyze the message to determine appropriate response types
            if "?" in content:
                response_types.extend(["reflection", "therapeutic"])
            elif any(word in content for word in ["feel", "think", "believe", "opinion", "emotion"]):
                response_types.extend(["reflection", "therapeutic", "cbt_reframing"])
            elif any(word in content for word in ["help", "advice", "suggest", "recommendation"]):
                response_types.extend(["advice", "cbt_reframing"])
            elif len(messages) > 5:  # After a few exchanges, occasionally summarize
                response_types.extend(["summarization", "therapeutic", "reflection"])
            else:
                response_types.extend(["validation", "reflection", "therapeutic"])
            
            # Select one response type randomly based on weights
            response_type = random.choice(response_types)
            
            # Generate response based on selected type
            template = random.choice(self.response_templates[response_type])
            return template.format(
                topic=topic1, 
                topic1=topic1, 
                topic2=topic2, 
                emotion=emotion, 
                suggestion=suggestion
            )
        
        # For other models, use the original logic
        if "?" in content:
            template = random.choice(self.response_templates["question"])
            return template.format(topic=topic1)
        
        elif any(word in content for word in ["feel", "think", "believe", "opinion"]):
            template = random.choice(self.response_templates["reflection"])
            return template.format(topic=topic1, emotion=emotion)
        
        elif any(word in content for word in ["help", "advice", "suggest", "recommendation"]):
            template = random.choice(self.response_templates["advice"])
            return template.format(suggestion=suggestion)
        
        else:
            # Combine validation with another template
            validation = random.choice(self.response_templates["validation"])
            
            if random.random() < 0.5:
                template = random.choice(self.response_templates["reflection"])
                return f"{validation} {template.format(topic=topic1, emotion=emotion)}"
            else:
                template = random.choice(self.response_templates["question"])
                return f"{validation} {template.format(topic=topic1)}"

    def _extract_topics(self, content: str) -> List[str]:
        """
        Extract potential topics from the content.

        Args:
            content (str): Content to extract topics from

        Returns:
            List[str]: Extracted topics
        """
        # Simple extraction of nouns and noun phrases
        # In a real implementation, this would use NLP techniques
        words = content.split()
        
        # Filter stop words
        stop_words = ["the", "and", "is", "in", "to", "a", "of", "for", "with", "on", "at"]
        filtered_words = [w for w in words if w.lower() not in stop_words and len(w) > 3]
        
        if not filtered_words:
            return ["that"]
        
        return filtered_words

    def _extract_emotions(self, content: str) -> List[str]:
        """
        Extract potential emotions from the content.

        Args:
            content (str): Content to extract emotions from

        Returns:
            List[str]: Extracted emotions
        """
        # Map of emotion keywords
        emotion_map = {
            "happy": ["happy", "joy", "glad", "excited", "pleased"],
            "sad": ["sad", "unhappy", "depressed", "down", "blue"],
            "angry": ["angry", "upset", "mad", "frustrated", "annoyed"],
            "anxious": ["anxious", "worried", "nervous", "concerned", "stress"],
            "afraid": ["afraid", "scared", "fearful", "terrified", "frightened"],
            "hopeful": ["hopeful", "optimistic", "positive", "encouraged"],
            "confused": ["confused", "uncertain", "unsure", "puzzled", "unclear"],
        }
        
        found_emotions = []
        
        for emotion, keywords in emotion_map.items():
            if any(keyword in content.lower() for keyword in keywords):
                found_emotions.append(emotion)
        
        if not found_emotions:
            return ["concerned"]
        
        return found_emotions

    def _generate_suggestion(self, topic: str) -> str:
        """
        Generate a random suggestion based on a topic.

        Args:
            topic (str): Topic to generate a suggestion for

        Returns:
            str: Generated suggestion
        """
        suggestions = [
            f"reflecting on {topic} for a few minutes each day",
            f"discussing {topic} with someone you trust",
            f"writing down your thoughts about {topic}",
            f"taking a step back to consider {topic} from different perspectives",
            f"setting specific goals related to {topic}",
            f"breaking down {topic} into smaller, manageable parts",
            f"practicing mindfulness when dealing with {topic}",
            f"seeking additional resources about {topic}",
        ]
        
        return random.choice(suggestions)

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
