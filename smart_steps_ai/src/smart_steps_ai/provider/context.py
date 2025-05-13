"""Context management for AI providers."""

import datetime
from typing import Dict, List, Optional, Union, Any

from ..memory import MemoryManager
from ..session.models import Message, MessageRole, Session
from ..utils import get_logger


class ContextManager:
    """
    Manager for context enrichment in AI provider requests.
    
    This class handles adding relevant context to AI requests based on session
    history, memory, and persona configuration.
    """

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """
        Initialize the context manager.

        Args:
            memory_manager (Optional[MemoryManager]): Memory manager for retrieving context
                If None, a new MemoryManager will be created
        """
        self.logger = get_logger(__name__)
        self.memory_manager = memory_manager or MemoryManager()

    def enrich_system_prompt(self, session: Session, base_prompt: str) -> str:
        """
        Enrich a system prompt with context for the session.

        Args:
            session (Session): The session to get context for
            base_prompt (str): The base system prompt to enrich

        Returns:
            str: Enriched system prompt
        """
        # Start with the base prompt
        enriched_prompt = base_prompt
        
        # Add persona context if available
        persona_context = self._get_persona_context(session)
        if persona_context:
            enriched_prompt += f"\n\n{persona_context}"
        
        # Add client context from memory
        client_context = self._get_client_context(session)
        if client_context:
            enriched_prompt += f"\n\n{client_context}"
        
        # Add session-specific context
        session_context = self._get_session_context(session)
        if session_context:
            enriched_prompt += f"\n\n{session_context}"
        
        self.logger.debug(f"Enriched system prompt for session {session.id}")
        return enriched_prompt

    def _get_persona_context(self, session: Session) -> str:
        """
        Get persona-specific context for the session.

        Args:
            session (Session): The session to get context for

        Returns:
            str: Persona context
        """
        # Extract relevant information from the persona metadata
        persona = session.persona_metadata
        
        context = f"You are acting as {persona.display_name}, a professional {persona.name}."
        
        # Add any additional role-specific context
        if persona.name == "professional_therapist":
            context += " As a therapist, prioritize empathetic listening, validation, and providing appropriate guidance."
        elif persona.name == "behavioral_analyst":
            context += " As a behavioral analyst, focus on observable behaviors, patterns, and evidence-based strategies."
        
        return context

    def _get_client_context(self, session: Session) -> str:
        """
        Get client-specific context from memory.

        Args:
            session (Session): The session to get client context for

        Returns:
            str: Client context
        """
        # Skip if memory system is not enabled
        if not self.memory_manager.enabled:
            return ""
        
        # Get client context from memory
        context = self.memory_manager.get_client_context(session.client_name)
        
        if context:
            return f"Client information:\n{context}"
        
        return ""

    def _get_session_context(self, session: Session) -> str:
        """
        Get session-specific context.

        Args:
            session (Session): The session to get context for

        Returns:
            str: Session context
        """
        context_parts = []
        
        # Add session type
        context_parts.append(f"This is a {session.session_type.value} session.")
        
        # Add session history summary if it's not the first session
        if self.memory_manager.enabled:
            # Query for past session summaries
            past_sessions = self.memory_manager.retrieve_memories(
                query=f"session summary for {session.client_name}",
                client_name=session.client_name,
                max_results=2,
            )
            
            if past_sessions:
                context_parts.append("Previous session summary:")
                for summary in past_sessions:
                    context_parts.append(f"- {summary}")
        
        # Add session tags if available
        if session.tags:
            context_parts.append(f"Session focus areas: {', '.join(session.tags)}")
        
        # Add custom fields if available
        if session.custom_fields:
            context_parts.append("Additional session information:")
            for key, value in session.custom_fields.items():
                context_parts.append(f"- {key}: {value}")
        
        return "\n".join(context_parts)

    def filter_messages(
        self, messages: List[Message], max_messages: Optional[int] = None
    ) -> List[Message]:
        """
        Filter and limit messages to include in a request.

        Args:
            messages (List[Message]): Messages to filter
            max_messages (Optional[int]): Maximum number of messages to include

        Returns:
            List[Message]: Filtered messages
        """
        # Start by removing internal messages
        filtered = [msg for msg in messages if msg.role != MessageRole.INTERNAL]
        
        # Limit to max_messages if specified
        if max_messages and len(filtered) > max_messages:
            # Keep the most recent messages
            filtered = filtered[-max_messages:]
        
        return filtered

    def prepare_session_context(
        self, 
        session: Session, 
        max_messages: Optional[int] = None,
        include_memory: bool = True,
    ) -> tuple[str, List[Message]]:
        """
        Prepare the full context for a session.

        Args:
            session (Session): The session to prepare context for
            max_messages (Optional[int]): Maximum number of messages to include
            include_memory (bool): Whether to include memory context

        Returns:
            tuple[str, List[Message]]: Enriched system prompt and filtered messages
        """
        # Get the persona's system prompt
        base_prompt = session.persona_metadata.description
        
        # Enrich the system prompt with context
        system_prompt = self.enrich_system_prompt(session, base_prompt)
        
        # Filter and limit messages
        filtered_messages = self.filter_messages(session.messages, max_messages)
        
        return system_prompt, filtered_messages
