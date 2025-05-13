"""
Tests for the persistence layer.
"""

import os
import tempfile
import unittest
from typing import Dict, Any

from smart_steps_ai.persistence.file_storage import FileStorage
from smart_steps_ai.persistence.persistence_manager import PersistenceManager
from smart_steps_ai.core.config_manager import ConfigManager

class TestFileStorage(unittest.TestCase):
    """Tests for the FileStorage class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = FileStorage(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
    
    def test_save_and_load(self):
        """Test saving and loading data."""
        # Save an item
        data = {"name": "Test Item", "value": 42}
        result = self.storage.save("test_collection", "test_item", data)
        self.assertTrue(result)
        
        # Load the item
        loaded_data = self.storage.load("test_collection", "test_item")
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["name"], "Test Item")
        self.assertEqual(loaded_data["value"], 42)
        
        # Check that metadata was added
        self.assertIn("_metadata", loaded_data)
        self.assertIn("lastModified", loaded_data["_metadata"])
    
    def test_delete(self):
        """Test deleting data."""
        # Save an item
        data = {"name": "Test Item", "value": 42}
        self.storage.save("test_collection", "test_item", data)
        
        # Check that the item exists
        self.assertTrue(self.storage.exists("test_collection", "test_item"))
        
        # Delete the item
        result = self.storage.delete("test_collection", "test_item")
        self.assertTrue(result)
        
        # Check that the item no longer exists
        self.assertFalse(self.storage.exists("test_collection", "test_item"))
        
        # Try loading the item
        loaded_data = self.storage.load("test_collection", "test_item")
        self.assertIsNone(loaded_data)
    
    def test_list_items(self):
        """Test listing items."""
        # Save some items
        data1 = {"name": "Item 1", "value": 1}
        data2 = {"name": "Item 2", "value": 2}
        data3 = {"name": "Item 3", "value": 3}
        
        self.storage.save("test_collection", "item1", data1)
        self.storage.save("test_collection", "item2", data2)
        self.storage.save("test_collection", "item3", data3)
        
        # List the items
        items = self.storage.list_items("test_collection")
        
        # Check that all items are in the list
        self.assertEqual(len(items), 3)
        self.assertIn("item1", items)
        self.assertIn("item2", items)
        self.assertIn("item3", items)
    
    def test_collection_management(self):
        """Test collection management."""
        # Create a collection
        result = self.storage.create_collection("new_collection")
        self.assertTrue(result)
        
        # Check that the collection exists
        collection_dir = os.path.join(self.temp_dir.name, "new_collection")
        self.assertTrue(os.path.exists(collection_dir))
        self.assertTrue(os.path.isdir(collection_dir))
        
        # Delete the collection
        result = self.storage.delete_collection("new_collection")
        self.assertTrue(result)
        
        # Check that the collection no longer exists
        self.assertFalse(os.path.exists(collection_dir))

class TestPersistenceManager(unittest.TestCase):
    """Tests for the PersistenceManager class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for test data
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a test configuration
        config = {
            "general": {
                "data_dir": self.temp_dir.name
            }
        }
        
        # Create a configuration manager with the test configuration
        config_file = os.path.join(self.temp_dir.name, "test_config.json")
        self.config_manager = ConfigManager(config_file)
        for key, value in config["general"].items():
            self.config_manager.set_config(f"general.{key}", value)
        
        # Create the persistence manager
        self.persistence_manager = PersistenceManager(self.config_manager)
    
    def tearDown(self):
        """Clean up the test environment."""
        self.temp_dir.cleanup()
    
    def test_session_management(self):
        """Test session management."""
        # Save a session
        session_data = {
            "id": "test_session",
            "client_id": "test_client",
            "start_time": "2023-01-01T12:00:00Z",
            "messages": []
        }
        
        result = self.persistence_manager.save_session("test_session", session_data)
        self.assertTrue(result)
        
        # Check that the session exists
        self.assertTrue(self.persistence_manager.session_exists("test_session"))
        
        # Load the session
        loaded_session = self.persistence_manager.load_session("test_session")
        self.assertIsNotNone(loaded_session)
        self.assertEqual(loaded_session["id"], "test_session")
        self.assertEqual(loaded_session["client_id"], "test_client")
        
        # List sessions
        sessions = self.persistence_manager.list_sessions()
        self.assertIn("test_session", sessions)
        
        # Delete the session
        result = self.persistence_manager.delete_session("test_session")
        self.assertTrue(result)
        
        # Check that the session no longer exists
        self.assertFalse(self.persistence_manager.session_exists("test_session"))
    
    def test_client_management(self):
        """Test client management."""
        # Save a client
        client_data = {
            "id": "test_client",
            "name": "Test Client",
            "email": "test@example.com"
        }
        
        result = self.persistence_manager.save_client("test_client", client_data)
        self.assertTrue(result)
        
        # Check that the client exists
        self.assertTrue(self.persistence_manager.client_exists("test_client"))
        
        # Load the client
        loaded_client = self.persistence_manager.load_client("test_client")
        self.assertIsNotNone(loaded_client)
        self.assertEqual(loaded_client["id"], "test_client")
        self.assertEqual(loaded_client["name"], "Test Client")
        
        # List clients
        clients = self.persistence_manager.list_clients()
        self.assertIn("test_client", clients)
        
        # Delete the client
        result = self.persistence_manager.delete_client("test_client")
        self.assertTrue(result)
        
        # Check that the client no longer exists
        self.assertFalse(self.persistence_manager.client_exists("test_client"))
    
    def test_persona_management(self):
        """Test persona management."""
        # Save a persona
        persona_data = {
            "id": "test_persona",
            "name": "Test Persona",
            "description": "A test persona"
        }
        
        result = self.persistence_manager.save_persona("test_persona", persona_data)
        self.assertTrue(result)
        
        # Check that the persona exists
        self.assertTrue(self.persistence_manager.persona_exists("test_persona"))
        
        # Load the persona
        loaded_persona = self.persistence_manager.load_persona("test_persona")
        self.assertIsNotNone(loaded_persona)
        self.assertEqual(loaded_persona["id"], "test_persona")
        self.assertEqual(loaded_persona["name"], "Test Persona")
        
        # List personas
        personas = self.persistence_manager.list_personas()
        self.assertIn("test_persona", personas)
        
        # Delete the persona
        result = self.persistence_manager.delete_persona("test_persona")
        self.assertTrue(result)
        
        # Check that the persona no longer exists
        self.assertFalse(self.persistence_manager.persona_exists("test_persona"))

if __name__ == "__main__":
    unittest.main()
