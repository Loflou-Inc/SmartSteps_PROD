"""
File-based storage implementation for the Smart Steps AI module.
"""

import os
import json
import time
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from ..utils.logging import get_logger

# Get logger
logger = get_logger("persistence.file_storage")

class FileStorage:
    """
    File-based storage implementation for persistent data.
    
    Stores data in JSON files organized in directories.
    """
    
    def __init__(self, base_dir: str):
        """
        Initialize the file storage.
        
        Args:
            base_dir: The base directory for storage.
        """
        self.base_dir = base_dir
        
        # Create the base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
        
        logger.debug(f"Initialized FileStorage with base directory: {self.base_dir}")
    
    def get_file_path(self, collection: str, item_id: str) -> str:
        """
        Get the file path for an item.
        
        Args:
            collection: The collection name.
            item_id: The item ID.
            
        Returns:
            The file path.
        """
        # Create the collection directory if it doesn't exist
        collection_dir = os.path.join(self.base_dir, collection)
        os.makedirs(collection_dir, exist_ok=True)
        
        # Return the file path
        return os.path.join(collection_dir, f"{item_id}.json")
    
    def save(self, collection: str, item_id: str, data: Dict[str, Any]) -> bool:
        """
        Save an item to storage.
        
        Args:
            collection: The collection name.
            item_id: The item ID.
            data: The data to save.
            
        Returns:
            True if the item was saved successfully, False otherwise.
        """
        file_path = self.get_file_path(collection, item_id)
        
        try:
            # Add metadata
            if "_metadata" not in data:
                data["_metadata"] = {}
            
            data["_metadata"]["lastModified"] = time.time()
            
            # Save the data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"Saved item {item_id} to collection {collection}")
            return True
        except Exception as e:
            logger.error(f"Error saving item {item_id} to collection {collection}: {e}")
            return False
    
    def load(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Load an item from storage.
        
        Args:
            collection: The collection name.
            item_id: The item ID.
            
        Returns:
            The item data, or None if not found.
        """
        file_path = self.get_file_path(collection, item_id)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.debug(f"Item {item_id} not found in collection {collection}")
            return None
        
        try:
            # Load the data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            logger.debug(f"Loaded item {item_id} from collection {collection}")
            return data
        except Exception as e:
            logger.error(f"Error loading item {item_id} from collection {collection}: {e}")
            return None
    
    def delete(self, collection: str, item_id: str) -> bool:
        """
        Delete an item from storage.
        
        Args:
            collection: The collection name.
            item_id: The item ID.
            
        Returns:
            True if the item was deleted successfully, False otherwise.
        """
        file_path = self.get_file_path(collection, item_id)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.debug(f"Item {item_id} not found in collection {collection}")
            return False
        
        try:
            # Delete the file
            os.remove(file_path)
            
            logger.debug(f"Deleted item {item_id} from collection {collection}")
            return True
        except Exception as e:
            logger.error(f"Error deleting item {item_id} from collection {collection}: {e}")
            return False
    
    def list_items(self, collection: str) -> List[str]:
        """
        List all items in a collection.
        
        Args:
            collection: The collection name.
            
        Returns:
            A list of item IDs.
        """
        collection_dir = os.path.join(self.base_dir, collection)
        
        # Check if the collection directory exists
        if not os.path.exists(collection_dir):
            logger.debug(f"Collection {collection} not found")
            return []
        
        try:
            # List all JSON files in the directory
            items = []
            for file_name in os.listdir(collection_dir):
                if file_name.endswith('.json'):
                    # Extract the item ID from the file name
                    item_id = file_name[:-5]  # Remove the .json extension
                    items.append(item_id)
            
            logger.debug(f"Listed {len(items)} items in collection {collection}")
            return items
        except Exception as e:
            logger.error(f"Error listing items in collection {collection}: {e}")
            return []
    
    def exists(self, collection: str, item_id: str) -> bool:
        """
        Check if an item exists in storage.
        
        Args:
            collection: The collection name.
            item_id: The item ID.
            
        Returns:
            True if the item exists, False otherwise.
        """
        file_path = self.get_file_path(collection, item_id)
        return os.path.exists(file_path)
    
    def get_metadata(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an item.
        
        Args:
            collection: The collection name.
            item_id: The item ID.
            
        Returns:
            The metadata, or None if not found.
        """
        # Load the item
        item = self.load(collection, item_id)
        
        if item is None:
            return None
        
        # Return the metadata
        return item.get("_metadata", {})
    
    def create_collection(self, collection: str) -> bool:
        """
        Create a collection.
        
        Args:
            collection: The collection name.
            
        Returns:
            True if the collection was created successfully, False otherwise.
        """
        collection_dir = os.path.join(self.base_dir, collection)
        
        try:
            # Create the directory
            os.makedirs(collection_dir, exist_ok=True)
            
            logger.debug(f"Created collection {collection}")
            return True
        except Exception as e:
            logger.error(f"Error creating collection {collection}: {e}")
            return False
    
    def delete_collection(self, collection: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection: The collection name.
            
        Returns:
            True if the collection was deleted successfully, False otherwise.
        """
        collection_dir = os.path.join(self.base_dir, collection)
        
        # Check if the collection directory exists
        if not os.path.exists(collection_dir):
            logger.debug(f"Collection {collection} not found")
            return False
        
        try:
            # Delete all files in the directory
            for file_name in os.listdir(collection_dir):
                file_path = os.path.join(collection_dir, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # Delete the directory
            os.rmdir(collection_dir)
            
            logger.debug(f"Deleted collection {collection}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection}: {e}")
            return False
