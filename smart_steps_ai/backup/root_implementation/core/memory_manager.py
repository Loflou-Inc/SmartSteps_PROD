"""
Memory management for the Smart Steps AI module.
"""

import os
import json
import time
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from ..utils.logging import get_logger
from .config_manager import ConfigManager

# Get logger
logger = get_logger("core.memory_manager")

class MemoryManager:
    """
    Manages memory for the Smart Steps AI module.
    
    Stores and retrieves memories relevant to client sessions.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the memory manager.
        
        Args:
            config_manager: The configuration manager to use.
                If None, a new one will be created.
        """
        self.config_manager = config_manager or ConfigManager()
        
        # Get the memory directory from the configuration
        self.memory_dir = self.config_manager.get_path("memory.memory_dir")
        
        # Get the maximum number of relevant memories to retrieve
        self.max_relevant_memories = self.config_manager.get_config(
            "memory.max_relevant_memories", 5)
        
        logger.debug(f"Initialized MemoryManager with memory directory: {self.memory_dir}")
    
    def get_client_memory_file(self, client_id: str) -> str:
        """
        Get the path to a client's memory file.
        
        Args:
            client_id: The client ID.
            
        Returns:
            The path to the memory file.
        """
        return os.path.join(self.memory_dir, f"{client_id}_memories.json")
    
    def load_memories(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Load memories for a client.
        
        Args:
            client_id: The client ID.
            
        Returns:
            A list of memories.
        """
        memory_file = self.get_client_memory_file(client_id)
        
        # Check if the memory file exists
        if not os.path.exists(memory_file):
            logger.debug(f"Memory file not found for client {client_id}")
            return []
        
        try:
            # Load the memories
            with open(memory_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
                
            logger.debug(f"Loaded {len(memories)} memories for client {client_id}")
            return memories
        except Exception as e:
            logger.error(f"Error loading memories for client {client_id}: {e}")
            return []
    
    def save_memories(self, client_id: str, memories: List[Dict[str, Any]]) -> bool:
        """
        Save memories for a client.
        
        Args:
            client_id: The client ID.
            memories: The memories to save.
            
        Returns:
            True if the memories were saved successfully, False otherwise.
        """
        memory_file = self.get_client_memory_file(client_id)
        
        try:
            # Create the memory directory if it doesn't exist
            os.makedirs(os.path.dirname(memory_file), exist_ok=True)
            
            # Save the memories
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(memories, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"Saved {len(memories)} memories for client {client_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving memories for client {client_id}: {e}")
            return False
    
    def add_memory(self, client_id: str, text: str, source: str = "session",
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a memory for a client.
        
        Args:
            client_id: The client ID.
            text: The memory text.
            source: The source of the memory (e.g., "session", "intake", "note").
            metadata: Additional metadata for the memory.
            
        Returns:
            True if the memory was added successfully, False otherwise.
        """
        # Validate input
        if not client_id or not text:
            logger.warning("Invalid input for add_memory")
            return False
        
        # Load existing memories
        memories = self.load_memories(client_id)
        
        # Check for duplicates
        for memory in memories:
            if memory.get("text") == text:
                logger.debug(f"Duplicate memory for client {client_id}, skipping")
                return True
        
        # Create a timestamp for the memory
        timestamp = time.time()
        date_str = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Create the memory
        memory = {
            "timestamp": timestamp,
            "date": date_str,
            "text": text,
            "source": source
        }
        
        # Add metadata if provided
        if metadata:
            memory["metadata"] = metadata
        
        # Add the memory to the list
        memories.append(memory)
        
        # Save the memories
        return self.save_memories(client_id, memories)
    
    def query_memories(self, client_id: str, query: str, 
                      top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Query memories for a client.
        
        Args:
            client_id: The client ID.
            query: The query to match against memories.
            top_k: The maximum number of memories to return.
                If None, uses the configured maximum.
            
        Returns:
            A list of relevant memories.
        """
        # Validate input
        if not client_id or not query:
            logger.warning("Invalid input for query_memories")
            return []
        
        # Use the configured maximum if not specified
        if top_k is None:
            top_k = self.max_relevant_memories
        
        # Load memories
        memories = self.load_memories(client_id)
        
        if not memories:
            logger.debug(f"No memories found for client {client_id}")
            return []
        
        # Implement a simple keyword-based search for now
        # This would be replaced with a proper vector search in a production system
        
        # Normalize the query
        query_words = set(query.lower().split())
        
        # Score memories based on keyword matches
        scored_memories = []
        for memory in memories:
            text = memory.get("text", "").lower()
            
            # Count matching words
            matches = sum(1 for word in query_words if word in text)
            
            # Only include memories with at least one match
            if matches > 0:
                scored_memories.append((memory, matches))
        
        # Sort by score (descending)
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top_k memories
        result = [memory for memory, _ in scored_memories[:top_k]]
        
        logger.debug(f"Found {len(result)} relevant memories for client {client_id}")
        return result
    
    def get_memory_context(self, client_id: str, query: str, 
                         format_str: str = "- {text}") -> str:
        """
        Get a formatted memory context for a query.
        
        Args:
            client_id: The client ID.
            query: The query to match against memories.
            format_str: The format string for each memory.
            
        Returns:
            A formatted memory context string.
        """
        # Query relevant memories
        memories = self.query_memories(client_id, query)
        
        if not memories:
            return "No relevant client history found."
        
        # Format the memories
        memory_lines = [format_str.format(**memory) for memory in memories]
        
        context = "Relevant client history:\n" + "\n".join(memory_lines)
        
        return context
    
    def delete_memory(self, client_id: str, timestamp: float) -> bool:
        """
        Delete a memory for a client.
        
        Args:
            client_id: The client ID.
            timestamp: The timestamp of the memory to delete.
            
        Returns:
            True if the memory was deleted successfully, False otherwise.
        """
        # Load memories
        memories = self.load_memories(client_id)
        
        # Find the memory to delete
        for i, memory in enumerate(memories):
            if memory.get("timestamp") == timestamp:
                # Remove the memory
                del memories[i]
                
                # Save the memories
                return self.save_memories(client_id, memories)
        
        logger.warning(f"Memory with timestamp {timestamp} not found for client {client_id}")
        return False
    
    def clear_memories(self, client_id: str) -> bool:
        """
        Clear all memories for a client.
        
        Args:
            client_id: The client ID.
            
        Returns:
            True if the memories were cleared successfully, False otherwise.
        """
        # Save an empty list of memories
        return self.save_memories(client_id, [])
    
    def extract_key_info(self, client_id: str, user_input: str, 
                        ai_response: str) -> Optional[str]:
        """
        Extract key information from a conversation turn.
        
        Args:
            client_id: The client ID.
            user_input: The user's input.
            ai_response: The AI's response.
            
        Returns:
            The extracted key information, or None if no key information was found.
        """
        # For this simplified version, we'll look for key phrases that might
        # indicate important information to remember
        
        key_phrases = [
            "my name is", "i am", "i'm", "i want", "i need", 
            "i prefer", "i like", "i don't like", "i dislike",
            "i've been", "i have been", "i've experienced",
            "important", "remember", "don't forget"
        ]
        
        # Check if any key phrases are in the user's input
        for phrase in key_phrases:
            if phrase in user_input.lower():
                # Found potentially important information
                return user_input
        
        # No key information found
        return None
    
    def process_conversation(self, client_id: str, user_input: str, 
                           ai_response: str) -> Optional[str]:
        """
        Process a conversation turn to extract and store key information.
        
        Args:
            client_id: The client ID.
            user_input: The user's input.
            ai_response: The AI's response.
            
        Returns:
            The extracted and stored key information, or None if no key information was found.
        """
        # Extract key information
        key_info = self.extract_key_info(client_id, user_input, ai_response)
        
        if key_info:
            # Add the memory
            success = self.add_memory(client_id, key_info, source="conversation")
            
            if success:
                logger.debug(f"Added memory for client {client_id}: {key_info}")
                return key_info
        
        return None
