"""
Enhanced persona management for the Smart Steps AI module.

This module implements the advanced persona system with layered memory,
knowledge integration, and adaptive learning capabilities.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class PersonaSchema:
    """Schema definitions and validation for enhanced personas."""
    
    CORE_SCHEMA = {
        "id": str,
        "name": str,
        "type": str,
        "core_attributes": {
            "education": list,
            "specializations": list,
            "professional_experience": list,
            "personality_traits": dict
        },
        "knowledge_sources": list,
        "memory_configuration": {
            "reflection_frequency": int,
            "learning_rate": float,
            "confidence_threshold": float
        },
        "growth_boundaries": {
            "allowed_domains": list,
            "personality_variance": float
        }
    }
    
    KNOWLEDGE_SOURCE_SCHEMA = {
        "id": str,
        "type": str,
        "path": str,
        "metadata": {
            "period": str,
            "relevance": list
        }
    }
    
    @classmethod
    def validate(cls, persona_data: Dict) -> List[str]:
        """
        Validate persona data against schema.
        
        Args:
            persona_data: Persona definition dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required top-level fields
        for field in ["id", "name", "type"]:
            if field not in persona_data:
                errors.append(f"Missing required field: {field}")
        
        # Check core_attributes if present
        if "core_attributes" in persona_data:
            core_attrs = persona_data["core_attributes"]
            for field in ["education", "specializations", "professional_experience"]:
                if field not in core_attrs:
                    errors.append(f"Missing required core attribute: {field}")
                elif not isinstance(core_attrs[field], list):
                    errors.append(f"Core attribute {field} must be a list")
            
            if "personality_traits" not in core_attrs:
                errors.append("Missing required core attribute: personality_traits")
            elif not isinstance(core_attrs["personality_traits"], dict):
                errors.append("personality_traits must be a dictionary")
        else:
            errors.append("Missing required section: core_attributes")
        
        # Check knowledge_sources if present
        if "knowledge_sources" in persona_data:
            if not isinstance(persona_data["knowledge_sources"], list):
                errors.append("knowledge_sources must be a list")
            else:
                for i, source in enumerate(persona_data["knowledge_sources"]):
                    source_errors = cls._validate_knowledge_source(source)
                    errors.extend([f"knowledge_source[{i}]: {err}" for err in source_errors])
        
        # Check memory_configuration if present
        if "memory_configuration" in persona_data:
            memory_config = persona_data["memory_configuration"]
            for field, field_type in [
                ("reflection_frequency", int),
                ("learning_rate", float),
                ("confidence_threshold", float)
            ]:
                if field not in memory_config:
                    errors.append(f"Missing memory configuration: {field}")
                elif not isinstance(memory_config[field], field_type):
                    errors.append(f"Memory configuration {field} must be {field_type.__name__}")
        
        # Check growth_boundaries if present
        if "growth_boundaries" in persona_data:
            growth = persona_data["growth_boundaries"]
            if "allowed_domains" not in growth:
                errors.append("Missing growth boundary: allowed_domains")
            elif not isinstance(growth["allowed_domains"], list):
                errors.append("allowed_domains must be a list")
            
            if "personality_variance" not in growth:
                errors.append("Missing growth boundary: personality_variance")
            elif not isinstance(growth["personality_variance"], (int, float)):
                errors.append("personality_variance must be a number")
        
        return errors
    
    @classmethod
    def _validate_knowledge_source(cls, source: Dict) -> List[str]:
        """Validate a knowledge source entry."""
        errors = []
        
        for field in ["id", "type", "path"]:
            if field not in source:
                errors.append(f"Missing required field: {field}")
        
        if "metadata" in source:
            metadata = source["metadata"]
            if "period" not in metadata:
                errors.append("Missing metadata: period")
            
            if "relevance" not in metadata:
                errors.append("Missing metadata: relevance")
            elif not isinstance(metadata["relevance"], list):
                errors.append("relevance metadata must be a list")
        else:
            errors.append("Missing required field: metadata")
        
        return errors
    
    @classmethod
    def create_template(cls) -> Dict:
        """Create a template persona definition."""
        return {
            "id": "",
            "name": "",
            "type": "",
            "core_attributes": {
                "education": [],
                "specializations": [],
                "professional_experience": [],
                "personality_traits": {}
            },
            "knowledge_sources": [],
            "memory_configuration": {
                "reflection_frequency": 5,
                "learning_rate": 0.3,
                "confidence_threshold": 0.7
            },
            "growth_boundaries": {
                "allowed_domains": [],
                "personality_variance": 0.2
            }
        }


