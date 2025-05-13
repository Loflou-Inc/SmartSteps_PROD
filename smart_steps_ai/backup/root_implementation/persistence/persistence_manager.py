"""
Persistence manager for the Smart Steps AI module.
"""

import os
from typing import Any, Dict, List, Optional, Union

from .file_storage import FileStorage
from ..utils.logging import get_logger
from ..core.config_manager import ConfigManager

# Get logger
logger = get_logger("persistence.persistence_manager")

class PersistenceManager:
    """
    Persistence manager for the Smart Steps AI module.
    
    Provides a unified interface for storing and retrieving data,
    regardless of the underlying storage mechanism.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the persistence manager.
        
        Args:
            config_manager: The configuration manager to use.
                If None, a new one will be created.
        """
        self.config_manager = config_manager or ConfigManager()
        
        # Get the data directory from the configuration
        data_dir = self.config_manager.get_path("general.data_dir")
        
        # Initialize the file storage
        self.file_storage = FileStorage(data_dir)
        
        logger.debug(f"Initialized PersistenceManager with data directory: {data_dir}")
        
        # Define collections
        self.collections = {
            "sessions": "sessions",
            "clients": "clients",
            "personas": "personas",
            "analytics": "analytics"
        }
        
        # Create collections if they don't exist
        for collection in self.collections.values():
            self.file_storage.create_collection(collection)
    
    def save_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Save a session.
        
        Args:
            session_id: The session ID.
            data: The session data.
            
        Returns:
            True if the session was saved successfully, False otherwise.
        """
        return self.file_storage.save(self.collections["sessions"], session_id, data)
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a session.
        
        Args:
            session_id: The session ID.
            
        Returns:
            The session data, or None if not found.
        """
        return self.file_storage.load(self.collections["sessions"], session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: The session ID.
            
        Returns:
            True if the session was deleted successfully, False otherwise.
        """
        return self.file_storage.delete(self.collections["sessions"], session_id)
    
    def list_sessions(self) -> List[str]:
        """
        List all sessions.
        
        Returns:
            A list of session IDs.
        """
        return self.file_storage.list_items(self.collections["sessions"])
    
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.
        
        Args:
            session_id: The session ID.
            
        Returns:
            True if the session exists, False otherwise.
        """
        return self.file_storage.exists(self.collections["sessions"], session_id)
    
    def save_client(self, client_id: str, data: Dict[str, Any]) -> bool:
        """
        Save a client.
        
        Args:
            client_id: The client ID.
            data: The client data.
            
        Returns:
            True if the client was saved successfully, False otherwise.
        """
        return self.file_storage.save(self.collections["clients"], client_id, data)
    
    def load_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a client.
        
        Args:
            client_id: The client ID.
            
        Returns:
            The client data, or None if not found.
        """
        return self.file_storage.load(self.collections["clients"], client_id)
    
    def delete_client(self, client_id: str) -> bool:
        """
        Delete a client.
        
        Args:
            client_id: The client ID.
            
        Returns:
            True if the client was deleted successfully, False otherwise.
        """
        return self.file_storage.delete(self.collections["clients"], client_id)
    
    def list_clients(self) -> List[str]:
        """
        List all clients.
        
        Returns:
            A list of client IDs.
        """
        return self.file_storage.list_items(self.collections["clients"])
    
    def client_exists(self, client_id: str) -> bool:
        """
        Check if a client exists.
        
        Args:
            client_id: The client ID.
            
        Returns:
            True if the client exists, False otherwise.
        """
        return self.file_storage.exists(self.collections["clients"], client_id)
    
    def save_persona(self, persona_id: str, data: Dict[str, Any]) -> bool:
        """
        Save a persona.
        
        Args:
            persona_id: The persona ID.
            data: The persona data.
            
        Returns:
            True if the persona was saved successfully, False otherwise.
        """
        return self.file_storage.save(self.collections["personas"], persona_id, data)
    
    def load_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a persona.
        
        Args:
            persona_id: The persona ID.
            
        Returns:
            The persona data, or None if not found.
        """
        return self.file_storage.load(self.collections["personas"], persona_id)
    
    def delete_persona(self, persona_id: str) -> bool:
        """
        Delete a persona.
        
        Args:
            persona_id: The persona ID.
            
        Returns:
            True if the persona was deleted successfully, False otherwise.
        """
        return self.file_storage.delete(self.collections["personas"], persona_id)
    
    def list_personas(self) -> List[str]:
        """
        List all personas.
        
        Returns:
            A list of persona IDs.
        """
        return self.file_storage.list_items(self.collections["personas"])
    
    def persona_exists(self, persona_id: str) -> bool:
        """
        Check if a persona exists.
        
        Args:
            persona_id: The persona ID.
            
        Returns:
            True if the persona exists, False otherwise.
        """
        return self.file_storage.exists(self.collections["personas"], persona_id)
    
    def save_analytics(self, analytics_id: str, data: Dict[str, Any]) -> bool:
        """
        Save analytics data.
        
        Args:
            analytics_id: The analytics ID.
            data: The analytics data.
            
        Returns:
            True if the analytics data was saved successfully, False otherwise.
        """
        return self.file_storage.save(self.collections["analytics"], analytics_id, data)
    
    def load_analytics(self, analytics_id: str) -> Optional[Dict[str, Any]]:
        """
        Load analytics data.
        
        Args:
            analytics_id: The analytics ID.
            
        Returns:
            The analytics data, or None if not found.
        """
        return self.file_storage.load(self.collections["analytics"], analytics_id)
    
    def delete_analytics(self, analytics_id: str) -> bool:
        """
        Delete analytics data.
        
        Args:
            analytics_id: The analytics ID.
            
        Returns:
            True if the analytics data was deleted successfully, False otherwise.
        """
        return self.file_storage.delete(self.collections["analytics"], analytics_id)
    
    def list_analytics(self) -> List[str]:
        """
        List all analytics data.
        
        Returns:
            A list of analytics IDs.
        """
        return self.file_storage.list_items(self.collections["analytics"])
    
    def analytics_exists(self, analytics_id: str) -> bool:
        """
        Check if analytics data exists.
        
        Args:
            analytics_id: The analytics ID.
            
        Returns:
            True if the analytics data exists, False otherwise.
        """
        return self.file_storage.exists(self.collections["analytics"], analytics_id)
    
    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a session.
        
        Args:
            session_id: The session ID.
            
        Returns:
            The metadata, or None if not found.
        """
        return self.file_storage.get_metadata(self.collections["sessions"], session_id)
    
    def get_client_metadata(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a client.
        
        Args:
            client_id: The client ID.
            
        Returns:
            The metadata, or None if not found.
        """
        return self.file_storage.get_metadata(self.collections["clients"], client_id)
    
    def get_persona_metadata(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a persona.
        
        Args:
            persona_id: The persona ID.
            
        Returns:
            The metadata, or None if not found.
        """
        return self.file_storage.get_metadata(self.collections["personas"], persona_id)
    
    def get_analytics_metadata(self, analytics_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for analytics data.
        
        Args:
            analytics_id: The analytics ID.
            
        Returns:
            The metadata, or None if not found.
        """
        return self.file_storage.get_metadata(self.collections["analytics"], analytics_id)
