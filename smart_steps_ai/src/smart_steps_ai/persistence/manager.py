"""Persistence manager for the Smart Steps AI module."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from ..config import get_config_manager
from ..utils import get_logger
from .storage import FileStorage, StorageInterface


class PersistenceManager:
    """
    Manager for data persistence operations.
    
    This class provides a unified interface for saving, loading, and managing
    data across different collections and storage backends.
    """

    def __init__(
        self,
        storage: Optional[StorageInterface] = None,
        base_dir: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize the persistence manager.

        Args:
            storage (Optional[StorageInterface]): Storage implementation (default: None)
                If None, a FileStorage instance will be created
            base_dir (Optional[Union[str, Path]]): Base directory for storage (default: None)
                Only used if storage is None
                If None, uses the data directory from the configuration
        """
        self.logger = get_logger(__name__)
        self.config = get_config_manager().get()
        
        # Set up storage
        if storage:
            self.storage = storage
        else:
            # Determine base directory
            if base_dir:
                data_dir = Path(base_dir)
            else:
                # Use the data directory from the configuration
                data_dir = Path(self.config.paths.sessions_dir).parent
            
            # Create file storage
            self.storage = FileStorage(data_dir)
        
        self.logger.debug("Initialized persistence manager")

    def save(
        self, data: Union[Dict[str, Any], BaseModel], key: str, collection: str
    ) -> bool:
        """
        Save data to storage.

        Args:
            data (Union[Dict[str, Any], BaseModel]): Data to save
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data

        Returns:
            bool: Success flag
        """
        return self.storage.save(data, key, collection)

    def load(
        self, key: str, collection: str, model_class: Optional[Type[BaseModel]] = None
    ) -> Optional[Union[Dict[str, Any], BaseModel]]:
        """
        Load data from storage.

        Args:
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data
            model_class (Optional[Type[BaseModel]]): Pydantic model class to validate and convert the data (default: None)

        Returns:
            Optional[Union[Dict[str, Any], BaseModel]]: Loaded data or None if not found
        """
        data = self.storage.load(key, collection)
        
        if data is None:
            return None
        
        # Convert to pydantic model if specified
        if model_class and data:
            try:
                return model_class(**data)
            except Exception as e:
                self.logger.error(f"Failed to convert data to model: {str(e)}")
                return None
        
        return data

    def delete(self, key: str, collection: str) -> bool:
        """
        Delete data from storage.

        Args:
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data

        Returns:
            bool: Success flag
        """
        return self.storage.delete(key, collection)

    def list_keys(self, collection: str) -> List[str]:
        """
        List all keys in a collection.

        Args:
            collection (str): Collection or category to list

        Returns:
            List[str]: List of keys
        """
        return self.storage.list_keys(collection)

    def exists(self, key: str, collection: str) -> bool:
        """
        Check if data exists in storage.

        Args:
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data

        Returns:
            bool: True if the data exists, False otherwise
        """
        data = self.storage.load(key, collection)
        return data is not None
