"""Provider manager for the Smart Steps AI module."""

import importlib
from typing import Dict, List, Optional, Type, Union

from ..config import get_config_manager
from ..utils import get_logger
from .interface import AIProvider, ProviderConfig


class ProviderManager:
    """
    Manager for AI providers.
    
    This class handles registration, initialization, and access to AI providers
    used for generating responses in sessions.
    """

    def __init__(self):
        """Initialize the provider manager."""
        self.logger = get_logger(__name__)
        self.config = get_config_manager().get()
        
        # Initialize provider registry
        self.providers: Dict[str, Type[AIProvider]] = {}
        
        # Initialize provider instances
        self.provider_instances: Dict[str, AIProvider] = {}
        
        # Register default providers
        self._register_default_providers()
        
        self.logger.debug("Initialized provider manager")

    def _register_default_providers(self) -> None:
        """Register default providers."""
        try:
            # Import providers dynamically to avoid circular imports
            from .anthropic import AnthropicProvider
            from .mock import MockProvider
            from .openai import OpenAIProvider
            from .jane_mock import JaneMockProvider
            
            # Register providers
            self.register_provider("anthropic", AnthropicProvider)
            self.register_provider("mock", MockProvider)
            self.register_provider("openai", OpenAIProvider)
            self.register_provider("jane_mock", JaneMockProvider)
            
            self.logger.debug("Registered default providers: anthropic, mock, openai, jane_mock")
        except ImportError as e:
            self.logger.warning(f"Failed to import default providers: {str(e)}")

    def register_provider(self, name: str, provider_class: Type[AIProvider]) -> bool:
        """
        Register a provider.

        Args:
            name (str): Name of the provider
            provider_class (Type[AIProvider]): Provider class

        Returns:
            bool: Success flag
        """
        try:
            if name in self.providers:
                self.logger.warning(f"Provider already registered: {name}")
                return False
            
            self.providers[name] = provider_class
            self.logger.debug(f"Registered provider: {name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to register provider {name}: {str(e)}")
            return False

    def unregister_provider(self, name: str) -> bool:
        """
        Unregister a provider.

        Args:
            name (str): Name of the provider

        Returns:
            bool: Success flag
        """
        try:
            if name not in self.providers:
                self.logger.warning(f"Provider not registered: {name}")
                return False
            
            # Remove provider class and instance if it exists
            del self.providers[name]
            
            if name in self.provider_instances:
                del self.provider_instances[name]
            
            self.logger.debug(f"Unregistered provider: {name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to unregister provider {name}: {str(e)}")
            return False

    def get_provider(self, name: Optional[str] = None) -> Optional[AIProvider]:
        """
        Get a provider instance.

        Args:
            name (Optional[str]): Name of the provider (default: None)
                If None, uses the default provider from the configuration

        Returns:
            Optional[AIProvider]: Provider instance or None if not found
        """
        try:
            # Use the default provider if name is not specified
            if name is None:
                name = self.config.ai.provider
            
            # Check if the provider is already instantiated
            if name in self.provider_instances:
                return self.provider_instances[name]
            
            # Check if the provider is registered
            if name not in self.providers:
                self.logger.warning(f"Provider not registered: {name}")
                return None
            
            # Create provider instance
            provider_class = self.providers[name]
            provider = provider_class()
            
            # Initialize the provider with configuration
            provider_config = self._get_provider_config(name)
            
            if not provider.initialize(provider_config):
                self.logger.error(f"Failed to initialize provider: {name}")
                return None
            
            # Store the instance
            self.provider_instances[name] = provider
            
            self.logger.debug(f"Created and initialized provider instance: {name}")
            return provider
        
        except Exception as e:
            self.logger.error(f"Failed to get provider {name}: {str(e)}")
            return None

    def load_provider_dynamically(self, module_path: str, class_name: str, name: str) -> bool:
        """
        Load a provider dynamically.

        Args:
            module_path (str): Path to the module
            class_name (str): Name of the provider class
            name (str): Name to register the provider under

        Returns:
            bool: Success flag
        """
        try:
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the provider class
            provider_class = getattr(module, class_name)
            
            # Validate that it's an AIProvider
            if not issubclass(provider_class, AIProvider):
                self.logger.error(f"Class {class_name} is not a subclass of AIProvider")
                return False
            
            # Register the provider
            return self.register_provider(name, provider_class)
        
        except ImportError as e:
            self.logger.error(f"Failed to import module {module_path}: {str(e)}")
            return False
        
        except AttributeError as e:
            self.logger.error(f"Class {class_name} not found in module {module_path}: {str(e)}")
            return False
        
        except Exception as e:
            self.logger.error(f"Failed to load provider {name}: {str(e)}")
            return False

    def list_providers(self) -> List[str]:
        """
        List all registered providers.

        Returns:
            List[str]: List of provider names
        """
        return list(self.providers.keys())

    def _get_provider_config(self, provider_name: str) -> ProviderConfig:
        """
        Get configuration for a provider.

        Args:
            provider_name (str): Name of the provider

        Returns:
            ProviderConfig: Provider configuration
        """
        # Get AI configuration
        ai_config = self.config.ai
        
        # Create a basic provider configuration
        provider_config = ProviderConfig(
            model=ai_config.default_model,
            max_tokens=ai_config.max_tokens,
            temperature=ai_config.temperature,
        )
        
        # Add API key from environment variables if available
        import os
        
        if provider_name == "anthropic":
            # Try to get from environment
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            
            if api_key:
                provider_config.api_key = api_key
                self.logger.debug("Using Anthropic API key from environment")
                
        elif provider_name == "openai":
            # Try to get from environment
            api_key = os.environ.get("OPENAI_API_KEY")
            
            if api_key:
                provider_config.api_key = api_key
                self.logger.debug("Using OpenAI API key from environment")
        
        # Add any additional provider-specific configuration
        # This can be expanded as needed for other providers
        
        return provider_config
