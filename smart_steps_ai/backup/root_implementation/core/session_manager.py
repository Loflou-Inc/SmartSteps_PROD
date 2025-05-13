"""
Session management for the Smart Steps AI module.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple

from ..utils.logging import get_logger
from ..utils.validation import is_valid_session_id, is_valid_client_id, is_valid_session_type
from .config_manager import ConfigManager
from .persona_manager import PersonaManager, Persona
from .memory_manager import MemoryManager
from ..persistence.persistence_manager import PersistenceManager

# Get logger
logger = get_logger("core.session_manager")

class Session:
    """
    Represents a session with a client.
    
    Contains session data, messages, and metadata.
    """
    
    def __init__(self, session_id: str, client_id: str, session_type: str,
                facilitator_id: Optional[str] = None, persona: Optional[Persona] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a session.
        
        Args:
            session_id: The session ID.
            client_id: The client ID.
            session_type: The session type.
            facilitator_id: The facilitator ID.
            persona: The persona to use for the session.
            metadata: Additional metadata for the session.
        """
        self.session_id = session_id
        self.client_id = client_id
        self.session_type = session_type
        self.facilitator_id = facilitator_id
        self.persona = persona
        self.start_time = datetime.now()
        self.end_time = None
        self.messages = []
        self.metadata = metadata or {}
        self.is_first_session = True  # This would be determined from client history
        
        logger.debug(f"Initialized session {session_id} for client {client_id}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a message to the session.
        
        Args:
            role: The role of the message sender (e.g., "user", "assistant").
            content: The message content.
            metadata: Additional metadata for the message.
            
        Returns:
            The added message.
        """
        timestamp = datetime.now()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp.isoformat(),
            "metadata": metadata or {}
        }
        
        self.messages.append(message)
        
        logger.debug(f"Added {role} message to session {self.session_id}")
        
        return message
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the session message history.
        
        Returns:
            The message history.
        """
        return self.messages
    
    def get_history_as_text(self) -> str:
        """
        Get the session message history as formatted text.
        
        Returns:
            The message history as text.
        """
        text = ""
        
        for message in self.messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                text += f"Client: {content}\n\n"
            elif role == "assistant":
                text += f"Assistant: {content}\n\n"
            else:
                text += f"{role.capitalize()}: {content}\n\n"
        
        return text
    
    def get_formatted_prompt(self, user_input: str, memory_context: Optional[str] = None) -> str:
        """
        Get a formatted prompt for the AI.
        
        Args:
            user_input: The user input.
            memory_context: Optional memory context.
            
        Returns:
            The formatted prompt.
        """
        if not self.persona:
            # Create a basic prompt if no persona is available
            prompt = "You are a helpful assistant.\n\n"
            
            # Add session history
            for message in self.messages:
                role = message["role"]
                content = message["content"]
                
                if role == "user":
                    prompt += f"Client: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
            
            # Add memory context if available
            if memory_context:
                prompt += f"\n{memory_context}\n"
            
            # Add the user input
            prompt += f"\nClient: {user_input}\nAssistant: "
            
            return prompt
        
        # Use the persona to format the prompt
        context = {
            "client_name": self.metadata.get("client_name", ""),
            "session_type": self.session_type,
            "is_first_session": self.is_first_session,
            "session_history": self.messages,
            "memory_context": memory_context
        }
        
        return self.persona.format_prompt(user_input, context)
    
    def end_session(self) -> Dict[str, Any]:
        """
        End the session and generate a summary.
        
        Returns:
            A session summary.
        """
        self.end_time = datetime.now()
        
        # Generate a basic summary
        summary = {
            "session_id": self.session_id,
            "client_id": self.client_id,
            "facilitator_id": self.facilitator_id,
            "session_type": self.session_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": (self.end_time - self.start_time).total_seconds() / 60,
            "message_count": len(self.messages)
        }
        
        logger.debug(f"Ended session {self.session_id}")
        
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the session to a dictionary.
        
        Returns:
            The session as a dictionary.
        """
        return {
            "session_id": self.session_id,
            "client_id": self.client_id,
            "facilitator_id": self.facilitator_id,
            "session_type": self.session_type,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "messages": self.messages,
            "metadata": self.metadata,
            "is_first_session": self.is_first_session
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], persona: Optional[Persona] = None) -> 'Session':
        """
        Create a session from a dictionary.
        
        Args:
            data: The session data.
            persona: The persona to use for the session.
            
        Returns:
            A new Session instance.
        """
        session = cls(
            session_id=data["session_id"],
            client_id=data["client_id"],
            session_type=data["session_type"],
            facilitator_id=data.get("facilitator_id"),
            persona=persona,
            metadata=data.get("metadata", {})
        )
        
        # Restore session times
        if "start_time" in data:
            try:
                session.start_time = datetime.fromisoformat(data["start_time"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid start_time format in session data: {data['start_time']}")
        
        if "end_time" in data and data["end_time"]:
            try:
                session.end_time = datetime.fromisoformat(data["end_time"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid end_time format in session data: {data['end_time']}")
        
        # Restore messages
        session.messages = data.get("messages", [])
        
        # Restore first session flag
        session.is_first_session = data.get("is_first_session", True)
        
        return session

class SessionManager:
    """
    Manages sessions for the Smart Steps AI module.
    
    Creates, tracks, and persists sessions.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None,
                persona_manager: Optional[PersonaManager] = None,
                memory_manager: Optional[MemoryManager] = None,
                persistence_manager: Optional[PersistenceManager] = None):
        """
        Initialize the session manager.
        
        Args:
            config_manager: The configuration manager to use.
            persona_manager: The persona manager to use.
            memory_manager: The memory manager to use.
            persistence_manager: The persistence manager to use.
        """
        self.config_manager = config_manager or ConfigManager()
        self.persona_manager = persona_manager or PersonaManager(self.config_manager)
        self.memory_manager = memory_manager or MemoryManager(self.config_manager)
        self.persistence_manager = persistence_manager or PersistenceManager(self.config_manager)
        
        # Active sessions
        self.active_sessions = {}
        
        # Session timeout in seconds
        self.session_timeout = self.config_manager.get_config("session.session_timeout", 3600)
        
        logger.debug(f"Initialized SessionManager with {len(self.active_sessions)} active sessions")
    
    def create_session(self, client_id: str, session_type: str,
                     facilitator_id: Optional[str] = None,
                     persona_name: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session.
        
        Args:
            client_id: The client ID.
            session_type: The session type.
            facilitator_id: The facilitator ID.
            persona_name: The name of the persona to use.
            metadata: Additional metadata for the session.
            
        Returns:
            The session ID.
            
        Raises:
            ValueError: If the input parameters are invalid.
        """
        # Validate input
        if not is_valid_client_id(client_id):
            raise ValueError(f"Invalid client ID: {client_id}")
        
        if not is_valid_session_type(session_type):
            raise ValueError(f"Invalid session type: {session_type}")
        
        # Get the persona
        persona = None
        if persona_name:
            persona = self.persona_manager.get_persona(persona_name)
        else:
            # Use the default persona
            persona = self.persona_manager.get_default_persona()
        
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Create the session
        session = Session(
            session_id=session_id,
            client_id=client_id,
            session_type=session_type,
            facilitator_id=facilitator_id,
            persona=persona,
            metadata=metadata
        )
        
        # Add the session to the active sessions
        self.active_sessions[session_id] = session
        
        # Persist the session
        self.persistence_manager.save_session(session_id, session.to_dict())
        
        logger.info(f"Created session {session_id} for client {client_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: The session ID.
            
        Returns:
            The session, or None if not found.
        """
        # Check if the session is active
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Check if the session exists in persistence
        if not self.persistence_manager.session_exists(session_id):
            logger.warning(f"Session not found: {session_id}")
            return None
        
        # Load the session from persistence
        session_data = self.persistence_manager.load_session(session_id)
        
        if not session_data:
            logger.warning(f"Failed to load session {session_id}")
            return None
        
        # Get the persona
        persona = None
        persona_name = session_data.get("metadata", {}).get("persona_name")
        if persona_name:
            persona = self.persona_manager.get_persona(persona_name)
        
        # Create the session
        session = Session.from_dict(session_data, persona)
        
        # Add the session to active sessions
        self.active_sessions[session_id] = session
        
        logger.debug(f"Loaded session {session_id} from persistence")
        
        return session
    
    def end_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        End a session.
        
        Args:
            session_id: The session ID.
            
        Returns:
            A session summary, or None if the session was not found.
        """
        # Get the session
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        # End the session
        summary = session.end_session()
        
        # Update the session in persistence
        self.persistence_manager.save_session(session_id, session.to_dict())
        
        # Remove the session from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Ended session {session_id}")
        
        return summary
    
    def add_message_to_session(self, session_id: str, role: str, content: str,
                             metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Add a message to a session.
        
        Args:
            session_id: The session ID.
            role: The role of the message sender.
            content: The message content.
            metadata: Additional metadata for the message.
            
        Returns:
            The added message, or None if the session was not found.
        """
        # Get the session
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        # Add the message
        message = session.add_message(role, content, metadata)
        
        # Update the session in persistence
        self.persistence_manager.save_session(session_id, session.to_dict())
        
        logger.debug(f"Added {role} message to session {session_id}")
        
        return message
    
    def get_ai_response(self, session_id: str, user_input: str) -> Optional[str]:
        """
        Get an AI response for a user input.
        
        Args:
            session_id: The session ID.
            user_input: The user input.
            
        Returns:
            The AI response, or None if the session was not found or an error occurred.
        """
        # Get the session
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        # Add the user message
        session.add_message("user", user_input)
        
        try:
            # Get memory context
            memory_context = None
            if self.memory_manager:
                memory_context = self.memory_manager.get_memory_context(session.client_id, user_input)
            
            # Format the prompt
            prompt = session.get_formatted_prompt(user_input, memory_context)
            
            # TODO: Get response from AI provider
            # This will be implemented in Phase 3: AI Provider Implementation
            # For now, return a placeholder response
            ai_response = "This is a placeholder response. AI provider implementation is coming in Phase 3."
            
            # Add the AI message
            session.add_message("assistant", ai_response)
            
            # Update the session in persistence
            self.persistence_manager.save_session(session_id, session.to_dict())
            
            # Process the conversation to extract and store key information
            if self.memory_manager:
                self.memory_manager.process_conversation(session.client_id, user_input, ai_response)
            
            logger.debug(f"Generated AI response for session {session_id}")
            
            return ai_response
        except Exception as e:
            logger.error(f"Error generating AI response for session {session_id}: {e}")
            return None
    
    def get_session_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get the history of a session.
        
        Args:
            session_id: The session ID.
            
        Returns:
            The session history, or None if the session was not found.
        """
        # Get the session
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        return session.get_history()
    
    def list_sessions(self, client_id: Optional[str] = None,
                    active_only: bool = False) -> List[Dict[str, Any]]:
        """
        List sessions.
        
        Args:
            client_id: Filter by client ID.
            active_only: Only include active sessions.
            
        Returns:
            A list of session metadata.
        """
        # Get all session IDs from persistence
        session_ids = self.persistence_manager.list_sessions()
        
        # Filter by client ID if specified
        if client_id:
            filtered_sessions = []
            
            for session_id in session_ids:
                # Load the session data
                session_data = self.persistence_manager.load_session(session_id)
                
                if session_data and session_data.get("client_id") == client_id:
                    # Check if the session is active if needed
                    if active_only and session_data.get("end_time") is not None:
                        continue
                    
                    # Add basic session metadata
                    filtered_sessions.append({
                        "session_id": session_id,
                        "session_type": session_data.get("session_type", ""),
                        "start_time": session_data.get("start_time", ""),
                        "end_time": session_data.get("end_time"),
                        "message_count": len(session_data.get("messages", []))
                    })
            
            return filtered_sessions
        
        # Include all sessions
        result = []
        
        for session_id in session_ids:
            # Load the session data
            session_data = self.persistence_manager.load_session(session_id)
            
            if session_data:
                # Check if the session is active if needed
                if active_only and session_data.get("end_time") is not None:
                    continue
                
                # Add basic session metadata
                result.append({
                    "session_id": session_id,
                    "client_id": session_data.get("client_id", ""),
                    "session_type": session_data.get("session_type", ""),
                    "start_time": session_data.get("start_time", ""),
                    "end_time": session_data.get("end_time"),
                    "message_count": len(session_data.get("messages", []))
                })
        
        return result
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: The session ID.
            
        Returns:
            True if the session was deleted successfully, False otherwise.
        """
        # Check if the session is active
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Delete the session from persistence
        return self.persistence_manager.delete_session(session_id)
    
    def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update the metadata of a session.
        
        Args:
            session_id: The session ID.
            metadata: The metadata to update.
            
        Returns:
            True if the metadata was updated successfully, False otherwise.
        """
        # Get the session
        session = self.get_session(session_id)
        
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        # Update the metadata
        session.metadata.update(metadata)
        
        # Update the session in persistence
        self.persistence_manager.save_session(session_id, session.to_dict())
        
        logger.debug(f"Updated metadata for session {session_id}")
        
        return True
