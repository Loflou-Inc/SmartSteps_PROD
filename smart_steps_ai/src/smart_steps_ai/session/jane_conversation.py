"""Enhanced conversation handler for Jane's persona."""

import re
import time
from typing import Dict, List, Optional, Union, Any, Tuple, Set

from ..config import get_config_manager
from ..memory import MemoryManager
from ..persona.enhanced_manager import EnhancedPersonaManager
from ..utils import get_logger
from .conversation import ConversationHandler
from .manager import SessionManager
from .models import Message, MessageRole, Session, SessionState


class JaneConversationHandler(ConversationHandler):
    """
    Enhanced conversation handler specifically for Jane's persona.
    
    This handler extends the basic ConversationHandler with special handling
    for Jane's biographical consistency and canonical detail management.
    """

    def __init__(
        self,
        session_manager: Optional[SessionManager] = None,
        provider_manager: Optional[Any] = None,
        memory_manager: Optional[MemoryManager] = None,
        enhanced_persona_manager: Optional[EnhancedPersonaManager] = None,
    ):
        """
        Initialize the Jane conversation handler.

        Args:
            session_manager (Optional[SessionManager]): Session manager
            provider_manager (Optional[Any]): Provider manager
            memory_manager (Optional[MemoryManager]): Memory manager
            enhanced_persona_manager (Optional[EnhancedPersonaManager]): Enhanced persona manager
        """
        # Call parent initializer
        super().__init__(session_manager, provider_manager, memory_manager)
        
        # Initialize the enhanced persona manager
        self.enhanced_persona_manager = enhanced_persona_manager or EnhancedPersonaManager()
        
        # Autobiographical categories
        self.autobiographical_categories = {
            "childhood", "family", "abuse", "trauma", "education", 
            "career", "therapy", "personal", "achievements", "relationships"
        }
        
        # Common biographical query patterns
        self.biographical_query_patterns = [
            r"what happened (?:when|at|during)(.+?)\?",
            r"tell me about (?:your|the)(.+?)\?",
            r"how did you feel when(.+?)\?",
            r"what was it like when(.+?)\?",
            r"(?:describe|explain) your experience(?:s)? with(.+?)\?",
            r"what do you remember about(.+?)\?",
            r"how did(.+?)affect you\?",
            r"(?:when|how) did(.+?)happen\?"
        ]
        
        self.logger.debug("Initialized Jane conversation handler")

    def send_message(
        self,
        session_id: str,
        message: str,
        role: MessageRole = MessageRole.CLIENT,
        provider_name: Optional[str] = None,
        **kwargs,
    ) -> Tuple[Optional[Message], Optional[Message]]:
        """
        Send a message in a session and get a response from Jane.
        
        This overrides the base send_message method to add Jane-specific processing.

        Args:
            session_id (str): ID of the session
            message (str): Message content
            role (MessageRole): Role of the sender (default: MessageRole.CLIENT)
            provider_name (Optional[str]): Name of the provider to use (default: None)
            **kwargs: Additional provider-specific parameters

        Returns:
            Tuple[Optional[Message], Optional[Message]]: 
                Tuple of (client message, assistant response) or (None, None) if failed
        """
        try:
            # Get the session
            session = self.session_manager.get_session(session_id)
            if not session:
                self.logger.error(f"Session not found: {session_id}")
                return None, None
                
            # Only apply special processing for Jane persona
            is_jane_session = session.persona_name == "jane-clinical-psychologist"
            
            # For Jane sessions, check if this is a biographical query
            if is_jane_session:
                # Get any relevant canonical details for this message
                relevant_details = self._get_relevant_biographical_details(message)
                
                # If there are relevant details, add them to the context
                if relevant_details:
                    # Include canonical details in provider context
                    kwargs['canonical_details'] = relevant_details
            
            # Call the parent method to send the message and get response
            client_msg, assistant_msg = super().send_message(
                session_id=session_id,
                message=message,
                role=role,
                provider_name=provider_name,
                **kwargs,
            )
            
            # For Jane sessions, extract and store any generated autobiographical details
            if is_jane_session and assistant_msg:
                self._extract_and_store_autobiographical_details(
                    session=session,
                    query=message,
                    response=assistant_msg.content
                )
            
            return client_msg, assistant_msg
        
        except Exception as e:
            self.logger.error(f"Failed to send message in Jane session {session_id}: {str(e)}")
            return None, None

    def _get_relevant_biographical_details(self, message: str) -> List[Dict[str, str]]:
        """
        Get relevant canonical details for a message.
        
        Args:
            message (str): Message content
            
        Returns:
            List[Dict[str, str]]: List of relevant canonical details
        """
        # Check if this is a biographical query
        if not self._is_biographical_query(message):
            return []
        
        # Get Jane's persona
        jane = self.enhanced_persona_manager.get_enhanced_persona("jane-clinical-psychologist")
        if not jane:
            self.logger.warning("Jane persona not found")
            return []
        
        # Extract potential categories from the message
        categories = self._extract_biographical_categories(message)
        
        # Get relevant details from both canonical details and life events
        details = []
        
        # First, check canonical details
        canonical_details = []
        for category in categories:
            # Add category-specific canonical details
            category_details = self.enhanced_persona_manager.get_canonical_details(
                persona_name="jane-clinical-psychologist",
                category=category
            )
            canonical_details.extend(category_details)
        
        # Also search by relevance
        relevant_details = self.enhanced_persona_manager.get_relevant_canonical_details(
            persona_name="jane-clinical-psychologist",
            query=message
        )
        
        # Combine and deduplicate
        all_details = {}
        for detail in canonical_details + relevant_details:
            if detail.id not in all_details:
                all_details[detail.id] = detail
        
        # Convert to format for provider context
        for detail_id, detail in all_details.items():
            details.append({
                "id": detail.id,
                "detail": detail.detail,
                "categories": ",".join(detail.categories),
                "usage_count": detail.usage_count
            })
            
            # Record usage
            self.enhanced_persona_manager.record_detail_usage(
                persona_name="jane-clinical-psychologist",
                detail_id=detail.id
            )
        
        # Get relevant life events as well
        if jane:
            for category in categories:
                life_events = jane.get_events_by_category(category)
                for event in life_events:
                    details.append({
                        "id": event.id,
                        "detail": f"{event.title}: {event.description}",
                        "categories": ",".join(event.categories),
                        "type": "life_event"
                    })
        
        # Sort by usage count (descending)
        details.sort(key=lambda d: d.get("usage_count", 0), reverse=True)
        
        return details[:5]  # Limit to top 5 most relevant details

    def _is_biographical_query(self, message: str) -> bool:
        """
        Determine if a message is a biographical query about Jane.
        
        Args:
            message (str): Message content
            
        Returns:
            bool: True if the message is a biographical query
        """
        message_lower = message.lower()
        
        # Check for first-person references
        has_first_person = any(term in message_lower for term in [
            "you", "your", "yourself", "yours", "when you", "did you", "were you"
        ])
        
        if not has_first_person:
            return False
        
        # Check for biographical patterns
        for pattern in self.biographical_query_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Check for keywords related to biographical information
        biographical_keywords = [
            "childhood", "grew up", "family", "parents", "siblings", "stepfather",
            "experience", "history", "past", "background", "remember", "felt", 
            "trauma", "education", "school", "university", "therapy", "healing",
            "marriage", "relationship", "career", "job", "work history"
        ]
        
        keyword_count = sum(1 for keyword in biographical_keywords if keyword in message_lower)
        
        return keyword_count >= 1

    def _extract_biographical_categories(self, message: str) -> Set[str]:
        """
        Extract relevant biographical categories from a message.
        
        Args:
            message (str): Message content
            
        Returns:
            Set[str]: Set of relevant biographical categories
        """
        message_lower = message.lower()
        
        # Check each category for relevant keywords
        categories = set()
        
        # Childhood
        if any(keyword in message_lower for keyword in ["childhood", "kid", "young", "grow up", "little", "youth"]):
            categories.add("childhood")
        
        # Family
        if any(keyword in message_lower for keyword in ["family", "parent", "mother", "father", "stepfather", "brother", "sister", "sibling"]):
            categories.add("family")
        
        # Abuse
        if any(keyword in message_lower for keyword in ["abuse", "hit", "hurt", "beat", "scream", "yell", "violence"]):
            categories.add("abuse")
        
        # Trauma
        if any(keyword in message_lower for keyword in ["trauma", "ptsd", "nightmare", "flashback", "scared", "afraid", "terrified"]):
            categories.add("trauma")
        
        # Education
        if any(keyword in message_lower for keyword in ["school", "college", "university", "study", "class", "education", "degree", "phd"]):
            categories.add("education")
        
        # Career
        if any(keyword in message_lower for keyword in ["job", "career", "work", "profession", "employment", "clinic", "hospital"]):
            categories.add("career")
        
        # Therapy
        if any(keyword in message_lower for keyword in ["therapy", "therapist", "counseling", "treatment", "recovery", "heal"]):
            categories.add("therapy")
        
        # Personal
        if any(keyword in message_lower for keyword in ["personal", "yourself", "your own", "your life", "your experience"]):
            categories.add("personal")
        
        # If no specific categories, add "personal" as a fallback
        if not categories:
            categories.add("personal")
        
        return categories

    def _extract_and_store_autobiographical_details(self, session: Session, query: str, response: str) -> None:
        """
        Extract and store autobiographical details from Jane's response.
        
        Args:
            session (Session): Current session
            query (str): Client query that prompted the response
            response (str): Jane's response
        """
        # Only process if this is a biographical query
        if not self._is_biographical_query(query):
            return
        
        # Get Jane's persona
        jane = self.enhanced_persona_manager.get_enhanced_persona("jane-clinical-psychologist")
        if not jane:
            self.logger.warning("Jane persona not found for detail extraction")
            return
        
        # Log for debugging
        self.logger.debug(f"Extracting autobiographical details from response: {response[:100]}...")
        
        # Extract sentences that might contain autobiographical information
        sentences = self._split_into_sentences(response)
        
        # Identify potential autobiographical sentences
        autobio_sentences = []
        
        for sentence in sentences:
            # Skip short sentences
            if len(sentence) < 15:
                continue
                
            # Check for first-person pronouns (indicators of autobiographical content)
            has_first_person = any(term in sentence.lower() for term in [
                " i ", "i've", "i'd", "i'll", "i'm", " me ", " my ", "myself", "mine"
            ])
            
            if has_first_person:
                # Add to candidates
                autobio_sentences.append(sentence)
                self.logger.debug(f"Found autobiographical candidate: {sentence}")
        
        # If we found potential autobiographical details
        if autobio_sentences:
            categories = self._extract_biographical_categories(query)
            
            # In a real implementation, we would use AI to determine if the sentence 
            # contains a specific biographical detail worth saving
            # For this implementation, we'll just take the longest sentence
            
            if autobio_sentences:
                # Get the longest one as it likely has the most detail
                autobio_sentences.sort(key=len, reverse=True)
                detail = autobio_sentences[0]
                
                # Store as canonical detail
                success, new_detail, error = self.enhanced_persona_manager.add_canonical_detail(
                    persona_name="jane-clinical-psychologist",
                    detail=detail,
                    context=query,
                    categories=list(categories),
                )
                
                if success and new_detail:
                    self.logger.info(f"Stored new canonical detail for Jane: {detail[:50]}...")
                else:
                    self.logger.warning(f"Failed to store canonical detail: {error}")
        else:
            self.logger.debug("No autobiographical sentences found in response")

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text (str): Text to split
            
        Returns:
            List[str]: List of sentences
        """
        # Simple sentence splitting - in a real implementation, 
        # this would use a more sophisticated approach
        text = text.replace("?", "?|").replace("!", "!|").replace(".", ".|")
        sentences = [s.strip() for s in text.split("|") if s.strip()]
        return sentences

    def _get_provider_response(
        self,
        session: Session,
        provider_name: Optional[str] = None,
        **kwargs,
    ) -> Optional[Message]:
        """
        Get a response from an AI provider for a session.
        
        Override to include Jane-specific processing.

        Args:
            session (Session): Session to get a response for
            provider_name (Optional[str]): Name of the provider to use (default: None)
            **kwargs: Additional provider-specific parameters

        Returns:
            Optional[Message]: Response message or None if failed
        """
        try:
            # Check if this is a Jane session
            is_jane_session = session.persona_name == "jane-clinical-psychologist"
            
            # For Jane sessions, enhance the system prompt with biographical information
            if is_jane_session:
                # Get canonical details from kwargs if available
                canonical_details = kwargs.pop('canonical_details', [])
                
                # Enhance the context with Jane-specific details
                enhanced_context = self._create_jane_specific_context(canonical_details)
                
                # Add to kwargs to be included in context
                kwargs['additional_context'] = enhanced_context
            
            # Call the parent method
            return super()._get_provider_response(
                session=session,
                provider_name=provider_name,
                **kwargs,
            )
        
        except Exception as e:
            self.logger.error(f"Failed to get Jane-specific provider response: {str(e)}")
            return None

    def _create_jane_specific_context(self, canonical_details: List[Dict[str, str]]) -> str:
        """
        Create Jane-specific context for the AI provider.
        
        Args:
            canonical_details (List[Dict[str, str]]): Canonical details to include
            
        Returns:
            str: Enhanced context
        """
        if not canonical_details:
            return ""
        
        context = "\n\nIMPORTANT BIOGRAPHICAL CONTEXT:\n"
        context += "When responding about your personal history, use the following details exactly. Do not make up any new details that contradict these:\n\n"
        
        for i, detail in enumerate(canonical_details, 1):
            context += f"{i}. {detail['detail']}\n"
        
        context += "\nIf asked about personal experiences not covered by these details, respond in a way that is consistent with them, maintaining psychological coherence with your trauma history and professional background."
        
        return context
