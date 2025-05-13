"""Enhanced persona management with canonical detail tracking."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
import json
from datetime import datetime

from pydantic import ValidationError

from ..config import get_config_manager
from ..utils import get_logger, load_json_file, save_json_file
from .models import Persona
from .enhanced_models import EnhancedPersona, CanonicalDetail
from .manager import PersonaManager


class EnhancedPersonaManager(PersonaManager):
    """
    Enhanced manager for professional personas with canonical detail tracking.
    
    This class extends the basic PersonaManager to support the enhanced persona
    model with multi-layered memory and canonical detail management.
    """

    def __init__(self, personas_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the enhanced persona manager.

        Args:
            personas_dir (Optional[Union[str, Path]]): Directory containing persona definitions (default: None)
                If None, uses the path from the configuration
        """
        # Initialize the base class
        super().__init__(personas_dir)
        
        # Enhanced personas storage
        self.enhanced_personas: Dict[str, EnhancedPersona] = {}
        
        # Load enhanced personas
        self._load_enhanced_personas()

    def _load_enhanced_personas(self) -> None:
        """Load all enhanced personas from the personas directory."""
        self.logger.debug(f"Loading enhanced personas from {self.personas_dir}")
        
        try:
            # Get all JSON files in the directory
            persona_files = list(self.personas_dir.glob("*.json"))
            
            if not persona_files:
                self.logger.warning(f"No persona files found in {self.personas_dir}")
                return
            
            # Load each persona file as EnhancedPersona
            for file_path in persona_files:
                self._load_enhanced_persona_file(file_path)
            
            self.logger.info(f"Loaded {len(self.enhanced_personas)} enhanced personas")
        
        except Exception as e:
            self.logger.error(f"Failed to load enhanced personas: {str(e)}")

    def _load_enhanced_persona_file(self, file_path: Path) -> None:
        """
        Load an enhanced persona from a JSON file.

        Args:
            file_path (Path): Path to the persona JSON file
        """
        self.logger.debug(f"Loading enhanced persona from {file_path}")
        
        try:
            # First try to load as an EnhancedPersona
            success, error, data = load_json_file(file_path, EnhancedPersona)
            
            if success and data is not None:
                # We successfully loaded as EnhancedPersona
                enhanced_persona = data
                
                # Store the persona in both collections
                self.personas[enhanced_persona.name] = enhanced_persona
                self.enhanced_personas[enhanced_persona.name] = enhanced_persona
                self.metadata_cache[enhanced_persona.name] = enhanced_persona.to_metadata()
                
                self.logger.debug(f"Loaded enhanced persona: {enhanced_persona.name}")
            else:
                # Try loading as a basic Persona instead
                self._load_persona_file(file_path)
        
        except Exception as e:
            self.logger.warning(f"Error loading enhanced persona from {file_path}: {str(e)}")
            # Fall back to base class loading
            self._load_persona_file(file_path)

    def get_enhanced_persona(self, name: str) -> Optional[EnhancedPersona]:
        """
        Get an enhanced persona by name.

        Args:
            name (str): Name of the persona

        Returns:
            Optional[EnhancedPersona]: Enhanced persona object or None if not found
        """
        if name not in self.enhanced_personas:
            # Check if it exists as a basic persona
            basic_persona = self.get_persona(name)
            if basic_persona and not isinstance(basic_persona, EnhancedPersona):
                self.logger.warning(f"Persona {name} exists but is not an enhanced persona")
            else:
                self.logger.warning(f"Enhanced persona not found: {name}")
            return None
        
        return self.enhanced_personas[name]

    def add_canonical_detail(self, persona_name: str, detail: str, context: str, 
                            categories: List[str], related_event_id: Optional[str] = None) -> Tuple[bool, Optional[CanonicalDetail], Optional[str]]:
        """
        Add a canonical detail to a persona's history.

        Args:
            persona_name (str): Name of the persona
            detail (str): The detail text
            context (str): Context where the detail was generated
            categories (List[str]): Categories for the detail
            related_event_id (Optional[str]): ID of related life event

        Returns:
            Tuple[bool, Optional[CanonicalDetail], Optional[str]]: 
                Success flag, created detail (if successful), and error message (if any)
        """
        # Get the enhanced persona
        persona = self.get_enhanced_persona(persona_name)
        if not persona:
            return False, None, f"Enhanced persona not found: {persona_name}"
        
        try:
            # Create the detail
            now = datetime.now()
            new_detail = CanonicalDetail(
                id=f"detail_{len(persona.canonical_details) + 1}_{now.timestamp()}",
                detail=detail,
                context=context,
                created_at=now,
                related_event_id=related_event_id,
                categories=categories,
                usage_count=1,
                reference_history=[str(now)]
            )
            
            # Add to persona
            persona.canonical_details.append(new_detail)
            
            # Save the updated persona
            self.update_enhanced_persona(persona)
            
            self.logger.info(f"Added canonical detail to persona {persona_name}")
            return True, new_detail, None
        
        except Exception as e:
            self.logger.error(f"Failed to add canonical detail: {str(e)}")
            return False, None, str(e)

    def get_canonical_details(self, persona_name: str, category: Optional[str] = None, 
                             query: Optional[str] = None, limit: int = 10) -> List[CanonicalDetail]:
        """
        Get canonical details for a persona.

        Args:
            persona_name (str): Name of the persona
            category (Optional[str]): Category to filter by
            query (Optional[str]): Text query to search for
            limit (int): Maximum number of details to return

        Returns:
            List[CanonicalDetail]: Matching canonical details
        """
        # Get the enhanced persona
        persona = self.get_enhanced_persona(persona_name)
        if not persona:
            return []
        
        # Start with all details
        details = persona.canonical_details.copy()
        
        # Filter by category if specified
        if category:
            details = [d for d in details if category in d.categories]
        
        # Filter by query if specified
        if query:
            query_lower = query.lower()
            details = [d for d in details if query_lower in d.detail.lower()]
        
        # Sort by usage count (descending) and created_at (descending)
        details.sort(key=lambda d: (d.usage_count, d.created_at), reverse=True)
        
        # Return limited number
        return details[:limit]

    def update_enhanced_persona(self, persona: EnhancedPersona) -> Tuple[bool, Optional[str]]:
        """
        Update an existing enhanced persona.

        Args:
            persona (EnhancedPersona): Enhanced persona to update

        Returns:
            Tuple[bool, Optional[str]]: Success flag and error message (if any)
        """
        try:
            # Check if the persona exists
            if persona.name not in self.personas:
                return False, f"Persona not found: {persona.name}"
            
            # Save the persona to a file
            file_path = self.personas_dir / f"{persona.name}.json"
            
            # Custom JSON serialization with datetime handling
            with open(file_path, "w", encoding="utf-8") as f:
                # Use Pydantic's model_dump
                json_data = persona.model_dump(exclude_none=True)
                
                # Custom handling for datetime objects
                def datetime_converter(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
                
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=datetime_converter)
            
            # Update caches
            self.personas[persona.name] = persona
            self.enhanced_personas[persona.name] = persona
            self.metadata_cache[persona.name] = persona.to_metadata()
            
            self.logger.info(f"Updated enhanced persona: {persona.name}")
            return True, None
        
        except Exception as e:
            self.logger.error(f"Failed to update enhanced persona: {str(e)}")
            return False, str(e)

    def record_detail_usage(self, persona_name: str, detail_id: str) -> bool:
        """
        Record usage of a canonical detail.

        Args:
            persona_name (str): Name of the persona
            detail_id (str): ID of the canonical detail

        Returns:
            bool: Success flag
        """
        # Get the enhanced persona
        persona = self.get_enhanced_persona(persona_name)
        if not persona:
            return False
        
        # Find the detail
        for detail in persona.canonical_details:
            if detail.id == detail_id:
                # Update usage count
                detail.usage_count += 1
                detail.reference_history.append(str(datetime.now()))
                
                # Save the updated persona
                self.update_enhanced_persona(persona)
                return True
        
        return False

    def get_relevant_canonical_details(self, persona_name: str, query: str, 
                                     limit: int = 5) -> List[CanonicalDetail]:
        """
        Get canonical details relevant to a query.

        Args:
            persona_name (str): Name of the persona
            query (str): Query text
            limit (int): Maximum number of details to return

        Returns:
            List[CanonicalDetail]: Relevant canonical details
        """
        # Get the enhanced persona
        persona = self.get_enhanced_persona(persona_name)
        if not persona:
            return []
        
        # In a real implementation, this would use embeddings for relevance.
        # This is a simplified version based on keyword matching.
        query_words = set(query.lower().split())
        scored_details = []
        
        for detail in persona.canonical_details:
            score = 0
            detail_text = detail.detail.lower()
            
            # Count matching words
            for word in query_words:
                if word in detail_text:
                    score += 1
            
            # Add category-based matching
            for category in detail.categories:
                if category.lower() in query.lower():
                    score += 2
            
            # Higher score for more frequently used details
            score += min(detail.usage_count / 5, 1)  # Cap at +1 for usage
            
            if score > 0:
                scored_details.append((detail, score))
        
        # Sort by relevance score (descending)
        scored_details.sort(key=lambda x: x[1], reverse=True)
        
        # Return top details
        return [detail for detail, _ in scored_details[:limit]]
