"""
Tests for the configuration manager.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path

from smart_steps_ai.core.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Tests for the ConfigManager class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test config files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "test_config.json")
    
    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
    
    def test_create_default_config(self):
        """Test that a default configuration is created."""
        # Create a config manager with a non-existent file
        config_manager = ConfigManager(self.config_file)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.config_file))
        
        # Check that the file contains a valid JSON object
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            self.assertIsInstance(config, dict)
            
            # Check that some expected keys are present
            self.assertIn("general", config)
            self.assertIn("ai_provider", config)
            self.assertIn("session", config)
    
    def test_get_config(self):
        """Test getting configuration values."""
        # Create a config manager
        config_manager = ConfigManager(self.config_file)
        
        # Get a value that should exist
        app_name = config_manager.get_config("general.app_name")
        self.assertEqual(app_name, "Smart Steps AI")
        
        # Get a value that doesn't exist
        missing_value = config_manager.get_config("non_existent.key", "default")
        self.assertEqual(missing_value, "default")
        
        # Get the entire config
        config = config_manager.get_config()
        self.assertIsInstance(config, dict)
    
    def test_set_config(self):
        """Test setting configuration values."""
        # Create a config manager
        config_manager = ConfigManager(self.config_file)
        
        # Set a value
        config_manager.set_config("general.app_name", "Test App")
        
        # Check that the value was updated
        app_name = config_manager.get_config("general.app_name")
        self.assertEqual(app_name, "Test App")
        
        # Set a nested value
        config_manager.set_config("new_section.nested.key", "value")
        
        # Check that the value was added
        nested_value = config_manager.get_config("new_section.nested.key")
        self.assertEqual(nested_value, "value")
        
        # Reload the config from file
        new_config_manager = ConfigManager(self.config_file)
        
        # Check that the changes were saved
        app_name = new_config_manager.get_config("general.app_name")
        self.assertEqual(app_name, "Test App")
        
        nested_value = new_config_manager.get_config("new_section.nested.key")
        self.assertEqual(nested_value, "value")
    
    def test_get_path(self):
        """Test getting paths from configuration."""
        # Create a config manager
        config_manager = ConfigManager(self.config_file)
        
        # Set a path
        test_path = os.path.join(self.temp_dir.name, "test_dir")
        config_manager.set_config("test.path", test_path)
        
        # Get the path
        path = config_manager.get_path("test.path")
        self.assertEqual(path, test_path)
        
        # Check that the directory was created
        self.assertTrue(os.path.exists(test_path))
        self.assertTrue(os.path.isdir(test_path))
        
        # Get a non-existent path
        missing_path = config_manager.get_path("non_existent.path")
        self.assertIsNone(missing_path)

if __name__ == "__main__":
    unittest.main()
