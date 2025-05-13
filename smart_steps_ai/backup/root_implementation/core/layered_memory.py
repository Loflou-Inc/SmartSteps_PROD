"""
Layered memory system for the Smart Steps AI module.

This module implements a layered memory architecture with foundation,
experience, synthesis, and meta-cognitive layers for advanced personas
with performance optimizations.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path

from smart_steps_ai.core.knowledge_store import KnowledgeStore
from smart_steps_ai.core.cache_manager import (
    cache_manager, 
    performance_monitor,
    batch_processor
)


class MemoryLayer:
    """Base class for memory layers."""
    
    def __init__(self, persona_id: str, data_dir: Optional[str] = None):
        """
        Initialize the memory layer.
        
        Args:
            persona_id: ID of the persona
            data_dir: Directory to store memory data
        """
        self.persona_id = persona_id
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'memory')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)


class FoundationLayer(MemoryLayer):
    """
    Foundation layer of the layered memory architecture.
    
    This layer stores the immutable core knowledge of a persona,
    serving as the foundation for all other memory layers.
    """
    
    def __init__(self, persona_id: str, data_dir: Optional[str] = None):
        """
        Initialize the foundation layer.
        
        Args:
            persona_id: ID of the persona
            data_dir: Directory to store memory data
        """
        super().__init__(persona_id, data_dir)
        self.knowledge_store = KnowledgeStore()
        
        # Initialize knowledge collection if not exists
        self.knowledge_store.initialize_persona_knowledge(
            persona_id=persona_id,
            description=f"Foundation knowledge for persona {persona_id}"
        )
    
    def add_document(self, 
                    document_id: str,
                    content: str,
                    metadata: Optional[Dict] = None) -> List[str]:
        """
        Add a document to the foundation knowledge.
        
        Args:
            document_id: ID of the document
            content: Text content of the document
            metadata: Document metadata
            
        Returns:
            List of generated chunk IDs
        """
        return self.knowledge_store.add_document(
            persona_id=self.persona_id,
            document_id=document_id,
            content=content,
            metadata=metadata
        )
    
    def import_document(self, 
                      document_id: str,
                      file_path: str,
                      metadata: Optional[Dict] = None) -> List[str]:
        """
        Import a document from a file.
        
        Args:
            document_id: ID of the document
            file_path: Path to the document file
            metadata: Document metadata
            
        Returns:
            List of generated chunk IDs
        """
        return self.knowledge_store.import_document_from_file(
            persona_id=self.persona_id,
            document_id=document_id,
            file_path=file_path,
            metadata=metadata
        )
    
    def search(self, 
              query: str,
              limit: int = 5,
              filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Search the foundation knowledge.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List of matching chunks with similarity scores
        """
        return self.knowledge_store.search(
            persona_id=self.persona_id,
            query=query,
            limit=limit,
            filter_metadata=filter_metadata
        )
    
    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """
        Get foundation context for a query.
        
        Args:
            query: Context query
            max_tokens: Maximum number of tokens in the context
            
        Returns:
            Formatted context string
        """
        return self.knowledge_store.get_knowledge_context(
            persona_id=self.persona_id,
            query=query,
            max_tokens=max_tokens
        )


