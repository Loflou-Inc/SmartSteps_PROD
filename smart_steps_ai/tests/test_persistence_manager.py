"""Test the PersistenceManager class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_steps_ai.persistence import PersistenceManager
from src.smart_steps_ai.persistence.storage import FileStorage


class TestPersistenceManager(unittest.TestCase):
    """Test the PersistenceManager class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for testing
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        
        # Initialize the storage and persistence manager
        self.storage = FileStorage(self.test_dir)
        self.persistence_manager = PersistenceManager(self.storage)
        
        # Test data
        self.test_collection = "test_collection"
        self.test_key = "test_key"
        self.test_data = {"name": "Test Data", "value": 42, "items": ["a", "b", "c"]}

    def tearDown(self):
        """Clean up the test environment."""
        # Remove the test collection directory if it exists
        collection_dir = self.test_dir / self.test_collection
        if collection_dir.exists():
            for file in collection_dir.glob("*.json"):
                file.unlink()
            collection_dir.rmdir()

    def test_save_load_data(self):
        """Test saving and loading data."""
        # Save the test data
        result = self.persistence_manager.save(self.test_data, self.test_key, self.test_collection)
        self.assertTrue(result, "Failed to save data")
        
        # Load the data
        loaded_data = self.persistence_manager.load(self.test_key, self.test_collection)
        
        # Verify the loaded data
        self.assertIsNotNone(loaded_data, "Loaded data is None")
        self.assertEqual(loaded_data["name"], self.test_data["name"])
        self.assertEqual(loaded_data["value"], self.test_data["value"])
        self.assertEqual(loaded_data["items"], self.test_data["items"])
        
        print(f"Successfully saved and loaded data: {loaded_data}")

    def test_list_keys(self):
        """Test listing keys in a collection."""
        # Save multiple items
        keys = ["key1", "key2", "key3"]
        for key in keys:
            self.persistence_manager.save({"key": key}, key, self.test_collection)
        
        # List the keys
        listed_keys = self.persistence_manager.list_keys(self.test_collection)
        
        # Verify the keys
        self.assertEqual(len(listed_keys), len(keys))
        for key in keys:
            self.assertIn(key, listed_keys)
        
        print(f"Successfully listed keys: {listed_keys}")

    def test_delete_data(self):
        """Test deleting data."""
        # Save the test data
        self.persistence_manager.save(self.test_data, self.test_key, self.test_collection)
        
        # Verify it exists
        self.assertTrue(self.persistence_manager.exists(self.test_key, self.test_collection))
        
        # Delete the data
        result = self.persistence_manager.delete(self.test_key, self.test_collection)
        self.assertTrue(result, "Failed to delete data")
        
        # Verify it no longer exists
        self.assertFalse(self.persistence_manager.exists(self.test_key, self.test_collection))
        
        print("Successfully deleted data")


if __name__ == "__main__":
    unittest.main()
