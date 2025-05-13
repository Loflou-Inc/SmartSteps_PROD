"""Insight generator for analyzing session data."""

import datetime
import json
from typing import Dict, List, Optional, Union, Any

from ..config import get_config_manager
from ..provider import ProviderManager
from ..provider.interface import MessageFormat, MessageRole, Message
from ..session import Session
from ..utils import get_logger
from .models import Insight, InsightCategory


class InsightGenerator:
    """
    Generator for extracting insights from session data.
    
    This class uses AI providers to analyze session content and generate
    meaningful insights across various categories like behavioral, emotional,
    cognitive, etc.
    """

    def __init__(self, provider_manager: Optional[ProviderManager] = None):
        """
        Initialize the insight generator.

        Args:
            provider_manager (Optional[ProviderManager]): Provider manager
                If None, a new ProviderManager will be created
        """
        self.logger = get_logger(__name__)
        self.config = get_config_manager().get()
        
        # Import here to avoid circular imports if not provided
        if provider_manager is None:
            from ..provider import ProviderManager
            self.provider_manager = ProviderManager()
        else:
            self.provider_manager = provider_manager
        
        self.logger.debug("Initialized insight generator")

    def generate_insights(
        self, 
        session: Session, 
        insight_types: Optional[List[str]] = None,
        provider_name: Optional[str] = None,
        max_insights: int = 10
    ) -> List[Insight]:
        """
        Generate insights from a session using AI.

        Args:
            session (Session): Session to analyze
            insight_types (Optional[List[str]]): Types of insights to generate
                If None, all types will be used
            provider_name (Optional[str]): Name of the provider to use
                If None, the default provider will be used
            max_insights (int): Maximum number of insights to generate

        Returns:
            List[Insight]: Generated insights
        """
        self.logger.info(f"Generating insights for session {session.id}")
        
        # Default insight types if not specified
        if insight_types is None:
            insight_types = [
                "behavioral", "cognitive", "emotional", "relational",
                "goal_related", "strength", "challenge", "pattern", 
                "progress", "strategy", "general"
            ]
        
        try:
            # Get the provider - we'll use whatever provider is available 
            # in testing mode too (mock provider), allowing more thorough testing
            provider = self.provider_manager.get_provider(provider_name)
            
            # Fall back to mock provider if requested provider not found
            if provider is None:
                self.logger.warning(f"Provider {provider_name} not found, trying mock provider")
                provider = self.provider_manager.get_provider("mock")
            
            # If no provider is available, use fallback insights
            if provider is None:
                self.logger.warning("No provider available, using fallback insights")
                return self._generate_fallback_insights(session, insight_types, max_insights)
            
            # Prepare the context for the AI
            system_prompt = self._build_system_prompt(insight_types)
            user_prompt = self._build_user_prompt(session)
            
            messages = [
                Message(role=MessageRole.SYSTEM, content=system_prompt),
                Message(role=MessageRole.CLIENT, content=user_prompt)  # Using CLIENT instead of USER
            ]
            
            # Get the response from the provider with timeout handling
            import time
            start_time = time.time()
            timeout = 5.0  # 5-second timeout
            
            try:
                response = provider.generate_response(
                    messages=messages,
                    temperature=0.3,  # Lower temperature for more consistent outputs
                    max_tokens=2000,  # Allow enough tokens for detailed insights
                    message_format=MessageFormat.JSON  # Request JSON output
                )
                elapsed_time = time.time() - start_time
                
                # If response takes too long in testing, use fallback
                if elapsed_time > timeout and self.config.app.environment == "testing":
                    self.logger.warning(f"Response generation timed out after {elapsed_time:.2f}s, using fallback")
                    return self._generate_fallback_insights(session, insight_types, max_insights)
                    
                # Parse the response
                insights = self._parse_ai_response(response.content, insight_types)
                
                # If we didn't get any valid insights, use fallback
                if not insights:
                    self.logger.warning("No valid insights parsed from provider response, using fallback")
                    return self._generate_fallback_insights(session, insight_types, max_insights)
                
                # Limit the number of insights
                insights = insights[:max_insights]
                
                self.logger.info(f"Generated {len(insights)} insights for session {session.id}")
                return insights
                
            except Exception as e:
                self.logger.error(f"Error generating response: {str(e)}")
                return self._generate_fallback_insights(session, insight_types, max_insights)
            
        except Exception as e:
            self.logger.error(f"Failed to generate insights: {str(e)}")
            self.logger.exception("Insight generation failed")
            # Fall back to fallback insights in case of failure
            return self._generate_fallback_insights(session, insight_types, max_insights)
    
    def _build_system_prompt(self, insight_types: List[str]) -> str:
        """
        Build the system prompt for insight generation.

        Args:
            insight_types (List[str]): Types of insights to generate

        Returns:
            str: System prompt
        """
        prompt = (
            "You are an expert therapeutic analysis system that specializes in extracting insights "
            "from conversation transcripts. Your task is to analyze the session transcript and "
            "generate meaningful insights that would be valuable for a therapist or facilitator.\n\n"
            
            "For each insight:\n"
            "1. Focus on the content and patterns in the conversation\n"
            "2. Identify meaningful observations about the client's thoughts, feelings, behaviors, or patterns\n"
            "3. Provide specific evidence from the conversation\n"
            "4. Assign a confidence level (0.0-1.0) based on how strongly the evidence supports the insight\n\n"
            
            "You should generate insights in the following categories:\n"
        )
        
        # Add descriptions for each insight type
        type_descriptions = {
            "behavioral": "Observable actions, habits, and behavioral patterns",
            "cognitive": "Thinking patterns, beliefs, thought processes, and cognitive distortions",
            "emotional": "Emotional states, emotional regulation, and emotional patterns",
            "relational": "How the client relates to others, relationship dynamics, and interpersonal patterns",
            "goal_related": "Progress toward stated goals, obstacles to goals, and alignment with values",
            "strength": "Client's resources, abilities, and positive qualities",
            "challenge": "Obstacles, difficulties, and areas for growth",
            "pattern": "Recurring themes, behaviors, or situations",
            "progress": "Changes, improvements, and developments over time",
            "strategy": "Potential approaches, techniques, or interventions that might be helpful",
            "general": "Overall observations about the session or client"
        }
        
        # Add only the requested insight types
        for insight_type in insight_types:
            if insight_type in type_descriptions:
                prompt += f"- {insight_type.capitalize()}: {type_descriptions[insight_type]}\n"
        
        prompt += (
            "\nYour response must be in JSON format with the following structure:\n"
            "{\n"
            '  "insights": [\n'
            "    {\n"
            '      "text": "The client shows a pattern of self-criticism when discussing work achievements",\n'
            '      "category": "cognitive",\n'
            '      "confidence": 0.85,\n'
            '      "evidence": ["In message 4, the client says...", "Later, when discussing..."]\n'
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n\n"
            "Ensure your response is valid JSON. Generate varied insights across the requested categories."
        )
        
        return prompt
    
    def _build_user_prompt(self, session: Session) -> str:
        """
        Build the user prompt containing the session information.

        Args:
            session (Session): Session to analyze

        Returns:
            str: User prompt
        """
        # Get session metadata
        session_info = (
            f"Session Information:\n"
            f"- Client: {session.client_name}\n"
            f"- Date: {session.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"- Duration: {session.duration_seconds // 60} minutes\n"
            f"- Number of messages: {session.messages_count}\n"
        )
        
        # Add tags if available
        if session.tags:
            session_info += f"- Tags: {', '.join(session.tags)}\n"
        
        # Add notes if available
        if hasattr(session, 'notes') and session.notes:
            session_info += f"- Session notes: {session.notes}\n"
        
        # Get conversation transcript
        transcript = session.get_conversation_text(include_role=True, include_timestamps=True)
        
        # Combine information
        prompt = f"{session_info}\n\nConversation Transcript:\n\n{transcript}\n\nPlease analyze this session and provide insights."
        
        return prompt
    
    def _parse_ai_response(self, response_text: str, insight_types: List[str]) -> List[Insight]:
        """
        Parse the AI response to extract insights.

        Args:
            response_text (str): Response from the AI provider
            insight_types (List[str]): Types of insights that were requested

        Returns:
            List[Insight]: Parsed insights
        """
        insights = []
        
        try:
            # Try to parse the JSON response
            response_json = self._extract_json_from_text(response_text)
            
            if isinstance(response_json, dict) and "insights" in response_json:
                for insight_data in response_json["insights"]:
                    try:
                        # Get category and ensure it's valid
                        category_str = insight_data.get("category", "general").lower()
                        try:
                            category = InsightCategory(category_str)
                        except ValueError:
                            # Default to general if category is invalid
                            self.logger.warning(f"Invalid insight category: {category_str}, using general")
                            category = InsightCategory.GENERAL
                        
                        # Create the insight
                        insight = Insight(
                            text=insight_data["text"],
                            category=category,
                            confidence=float(insight_data.get("confidence", 0.8)),
                            evidence=insight_data.get("evidence", []),
                            metadata={"source": "ai"}
                        )
                        
                        insights.append(insight)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse insight: {str(e)}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {str(e)}")
            self.logger.error(f"Response text: {response_text}")
            # Return empty list in case of parsing failure
            return insights
    
    def _extract_json_from_text(self, text: str) -> Dict:
        """
        Extract JSON from text that might contain non-JSON elements.

        Args:
            text (str): Text that might contain JSON

        Returns:
            Dict: Extracted JSON or empty dict if parsing fails
        """
        try:
            # First try to parse the entire text as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # If that fails, try to find JSON between curly braces
            import re
            json_pattern = r'\{[\s\S]*\}'
            match = re.search(json_pattern, text)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            
            # If all else fails, return empty dict
            return {}
    
    def _generate_fallback_insights(
        self, session: Session, insight_types: List[str], max_insights: int = 10
    ) -> List[Insight]:
        """
        Generate fallback insights through basic text analysis.

        Args:
            session (Session): Session to analyze
            insight_types (List[str]): Types of insights to generate
            max_insights (int): Maximum number of insights to generate

        Returns:
            List[Insight]: Fallback insights based on basic text analysis
        """
        self.logger.info(f"Generating fallback insights for session {session.id}")
        
        insights = []
        
        # Get conversation text
        conversation_text = session.get_conversation_text(include_role=True)
        
        # Basic text analysis for emotional content
        emotional_terms = {
            "anxiety": ["anxious", "worried", "nervous", "panic", "fear", "stress", "tension"],
            "sadness": ["sad", "depressed", "down", "unhappy", "grief", "sorrow", "blue"],
            "anger": ["angry", "frustrated", "upset", "mad", "irritated", "annoyed", "rage"],
            "joy": ["happy", "joy", "excited", "pleased", "glad", "content", "satisfied"],
        }
        
        # Check for emotional terms
        detected_emotions = {}
        for emotion, terms in emotional_terms.items():
            count = 0
            for term in terms:
                # Count occurrences of the term in the conversation
                count += conversation_text.lower().count(term)
            if count > 0:
                detected_emotions[emotion] = count
        
        # Generate insights based on detected emotions
        for emotion, count in sorted(detected_emotions.items(), key=lambda x: x[1], reverse=True):
            if len(insights) >= max_insights:
                break
                
            # Only include emotions with significant presence
            if count > 1:
                text = f"The client expresses {emotion} during the session, which appears {count} times in the conversation."
                insight = Insight(
                    text=text,
                    category=InsightCategory.EMOTIONAL,
                    confidence=min(0.5 + (count * 0.05), 0.9),  # Higher count = higher confidence, max 0.9
                    evidence=[f"Found {count} instances of {emotion}-related terms"],
                    metadata={"source": "fallback", "emotion": emotion, "count": str(count)}
                )
                insights.append(insight)
        
        # Basic session structure analysis
        message_count = session.messages_count
        client_messages = sum(1 for msg in session.messages if msg.role == MessageRole.CLIENT)
        
        if message_count > 10 and len(insights) < max_insights:
            engagement_level = "high" if client_messages > (message_count * 0.4) else "moderate"
            text = f"The client shows {engagement_level} engagement with {client_messages} messages out of {message_count} total messages."
            insight = Insight(
                text=text,
                category=InsightCategory.BEHAVIORAL,
                confidence=0.8,
                evidence=[f"Client message count: {client_messages}", f"Total message count: {message_count}"],
                metadata={"source": "fallback", "client_messages": str(client_messages)}
            )
            insights.append(insight)
        
        # Analyze message length patterns
        if len(insights) < max_insights:
            client_msg_lengths = [len(msg.content) for msg in session.messages if msg.role == MessageRole.CLIENT]
            if client_msg_lengths:
                avg_length = sum(client_msg_lengths) / len(client_msg_lengths)
                if avg_length < 50:
                    verbosity = "brief and concise"
                    confidence = 0.7
                elif avg_length < 150:
                    verbosity = "moderately detailed"
                    confidence = 0.8
                else:
                    verbosity = "highly detailed and verbose"
                    confidence = 0.9
                    
                text = f"The client's communication style is {verbosity}, with an average message length of {int(avg_length)} characters."
                insight = Insight(
                    text=text,
                    category=InsightCategory.PATTERN,
                    confidence=confidence,
                    evidence=[f"Average client message length: {int(avg_length)} characters"],
                    metadata={"source": "fallback", "avg_length": str(int(avg_length))}
                )
                insights.append(insight)
        
        # Add general fallback insight if we still don't have enough
        if not insights:
            text = "Basic analysis indicates this conversation would benefit from more in-depth analysis."
            insight = Insight(
                text=text,
                category=InsightCategory.GENERAL,
                confidence=0.6,
                evidence=["Generated as fallback insight due to insufficient data"],
                metadata={"source": "fallback"}
            )
            insights.append(insight)
        
        self.logger.info(f"Generated {len(insights)} fallback insights for session {session.id}")
        return insights
