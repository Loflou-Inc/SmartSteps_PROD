"""Storage interfaces for the Smart Steps AI module."""

import json
import os
import datetime
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from ..utils import get_logger


# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that can handle datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


class StorageInterface(ABC):
    """Abstract interface for storage implementations."""

    @abstractmethod
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
        pass

    @abstractmethod
    def load(
        self, key: str, collection: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load data from storage.

        Args:
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data

        Returns:
            Optional[Dict[str, Any]]: Loaded data or None if not found
        """
        pass

    @abstractmethod
    def delete(self, key: str, collection: str) -> bool:
        """
        Delete data from storage.

        Args:
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data

        Returns:
            bool: Success flag
        """
        pass

    @abstractmethod
    def list_keys(self, collection: str) -> List[str]:
        """
        List all keys in a collection.

        Args:
            collection (str): Collection or category to list

        Returns:
            List[str]: List of keys
        """
        pass


class FileStorage(StorageInterface):
    """File-based storage implementation."""

    def __init__(self, base_dir: Union[str, Path]):
        """
        Initialize file storage.

        Args:
            base_dir (Union[str, Path]): Base directory for storage
        """
        self.logger = get_logger(__name__)
        self.base_dir = Path(base_dir)
        
        # Create base directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.debug(f"Initialized file storage at {self.base_dir}")

    def _get_collection_dir(self, collection: str) -> Path:
        """
        Get the directory for a collection.

        Args:
            collection (str): Collection name

        Returns:
            Path: Collection directory
        """
        collection_dir = self.base_dir / collection
        collection_dir.mkdir(parents=True, exist_ok=True)
        return collection_dir

    def _get_file_path(self, key: str, collection: str) -> Path:
        """
        Get the file path for a key in a collection.

        Args:
            key (str): Unique identifier
            collection (str): Collection name

        Returns:
            Path: File path
        """
        # Sanitize the key to be a valid filename
        safe_key = key.replace("/", "_").replace("\\", "_").replace(":", "_")
        return self._get_collection_dir(collection) / f"{safe_key}.json"

    def save(
        self, data: Union[Dict[str, Any], BaseModel], key: str, collection: str
    ) -> bool:
        """
        Save data to a JSON file.

        Args:
            data (Union[Dict[str, Any], BaseModel]): Data to save
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data

        Returns:
            bool: Success flag
        """
        try:
            file_path = self._get_file_path(key, collection)
            
            # Create directory structure if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert pydantic model to dict if needed
            if isinstance(data, BaseModel):
                try:
                    # Try new pydantic v2 method first
                    data_dict = data.model_dump()
                except AttributeError:
                    # Fall back to pydantic v1 method
                    try:
                        data_dict = data.dict()
                    except Exception as e:
                        # If both fail, try direct conversion to dict
                        self.logger.warning(f"Failed to convert model to dict using standard methods: {str(e)}")
                        data_dict = dict(data)
            else:
                data_dict = data
            
            # Write to a temporary file first to avoid corruption
            temp_path = file_path.with_suffix('.tmp')
            
            # Save the data
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
            
            # Verify the file was written successfully by reading it back
            try:
                with open(temp_path, "r", encoding="utf-8") as f:
                    _ = json.load(f)  # Just to validate it's proper JSON
            except json.JSONDecodeError as e:
                self.logger.error(f"File verification failed: {str(e)}")
                temp_path.unlink(missing_ok=True)
                return False
                
            # If verification passes, rename temp file to actual file
            if file_path.exists():
                file_path.unlink()
            temp_path.rename(file_path)
            
            self.logger.debug(f"Successfully saved data to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save data to {collection}/{key}: {str(e)}")
            return False

    def load(
        self, key: str, collection: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load data from a JSON file.

        Args:
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data

        Returns:
            Optional[Dict[str, Any]]: Loaded data or None if not found
        """
        try:
            file_path = self._get_file_path(key, collection)
            
            if not file_path.exists():
                self.logger.debug(f"File not found: {file_path}")
                return None
            
            if not file_path.is_file():
                self.logger.warning(f"Not a file: {file_path}")
                return None
                
            if file_path.stat().st_size == 0:
                self.logger.warning(f"Empty file: {file_path}")
                return None
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if not isinstance(data, dict):
                    self.logger.warning(f"File does not contain a dictionary: {file_path}")
                    return None
                
                self.logger.debug(f"Successfully loaded data from {file_path}")
                return data
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON in file {file_path}: {str(e)}")
                # Check if there's a backup/temp file we can try
                temp_path = file_path.with_suffix('.tmp')
                if temp_path.exists() and temp_path.is_file():
                    self.logger.info(f"Attempting to load from temp file: {temp_path}")
                    with open(temp_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return data
                return None
        
        except Exception as e:
            self.logger.error(f"Failed to load data from {collection}/{key}: {str(e)}")
            return None

    def delete(self, key: str, collection: str) -> bool:
        """
        Delete a JSON file.

        Args:
            key (str): Unique identifier for the data
            collection (str): Collection or category for the data

        Returns:
            bool: Success flag
        """
        try:
            file_path = self._get_file_path(key, collection)
            
            if not file_path.exists():
                self.logger.debug(f"File not found for deletion: {file_path}")
                return False
            
            file_path.unlink()
            self.logger.debug(f"Deleted file: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to delete file: {str(e)}")
            return False

    def list_keys(self, collection: str) -> List[str]:
        """
        List all keys in a collection.

        Args:
            collection (str): Collection or category to list

        Returns:
            List[str]: List of keys
        """
        try:
            collection_dir = self._get_collection_dir(collection)
            
            # Find all JSON files in the collection directory
            json_files = list(collection_dir.glob("*.json"))
            
            # Extract the keys from the filenames
            keys = [file.stem for file in json_files]
            
            self.logger.debug(f"Listed {len(keys)} keys in collection {collection}")
            return keys
        
        except Exception as e:
            self.logger.error(f"Failed to list keys: {str(e)}")
            return []
