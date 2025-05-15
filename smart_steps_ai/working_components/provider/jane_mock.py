"""Jane-specific provider for the SmartSteps platform."""

import random
import time
import logging
import os
from typing import Dict, List, Optional, Any

from .message import Message, MessageRole
from .interface import ProviderConfig, ProviderResponse
from .mock import MockProvider

from smart_steps_ai.memory.models import MemoryType, MemoryStatus, JaneMemory
from smart_steps_ai.memory.store import MemoryStore
from smart_steps_ai.memory.retrieval import get_relevant_jane_memories


# Setup logging
logger = logging.getLogger(__name__)


class JaneMockProvider(MockProvider):
    """
    Mock provider specifically for Jane's persona.
    
    This class extends the basic MockProvider to generate responses
    that simulate Jane talking about her own experiences in the first person.
    It now uses the memory system for retrieving Jane's memories, falling back
    to templates only when no memories are found.
    """

    def __init__(self):
        """Initialize the Jane mock provider."""
        super().__init__()
        
        # Initialize the memory store
        memory_store_path = os.environ.get(
            "SMARTSTEPS_MEMORY_PATH", 
            os.path.join(os.path.dirname(__file__), "../../../memory_store")
        )
        os.makedirs(memory_store_path, exist_ok=True)
        
        try:
            self.memory_store = MemoryStore(memory_store_path)
            logger.info(f"Initialized memory store at {memory_store_path}")
        except Exception as e:
            logger.error(f"Failed to initialize memory store: {e}")
            self.memory_store = None
        
        # Add Jane-specific response templates as a fallback
        self.jane_templates = {
            "abuse": [
                "The last incident with my stepfather happened on my 16th birthday. He threw me against a wall when I asked to go out with friends. That was the day I finally told my mother everything.",
                "My stepfather's abuse started when I was 7. At first, it was just yelling and verbal humiliation, but by the time I was 10, it became physical.",
                "I remember hiding in my closet during many of those incidents. I would cover my ears and recite the multiplication tables to block out the sounds of his anger.",
                "The most difficult part of the abuse was the unpredictability. I never knew what would trigger his rage - sometimes it was my grades, sometimes it was just the way I looked at him.",
            ],
            "therapy": [
                "My own therapy journey started during graduate school. I initially resisted the idea that I needed help, but a caring mentor encouraged me to seek support.",
                "The breakthrough in my own therapy came when I realized that my perfectionism was actually a response to the chaos of my childhood. I needed to feel in control of something.",
                "I've been on both sides of the therapeutic relationship, and that's shaped how I approach my work. I know how vulnerable it feels to share your pain with someone.",
                "My personal healing process took years, and there were many setbacks. That's partly why I believe so deeply in the resilience of the human spirit.",
            ],
            "education": [
                "During my PhD at Northwestern, I focused my research on resilience factors in adult survivors of childhood trauma. It was deeply personal work.",
                "My undergraduate years at University of Michigan were challenging - I was still dealing with unprocessed trauma and didn't have good support systems yet.",
                "I struggled with imposter syndrome throughout my education. Despite my academic achievements, I always felt like someone would discover I didn't belong there.",
                "My dissertation committee didn't know that my research questions stemmed from my own experiences. I disclosed that to my advisor later, after graduation.",
            ],
            "career": [
                "I've been the Clinical Director at Lakeside Trauma Recovery Center since 2018. Before that, I worked at a university counseling center for about eight years.",
                "My first job after getting my license was at a community mental health center. The caseload was overwhelming, but I learned so much about different types of trauma.",
                "Working with trauma survivors has been healing for me too. Every client who rebuilds their life reinforces my belief that recovery is possible.",
                "I've always been drawn to clinical work more than research, though I do try to stay current with the trauma treatment literature.",
            ],
        }

    @property
    def name(self) -> str:
        """Get the name of the provider."""
        return "jane_mock"
        
    def generate_response(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """
        Generate a response as Jane, using memory system when possible.

        Args:
            messages (List[Message]): List of messages in the conversation
            system_prompt (Optional[str]): System prompt to use (default: None)
            **kwargs: Additional provider-specific parameters

        Returns:
            ProviderResponse: Response with Jane's memories or fallback
        """
        # Get the last message
        last_message = messages[-1] if messages else None
        
        if not last_message or last_message.role != MessageRole.CLIENT:
            return super().generate_response(messages, system_prompt, **kwargs)
        
        # Check if this might be a biographical query about Jane
        content = last_message.content.lower()
        
        # Look for first-person queries
        is_about_jane = any(term in content for term in [
            "you", "your", "yourself", "yours", "when you", "did you", "were you"
        ])
        
        if not is_about_jane:
            return super().generate_response(messages, system_prompt, **kwargs)
        
        # Try to retrieve relevant memories
        response_content = self._get_memory_response(content)
        
        # If no memories found, fall back to templates
        if not response_content:
            response_content = self._get_template_response(content)
        
        # If still no suitable response, use default mock
        if not response_content:
            return super().generate_response(messages, system_prompt, **kwargs)
        
        # Add a therapeutic redirection at the end
        redirections = [
            "\n\nBut enough about me - I'm curious about your experiences. How does hearing about this make you feel?",
            "\n\nI share this with you because it might help you understand my approach. How does this relate to your own situation?",
            "\n\nI don't usually share this much about myself, but I thought it might be relevant to what you're going through. Would you like to tell me more about your own experiences?",
            "\n\nNow, I'd like to shift our focus back to you. How does what I've shared resonate with your own journey?"
        ]
        
        response_content += random.choice(redirections)
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Create provider response
        result = ProviderResponse(
            content=response_content,
            model=self.config.model if self.config else "jane-with-memory"
        )
        
        return result
    
    def _get_memory_response(self, query: str) -> Optional[str]:
        """
        Get a response based on Jane's memories.
        
        Args:
            query: The user's query
            
        Returns:
            Response content if memories found, None otherwise
        """
        # Check if memory store is available
        if not self.memory_store:
            logger.warning("Memory store not available, falling back to templates")
            return None
        
        try:
            # Get relevant memories
            memories = get_relevant_jane_memories(query, self.memory_store)
            
            # If no memories found, log and return None
            if not memories:
                logger.info(f"memory.miss: No relevant memories for query '{query}'")
                return None
            
            # Use the most relevant memory's content
            memory = memories[0]
            logger.info(f"memory.hit: Found memory '{memory.id}' for query '{query}'")
            
            return memory.content
            
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return None
    
    def _get_template_response(self, query: str) -> Optional[str]:
        """
        Get a response from the template fallbacks.
        
        Args:
            query: The user's query
            
        Returns:
            Response content if template matched, None otherwise
        """
        # Check for abuse/trauma related questions
        if any(term in query for term in ["abuse", "trauma", "stepfather", "hurt", "childhood"]):
            return random.choice(self.jane_templates["abuse"])
        
        # Check for therapy related questions
        elif any(term in query for term in ["therapy", "healing", "recovery", "your own experience"]):
            return random.choice(self.jane_templates["therapy"])
        
        # Check for education related questions
        elif any(term in query for term in ["school", "college", "university", "study", "education", "phd"]):
            return random.choice(self.jane_templates["education"])
        
        # Check for career related questions
        elif any(term in query for term in ["job", "career", "work", "profession"]):
            return random.choice(self.jane_templates["career"])
        
        # No template matched
        return None
