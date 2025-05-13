"""Jane-specific mock provider for testing."""

import datetime
import random
import time
from typing import Dict, List, Optional, Any

from ..utils import get_logger
from .interface import AIProvider, ProviderConfig, ProviderResponse
from .mock import MockProvider
from ..session.models import Message, MessageRole


class JaneMockProvider(MockProvider):
    """
    Mock provider specifically for Jane's persona.
    
    This class extends the basic MockProvider to generate responses
    that simulate Jane talking about her own experiences in the first person.
    """

    def __init__(self):
        """Initialize the Jane mock provider."""
        super().__init__()
        
        # Add Jane-specific response templates
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
        
    def initialize(self, config: ProviderConfig) -> bool:
        """
        Initialize the Jane mock provider.

        Args:
            config (ProviderConfig): Provider configuration

        Returns:
            bool: Success flag
        """
        # Call parent initialize
        success = super().initialize(config)
        
        if success:
            self.logger.info(f"Initialized Jane mock provider with model: {config.model}")
        
        return success

    def generate_response(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> ProviderResponse:
        """
        Generate a mock response as Jane.

        Args:
            messages (List[Message]): List of messages in the conversation
            system_prompt (Optional[str]): System prompt to use (default: None)
            **kwargs: Additional provider-specific parameters

        Returns:
            ProviderResponse: Mock response
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
        
        # Determine which topic the query is about
        response_content = ""
        
        # Check for abuse/trauma related questions
        if any(term in content for term in ["abuse", "trauma", "stepfather", "hurt", "childhood"]):
            response_content = random.choice(self.jane_templates["abuse"])
        
        # Check for therapy related questions
        elif any(term in content for term in ["therapy", "healing", "recovery", "your own experience"]):
            response_content = random.choice(self.jane_templates["therapy"])
        
        # Check for education related questions
        elif any(term in content for term in ["school", "college", "university", "study", "education", "phd"]):
            response_content = random.choice(self.jane_templates["education"])
        
        # Check for career related questions
        elif any(term in content for term in ["job", "career", "work", "profession"]):
            response_content = random.choice(self.jane_templates["career"])
        
        # Use default mock response if no specific topic was matched
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
        
        # Calculate mock usage
        input_tokens = sum(len(msg.content) // 4 for msg in messages)
        output_tokens = len(response_content) // 4
        
        # Create provider response
        result = ProviderResponse(
            content=response_content,
            raw_response={
                "model": self.config.model if self.config else "mock-jane",
                "content": response_content,
                "finish_reason": "stop",
            },
            model=self.config.model if self.config else "mock-jane",
            finish_reason="stop",
            usage={
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
            latency_ms=500,  # Simulated latency
            request_id=f"mock-jane-{datetime.datetime.now().timestamp()}",
            metadata={
                "provider": "mock",
                "model": "mock-jane",
                "is_biographical": "true"
            }
        )
        
        self.logger.debug(f"Generated Jane mock response: {response_content[:50]}...")
        return result