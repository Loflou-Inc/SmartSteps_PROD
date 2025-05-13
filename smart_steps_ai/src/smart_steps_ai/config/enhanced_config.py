"""Enhanced configuration management for the Smart Steps AI module."""

import json
import os
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from ..utils.enhanced_logging import get_logger
from ..utils.enhanced_validation import load_json_file, save_json_file, validate_schema
from ..utils.env import get_env, get_env_bool, get_env_int, get_env_list, get_env_float


class ConfigManager:
    """
    Configuration manager for the Smart Steps AI module.
    
    This class manages loading, accessing, and saving configuration settings
    from various sources (environment variables, config files, defaults).
    It implements a singleton pattern to ensure consistent configuration
    across the application.
    """
    
    # Singleton instance
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Create a singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ConfigManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(
        self,
        config_file: Optional[Union[str, Path]] = None,
        env_prefix: str = "SMART_STEPS_",
        auto_save: bool = False,
        schema: Optional[Any] = None,
    ):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (Optional[Union[str, Path]]): Path to config file (default: None)
            env_prefix (str): Prefix for environment variables (default: "SMART_STEPS_")
            auto_save (bool): Whether to auto-save changes to config file (default: False)
            schema (Optional[Any]): Optional Pydantic schema for validation
        """
        # Skip initialization if already initialized
        if self._initialized:
            return
            
        self.logger = get_logger(__name__)
        self.config_file = Path(config_file) if config_file else None
        self.env_prefix = env_prefix
        self.auto_save = auto_save
        self.schema = schema
        
        # Initialize configuration
        self._config = {}
        self._defaults = {}
        self._modified_keys = set()
        
        # Load configuration
        self._load_config()
        
        self._initialized = True
        self.logger.info("Configuration manager initialized")
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Start with defaults
        self._config = deepcopy(self._defaults)
        
        # Load from config file if available
        if self.config_file and self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    
                # Merge file config with current config
                self._deep_merge(self._config, file_config)
                
                self.logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                self.logger.error(f"Failed to load configuration from {self.config_file}: {str(e)}")
        
        # Load from environment variables
        self._load_from_env()
        
        # Validate configuration if schema is provided
        if self.schema:
            self._validate_config()
        
        # Reset modified keys
        self._modified_keys = set()
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_vars = {k: v for k, v in os.environ.items() if k.startswith(self.env_prefix)}
        
        for key, value in env_vars.items():
            # Remove prefix and convert to lowercase
            config_key = key[len(self.env_prefix):].lower()
            
            # Split by double underscore to create nested keys
            path = config_key.split('__')
            
            # Determine value type and convert
            if value.lower() in ('true', 'false'):
                # Boolean
                converted_value = value.lower() == 'true'
            elif value.isdigit():
                # Integer
                converted_value = int(value)
            elif value.replace('.', '', 1).isdigit() and value.count('.') == 1:
                # Float
                converted_value = float(value)
            elif value.startswith('[') and value.endswith(']'):
                # List (simple implementation)
                try:
                    converted_value = json.loads(value)
                except json.JSONDecodeError:
                    # Fallback to comma-separated list
                    converted_value = [item.strip() for item in value[1:-1].split(',')]
            else:
                # String
                converted_value = value
            
            # Update config with the value
            self._set_nested_value(self._config, path, converted_value)
            
        if env_vars:
            self.logger.info(f"Loaded {len(env_vars)} environment variables with prefix {self.env_prefix}")
    
    def _validate_config(self) -> None:
        """Validate configuration against schema."""
        if not self.schema:
            return
            
        try:
            success, error, _ = validate_schema(self._config, self.schema)
            if not success:
                self.logger.warning(f"Configuration validation failed: {error}")
            else:
                self.logger.info("Configuration validation successful")
        except Exception as e:
            self.logger.error(f"Error validating configuration: {str(e)}")
    
    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """
        Deep merge source dict into target dict.
        
        Args:
            target (Dict): Target dictionary to merge into
            source (Dict): Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursive merge for nested dictionaries
                self._deep_merge(target[key], value)
            else:
                # Replace or add value
                target[key] = value
    
    def _get_nested_value(self, d: Dict, path: List[str]) -> Any:
        """
        Get a nested value from a dictionary using a path.
        
        Args:
            d (Dict): Dictionary to get value from
            path (List[str]): Path to the value
            
        Returns:
            Any: Value at the path or None if not found
        """
        current = d
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _set_nested_value(self, d: Dict, path: List[str], value: Any) -> None:
        """
        Set a nested value in a dictionary using a path.
        
        Args:
            d (Dict): Dictionary to set value in
            path (List[str]): Path to the value
            value (Any): Value to set
        """
        current = d
        # Navigate to the parent of the target key
        for key in path[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[path[-1]] = value
        
        # Mark as modified
        self._modified_keys.add('.'.join(path))
    
    def _has_nested_key(self, d: Dict, path: List[str]) -> bool:
        """
        Check if a nested key exists in a dictionary.
        
        Args:
            d (Dict): Dictionary to check
            path (List[str]): Path to the key
            
        Returns:
            bool: True if the key exists
        """
        current = d
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False
        return True
    
    def _delete_nested_key(self, d: Dict, path: List[str]) -> bool:
        """
        Delete a nested key from a dictionary.
        
        Args:
            d (Dict): Dictionary to delete from
            path (List[str]): Path to the key
            
        Returns:
            bool: True if the key was deleted
        """
        if not path:
            return False
            
        current = d
        # Navigate to the parent of the target key
        for key in path[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False
        
        # Delete the key
        if isinstance(current, dict) and path[-1] in current:
            del current[path[-1]]
            
            # Mark as modified
            self._modified_keys.add('.'.join(path))
            return True
            
        return False
    
    def set_defaults(self, defaults: Dict[str, Any]) -> None:
        """
        Set default configuration values.
        
        Args:
            defaults (Dict[str, Any]): Default configuration values
        """
        self._defaults = deepcopy(defaults)
        
        # Only use defaults for keys that don't exist in current config
        for key, value in self._defaults.items():
            if key not in self._config:
                self._config[key] = deepcopy(value)
                
        self.logger.info(f"Set {len(defaults)} default configuration values")
    
    def get(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key (Optional[str]): Configuration key with dots for nested keys (default: None)
                If None, returns the entire configuration
            default (Any): Default value if the key is not found (default: None)
            
        Returns:
            Any: Configuration value or default
        """
        if key is None:
            return deepcopy(self._config)
            
        # Split key by dots for nested access
        path = key.split('.')
        
        # Get the value
        value = self._get_nested_value(self._config, path)
        
        # Return default if not found
        if value is None:
            return default
            
        # Return a deep copy to prevent modification of internal state
        return deepcopy(value)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key (str): Configuration key with dots for nested keys
            value (Any): Value to set
        """
        # Split key by dots for nested access
        path = key.split('.')
        
        # Set the value
        self._set_nested_value(self._config, path, value)
        
        # Save if auto-save is enabled
        if self.auto_save and self.config_file:
            self.save()
            
        self.logger.debug(f"Set configuration value for {key}")
    
    def update(self, config: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            config (Dict[str, Any]): New configuration values
        """
        # Deep merge the new config
        self._deep_merge(self._config, config)
        
        # Mark all keys as modified (simplification)
        self._modified_keys.update(self._flatten_keys(config))
        
        # Save if auto-save is enabled
        if self.auto_save and self.config_file:
            self.save()
            
        self.logger.info(f"Updated configuration with {len(config)} keys")
    
    def has(self, key: str) -> bool:
        """
        Check if a configuration key exists.
        
        Args:
            key (str): Configuration key with dots for nested keys
            
        Returns:
            bool: True if the key exists
        """
        # Split key by dots for nested access
        path = key.split('.')
        
        # Check if the key exists
        return self._has_nested_key(self._config, path)
    
    def delete(self, key: str) -> bool:
        """
        Delete a configuration key.
        
        Args:
            key (str): Configuration key with dots for nested keys
            
        Returns:
            bool: True if the key was deleted
        """
        # Split key by dots for nested access
        path = key.split('.')
        
        # Delete the key
        deleted = self._delete_nested_key(self._config, path)
        
        # Save if auto-save is enabled and key was deleted
        if deleted and self.auto_save and self.config_file:
            self.save()
            
        if deleted:
            self.logger.debug(f"Deleted configuration key {key}")
            
        return deleted
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = deepcopy(self._defaults)
        self._modified_keys = set()
        
        # Save if auto-save is enabled
        if self.auto_save and self.config_file:
            self.save()
            
        self.logger.info("Reset configuration to defaults")
    
    def reload(self) -> None:
        """Reload configuration from file and environment variables."""
        self._load_config()
        self.logger.info("Reloaded configuration")
    
    def save(self, config_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config_file (Optional[Union[str, Path]]): Path to save to (default: None)
                If None, uses the current config_file
                
        Returns:
            bool: True if the configuration was saved successfully
        """
        # Use provided file or current config file
        file_path = Path(config_file) if config_file else self.config_file
        
        if not file_path:
            self.logger.warning("No config file specified for saving")
            return False
            
        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Saved configuration to {file_path}")
            
            # Reset modified keys
            self._modified_keys = set()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {file_path}: {str(e)}")
            return False
    
    def get_modified(self) -> Dict[str, Any]:
        """
        Get modified configuration values.
        
        Returns:
            Dict[str, Any]: Dictionary of modified keys and their values
        """
        modified = {}
        
        for key in self._modified_keys:
            path = key.split('.')
            value = self._get_nested_value(self._config, path)
            
            if value is not None:
                # Build nested structure for the key
                current = modified
                for p in path[:-1]:
                    if p not in current:
                        current[p] = {}
                    current = current[p]
                current[path[-1]] = deepcopy(value)
                
        return modified
    
    def _flatten_keys(self, d: Dict, prefix: str = '') -> Set[str]:
        """
        Flatten dictionary keys with dot notation.
        
        Args:
            d (Dict): Dictionary to flatten
            prefix (str): Prefix for keys (default: '')
            
        Returns:
            Set[str]: Set of flattened keys
        """
        keys = set()
        
        for key, value in d.items():
            new_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                keys.update(self._flatten_keys(value, new_key))
            else:
                keys.add(new_key)
                
        return keys
    
    def get_env(
        self, key: str, default: Optional[Any] = None, required: bool = False
    ) -> Any:
        """
        Get an environment variable with the configured prefix.
        
        Args:
            key (str): Environment variable key without prefix
            default (Optional[Any]): Default value if not found (default: None)
            required (bool): Whether the variable is required (default: False)
            
        Returns:
            Any: Environment variable value or default
            
        Raises:
            ValueError: If required=True and the variable is not found
        """
        return get_env(f"{self.env_prefix}{key}", default, required)
    
    def get_env_bool(
        self, key: str, default: bool = False, required: bool = False
    ) -> bool:
        """
        Get a boolean environment variable with the configured prefix.
        
        Args:
            key (str): Environment variable key without prefix
            default (bool): Default value if not found (default: False)
            required (bool): Whether the variable is required (default: False)
            
        Returns:
            bool: Boolean value of the environment variable
            
        Raises:
            ValueError: If required=True and the variable is not found
        """
        return get_env_bool(f"{self.env_prefix}{key}", default, required)
    
    def get_env_int(
        self, key: str, default: Optional[int] = None, required: bool = False
    ) -> Optional[int]:
        """
        Get an integer environment variable with the configured prefix.
        
        Args:
            key (str): Environment variable key without prefix
            default (Optional[int]): Default value if not found (default: None)
            required (bool): Whether the variable is required (default: False)
            
        Returns:
            Optional[int]: Integer value of the environment variable
            
        Raises:
            ValueError: If required=True and the variable is not found or if the value cannot be converted to int
        """
        return get_env_int(f"{self.env_prefix}{key}", default, required)
    
    def get_env_float(
        self, key: str, default: Optional[float] = None, required: bool = False
    ) -> Optional[float]:
        """
        Get a float environment variable with the configured prefix.
        
        Args:
            key (str): Environment variable key without prefix
            default (Optional[float]): Default value if not found (default: None)
            required (bool): Whether the variable is required (default: False)
            
        Returns:
            Optional[float]: Float value of the environment variable
            
        Raises:
            ValueError: If required=True and the variable is not found or if the value cannot be converted to float
        """
        return get_env_float(f"{self.env_prefix}{key}", default, required)
    
    def get_env_list(
        self, key: str, default: Optional[list] = None, required: bool = False, separator: str = ","
    ) -> list:
        """
        Get a list environment variable with the configured prefix.
        
        Args:
            key (str): Environment variable key without prefix
            default (Optional[list]): Default value if not found (default: None)
            required (bool): Whether the variable is required (default: False)
            separator (str): Separator character (default: ",")
            
        Returns:
            list: List value of the environment variable
            
        Raises:
            ValueError: If required=True and the variable is not found
        """
        return get_env_list(f"{self.env_prefix}{key}", default, required, separator)


# Singleton instance
_config_manager_instance = None


def get_config_manager() -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Returns:
        ConfigManager: Configuration manager instance
    """
    global _config_manager_instance
    
    if _config_manager_instance is None:
        # Try to find config file in standard locations
        config_file = None
        locations = [
            Path.cwd() / "config" / "config.json",
            Path.cwd() / "config.json",
            Path.cwd().parent / "config" / "config.json",
            Path.cwd().parent / "config.json",
        ]
        
        for location in locations:
            if location.exists():
                config_file = location
                break
                
        # Create instance with found config file
        _config_manager_instance = ConfigManager(config_file=config_file)
        
        # Set default configuration
        _config_manager_instance.set_defaults({
            "app": {
                "name": "Smart Steps AI",
                "version": "0.1.0",
                "environment": "development",
                "debug": True,
                "log_level": "info"
            },
            "api": {
                "host": "127.0.0.1",
                "port": 8000,
                "cors_origins": ["*"],
                "api_keys_enabled": False,
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            },
            "database": {
                "type": "file",
                "path": "data"
            },
            "providers": {
                "openai": {
                    "enabled": True,
                    "default_model": "gpt-3.5-turbo"
                },
                "anthropic": {
                    "enabled": False,
                    "default_model": "claude-2"
                }
            },
            "memory": {
                "enabled": True,
                "max_items": 1000,
                "file_path": "data/memory"
            },
            "personas": {
                "default": "dr_hayes",
                "directory": "config/personas"
            }
        })
        
    return _config_manager_instance