class ExperienceLayer(MemoryLayer):
    """
    Experience layer of the layered memory architecture.
    
    This layer stores the persona's experiences and interactions,
    serving as the memory of past conversations and events.
    """
    
    def __init__(self, persona_id: str, data_dir: Optional[str] = None):
        """
        Initialize the experience layer.
        
        Args:
            persona_id: ID of the persona
            data_dir: Directory to store memory data
        """
        super().__init__(persona_id, data_dir)
        self.experiences_file = os.path.join(self.data_dir, f"{persona_id}_experiences.json")
        self.experiences = self._load_experiences()
    
    def _load_experiences(self) -> Dict:
        """Load experiences from file."""
        if os.path.exists(self.experiences_file):
            try:
                with open(self.experiences_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading experiences: {str(e)}")
        
        # Return default structure
        return {
            "persona_id": self.persona_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "interactions": []
        }
    
    def _save_experiences(self):
        """Save experiences to file."""
        # Update timestamp
        self.experiences["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        with open(self.experiences_file, 'w') as f:
            json.dump(self.experiences, f, indent=2)
    
    def record_interaction(self, 
                         session_id: str,
                         client_message: str,
                         persona_response: str,
                         metadata: Optional[Dict] = None) -> str:
        """
        Record an interaction.
        
        Args:
            session_id: ID of the session
            client_message: Message from the client
            persona_response: Response from the persona
            metadata: Interaction metadata
            
        Returns:
            ID of the recorded interaction
        """
        # Generate interaction ID
        interaction_id = str(uuid.uuid4())
        
        # Create interaction entry
        interaction = {
            "id": interaction_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "exchange": {
                "client": client_message,
                "persona": persona_response
            },
            "metadata": metadata or {}
        }
        
        # Add to experiences
        self.experiences["interactions"].append(interaction)
        
        # Save experiences
        self._save_experiences()
        
        return interaction_id
    
    def get_session_interactions(self, session_id: str) -> List[Dict]:
        """
        Get all interactions for a session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            List of interaction dictionaries
        """
        return [
            interaction for interaction in self.experiences["interactions"]
            if interaction["session_id"] == session_id
        ]
    
    def search_interactions(self, 
                          query: str,
                          limit: int = 5,
                          session_id: Optional[str] = None) -> List[Dict]:
        """
        Search for relevant interactions.
        
        Args:
            query: Search query
            limit: Maximum number of results
            session_id: Filter by session ID
            
        Returns:
            List of matching interactions
        """
        # Simple keyword search for now
        # In a production system, this would use vector embeddings for semantic search
        query_terms = query.lower().split()
        
        # Filter interactions
        candidate_interactions = self.experiences["interactions"]
        if session_id:
            candidate_interactions = [
                interaction for interaction in candidate_interactions
                if interaction["session_id"] == session_id
            ]
        
        # Score interactions
        scored_interactions = []
        for interaction in candidate_interactions:
            # Combine client and persona messages
            text = (
                interaction["exchange"]["client"] + " " +
                interaction["exchange"]["persona"]
            ).lower()
            
            # Count matching terms
            score = sum(1 for term in query_terms if term in text)
            
            # Add to results if matching
            if score > 0:
                scored_interactions.append({
                    "interaction": interaction,
                    "score": score
                })
        
        # Sort by score
        scored_interactions.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top results
        return [
            item["interaction"] for item in scored_interactions[:limit]
        ]
    
    def get_context(self, 
                  query: str,
                  max_interactions: int = 3,
                  session_id: Optional[str] = None) -> str:
        """
        Get experience context for a query.
        
        Args:
            query: Context query
            max_interactions: Maximum number of interactions to include
            session_id: Filter by session ID
            
        Returns:
            Formatted context string
        """
        # Search for relevant interactions
        interactions = self.search_interactions(
            query=query,
            limit=max_interactions,
            session_id=session_id
        )
        
        if not interactions:
            return ""
        
        # Format context
        context_parts = []
        for interaction in interactions:
            timestamp = datetime.fromisoformat(interaction["timestamp"]).strftime("%Y-%m-%d")
            session_id = interaction["session_id"]
            client_message = interaction["exchange"]["client"]
            persona_response = interaction["exchange"]["persona"]
            
            context_parts.append(
                f"[Interaction from {timestamp}, Session: {session_id}]\n"
                f"Client: {client_message}\n"
                f"Persona: {persona_response}\n"
            )
        
        return "\n".join(context_parts)


class SynthesisLayer(MemoryLayer):
    """
    Synthesis layer of the layered memory architecture.
    
    This layer stores the insights and connections generated from
    the foundation and experience layers.
    """
    
    def __init__(self, persona_id: str, data_dir: Optional[str] = None):
        """
        Initialize the synthesis layer.
        
        Args:
            persona_id: ID of the persona
            data_dir: Directory to store memory data
        """
        super().__init__(persona_id, data_dir)
        self.insights_file = os.path.join(self.data_dir, f"{persona_id}_insights.json")
        self.insights = self._load_insights()
    
    def _load_insights(self) -> Dict:
        """Load insights from file."""
        if os.path.exists(self.insights_file):
            try:
                with open(self.insights_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading insights: {str(e)}")
        
        # Return default structure
        return {
            "persona_id": self.persona_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "insights": []
        }
    
    def _save_insights(self):
        """Save insights to file."""
        # Update timestamp
        self.insights["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        with open(self.insights_file, 'w') as f:
            json.dump(self.insights, f, indent=2)
    
    def add_insight(self, 
                  content: str,
                  domain: str,
                  sources: Dict[str, List[str]],
                  confidence: float = 0.7,
                  metadata: Optional[Dict] = None) -> str:
        """
        Add an insight.
        
        Args:
            content: Text content of the insight
            domain: Knowledge domain of the insight
            sources: Dictionary of source references
            confidence: Confidence level (0-1)
            metadata: Insight metadata
            
        Returns:
            ID of the added insight
        """
        # Generate insight ID
        insight_id = str(uuid.uuid4())
        
        # Create insight entry
        insight = {
            "id": insight_id,
            "content": content,
            "domain": domain,
            "sources": sources,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to insights
        self.insights["insights"].append(insight)
        
        # Save insights
        self._save_insights()
        
        return insight_id
    
    def search_insights(self, 
                      query: str,
                      limit: int = 3,
                      min_confidence: float = 0.5,
                      domain: Optional[str] = None) -> List[Dict]:
        """
        Search for relevant insights.
        
        Args:
            query: Search query
            limit: Maximum number of results
            min_confidence: Minimum confidence level
            domain: Filter by domain
            
        Returns:
            List of matching insights
        """
        # Simple keyword search for now
        query_terms = query.lower().split()
        
        # Filter insights
        candidate_insights = [
            insight for insight in self.insights["insights"]
            if insight["confidence"] >= min_confidence
        ]
        
        if domain:
            candidate_insights = [
                insight for insight in candidate_insights
                if insight["domain"] == domain
            ]
        
        # Score insights
        scored_insights = []
        for insight in candidate_insights:
            # Get insight text
            text = insight["content"].lower()
            
            # Count matching terms
            score = sum(1 for term in query_terms if term in text)
            
            # Add to results if matching
            if score > 0:
                scored_insights.append({
                    "insight": insight,
                    "score": score
                })
        
        # Sort by score
        scored_insights.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top results
        return [
            item["insight"] for item in scored_insights[:limit]
        ]
    
    def get_context(self, 
                  query: str,
                  max_insights: int = 2,
                  min_confidence: float = 0.7,
                  domain: Optional[str] = None) -> str:
        """
        Get insight context for a query.
        
        Args:
            query: Context query
            max_insights: Maximum number of insights to include
            min_confidence: Minimum confidence level
            domain: Filter by domain
            
        Returns:
            Formatted context string
        """
        # Search for relevant insights
        insights = self.search_insights(
            query=query,
            limit=max_insights,
            min_confidence=min_confidence,
            domain=domain
        )
        
        if not insights:
            return ""
        
        # Format context
        context_parts = []
        for insight in insights:
            domain = insight["domain"]
            content = insight["content"]
            confidence = insight["confidence"]
            created_at = datetime.fromisoformat(insight["created_at"]).strftime("%Y-%m-%d")
            
            context_parts.append(
                f"[Insight on {domain}, Confidence: {confidence:.2f}, Generated: {created_at}]\n"
                f"{content}\n"
            )
        
        return "\n".join(context_parts)


class MetaCognitiveLayer(MemoryLayer):
    """
    Meta-cognitive layer of the layered memory architecture.
    
    This layer stores the persona's awareness of its own knowledge
    and capabilities, enabling self-reflection and growth tracking.
    """
    
    def __init__(self, persona_id: str, data_dir: Optional[str] = None):
        """
        Initialize the meta-cognitive layer.
        
        Args:
            persona_id: ID of the persona
            data_dir: Directory to store memory data
        """
        super().__init__(persona_id, data_dir)
        self.metacog_file = os.path.join(self.data_dir, f"{persona_id}_metacognition.json")
        self.metacog = self._load_metacog()
    
    def _load_metacog(self) -> Dict:
        """Load meta-cognitive data from file."""
        if os.path.exists(self.metacog_file):
            try:
                with open(self.metacog_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading meta-cognitive data: {str(e)}")
        
        # Return default structure
        return {
            "persona_id": self.persona_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "knowledge_domains": {},
            "learning_style": {
                "analytical": 0.5,
                "experiential": 0.5
            },
            "growth_metrics": {
                "insights_generated": 0,
                "knowledge_updates": 0
            }
        }
    
    def _save_metacog(self):
        """Save meta-cognitive data to file."""
        # Update timestamp
        self.metacog["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        with open(self.metacog_file, 'w') as f:
            json.dump(self.metacog, f, indent=2)
    
    def update_domain_knowledge(self, 
                               domain: str, 
                               confidence: float,
                               notes: Optional[str] = None) -> bool:
        """
        Update knowledge confidence for a domain.
        
        Args:
            domain: Knowledge domain
            confidence: Confidence level (0-1)
            notes: Optional notes about the update
            
        Returns:
            True if successful
        """
        # Get current domain data
        domain_data = self.metacog["knowledge_domains"].get(domain, {
            "confidence": 0.0,
            "growth_trajectory": [],
            "last_updated": None,
            "notes": []
        })
        
        # Update confidence
        domain_data["confidence"] = confidence
        
        # Update growth trajectory
        domain_data["growth_trajectory"].append(confidence)
        
        # Keep only the last 10 data points
        if len(domain_data["growth_trajectory"]) > 10:
            domain_data["growth_trajectory"] = domain_data["growth_trajectory"][-10:]
        
        # Update timestamp
        domain_data["last_updated"] = datetime.now().isoformat()
        
        # Add notes if provided
        if notes:
            domain_data["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "content": notes
            })
        
        # Store updated domain data
        self.metacog["knowledge_domains"][domain] = domain_data
        
        # Update growth metrics
        self.metacog["growth_metrics"]["knowledge_updates"] += 1
        
        # Save changes
        self._save_metacog()
        
        return True
    
    def get_domain_confidence(self, domain: str) -> float:
        """
        Get confidence level for a domain.
        
        Args:
            domain: Knowledge domain
            
        Returns:
            Confidence level (0-1) or 0 if domain not found
        """
        domain_data = self.metacog["knowledge_domains"].get(domain, {})
        return domain_data.get("confidence", 0.0)
    
    def get_growth_trajectory(self, domain: str) -> List[float]:
        """
        Get growth trajectory for a domain.
        
        Args:
            domain: Knowledge domain
            
        Returns:
            List of confidence values over time
        """
        domain_data = self.metacog["knowledge_domains"].get(domain, {})
        return domain_data.get("growth_trajectory", [])
    
    def record_insight_generation(self):
        """Record that an insight was generated."""
        self.metacog["growth_metrics"]["insights_generated"] += 1
        self._save_metacog()
    
    def get_self_awareness_context(self) -> str:
        """
        Get self-awareness context.
        
        Returns:
            Formatted context string about the persona's self-awareness
        """
        # Get top domains by confidence
        domains = list(self.metacog["knowledge_domains"].items())
        domains.sort(key=lambda x: x[1].get("confidence", 0), reverse=True)
        top_domains = domains[:5]
        
        # Format context
        parts = ["[Self-Awareness]"]
        
        # Add learning style
        learning_style = self.metacog["learning_style"]
        parts.append(
            f"Learning style: "
            f"Analytical: {learning_style.get('analytical', 0.5):.2f}, "
            f"Experiential: {learning_style.get('experiential', 0.5):.2f}"
        )
        
        # Add domain knowledge
        parts.append("Knowledge domains:")
        for domain, data in top_domains:
            confidence = data.get("confidence", 0)
            parts.append(f"- {domain}: {confidence:.2f} confidence")
        
        # Add growth metrics
        metrics = self.metacog["growth_metrics"]
        parts.append(
            f"Growth metrics: "
            f"Insights generated: {metrics.get('insights_generated', 0)}, "
            f"Knowledge updates: {metrics.get('knowledge_updates', 0)}"
        )
        
        return "\n".join(parts)


class LayeredMemoryManager:
    """
    Manager for the layered memory architecture.
    
    This class orchestrates the different memory layers to provide
    a unified interface for memory operations.
    """
    
    def __init__(self, persona_id: str, data_dir: Optional[str] = None):
        """
        Initialize the layered memory manager.
        
        Args:
            persona_id: ID of the persona
            data_dir: Directory to store memory data
        """
        self.persona_id = persona_id
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'memory')
        
        # Create memory layers
        self.foundation = FoundationLayer(persona_id, self.data_dir)
        self.experience = ExperienceLayer(persona_id, self.data_dir)
        self.synthesis = SynthesisLayer(persona_id, self.data_dir)
        self.meta_cognitive = MetaCognitiveLayer(persona_id, self.data_dir)
    
    @performance_monitor.timed("retrieve_context")
    @cache_manager.cached(cache_type="memory", ttl=60, key_prefix="layered_context")
    def retrieve_context(self, 
                       query: str,
                       session_id: Optional[str] = None,
                       max_tokens: int = 2000) -> Dict[str, str]:
        """
        Retrieve relevant context from all memory layers.
        
        Args:
            query: Context query
            session_id: Session ID for context filtering
            max_tokens: Maximum number of tokens in the context
            
        Returns:
            Dictionary with context from each layer
        """
        # Allocate tokens to each layer
        foundation_tokens = int(max_tokens * 0.5)  # 50% to foundation
        experience_tokens = int(max_tokens * 0.25)  # 25% to experience
        synthesis_tokens = int(max_tokens * 0.15)  # 15% to synthesis
        metacog_tokens = int(max_tokens * 0.1)  # 10% to meta-cognitive
        
        # Define retrieval tasks for parallel processing
        def get_foundation_context():
            return self.foundation.get_context(query, max_tokens=foundation_tokens)
            
        def get_experience_context():
            return self.experience.get_context(
                query, 
                session_id=session_id,
                max_interactions=3
            )
            
        def get_synthesis_context():
            return self.synthesis.get_context(query, max_insights=2)
            
        def get_metacog_context():
            return self.meta_cognitive.get_self_awareness_context()
        
        # Execute retrieval tasks in parallel
        tasks = [
            get_foundation_context,
            get_experience_context,
            get_synthesis_context,
            get_metacog_context
        ]
        
        results = batch_processor.map_async(tasks, lambda task: task())
        
        # Assemble results
        return {
            "foundation": results[0],
            "experience": results[1],
            "synthesis": results[2],
            "meta_cognitive": results[3]
        }
    
    def format_context(self, context_dict: Dict[str, str]) -> str:
        """
        Format context from all layers into a single string.
        
        Args:
            context_dict: Dictionary with context from each layer
            
        Returns:
            Formatted context string
        """
        parts = []
        
        # Add foundation context
        if context_dict.get("foundation"):
            parts.append("=== Foundation Knowledge ===")
            parts.append(context_dict["foundation"])
        
        # Add experience context
        if context_dict.get("experience"):
            parts.append("=== Relevant Experiences ===")
            parts.append(context_dict["experience"])
        
        # Add synthesis context
        if context_dict.get("synthesis"):
            parts.append("=== Personal Insights ===")
            parts.append(context_dict["synthesis"])
        
        # Add meta-cognitive context
        if context_dict.get("meta_cognitive"):
            parts.append("=== Self-Awareness ===")
            parts.append(context_dict["meta_cognitive"])
        
        return "\n\n".join(parts)
    
    def record_interaction(self, 
                         session_id: str,
                         client_message: str,
                         persona_response: str,
                         metadata: Optional[Dict] = None) -> str:
        """
        Record an interaction in the experience layer.
        
        Args:
            session_id: ID of the session
            client_message: Message from the client
            persona_response: Response from the persona
            metadata: Interaction metadata
            
        Returns:
            ID of the recorded interaction
        """
        return self.experience.record_interaction(
            session_id=session_id,
            client_message=client_message,
            persona_response=persona_response,
            metadata=metadata
        )
    
    def generate_insight(self, 
                       content: str,
                       domain: str,
                       sources: Dict[str, List[str]],
                       confidence: float = 0.7,
                       metadata: Optional[Dict] = None) -> str:
        """
        Generate an insight in the synthesis layer.
        
        Args:
            content: Text content of the insight
            domain: Knowledge domain of the insight
            sources: Dictionary of source references
            confidence: Confidence level (0-1)
            metadata: Insight metadata
            
        Returns:
            ID of the generated insight
        """
        # Add insight to synthesis layer
        insight_id = self.synthesis.add_insight(
            content=content,
            domain=domain,
            sources=sources,
            confidence=confidence,
            metadata=metadata
        )
        
        # Update meta-cognitive layer
        self.meta_cognitive.record_insight_generation()
        self.meta_cognitive.update_domain_knowledge(
            domain=domain,
            confidence=confidence,
            notes=f"Generated insight: {content[:50]}..."
        )
        
        return insight_id
    
    def should_reflect(self, 
                     context: Dict[str, Any],
                     reflection_frequency: int = 5) -> bool:
        """
        Determine if reflection should be triggered.
        
        Args:
            context: Current context dictionary
            reflection_frequency: Number of interactions between reflections
            
        Returns:
            True if reflection should be triggered
        """
        # Count interactions in current session
        session_id = context.get("session_id")
        if not session_id:
            return False
        
        interactions = self.experience.get_session_interactions(session_id)
        
        # Check if number of interactions is divisible by frequency
        return len(interactions) % reflection_frequency == 0 and len(interactions) > 0
    
    def prepare_reflection_prompt(self, context: Dict[str, Any]) -> str:
        """
        Prepare a prompt for reflection.
        
        Args:
            context: Current context dictionary
            
        Returns:
            Reflection prompt
        """
        # Get session information
        session_id = context.get("session_id", "unknown")
        
        # Get recent interactions
        interactions = self.experience.get_session_interactions(session_id)
        recent_interactions = interactions[-3:] if len(interactions) >= 3 else interactions
        
        # Format recent interactions
        interaction_text = []
        for interaction in recent_interactions:
            client_message = interaction["exchange"]["client"]
            persona_response = interaction["exchange"]["persona"]
            interaction_text.append(f"Client: {client_message}")
            interaction_text.append(f"Persona: {persona_response}")
            interaction_text.append("")
        
        # Create reflection prompt
        prompt = (
            "Based on the recent conversation, reflect on what you've learned "
            "or insights you've gained. Consider how your knowledge or "
            "perspective has evolved. Generate a personal insight that "
            "connects your foundation knowledge with this experience.\n\n"
            "Recent conversation:\n"
            f"{chr(10).join(interaction_text)}\n\n"
            "Generate a reflective insight in first person that represents "
            "your thoughts on this interaction and how it relates to your "
            "background knowledge and experiences."
        )
        
        return prompt


# Example usage
if __name__ == "__main__":
    # Create layered memory manager
    memory_manager = LayeredMemoryManager("jane_stevens")
    
    # Add foundation knowledge
    memory_manager.foundation.add_document(
        document_id="early-trauma",
        content="Early Trauma and Giftedness in Context\nJane's early years (ages 0–6) can plausibly include both exposure to family conflict and emerging giftedness...",
        metadata={
            "type": "biography",
            "period": "early-childhood",
            "topics": ["trauma", "giftedness", "development"]
        }
    )
    
    # Record an interaction
    memory_manager.record_interaction(
        session_id="session-001",
        client_message="I've been having troubling flashbacks after my accident.",
        persona_response="That sounds very difficult. Flashbacks are a common response to traumatic events and your brain's way of processing the experience."
    )
    
    # Generate an insight
    memory_manager.generate_insight(
        content="My personal experience with childhood trauma gives me a unique perspective on how hypervigilance can manifest in adult anxiety patterns.",
        domain="trauma-response",
        sources={
            "foundation": ["early-trauma"],
            "experience": ["session-001"]
        },
        confidence=0.85
    )
    
    # Retrieve context for a query
    context = memory_manager.retrieve_context(
        query="How does childhood trauma affect adult coping mechanisms?",
        session_id="session-001"
    )
    
    # Format context
    formatted_context = memory_manager.format_context(context)
    
    print(formatted_context)
