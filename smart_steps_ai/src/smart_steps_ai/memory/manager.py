"""Memory management for the Smart Steps AI module."""

import datetime
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..config import get_config_manager
from ..session.models import Session
from ..utils import get_logger
from .models import MemoryEntry, MemorySource, MemoryType


class MemoryManager:
    """
    Manager for memory integration.
    
    This class provides integration with the Claude Memory System, allowing
    storage and retrieval of important information across sessions.
    """

    def __init__(self, memory_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the memory manager.

        Args:
            memory_dir (Optional[Union[str, Path]]): Path to the memory system directory (default: None)
                If None, uses the path from the configuration
        """
        self.logger = get_logger(__name__)
        self.config = get_config_manager().get()
        
        # Set memory directory
        if memory_dir:
            self.memory_dir = Path(memory_dir)
        else:
            self.memory_dir = Path(self.config.memory.memory_dir)
        
        # Check if memory integration is enabled
        self.enabled = self.config.memory.enabled
        
        if not self.enabled:
            self.logger.info("Memory integration is disabled")
            return
        
        # Check if the memory directory exists
        if not self.memory_dir.exists():
            self.logger.warning(f"Memory directory not found: {self.memory_dir}")
            self.enabled = False
            return
        
        # Check if the memory integration script exists
        self.integration_script = self.memory_dir / "claude_dc_integration.py"
        if not self.integration_script.exists():
            self.logger.warning(f"Memory integration script not found: {self.integration_script}")
            self.enabled = False
            return
        
        self.logger.info(f"Memory integration initialized with directory: {self.memory_dir}")

    def store_memory(
        self,
        text: str,
        client_name: str,
        memory_type: Union[str, MemoryType],
        source_type: str,
        source_id: str,
        source_reference: Optional[str] = None,
        importance: int = 5,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """
        Store a memory in the memory system.

        Args:
            text (str): Memory text
            client_name (str): Name of the client
            memory_type (Union[str, MemoryType]): Type of memory
            source_type (str): Type of source (e.g., "session", "analysis")
            source_id (str): ID of the source
            source_reference (Optional[str]): Additional reference for the source (default: None)
            importance (int): Importance level from 1-10 (default: 5)
            metadata (Optional[Dict[str, str]]): Additional metadata (default: None)
            tags (Optional[List[str]]): Tags for the memory (default: None)

        Returns:
            bool: Success flag
        """
        if not self.enabled:
            self.logger.debug("Memory integration is disabled, not storing memory")
            return False
        
        try:
            # Convert memory_type to enum if it's a string
            if isinstance(memory_type, str):
                try:
                    memory_type = MemoryType(memory_type)
                except ValueError:
                    self.logger.warning(f"Invalid memory type: {memory_type}, using CUSTOM")
                    memory_type = MemoryType.CUSTOM
            
            # Add client name and memory type to tags
            all_tags = tags or []
            all_tags.append(f"client:{client_name}")
            all_tags.append(f"type:{memory_type.value}")
            
            # Create a memory entry
            memory = MemoryEntry(
                id=str(uuid.uuid4()),
                text=text,
                type=memory_type,
                client_name=client_name,
                source=MemorySource(
                    type=source_type,
                    id=source_id,
                    reference=source_reference,
                ),
                importance=importance,
                metadata=metadata or {},
                tags=all_tags,
            )
            
            # Store the memory using the claude_dc_integration.py script
            result = self._run_memory_command("remember", text)
            
            if result:
                self.logger.debug(f"Stored memory: {text[:50]}...")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Failed to store memory: {str(e)}")
            return False

    def retrieve_memories(
        self,
        query: str,
        client_name: Optional[str] = None,
        memory_type: Optional[Union[str, MemoryType]] = None,
        max_results: int = 5,
    ) -> List[str]:
        """
        Retrieve memories related to a query.

        Args:
            query (str): Search query
            client_name (Optional[str]): Filter by client name (default: None)
            memory_type (Optional[Union[str, MemoryType]]): Filter by memory type (default: None)
            max_results (int): Maximum number of results to return (default: 5)

        Returns:
            List[str]: List of memory texts
        """
        if not self.enabled:
            self.logger.debug("Memory integration is disabled, not retrieving memories")
            return []
        
        try:
            # Build the search query
            search_query = query
            
            # Add filters if specified
            if client_name:
                search_query = f"{search_query} client:{client_name}"
            
            if memory_type:
                memory_type_value = memory_type.value if isinstance(memory_type, MemoryType) else memory_type
                search_query = f"{search_query} type:{memory_type_value}"
            
            # Retrieve memories using the claude_dc_integration.py script
            result = self._run_memory_command("recall", search_query)
            
            if not result:
                return []
            
            # Parse the results
            # The recall command returns a numbered list of memories
            memories = []
            lines = result.strip().split("\n")
            
            # Skip the first line (header)
            for line in lines[1:]:
                # Extract the memory text (skip the number and dot)
                parts = line.split(". ", 1)
                if len(parts) > 1 and parts[0].strip().isdigit():
                    memories.append(parts[1].strip())
                    
                    # Stop when we reach max_results
                    if len(memories) >= max_results:
                        break
            
            self.logger.debug(f"Retrieved {len(memories)} memories for query: {query}")
            return memories
        
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories: {str(e)}")
            return []

    def get_memory_context(
        self,
        query: str,
        client_name: Optional[str] = None,
        memory_type: Optional[Union[str, MemoryType]] = None,
    ) -> str:
        """
        Get a memory context for a query.

        Args:
            query (str): Search query
            client_name (Optional[str]): Filter by client name (default: None)
            memory_type (Optional[Union[str, MemoryType]]): Filter by memory type (default: None)

        Returns:
            str: Memory context
        """
        if not self.enabled:
            self.logger.debug("Memory integration is disabled, not getting memory context")
            return ""
        
        try:
            # Build the search query
            search_query = query
            
            # Add filters if specified
            if client_name:
                search_query = f"{search_query} client:{client_name}"
            
            if memory_type:
                memory_type_value = memory_type.value if isinstance(memory_type, MemoryType) else memory_type
                search_query = f"{search_query} type:{memory_type_value}"
            
            # Get memory context using the claude_dc_integration.py script
            result = self._run_memory_command("context", search_query)
            
            if not result:
                return ""
            
            self.logger.debug(f"Got memory context for query: {query}")
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to get memory context: {str(e)}")
            return ""

    def store_session_summary(self, session: Session, summary: str) -> bool:
        """
        Store a session summary in memory.

        Args:
            session (Session): Session
            summary (str): Session summary

        Returns:
            bool: Success flag
        """
        return self.store_memory(
            text=summary,
            client_name=session.client_name,
            memory_type=MemoryType.SESSION_SUMMARY,
            source_type="session",
            source_id=session.id,
            importance=7,
            metadata={
                "persona": session.persona_name,
                "session_type": session.session_type.value,
                "messages_count": str(session.messages_count),
                "duration_seconds": str(session.duration_seconds),
            },
            tags=["session_summary"] + session.tags,
        )

    def store_session_insight(
        self, session: Session, insight: str, importance: int = 6
    ) -> bool:
        """
        Store a session insight in memory.

        Args:
            session (Session): Session
            insight (str): Insight
            importance (int): Importance level from 1-10 (default: 6)

        Returns:
            bool: Success flag
        """
        return self.store_memory(
            text=insight,
            client_name=session.client_name,
            memory_type=MemoryType.INSIGHT,
            source_type="session",
            source_id=session.id,
            importance=importance,
            tags=["insight"] + session.tags,
        )

    def store_client_information(
        self, client_name: str, information: str, importance: int = 8
    ) -> bool:
        """
        Store client information in memory.

        Args:
            client_name (str): Name of the client
            information (str): Client information
            importance (int): Importance level from 1-10 (default: 8)

        Returns:
            bool: Success flag
        """
        return self.store_memory(
            text=information,
            client_name=client_name,
            memory_type=MemoryType.CLIENT_INFORMATION,
            source_type="client_profile",
            source_id=f"client_{client_name}",
            importance=importance,
            tags=["client_information"],
        )

    def get_client_context(self, client_name: str) -> str:
        """
        Get a memory context for a client.

        Args:
            client_name (str): Name of the client

        Returns:
            str: Memory context
        """
        return self.get_memory_context(
            query=f"client information for {client_name}",
            client_name=client_name,
        )

    def get_session_context(self, client_name: str, query: str) -> str:
        """
        Get a memory context for a session.

        Args:
            client_name (str): Name of the client
            query (str): Search query

        Returns:
            str: Memory context
        """
        return self.get_memory_context(
            query=query,
            client_name=client_name,
        )

    def _run_memory_command(self, command: str, content: str) -> Optional[str]:
        """
        Run a memory command using the claude_dc_integration.py script.

        Args:
            command (str): Command name (remember, recall, context, list)
            content (str): Command content

        Returns:
            Optional[str]: Command output or None if the command failed
        """
        try:
            # Check if script exists
            if not self.integration_script.exists():
                self.logger.error(f"Memory integration script not found: {self.integration_script}")
                return None
            
            # Build the command
            cmd = [
                sys.executable,
                str(self.integration_script),
                command,
                content,
            ]
            
            # Run the command
            result = subprocess.run(
                cmd,
                cwd=str(self.memory_dir),
                capture_output=True,
                text=True,
                check=False,
            )
            
            # Check for errors
            if result.returncode != 0:
                self.logger.error(f"Memory command failed: {result.stderr}")
                return None
            
            return result.stdout
        
        except Exception as e:
            self.logger.error(f"Failed to run memory command: {str(e)}")
            return None
