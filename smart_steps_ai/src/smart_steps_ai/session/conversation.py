"""Conversation handler for interactive sessions."""

import datetime
import time
from typing import Dict, List, Optional, Union, Any

from ..config import get_config_manager
from ..memory import MemoryManager
from ..utils import get_logger
from .manager import SessionManager
from .models import Message, MessageRole, Session, SessionState


class ConversationHandler:
    """
    Handler for interactive conversations in sessions.
    
    This class manages the flow of messages between clients and AI providers,
    handling context management, provider selection, and response processing.
    """

    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        provider_manager: Optional[Any] = None,
        memory_manager: Optional[MemoryManager] = None,
    ):
        """
        Initialize the conversation handler.

        Args:
            session_manager (Optional[SessionManager]): Session manager
                If None, a new SessionManager will be created
            provider_manager (Optional[Any]): Provider manager
                If None, a new ProviderManager will be created
            memory_manager (Optional[MemoryManager]): Memory manager
                If None, a new MemoryManager will be created
        """
        self.logger = get_logger(__name__)
        self.config = get_config_manager().get()
        
        # Import here to avoid circular imports
        from ..provider import ProviderManager
        from ..provider.context import ContextManager
        
        # Initialize managers
        self.session_manager = session_manager or SessionManager()
        self.provider_manager = provider_manager or ProviderManager()
        self.memory_manager = memory_manager or MemoryManager()
        
        # Create context manager
        self.context_manager = ContextManager(memory_manager=self.memory_manager)
        
        self.logger.debug("Initialized conversation handler")

    def send_message(
        self,
        session_id: str,
        message: str,
        role: MessageRole = MessageRole.CLIENT,
        provider_name: Optional[str] = None,
        **kwargs,
    ) -> tuple[Optional[Message], Optional[Message]]:
        """
        Send a message in a session and get a response.

        Args:
            session_id (str): ID of the session
            message (str): Message content
            role (MessageRole): Role of the sender (default: MessageRole.CLIENT)
            provider_name (Optional[str]): Name of the provider to use (default: None)
                If None, uses the default provider from the configuration
            **kwargs: Additional provider-specific parameters

        Returns:
            tuple[Optional[Message], Optional[Message]]: 
                Tuple of (client message, assistant response) or (None, None) if failed
        """
        try:
            # Get the session
            session = self.session_manager.get_session(session_id)
            if not session:
                self.logger.error(f"Session not found: {session_id}")
                return None, None
            
            # Check if the session is active
            if session.state not in [SessionState.CREATED, SessionState.ACTIVE]:
                self.logger.warning(f"Session {session_id} is not active (state: {session.state})")
                
                # If the session is paused, resume it
                if session.state == SessionState.PAUSED:
                    self.session_manager.update_session_state(session_id, SessionState.ACTIVE)
                    self.logger.info(f"Resumed session {session_id}")
                else:
                    return None, None
            
            # Add the client message to the session
            client_message = self.session_manager.add_message(
                session_id=session_id,
                role=role,
                content=message,
            )
            
            # Get a response from the AI provider
            response_message = self._get_provider_response(
                session=session,
                provider_name=provider_name,
                **kwargs,
            )
            
            if not response_message:
                self.logger.error(f"Failed to get response from provider for session {session_id}")
                return client_message, None
            
            return client_message, response_message
        
        except Exception as e:
            self.logger.error(f"Failed to send message in session {session_id}: {str(e)}")
            return None, None

    def _get_provider_response(
        self,
        session: Session,
        provider_name: Optional[str] = None,
        **kwargs,
    ) -> Optional[Message]:
        """
        Get a response from an AI provider for a session.

        Args:
            session (Session): Session to get a response for
            provider_name (Optional[str]): Name of the provider to use (default: None)
                If None, uses the default provider from the configuration
            **kwargs: Additional provider-specific parameters

        Returns:
            Optional[Message]: Response message or None if failed
        """
        try:
            # Get the provider
            provider = self.provider_manager.get_provider(provider_name)
            if not provider:
                self.logger.error(f"Provider not found: {provider_name or 'default'}")
                return None
            
            # Prepare context for the request
            system_prompt, filtered_messages = self.context_manager.prepare_session_context(
                session=session,
                max_messages=session.config.max_history_length,
            )
            
            # Record start time for latency measurement
            start_time = time.time()
            
            # Get a response from the provider
            response = provider.generate_response(
                messages=filtered_messages,
                system_prompt=system_prompt,
                **kwargs,
            )
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Check for errors
            if response.error:
                self.logger.error(f"Provider error: {response.error}")
                return None
            
            # Add the response to the session
            response_message = self.session_manager.add_message(
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content=response.content,
                metadata={
                    "provider": provider.name,
                    "model": response.model,
                    "latency_ms": str(latency_ms),
                    "tokens_input": str(response.usage.get("input_tokens", 0)),
                    "tokens_output": str(response.usage.get("output_tokens", 0)),
                },
            )
            
            # Store important information in memory
            self._store_response_memories(session, response)
            
            return response_message
        
        except Exception as e:
            self.logger.error(f"Failed to get provider response: {str(e)}")
            return None

    def _store_response_memories(self, session: Session, response: Any) -> None:
        """
        Store important information from a provider response in memory.

        Args:
            session (Session): Session the response is for
            response (Any): Provider response
        """
        # Skip if memory system is not enabled
        if not self.memory_manager.enabled:
            return
        
        # For now, we'll just store the response as a basic memory
        # In a real implementation, this would analyze the response for important insights
        
        # Check if the response is long enough to be worth storing
        if len(response.content) > 100:
            self.memory_manager.store_memory(
                text=response.content,
                client_name=session.client_name,
                memory_type="observation",
                source_type="session",
                source_id=session.id,
                importance=5,  # Medium importance
            )

    def get_conversation_history(
        self, session_id: str, max_messages: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get the conversation history for a session.

        Args:
            session_id (str): ID of the session
            max_messages (Optional[int]): Maximum number of messages to return

        Returns:
            Optional[List[Dict[str, Any]]]: Conversation history or None if failed
        """
        try:
            # Get the session
            session = self.session_manager.get_session(session_id)
            if not session:
                self.logger.error(f"Session not found: {session_id}")
                return None
            
            # Get the messages
            messages = session.get_conversation_history(max_messages)
            
            # Format messages for display
            formatted_messages = []
            for message in messages:
                formatted_messages.append({
                    "id": message.id,
                    "role": message.role.value,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat(),
                    "metadata": message.metadata,
                })
            
            return formatted_messages
        
        except Exception as e:
            self.logger.error(f"Failed to get conversation history for session {session_id}: {str(e)}")
            return None

    def create_new_session(
        self,
        client_name: str,
        persona_name: Optional[str] = None,
        session_type: str = "standard",
        initial_message: Optional[str] = None,
        provider_name: Optional[str] = None,  # Added provider_name parameter
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new session and optionally send an initial message.

        Args:
            client_name (str): Name of the client
            persona_name (Optional[str]): Name of the persona (default: None)
            session_type (str): Type of session (default: "standard")
            initial_message (Optional[str]): Initial message to send (default: None)
            provider_name (Optional[str]): Name of the provider to use (default: None)

        Returns:
            Optional[Dict[str, Any]]: Session information or None if failed
        """
        try:
            # Create a new session
            session = self.session_manager.create_session(
                client_name=client_name,
                persona_name=persona_name,
                session_type=session_type,
            )
            
            # If an initial message is provided, send it
            if initial_message:
                client_msg, assistant_msg = self.send_message(
                    session_id=session.id,
                    message=initial_message,
                    provider_name=provider_name,  # Pass along the provider name
                )
                
                # If the assistant didn't respond, log a warning
                if not assistant_msg:
                    self.logger.warning(f"No assistant response for initial message in session {session.id}")
            
            # Return session information
            return {
                "id": session.id,
                "client_name": session.client_name,
                "persona_name": session.persona_name,
                "session_type": session.session_type.value,
                "created_at": session.created_at.isoformat(),
                "state": session.state.value,
            }
        
        except Exception as e:
            self.logger.error(f"Failed to create new session: {str(e)}")
            return None
