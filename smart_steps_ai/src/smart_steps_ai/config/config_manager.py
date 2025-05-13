"""Configuration manager for the Smart Steps AI module."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..utils import get_logger, load_dotenv, get_env
from .models import Config


class ConfigManager:
    """
    Configuration manager for loading and accessing application settings.
    
    This class handles loading configuration from various sources (default files,
    custom files, environment variables) and provides access to the configuration.
    """

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        load_env: bool = True,
        env_prefix: str = "SMART_STEPS_",
    ):
        """
        Initialize the configuration manager.

        Args:
            config_path (Optional[Union[str, Path]]): Path to custom config file (default: None)
            load_env (bool): Whether to load environment variables (default: True)
            env_prefix (str): Prefix for environment variables (default: "SMART_STEPS_")
        """
        self.logger = get_logger(__name__)
        self.env_prefix = env_prefix
        
        # Load environment variables if enabled
        if load_env:
            load_dotenv()
        
        # Load default configuration
        self.config = self._load_default_config()
        
        # Override with custom configuration if provided
        if config_path:
            self._load_custom_config(config_path)
        
        # Override with environment variables
        self._apply_env_overrides()
        
        self.logger.info(f"Configuration loaded successfully")

    def _load_default_config(self) -> Config:
        """
        Load the default configuration.

        Returns:
            Config: Default configuration
        """
        # Get the path to the default config file
        # Since we're in src/smart_steps_ai/config/config_manager.py, 
        # we need to go up 3 directories to reach the project root
        default_config_path = (
            Path(__file__).parent.parent.parent.parent / "config" / "defaults" / "config.json"
        )
        
        self.logger.debug(f"Loading default configuration from {default_config_path}")
        
        try:
            with open(default_config_path, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
            
            return Config(**config_dict)
        
        except Exception as e:
            self.logger.error(f"Failed to load default configuration: {str(e)}")
            return Config()

    def _load_custom_config(self, config_path: Union[str, Path]) -> None:
        """
        Load a custom configuration file and merge with the default.

        Args:
            config_path (Union[str, Path]): Path to the custom config file
        """
        path = Path(config_path)
        
        if not path.exists():
            self.logger.warning(f"Custom configuration file not found: {path}")
            return
        
        self.logger.debug(f"Loading custom configuration from {path}")
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                custom_config = json.load(f)
            
            # Merge with default config
            config_dict = self.config.model_dump()
            self._deep_merge(config_dict, custom_config)
            
            # Update configuration
            self.config = Config(**config_dict)
            
            self.logger.debug("Custom configuration loaded and merged successfully")
        
        except Exception as e:
            self.logger.error(f"Failed to load custom configuration: {str(e)}")

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to the configuration."""
        self.logger.debug("Applying environment variable overrides")
        
        # Convert config to dict for modification
        config_dict = self.config.model_dump()
        
        # Get all environment variables with the specified prefix
        for env_key, env_value in os.environ.items():
            if not env_key.startswith(self.env_prefix):
                continue
            
            # Convert environment variable to config path
            # E.g., SMART_STEPS_APP_LOG_LEVEL -> app.log_level
            config_path = env_key[len(self.env_prefix):].lower().replace("_", ".")
            
            # Apply the override
            self._set_nested_value(config_dict, config_path.split("."), env_value)
        
        # Update configuration
        try:
            self.config = Config(**config_dict)
            self.logger.debug("Environment variable overrides applied successfully")
        except Exception as e:
            self.logger.error(f"Failed to apply environment overrides: {str(e)}")

    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Deep merge two dictionaries.

        Args:
            target (Dict[str, Any]): Target dictionary to merge into
            source (Dict[str, Any]): Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def _set_nested_value(self, config_dict: Dict[str, Any], path: list, value: str) -> None:
        """
        Set a nested value in the configuration dictionary.

        Args:
            config_dict (Dict[str, Any]): Configuration dictionary
            path (list): Path to the configuration value
            value (str): Value to set
        """
        if len(path) == 0:
            return
        
        if len(path) == 1:
            key = path[0]
            if key in config_dict:
                # Convert value to the appropriate type based on the existing value
                if isinstance(config_dict[key], bool):
                    config_dict[key] = value.lower() in ("true", "1", "yes", "y", "on", "t")
                elif isinstance(config_dict[key], int):
                    try:
                        config_dict[key] = int(value)
                    except ValueError:
                        self.logger.warning(f"Could not convert {value} to int for {key}")
                elif isinstance(config_dict[key], float):
                    try:
                        config_dict[key] = float(value)
                    except ValueError:
                        self.logger.warning(f"Could not convert {value} to float for {key}")
                else:
                    config_dict[key] = value
            return
        
        key = path[0]
        if key in config_dict and isinstance(config_dict[key], dict):
            self._set_nested_value(config_dict[key], path[1:], value)

    def get_config(self) -> Config:
        """
        Get the complete configuration.

        Returns:
            Config: Complete configuration
        """
        return self.config

    def get(self, section: Optional[str] = None) -> Any:
        """
        Get a section of the configuration or the complete configuration.

        Args:
            section (Optional[str]): Section to get (e.g., "app", "paths") (default: None)

        Returns:
            Any: Configuration section or complete configuration
        """
        if section is None:
            return self.config
        
        if hasattr(self.config, section):
            return getattr(self.config, section)
        
        self.logger.warning(f"Configuration section not found: {section}")
        return None

    def save_config(self, file_path: Union[str, Path]) -> bool:
        """
        Save the current configuration to a file.

        Args:
            file_path (Union[str, Path]): Path to save the configuration

        Returns:
            bool: Success flag
        """
        path = Path(file_path)
        
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.config.model_dump(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to {path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False


# Global instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(
    config_path: Optional[Union[str, Path]] = None,
    load_env: bool = True,
    env_prefix: str = "SMART_STEPS_",
    force_reload: bool = False,
) -> ConfigManager:
    """
    Get the global configuration manager instance.

    Args:
        config_path (Optional[Union[str, Path]]): Path to custom config file (default: None)
        load_env (bool): Whether to load environment variables (default: True)
        env_prefix (str): Prefix for environment variables (default: "SMART_STEPS_")
        force_reload (bool): Whether to force reloading the configuration (default: False)

    Returns:
        ConfigManager: Configuration manager instance
    """
    global _config_manager
    
    if _config_manager is None or force_reload:
        _config_manager = ConfigManager(config_path, load_env, env_prefix)
    
    return _config_manager
