"""OpenAI provider implementation."""

import os
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import tiktoken
from openai import OpenAI
from openai.types.chat import ChatCompletion

from ..utils import get_logger
from ..session.models import Message, MessageRole
from .interface import AIProvider, MessageFormat, ProviderConfig, ProviderResponse


class OpenAIProvider(AIProvider):
    """Provider for OpenAI's API."""

    def __init__(self):
        """Initialize the OpenAI provider."""
        self.logger = get_logger(__name__)
        self.client = None
        self.config = None
        self.encoder = None

    @property
    def name(self) -> str:
        """Get the name of the provider."""
        return "openai"

    @property
    def available_models(self) -> List[str]:
        """Get the list of available models."""
        return [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]

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
            
            # Get API key from config or environment
            api_key = config.api_key or os.environ.get("OPENAI_API_KEY")
            
            if not api_key:
                self.logger.error("OpenAI API key not found")
                return False
            
            # Initialize the client
            self.client = OpenAI(api_key=api_key)
            
            # Initialize the encoder based on model
            try:
                model_name = self._get_encoding_name(config.model)
                self.encoder = tiktoken.encoding_for_model(model_name)
            except Exception as e:
                self.logger.warning(f"Failed to initialize encoder for model {config.model}: {str(e)}")
                # Use a safe fallback approach
                try:
                    self.encoder = tiktoken.get_encoding("cl100k_base")  # Fallback encoding
                except Exception:
                    # Last resort fallback if everything fails
                    self.logger.warning("Using simple token counting as fallback")
                    self.encoder = None
            
            self.logger.debug(f"Initialized OpenAI provider with model {config.model}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            return False

    def _get_encoding_name(self, model: str) -> str:
        """
        Get the encoding name for a model.

        Args:
            model (str): Model name

        Returns:
            str: Encoding name
        """
        # For most GPT-4 and GPT-3.5 models, cl100k_base is the right encoding
        if model.startswith(("gpt-4", "gpt-3.5")):
            return "cl100k_base"
        
        return model

    def generate_response(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """
        Generate a response from the OpenAI API.

        Args:
            messages (List[Message]): List of messages in the conversation
            system_prompt (Optional[str]): System prompt to use (default: None)
            **kwargs: Additional provider-specific parameters

        Returns:
            ProviderResponse: Response from the provider
        """
        if not self.client or not self.config:
            self.logger.error("Provider not initialized")
            return ProviderResponse(
                content="Error: Provider not initialized",
                model="unknown",
                error="Provider not initialized",
            )
        
        try:
            # Merge configuration with kwargs
            params = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }
            
            # Add top_p if set
            if self.config.top_p is not None:
                params["top_p"] = self.config.top_p
            
            # Add stop sequences if set
            if self.config.stop_sequences:
                params["stop"] = self.config.stop_sequences
            
            # Override with any kwargs
            params.update(kwargs)
            
            # Format messages for the provider API
            formatted_messages = self.format_messages(messages, system_prompt)
            
            # Record start time for latency calculation
            start_time = time.time()
            
            # Make the API call
            response = self.client.chat.completions.create(
                messages=formatted_messages,
                **params
            )
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract relevant information from the response
            finish_reason = response.choices[0].finish_reason
            content = response.choices[0].message.content or ""
            
            # Build the usage info
            usage = {}
            if hasattr(response, "usage"):
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            # Build the provider response
            return ProviderResponse(
                content=content,
                raw_response=response.model_dump(),  # Convert to dict
                model=response.model,
                finish_reason=finish_reason,
                usage=usage,
                latency_ms=latency_ms,
                request_id=response.id,
                metadata={
                    "provider": self.name,
                    "model": response.model,
                    "latency_ms": latency_ms,
                    "tokens_input": usage.get("prompt_tokens", 0),
                    "tokens_output": usage.get("completion_tokens", 0),
                }
            )
        
        except Exception as e:
            self.logger.error(f"Failed to generate response: {str(e)}")
            return ProviderResponse(
                content=f"Error generating response: {str(e)}",
                model=self.config.model if self.config else "unknown",
                error=str(e),
                metadata={
                    "provider": self.name,
                    "error": str(e),
                }
            )

    def format_messages(
        self, messages: List[Message], system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Format messages for the OpenAI API.

        Args:
            messages (List[Message]): List of messages to format
            system_prompt (Optional[str]): System prompt to include (default: None)

        Returns:
            List[Dict[str, str]]: Formatted messages for the OpenAI API
        """
        formatted = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation messages
        for message in messages:
            # Transform the role
            role = self.transform_role(message.role)
            
            # Add the message
            formatted.append({
                "role": role,
                "content": message.content
            })
        
        return formatted

    def transform_role(self, role: MessageRole) -> str:
        """
        Transform a message role to the OpenAI format.

        Args:
            role (MessageRole): Role to transform

        Returns:
            str: Transformed role
        """
        # OpenAI uses "user", "assistant", "system"
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
        Validate the API key for the provider.

        Returns:
            bool: True if the API key is valid, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Make a minimal API call to check if the key is valid
            # Using list models as it's a lightweight call
            self.client.models.list()
            return True
        
        except Exception as e:
            self.logger.error(f"API key validation failed: {str(e)}")
            return False

    def get_token_count(self, text: str) -> int:
        """
        Get the token count for a text.

        Args:
            text (str): Text to count tokens for

        Returns:
            int: Token count
        """
        if not self.encoder:
            # Fallback to approximate count if encoder not available
            return len(text) // 4  # Very rough estimate
        
        try:
            tokens = self.encoder.encode(text)
            return len(tokens)
        
        except Exception as e:
            self.logger.error(f"Failed to count tokens: {str(e)}")
            return len(text) // 4  # Fallback to approximate count
