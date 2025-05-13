"""Anthropic provider for AI integration."""

import datetime
import json
import os
import time
from typing import Dict, List, Optional, Union, Any

import anthropic

from ..utils import get_logger
from .interface import AIProvider, MessageFormat, ProviderConfig, ProviderResponse
from ..session.models import Message, MessageRole


class AnthropicProvider(AIProvider):
    """
    Provider for Anthropic's Claude API.
    
    This class implements the AIProvider interface for Anthropic's Claude models,
    allowing integration with Claude for generating responses.
    """

    def __init__(self):
        """Initialize the Anthropic provider."""
        self.logger = get_logger(__name__)
        self.client = None
        self.config = None
        self._available_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20240620",
            "claude-3-5-sonnet-20240620-collection",
            "claude-3-5-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2",
        ]

    @property
    def name(self) -> str:
        """Get the name of the provider."""
        return "anthropic"

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
            if not config.api_key:
                # Try to get API key from environment
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                
                if not api_key:
                    self.logger.error("Anthropic API key not provided")
                    return False
                
                config.api_key = api_key
            
            # Create the Anthropic client
            self.client = anthropic.Anthropic(api_key=config.api_key)
            
            # Store the configuration
            self.config = config
            
            # Validate API key
            if not self.validate_api_key():
                self.logger.error("Invalid Anthropic API key")
                return False
            
            self.logger.info(f"Initialized Anthropic provider with model: {config.model}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic provider: {str(e)}")
            return False

    def generate_response(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """
        Generate a response from the Anthropic API.

        Args:
            messages (List[Message]): List of messages in the conversation
            system_prompt (Optional[str]): System prompt to use (default: None)
            **kwargs: Additional provider-specific parameters

        Returns:
            ProviderResponse: Response from the provider
        """
        try:
            if not self.client:
                raise ValueError("Anthropic provider not initialized")
            
            # Format messages for the API
            formatted_messages = self.format_messages(messages, system_prompt)
            
            # Prepare parameters
            params = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": formatted_messages,
            }
            
            # Add system prompt if provided
            if system_prompt:
                params["system"] = system_prompt
            
            # Add stop sequences if provided
            if self.config.stop_sequences:
                params["stop_sequences"] = self.config.stop_sequences
            
            # Add top_p if provided
            if self.config.top_p is not None:
                params["top_p"] = self.config.top_p
            
            # Add any additional parameters from kwargs
            params.update(kwargs)
            
            # Record start time
            start_time = time.time()
            
            # Make the API call
            response = self.client.messages.create(**params)
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Create provider response
            result = ProviderResponse(
                content=response.content[0].text,
                raw_response=response.model_dump(),
                model=response.model,
                finish_reason=response.stop_reason,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                latency_ms=latency_ms,
                request_id=response.id,
            )
            
            self.logger.debug(f"Generated response from Anthropic API: {response.stop_reason}")
            return result
        
        except anthropic.APIError as e:
            self.logger.error(f"Anthropic API error: {str(e)}")
            return ProviderResponse(
                content="",
                model=self.config.model,
                error=f"Anthropic API error: {str(e)}",
            )
        
        except Exception as e:
            self.logger.error(f"Failed to generate response from Anthropic API: {str(e)}")
            return ProviderResponse(
                content="",
                model=self.config.model,
                error=f"Failed to generate response: {str(e)}",
            )

    def format_messages(
        self, messages: List[Message], system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Format messages for the Anthropic API.

        Args:
            messages (List[Message]): List of messages to format
            system_prompt (Optional[str]): System prompt to include (default: None)

        Returns:
            List[Dict[str, Any]]: Formatted messages for the Anthropic API
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

    def transform_role(self, role: MessageRole) -> str:
        """
        Transform a message role to the Anthropic API format.

        Args:
            role (MessageRole): Role to transform

        Returns:
            str: Transformed role
        """
        if role == MessageRole.SYSTEM:
            return "system"
        elif role == MessageRole.ASSISTANT:
            return "assistant"
        elif role == MessageRole.CLIENT:
            return "user"
        else:
            return "user"  # Default fallback

    def validate_api_key(self) -> bool:
        """
        Validate the API key for Anthropic.

        Returns:
            bool: True if the API key is valid, False otherwise
        """
        try:
            if not self.client:
                return False
            
            # Make a simple API call to validate the key
            # Using a minimal request to minimize token usage
            self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}],
                temperature=0.0,
            )
            
            return True
        
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return False

    def get_token_count(self, text: str) -> int:
        """
        Get the token count for a text using Anthropic's tokenizer.

        Args:
            text (str): Text to count tokens for

        Returns:
            int: Token count
        """
        try:
            if not self.client:
                raise ValueError("Anthropic provider not initialized")
            
            # Use Anthropic's token counting method
            count = anthropic.count_tokens(text)
            return count
        
        except Exception as e:
            self.logger.error(f"Failed to count tokens: {str(e)}")
            # Fallback to a simple estimation (1 token ≈ 4 characters)
            return len(text) // 4
