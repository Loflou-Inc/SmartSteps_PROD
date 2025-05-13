"""Persona management for the Smart Steps AI module."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from pydantic import ValidationError

from ..config import get_config_manager
from ..utils import get_logger, load_json_file, save_json_file
from .models import Persona, PersonaMetadata


class PersonaManager:
    """
    Manager for professional personas.
    
    This class handles loading, validating, and retrieving professional persona
    definitions used by the AI system.
    """

    def __init__(self, personas_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the persona manager.

        Args:
            personas_dir (Optional[Union[str, Path]]): Directory containing persona definitions (default: None)
                If None, uses the path from the configuration
        """
        self.logger = get_logger(__name__)
        self.config = get_config_manager().get()
        
        # Set personas directory
        if personas_dir:
            self.personas_dir = Path(personas_dir)
        else:
            self.personas_dir = Path(self.config.paths.personas_dir)
        
        # Initialize storage
        self.personas: Dict[str, Persona] = {}
        self.metadata_cache: Dict[str, PersonaMetadata] = {}
        
        # Load personas
        self._load_personas()

    def _load_personas(self) -> None:
        """Load all personas from the personas directory."""
        self.logger.debug(f"Loading personas from {self.personas_dir}")
        
        # Create directory if it doesn't exist
        self.personas_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Get all JSON files in the directory
            persona_files = list(self.personas_dir.glob("*.json"))
            
            if not persona_files:
                self.logger.warning(f"No persona files found in {self.personas_dir}")
                return
            
            # Load each persona file
            for file_path in persona_files:
                self._load_persona_file(file_path)
            
            self.logger.info(f"Loaded {len(self.personas)} personas")
        
        except Exception as e:
            self.logger.error(f"Failed to load personas: {str(e)}")

    def _load_persona_file(self, file_path: Path) -> None:
        """
        Load a persona from a JSON file.

        Args:
            file_path (Path): Path to the persona JSON file
        """
        self.logger.debug(f"Loading persona from {file_path}")
        
        try:
            # Load and validate the persona
            success, error, data = load_json_file(file_path, Persona)
            
            if not success or data is None:
                self.logger.warning(f"Failed to load persona from {file_path}: {error}")
                return
            
            persona = data
            
            # Store the persona
            self.personas[persona.name] = persona
            self.metadata_cache[persona.name] = persona.to_metadata()
            
            self.logger.debug(f"Loaded persona: {persona.name}")
        
        except Exception as e:
            self.logger.warning(f"Error loading persona from {file_path}: {str(e)}")

    def get_persona(self, name: str) -> Optional[Persona]:
        """
        Get a persona by name.

        Args:
            name (str): Name of the persona

        Returns:
            Optional[Persona]: Persona object or None if not found
        """
        if name not in self.personas:
            self.logger.warning(f"Persona not found: {name}")
            return None
        
        return self.personas[name]

    def get_system_prompt(self, name: str) -> str:
        """
        Get the system prompt for a persona.

        Args:
            name (str): Name of the persona

        Returns:
            str: System prompt for the persona

        Raises:
            ValueError: If the persona is not found
        """
        persona = self.get_persona(name)
        if persona is None:
            raise ValueError(f"Persona not found: {name}")
        
        return persona.system_prompt

    def list_personas(self) -> List[PersonaMetadata]:
        """
        Get a list of all available personas.

        Returns:
            List[PersonaMetadata]: List of persona metadata
        """
        return list(self.metadata_cache.values())

    def create_persona(self, persona: Persona) -> Tuple[bool, Optional[str]]:
        """
        Create a new persona.

        Args:
            persona (Persona): Persona to create

        Returns:
            Tuple[bool, Optional[str]]: Success flag and error message (if any)
        """
        try:
            # Validate the persona
            if persona.name in self.personas:
                return False, f"Persona already exists: {persona.name}"
            
            # Save the persona to a file
            file_path = self.personas_dir / f"{persona.name}.json"
            success, error = save_json_file(persona, file_path)
            
            if not success:
                return False, f"Failed to save persona: {error}"
            
            # Add to cache
            self.personas[persona.name] = persona
            self.metadata_cache[persona.name] = persona.to_metadata()
            
            self.logger.info(f"Created persona: {persona.name}")
            return True, None
        
        except Exception as e:
            self.logger.error(f"Failed to create persona: {str(e)}")
            return False, str(e)

    def update_persona(self, persona: Persona) -> Tuple[bool, Optional[str]]:
        """
        Update an existing persona.

        Args:
            persona (Persona): Persona to update

        Returns:
            Tuple[bool, Optional[str]]: Success flag and error message (if any)
        """
        try:
            # Check if the persona exists
            if persona.name not in self.personas:
                return False, f"Persona not found: {persona.name}"
            
            # Save the persona to a file
            file_path = self.personas_dir / f"{persona.name}.json"
            success, error = save_json_file(persona, file_path)
            
            if not success:
                return False, f"Failed to save persona: {error}"
            
            # Update cache
            self.personas[persona.name] = persona
            self.metadata_cache[persona.name] = persona.to_metadata()
            
            self.logger.info(f"Updated persona: {persona.name}")
            return True, None
        
        except Exception as e:
            self.logger.error(f"Failed to update persona: {str(e)}")
            return False, str(e)

    def get_provider_info(self, name: str) -> Optional[Dict[str, str]]:
        """
        Get provider information for a persona.

        Args:
            name (str): Name of the persona

        Returns:
            Optional[Dict[str, str]]: Provider information or None if not found
        """
        persona = self.get_persona(name)
        if persona is None:
            return None
        
        return {
            "provider": persona.provider,
            "model": persona.model
        }

    def delete_persona(self, name: str) -> Tuple[bool, Optional[str]]:
        """
        Delete a persona.

        Args:
            name (str): Name of the persona to delete

        Returns:
            Tuple[bool, Optional[str]]: Success flag and error message (if any)
        """
        try:
            # Check if the persona exists
            if name not in self.personas:
                return False, f"Persona not found: {name}"
            
            # Delete the persona file
            file_path = self.personas_dir / f"{name}.json"
            
            if file_path.exists():
                file_path.unlink()
            
            # Remove from cache
            del self.personas[name]
            del self.metadata_cache[name]
            
            self.logger.info(f"Deleted persona: {name}")
            return True, None
        
        except Exception as e:
            self.logger.error(f"Failed to delete persona: {str(e)}")
            return False, str(e)
            
    def reload_personas(self) -> None:
        """Reload all personas from the personas directory."""
        self.personas = {}
        self.metadata_cache = {}
        self._load_personas()
