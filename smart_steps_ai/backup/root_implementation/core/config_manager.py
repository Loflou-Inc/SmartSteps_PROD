"""
Configuration management for the Smart Steps AI module.
"""

import os
import json
from typing import Any, Dict, Optional, List, Union
from pathlib import Path

from ..utils.logging import get_logger

# Get logger
logger = get_logger("core.config_manager")

# Default configuration directory is in the project root
DEFAULT_CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config"
)

# Default configuration file
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "default_config.json")

class ConfigManager:
    """
    Configuration manager for the Smart Steps AI module.
    
    Handles loading, saving, and accessing configuration settings.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file. Defaults to config/default_config.json
                in the project root.
        """
        self.config_file = config_file or DEFAULT_CONFIG_FILE
        self.config_dir = os.path.dirname(self.config_file)
        
        # Create config directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        logger.debug(f"Initialized ConfigManager with config file: {self.config_file}")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            The configuration as a dictionary.
        """
        # Check if the config file exists
        if not os.path.exists(self.config_file):
            logger.warning(f"Configuration file not found: {self.config_file}")
            logger.info("Creating default configuration")
            self.create_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.debug(f"Loaded configuration from {self.config_file}")
                return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            return self.get_default_config()
    
    def create_default_config(self) -> None:
        """
        Create a default configuration file.
        """
        default_config = self.get_default_config()
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
                logger.info(f"Created default configuration file: {self.config_file}")
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.
        
        Returns:
            The default configuration as a dictionary.
        """
        return {
            "general": {
                "app_name": "Smart Steps AI",
                "version": "0.1.0",
                "data_dir": os.path.join(os.path.dirname(self.config_dir), "data"),
                "logs_dir": os.path.join(os.path.dirname(self.config_dir), "logs"),
                "log_level": "INFO"
            },
            "ai_provider": {
                "default_provider": "anthropic",
                "anthropic": {
                    "model": "claude-3-opus-20240229",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "openai": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                "local_llm": {
                    "model_path": "",
                    "context_size": 4096,
                    "temperature": 0.7
                }
            },
            "persona": {
                "default_persona": "professional_therapist",
                "personas_dir": os.path.join(self.config_dir, "personas")
            },
            "session": {
                "session_timeout": 3600,  # 1 hour
                "max_session_history": 100,
                "sessions_dir": os.path.join(os.path.dirname(self.config_dir), "data", "sessions")
            },
            "memory": {
                "memory_dir": os.path.join(os.path.dirname(self.config_dir), "data", "memory"),
                "max_relevant_memories": 5
            },
            "analysis": {
                "default_analysis_type": "full",
                "reports_dir": os.path.join(os.path.dirname(self.config_dir), "data", "analytics"),
                "templates_dir": os.path.join(self.config_dir, "templates")
            }
        }
    
    def save_config(self) -> None:
        """
        Save the current configuration to file.
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
                logger.debug(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The key to get, in dot notation (e.g., "ai_provider.anthropic.model").
                If None, returns the entire configuration.
            default: The default value to return if the key is not found.
            
        Returns:
            The configuration value, or the default if not found.
        """
        if key is None:
            return self.config
        
        # Split the key by dots
        parts = key.split('.')
        
        # Navigate through the config
        value = self.config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                logger.debug(f"Configuration key not found: {key}, returning default: {default}")
                return default
        
        return value
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The key to set, in dot notation (e.g., "ai_provider.anthropic.model").
            value: The value to set.
        """
        # Split the key by dots
        parts = key.split('.')
        
        # Navigate through the config
        config = self.config
        for i, part in enumerate(parts[:-1]):
            if part not in config:
                config[part] = {}
            config = config[part]
        
        # Set the value
        config[parts[-1]] = value
        
        # Save the configuration
        self.save_config()
        
        logger.debug(f"Set configuration key {key} to {value}")
    
    def get_path(self, key: str, create: bool = True) -> Optional[str]:
        """
        Get a path from the configuration and ensure it exists.
        
        Args:
            key: The key to get, in dot notation (e.g., "general.data_dir").
            create: Whether to create the directory if it doesn't exist.
            
        Returns:
            The path, or None if not found.
        """
        path = self.get_config(key)
        if path is None:
            logger.warning(f"Path not found in configuration: {key}")
            return None
        
        # Create the directory if it doesn't exist
        if create and not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                logger.debug(f"Created directory: {path}")
            except Exception as e:
                logger.error(f"Error creating directory {path}: {e}")
                return None
        
        return path
