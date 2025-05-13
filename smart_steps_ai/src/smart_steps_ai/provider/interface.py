"""Interface definitions for AI providers."""

import abc
import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, Field

from ..session.models import Message, MessageRole


class MessageFormat(str, Enum):
    """Format of messages for AI providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    TEXT = "text"
    JSON = "json"
    CUSTOM = "custom"


class ProviderConfig(BaseModel):
    """Configuration for an AI provider."""

    api_key: Optional[str] = None
    model: str
    max_tokens: int = 1000
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    stop_sequences: List[str] = Field(default_factory=list)
    message_format: MessageFormat = MessageFormat.TEXT
    system_prompt_template: Optional[str] = None
    extra_params: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic config."""
        extra = "allow"
        arbitrary_types_allowed = True


class ProviderResponse(BaseModel):
    """Response from an AI provider."""

    content: str
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    model: str
    finish_reason: Optional[str] = None
    usage: Dict[str, int] = Field(default_factory=dict)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    latency_ms: Optional[int] = None
    request_id: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIProvider(abc.ABC):
    """Abstract base class for AI providers."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Get the name of the provider."""
        pass

    @property
    @abc.abstractmethod
    def available_models(self) -> List[str]:
        """Get the list of available models."""
        pass

    @abc.abstractmethod
    def initialize(self, config: ProviderConfig) -> bool:
        """
        Initialize the provider with the given configuration.

        Args:
            config (ProviderConfig): Provider configuration

        Returns:
            bool: Success flag
        """
        pass

    @abc.abstractmethod
    def generate_response(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """
        Generate a response from the AI provider.

        Args:
            messages (List[Message]): List of messages in the conversation
            system_prompt (Optional[str]): System prompt to use (default: None)
            **kwargs: Additional provider-specific parameters

        Returns:
            ProviderResponse: Response from the provider
        """
        pass

    @abc.abstractmethod
    def format_messages(
        self, messages: List[Message], system_prompt: Optional[str] = None
    ) -> Any:
        """
        Format messages for the provider's API.

        Args:
            messages (List[Message]): List of messages to format
            system_prompt (Optional[str]): System prompt to include (default: None)

        Returns:
            Any: Formatted messages for the provider
        """
        pass

    @abc.abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate the API key for the provider.

        Returns:
            bool: True if the API key is valid, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Get the token count for a text.

        Args:
            text (str): Text to count tokens for

        Returns:
            int: Token count
        """
        pass

    def transform_role(self, role: MessageRole) -> str:
        """
        Transform a message role to the provider's format.

        Args:
            role (MessageRole): Role to transform

        Returns:
            str: Transformed role
        """
        # Default mapping - can be overridden by specific providers
        if role == MessageRole.SYSTEM:
            return "system"
        elif role == MessageRole.ASSISTANT:
            return "assistant"
        elif role == MessageRole.CLIENT:
            return "user"
        else:
            return "user"  # Default fallback
