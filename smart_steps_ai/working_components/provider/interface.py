"""Mock provider interface"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class MessageFormat:
    """Message format constants."""
    
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    BASIC = "basic"

class ProviderConfig:
    """Configuration for a provider."""
    
    def __init__(self, model, api_key=None, extra_params=None):
        self.model = model
        self.api_key = api_key
        self.extra_params = extra_params or {}

class ProviderResponse:
    """Response from a provider."""
    
    def __init__(
        self,
        content,
        raw_response=None,
        model=None,
        finish_reason=None,
        usage=None,
        latency_ms=None,
        request_id=None,
        error=None,
        metadata=None
    ):
        self.content = content
        self.raw_response = raw_response
        self.model = model
        self.finish_reason = finish_reason
        self.usage = usage or {}
        self.latency_ms = latency_ms
        self.request_id = request_id
        self.error = error
        self.metadata = metadata or {}

class AIProvider(ABC):
    """Base class for AI providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the provider."""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """Get the list of available models."""
        pass
    
    @abstractmethod
    def initialize(self, config: ProviderConfig) -> bool:
        """
        Initialize the provider with the given configuration.
        
        Args:
            config (ProviderConfig): Provider configuration
            
        Returns:
            bool: Success flag
        """
        pass
    
    @abstractmethod
    def generate_response(
        self,
        messages: List,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """
        Generate a response from the AI.
        
        Args:
            messages: List of messages
            system_prompt (Optional[str]): System prompt
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ProviderResponse: Response from the AI
        """
        pass
    
    @abstractmethod
    def format_messages(
        self, messages: List, system_prompt: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Format messages for the provider.
        
        Args:
            messages: List of messages
            system_prompt (Optional[str]): System prompt
            
        Returns:
            List[Dict[str, Any]]: Formatted messages
        """
        pass
    
    def transform_role(self, role: str) -> str:
        """
        Transform a role to the provider's format.
        
        Args:
            role (str): Role to transform
            
        Returns:
            str: Transformed role
        """
        role_mapping = {
            "system": "system",
            "user": "user",
            "client": "user",
            "assistant": "assistant",
            "ai": "assistant",
            "internal": "system",
        }
        
        return role_mapping.get(role.lower(), "user")
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate the API key for the provider.
        
        Returns:
            bool: True if the API key is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_token_count(self, text: str) -> int:
        """
        Get the token count for a text.
        
        Args:
            text (str): Text to count tokens for
            
        Returns:
            int: Token count
        """
        pass
