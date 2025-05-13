"""
Persona management for the Smart Steps AI module.
"""

import os
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from ..utils.logging import get_logger
from ..utils.validation import validate_persona, validate_persona_file
from ..utils.formatting import format_template
from .config_manager import ConfigManager

# Get logger
logger = get_logger("core.persona_manager")

class Persona:
    """
    Represents an AI professional persona with configurable traits,
    conversation style, and expertise areas.
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a persona from data.
        
        Args:
            data: The persona data.
        """
        self.data = data
        self.name = data.get("name", "")
        self.display_name = data.get("display_name", "")
        self.version = data.get("version", "1.0.0")
        self.description = data.get("description", "")
        self.system_prompt = data.get("system_prompt", "")
        
        # Optional properties
        self.personality_traits = data.get("personality_traits", {})
        self.expertise_areas = data.get("expertise_areas", [])
        self.conversation_style = data.get("conversation_style", {})
        self.analysis_approach = data.get("analysis_approach", {})
        self.rules = data.get("rules", [])
        self.examples = data.get("examples", [])
        
        logger.debug(f"Initialized persona: {self.name}")
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the persona.
        
        Returns:
            The system prompt.
        """
        return self.system_prompt
    
    def get_greeting(self, client_name: str, is_first_session: bool = False) -> str:
        """
        Get a greeting for the client.
        
        Args:
            client_name: The client's name.
            is_first_session: Whether this is the first session with the client.
            
        Returns:
            A greeting message.
        """
        greeting_format = self.conversation_style.get("greeting_format", "")
        
        if not greeting_format:
            # Default greeting
            if is_first_session:
                return f"Hello {client_name}. It's nice to meet you today."
            else:
                return f"Hello {client_name}. It's good to see you again."
        
        # Format the greeting
        return format_template(greeting_format, {
            "client_name": client_name,
            "is_first_session": is_first_session
        })
    
    def get_closing(self) -> str:
        """
        Get a closing message.
        
        Returns:
            A closing message.
        """
        return self.conversation_style.get("closing_format", "")
    
    def get_conversation_examples(self) -> List[Dict[str, str]]:
        """
        Get conversation examples for the persona.
        
        Returns:
            A list of conversation examples.
        """
        return self.examples
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata for the persona.
        
        Returns:
            Metadata for the persona.
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "description": self.description,
            "expertise_areas": self.expertise_areas,
            "personality_traits": self.personality_traits
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the persona to a dictionary.
        
        Returns:
            The persona as a dictionary.
        """
        return self.data
    
    def get_typical_phrases(self) -> List[str]:
        """
        Get typical phrases used by the persona.
        
        Returns:
            A list of typical phrases.
        """
        return self.conversation_style.get("typical_phrases", [])
    
    def get_session_structure(self) -> List[str]:
        """
        Get the session structure for the persona.
        
        Returns:
            A list of session structure elements.
        """
        return self.conversation_style.get("session_structure", [])
    
    def format_prompt(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Format a prompt for the persona.
        
        Args:
            user_input: The user input to respond to.
            context: Optional context information.
            
        Returns:
            A formatted prompt.
        """
        # Start with the system prompt
        prompt = self.system_prompt
        
        # Add session context if available
        if context:
            client_name = context.get("client_name", "")
            session_type = context.get("session_type", "")
            is_first_session = context.get("is_first_session", False)
            session_history = context.get("session_history", [])
            memory_context = context.get("memory_context", "")
            
            # Add session information
            if client_name:
                prompt += f"\n\nYou are in a {session_type} session with {client_name}."
            
            # Add memory context if available
            if memory_context:
                prompt += f"\n\n{memory_context}"
            
            # Add session history if available
            if session_history:
                prompt += "\n\nSession history:"
                for message in session_history:
                    role = message.get("role", "")
                    content = message.get("content", "")
                    
                    if role == "user":
                        prompt += f"\nClient: {content}"
                    elif role == "assistant":
                        prompt += f"\nYou: {content}"
        
        # Add the user input
        prompt += f"\n\nClient: {user_input}\n\nYou: "
        
        return prompt

class PersonaManager:
    """
    Manages AI professional personas for the Smart Steps AI module.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize the persona manager.
        
        Args:
            config_manager: The configuration manager to use.
                If None, a new one will be created.
        """
        self.config_manager = config_manager or ConfigManager()
        
        # Get the personas directory from the configuration
        self.personas_dir = self.config_manager.get_config("persona.personas_dir")
        
        if not self.personas_dir:
            # Use the default personas directory
            self.personas_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "config",
                "personas"
            )
        
        # Create the personas directory if it doesn't exist
        os.makedirs(self.personas_dir, exist_ok=True)
        
        logger.debug(f"Initialized PersonaManager with personas directory: {self.personas_dir}")
        
        # Load personas
        self.personas = {}
        self.load_personas()
    
    def load_personas(self) -> None:
        """
        Load all personas from the personas directory.
        """
        # Clear existing personas
        self.personas = {}
        
        # Check if the personas directory exists
        if not os.path.exists(self.personas_dir):
            logger.warning(f"Personas directory not found: {self.personas_dir}")
            return
        
        # Load all JSON files in the personas directory
        for file_name in os.listdir(self.personas_dir):
            if file_name.endswith('.json'):
                file_path = os.path.join(self.personas_dir, file_name)
                
                try:
                    # Validate the persona file
                    validation_errors = validate_persona_file(file_path)
                    
                    if validation_errors:
                        logger.warning(f"Invalid persona file: {file_path}")
                        for error in validation_errors:
                            logger.warning(f"  {error}")
                        continue
                    
                    # Load the persona data
                    with open(file_path, 'r', encoding='utf-8') as f:
                        persona_data = json.load(f)
                        
                        # Create a Persona object
                        persona = Persona(persona_data)
                        
                        # Add the persona to the collection
                        self.personas[persona.name] = persona
                        
                        logger.debug(f"Loaded persona: {persona.name}")
                except Exception as e:
                    logger.error(f"Error loading persona file {file_path}: {e}")
        
        logger.info(f"Loaded {len(self.personas)} personas")
    
    def get_persona(self, name: str) -> Optional[Persona]:
        """
        Get a persona by name.
        
        Args:
            name: The name of the persona.
            
        Returns:
            The persona, or None if not found.
        """
        if name not in self.personas:
            logger.warning(f"Persona not found: {name}")
            return None
        
        return self.personas[name]
    
    def get_default_persona(self) -> Optional[Persona]:
        """
        Get the default persona.
        
        Returns:
            The default persona, or None if not found.
        """
        default_persona_name = self.config_manager.get_config("persona.default_persona")
        
        if not default_persona_name:
            # No default persona configured, use the first one
            if not self.personas:
                logger.warning("No personas available")
                return None
            
            default_persona_name = next(iter(self.personas.keys()))
        
        return self.get_persona(default_persona_name)
    
    def list_personas(self) -> List[str]:
        """
        List all personas.
        
        Returns:
            A list of persona names.
        """
        return list(self.personas.keys())
    
    def list_persona_metadata(self) -> List[Dict[str, Any]]:
        """
        List metadata for all personas.
        
        Returns:
            A list of persona metadata.
        """
        return [persona.get_metadata() for persona in self.personas.values()]
    
    def save_persona(self, persona_data: Dict[str, Any]) -> bool:
        """
        Save a persona.
        
        Args:
            persona_data: The persona data.
            
        Returns:
            True if the persona was saved successfully, False otherwise.
        """
        # Validate the persona data
        validation_errors = validate_persona(persona_data)
        
        if validation_errors:
            logger.warning("Invalid persona data")
            for error in validation_errors:
                logger.warning(f"  {error}")
            return False
        
        # Get the persona name
        persona_name = persona_data.get("name")
        
        if not persona_name:
            logger.warning("Persona data is missing a name")
            return False
        
        # Create the file path
        file_path = os.path.join(self.personas_dir, f"{persona_name}.json")
        
        try:
            # Save the persona data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(persona_data, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"Saved persona: {persona_name}")
            
            # Reload personas
            self.load_personas()
            
            return True
        except Exception as e:
            logger.error(f"Error saving persona {persona_name}: {e}")
            return False
    
    def delete_persona(self, name: str) -> bool:
        """
        Delete a persona.
        
        Args:
            name: The name of the persona.
            
        Returns:
            True if the persona was deleted successfully, False otherwise.
        """
        # Check if the persona exists
        if name not in self.personas:
            logger.warning(f"Persona not found: {name}")
            return False
        
        # Create the file path
        file_path = os.path.join(self.personas_dir, f"{name}.json")
        
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.warning(f"Persona file not found: {file_path}")
            return False
        
        try:
            # Delete the file
            os.remove(file_path)
            
            logger.debug(f"Deleted persona: {name}")
            
            # Remove the persona from the collection
            del self.personas[name]
            
            return True
        except Exception as e:
            logger.error(f"Error deleting persona {name}: {e}")
            return False
    
    def set_default_persona(self, name: str) -> bool:
        """
        Set the default persona.
        
        Args:
            name: The name of the persona.
            
        Returns:
            True if the default persona was set successfully, False otherwise.
        """
        # Check if the persona exists
        if name not in self.personas:
            logger.warning(f"Persona not found: {name}")
            return False
        
        # Set the default persona
        self.config_manager.set_config("persona.default_persona", name)
        
        logger.debug(f"Set default persona: {name}")
        
        return True
