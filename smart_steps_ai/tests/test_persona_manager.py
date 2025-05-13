"""Test the PersonaManager class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_steps_ai.config import get_config_manager
from src.smart_steps_ai.persona import PersonaManager
from src.smart_steps_ai.persona.models import Persona, PersonalityTraits, ConversationStyle


class TestPersonaManager(unittest.TestCase):
    """Test the PersonaManager class."""

    def setUp(self):
        """Set up the test environment."""
        # Get the personas directory from the config
        config = get_config_manager().get()
        self.personas_dir = Path(config.paths.personas_dir)
        
        # Initialize the persona manager
        self.persona_manager = PersonaManager(self.personas_dir)

    def test_load_personas(self):
        """Test loading personas from the directory."""
        # Get all personas
        personas = self.persona_manager.list_personas()
        
        # Ensure we have at least one persona
        self.assertGreater(len(personas), 0, "No personas were loaded")
        
        # Print the loaded personas
        print(f"Loaded {len(personas)} personas:")
        for persona in personas:
            print(f"  - {persona.name} ({persona.display_name}): {persona.description}")

    def test_get_persona(self):
        """Test getting a specific persona."""
        # Get the default persona
        default_persona = self.persona_manager.get_default_persona()
        
        # Ensure we have a default persona
        self.assertIsNotNone(default_persona, "Default persona is None")
        
        # Get the same persona directly
        persona = self.persona_manager.get_persona(default_persona.name)
        
        # Ensure we got the same persona
        self.assertEqual(persona.name, default_persona.name)
        self.assertEqual(persona.display_name, default_persona.display_name)
        
        # Print the persona details
        print(f"Default persona: {persona.name} ({persona.display_name})")
        print(f"Description: {persona.description}")
        print(f"Expertise areas: {persona.expertise_areas}")


if __name__ == "__main__":
    unittest.main()
