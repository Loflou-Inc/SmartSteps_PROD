"""Test the SessionManager class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_steps_ai.persistence import PersistenceManager
from src.smart_steps_ai.persona import PersonaManager
from src.smart_steps_ai.session import SessionManager
from src.smart_steps_ai.session.models import MessageRole, SessionState, SessionType


class TestSessionManager(unittest.TestCase):
    """Test the SessionManager class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test directory for persistence
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        
        # Initialize persistence manager with test directory
        self.persistence_manager = PersistenceManager(base_dir=self.test_dir)
        
        # Initialize persona manager
        self.persona_manager = PersonaManager()
        
        # Initialize session manager
        self.session_manager = SessionManager(
            persistence_manager=self.persistence_manager,
            persona_manager=self.persona_manager,
        )
        
        # Test client name
        self.client_name = "Test Client"

    def tearDown(self):
        """Clean up the test environment."""
        # Clean up test data
        sessions_dir = self.test_dir / "sessions"
        if sessions_dir.exists():
            for file in sessions_dir.glob("*.json"):
                file.unlink()
        
        metadata_dir = self.test_dir / "session_metadata"
        if metadata_dir.exists():
            for file in metadata_dir.glob("*.json"):
                file.unlink()

    def test_create_session(self):
        """Test creating a session."""
        # Get the default persona
        default_persona = self.persona_manager.get_default_persona()
        self.assertIsNotNone(default_persona, "Default persona is None")
        
        # Create a session
        session = self.session_manager.create_session(
            client_name=self.client_name,
            persona_name=default_persona.name,
            session_type=SessionType.INITIAL,
        )
        
        # Verify session properties
        self.assertIsNotNone(session, "Created session is None")
        self.assertEqual(session.client_name, self.client_name)
        self.assertEqual(session.persona_name, default_persona.name)
        self.assertEqual(session.session_type, SessionType.INITIAL)
        self.assertEqual(session.state, SessionState.CREATED)
        self.assertEqual(session.messages_count, 0)
        
        print(f"Created session {session.id} for client {session.client_name}")

    def test_add_message(self):
        """Test adding a message to a session."""
        # Create a session
        session = self.session_manager.create_session(client_name=self.client_name)
        
        # Add a message
        message_content = "Hello, this is a test message."
        message = self.session_manager.add_message(
            session_id=session.id,
            role=MessageRole.CLIENT,
            content=message_content,
        )
        
        # Verify message properties
        self.assertIsNotNone(message, "Added message is None")
        self.assertEqual(message.role, MessageRole.CLIENT)
        self.assertEqual(message.content, message_content)
        
        # Get the updated session
        updated_session = self.session_manager.get_session(session.id)
        
        # Verify session updates
        self.assertIsNotNone(updated_session, "Updated session is None")
        self.assertEqual(updated_session.messages_count, 1)
        self.assertEqual(updated_session.state, SessionState.ACTIVE)
        
        # Get the message from the session
        self.assertEqual(len(updated_session.messages), 1)
        self.assertEqual(updated_session.messages[0].content, message_content)
        
        print(f"Added message to session {session.id}: {message.role.value} - {message.content}")

    def test_list_sessions(self):
        """Test listing sessions."""
        # Create multiple sessions
        session1 = self.session_manager.create_session(client_name=self.client_name)
        session2 = self.session_manager.create_session(client_name="Another Client")
        session3 = self.session_manager.create_session(client_name=self.client_name)
        
        # List all sessions
        all_sessions = self.session_manager.list_sessions()
        
        # Verify list
        self.assertEqual(len(all_sessions), 3)
        
        # Filter by client name
        client_sessions = self.session_manager.list_sessions(client_name=self.client_name)
        
        # Verify filtered list
        self.assertEqual(len(client_sessions), 2)
        for session in client_sessions:
            self.assertEqual(session.client_name, self.client_name)
        
        print(f"Listed sessions: {len(all_sessions)} total, {len(client_sessions)} for client {self.client_name}")

    def test_session_state_transitions(self):
        """Test session state transitions."""
        # Create a session
        session = self.session_manager.create_session(client_name=self.client_name)
        
        # Verify initial state
        self.assertEqual(session.state, SessionState.CREATED)
        
        # Start the session
        success = self.session_manager.update_session_state(session.id, SessionState.ACTIVE)
        self.assertTrue(success, "Failed to update session state")
        
        # Verify state
        session = self.session_manager.get_session(session.id)
        self.assertEqual(session.state, SessionState.ACTIVE)
        
        # Pause the session
        success = self.session_manager.update_session_state(session.id, SessionState.PAUSED)
        self.assertTrue(success, "Failed to update session state")
        
        # Verify state
        session = self.session_manager.get_session(session.id)
        self.assertEqual(session.state, SessionState.PAUSED)
        
        # Resume the session
        success = self.session_manager.update_session_state(session.id, SessionState.ACTIVE)
        self.assertTrue(success, "Failed to update session state")
        
        # Verify state
        session = self.session_manager.get_session(session.id)
        self.assertEqual(session.state, SessionState.ACTIVE)
        
        # Complete the session
        success = self.session_manager.update_session_state(session.id, SessionState.COMPLETED)
        self.assertTrue(success, "Failed to update session state")
        
        # Verify state
        session = self.session_manager.get_session(session.id)
        self.assertEqual(session.state, SessionState.COMPLETED)
        self.assertIsNotNone(session.end_time, "End time is None for completed session")
        
        print(f"Successfully tested session state transitions for session {session.id}")


if __name__ == "__main__":
    unittest.main()