class EnhancedPersonaManager:
    """
    Enhanced persona manager with support for advanced persona features.
    
    This manager provides functionality for creating, editing, and validating
    complex personas with layered memory and knowledge integration.
    """
    
    def __init__(self, config_path: Optional[str] = None, personas_dir: Optional[str] = None):
        """
        Initialize the enhanced persona manager.
        
        Args:
            config_path: Path to the configuration file
            personas_dir: Directory to store persona data
        """
        self.config = {}
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        self.personas_dir = personas_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'personas')
        self.personas = {}
        self.memory_managers = {}
        
        # Ensure personas directory exists
        os.makedirs(self.personas_dir, exist_ok=True)
        
        # Load existing personas
        self._load_personas()
    
    def _load_personas(self):
        """Load all persona definitions from the personas directory."""
        persona_files = os.path.join(self.personas_dir, '*.json')
        for persona_file in Path(self.personas_dir).glob('*.json'):
            try:
                with open(persona_file, 'r') as f:
                    persona_data = json.load(f)
                    
                # Validate persona data
                errors = PersonaSchema.validate(persona_data)
                if not errors:
                    self.personas[persona_data['id']] = persona_data
                else:
                    print(f"Warning: Invalid persona definition in {persona_file}: {errors}")
            except Exception as e:
                print(f"Error loading persona from {persona_file}: {str(e)}")
    
    def create_persona(self, 
                      name: str, 
                      persona_type: str, 
                      core_attributes: Dict[str, Any],
                      knowledge_sources: Optional[List[Dict]] = None,
                      memory_configuration: Optional[Dict] = None,
                      growth_boundaries: Optional[Dict] = None) -> str:
        """
        Create a new enhanced persona.
        
        Args:
            name: Name of the persona
            persona_type: Type of professional persona
            core_attributes: Core attributes dictionary
            knowledge_sources: List of knowledge source dictionaries
            memory_configuration: Memory configuration settings
            growth_boundaries: Growth boundary settings
            
        Returns:
            ID of the created persona
        """
        # Generate a unique ID based on name
        persona_id = name.lower().replace(' ', '_')
        
        # Ensure ID is unique
        if persona_id in self.personas:
            base_id = persona_id
            counter = 1
            while persona_id in self.personas:
                persona_id = f"{base_id}_{counter}"
                counter += 1
        
        # Create persona definition
        persona = {
            "id": persona_id,
            "name": name,
            "type": persona_type,
            "core_attributes": core_attributes,
            "knowledge_sources": knowledge_sources or [],
            "memory_configuration": memory_configuration or {
                "reflection_frequency": 5,
                "learning_rate": 0.3,
                "confidence_threshold": 0.7
            },
            "growth_boundaries": growth_boundaries or {
                "allowed_domains": [persona_type],
                "personality_variance": 0.2
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1
        }
        
        # Validate persona
        errors = PersonaSchema.validate(persona)
        if errors:
            raise ValueError(f"Invalid persona definition: {errors}")
        
        # Save persona
        self.personas[persona_id] = persona
        self._save_persona(persona_id)
        
        return persona_id
    
    def update_persona(self, persona_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing persona.
        
        Args:
            persona_id: ID of the persona to update
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        if persona_id not in self.personas:
            return False
        
        # Get current persona
        persona = self.personas[persona_id].copy()
        
        # Apply updates (excluding id, created_at)
        for key, value in updates.items():
            if key in ["id", "created_at"]:
                continue
                
            if key in ["core_attributes", "memory_configuration", "growth_boundaries"] and key in persona:
                # Update nested dictionary
                persona[key].update(value)
            elif key == "knowledge_sources" and key in persona:
                # Add/update knowledge sources
                existing_ids = {src["id"] for src in persona[key]}
                for source in value:
                    if source["id"] in existing_ids:
                        # Update existing source
                        for i, src in enumerate(persona[key]):
                            if src["id"] == source["id"]:
                                persona[key][i] = source
                                break
                    else:
                        # Add new source
                        persona[key].append(source)
            else:
                # Direct update
                persona[key] = value
        
        # Update metadata
        persona["updated_at"] = datetime.now().isoformat()
        persona["version"] = persona.get("version", 0) + 1
        
        # Validate updated persona
        errors = PersonaSchema.validate(persona)
        if errors:
            print(f"Invalid persona update: {errors}")
            return False
        
        # Save updated persona
        self.personas[persona_id] = persona
        self._save_persona(persona_id)
        
        return True
    
    def get_persona(self, persona_id: str) -> Optional[Dict]:
        """
        Get a persona by ID.
        
        Args:
            persona_id: ID of the persona
            
        Returns:
            Persona definition dictionary or None if not found
        """
        return self.personas.get(persona_id)
    
    def list_personas(self) -> List[Dict]:
        """
        List all available personas.
        
        Returns:
            List of persona metadata dictionaries
        """
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "type": p["type"],
                "created_at": p.get("created_at"),
                "updated_at": p.get("updated_at"),
                "version": p.get("version", 1)
            }
            for p in self.personas.values()
        ]
    
    def delete_persona(self, persona_id: str) -> bool:
        """
        Delete a persona.
        
        Args:
            persona_id: ID of the persona to delete
            
        Returns:
            True if successful, False if persona not found
        """
        if persona_id not in self.personas:
            return False
        
        # Remove from memory
        del self.personas[persona_id]
        
        # Remove from disk
        persona_file = os.path.join(self.personas_dir, f"{persona_id}.json")
        if os.path.exists(persona_file):
            os.remove(persona_file)
        
        return True
    
    def add_knowledge_source(self, 
                            persona_id: str, 
                            source_id: str,
                            source_type: str,
                            source_path: str,
                            metadata: Dict) -> bool:
        """
        Add a knowledge source to a persona.
        
        Args:
            persona_id: ID of the persona
            source_id: ID of the knowledge source
            source_type: Type of knowledge source
            source_path: Path to the knowledge source file
            metadata: Metadata dictionary for the source
            
        Returns:
            True if successful, False otherwise
        """
        if persona_id not in self.personas:
            return False
        
        # Create source definition
        source = {
            "id": source_id,
            "type": source_type,
            "path": source_path,
            "metadata": metadata,
            "added_at": datetime.now().isoformat()
        }
        
        # Validate source
        errors = PersonaSchema._validate_knowledge_source(source)
        if errors:
            print(f"Invalid knowledge source: {errors}")
            return False
        
        # Add to persona
        if "knowledge_sources" not in self.personas[persona_id]:
            self.personas[persona_id]["knowledge_sources"] = []
        
        # Check if source already exists
        for i, src in enumerate(self.personas[persona_id]["knowledge_sources"]):
            if src["id"] == source_id:
                # Update existing source
                self.personas[persona_id]["knowledge_sources"][i] = source
                self._save_persona(persona_id)
                return True
        
        # Add new source
        self.personas[persona_id]["knowledge_sources"].append(source)
        
        # Update metadata
        self.personas[persona_id]["updated_at"] = datetime.now().isoformat()
        self.personas[persona_id]["version"] = self.personas[persona_id].get("version", 0) + 1
        
        # Save updated persona
        self._save_persona(persona_id)
        
        return True
    
    def remove_knowledge_source(self, persona_id: str, source_id: str) -> bool:
        """
        Remove a knowledge source from a persona.
        
        Args:
            persona_id: ID of the persona
            source_id: ID of the knowledge source
            
        Returns:
            True if successful, False otherwise
        """
        if persona_id not in self.personas:
            return False
        
        if "knowledge_sources" not in self.personas[persona_id]:
            return False
        
        # Find and remove source
        sources = self.personas[persona_id]["knowledge_sources"]
        for i, src in enumerate(sources):
            if src["id"] == source_id:
                del sources[i]
                
                # Update metadata
                self.personas[persona_id]["updated_at"] = datetime.now().isoformat()
                self.personas[persona_id]["version"] = self.personas[persona_id].get("version", 0) + 1
                
                # Save updated persona
                self._save_persona(persona_id)
                
                return True
        
        return False
    
    def validate_persona(self, persona_id: str) -> List[str]:
        """
        Validate a persona's definition.
        
        Args:
            persona_id: ID of the persona
            
        Returns:
            List of validation errors (empty if valid)
        """
        if persona_id not in self.personas:
            return ["Persona not found"]
        
        return PersonaSchema.validate(self.personas[persona_id])
    
    def _save_persona(self, persona_id: str):
        """Save persona to disk."""
        if persona_id not in self.personas:
            return
        
        persona_file = os.path.join(self.personas_dir, f"{persona_id}.json")
        with open(persona_file, 'w') as f:
            json.dump(self.personas[persona_id], f, indent=2)
    
    def import_from_file(self, file_path: str) -> Optional[str]:
        """
        Import a persona from a file.
        
        Args:
            file_path: Path to the persona definition file
            
        Returns:
            ID of the imported persona or None if invalid
        """
        try:
            with open(file_path, 'r') as f:
                persona_data = json.load(f)
            
            # Validate persona data
            errors = PersonaSchema.validate(persona_data)
            if errors:
                print(f"Invalid persona definition: {errors}")
                return None
            
            # Add persona
            persona_id = persona_data["id"]
            self.personas[persona_id] = persona_data
            self._save_persona(persona_id)
            
            return persona_id
        
        except Exception as e:
            print(f"Error importing persona: {str(e)}")
            return None
    
    def export_to_file(self, persona_id: str, file_path: str) -> bool:
        """
        Export a persona to a file.
        
        Args:
            persona_id: ID of the persona
            file_path: Path to save the persona definition
            
        Returns:
            True if successful, False otherwise
        """
        if persona_id not in self.personas:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.personas[persona_id], f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting persona: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Create enhanced persona manager
    manager = EnhancedPersonaManager()
    
    # Create a sample persona
    persona_id = manager.create_persona(
        name="Dr. Jane Stevens",
        persona_type="clinical_psychologist",
        core_attributes={
            "education": ["University of Chicago", "Northwestern University"],
            "specializations": ["trauma", "PTSD", "personality disorders"],
            "professional_experience": ["NOPH", "private practice"],
            "personality_traits": {
                "empathy": 0.9,
                "analytical": 0.8,
                "resilience": 0.85
            }
        }
    )
    
    # Add knowledge sources
    manager.add_knowledge_source(
        persona_id=persona_id,
        source_id="jane-early-trauma",
        source_type="biography",
        source_path="personas/Jane/Jane-Early Trauma and Giftedness in Context.pdf",
        metadata={
            "period": "early-childhood",
            "relevance": ["trauma", "development", "coping-mechanisms"]
        }
    )
    
    # List all personas
    personas = manager.list_personas()
    for p in personas:
        print(f"{p['name']} ({p['id']}): {p['type']}")
