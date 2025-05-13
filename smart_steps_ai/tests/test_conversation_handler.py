"""Test the ConversationHandler class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import provider manager first to avoid circular imports
from src.smart_steps_ai.provider import ProviderManager
from src.smart_steps_ai.memory import MemoryManager
from src.smart_steps_ai.persistence import PersistenceManager
from src.smart_steps_ai.session import ConversationHandler, MessageRole


class TestConversationHandler(unittest.TestCase):
    """Test the ConversationHandler class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test directory for persistence
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        
        # Initialize persistence manager with test directory
        self.persistence_manager = PersistenceManager(base_dir=self.test_dir)
        
        # Initialize memory manager
        self.memory_manager = MemoryManager()
        
        # Initialize provider manager
        self.provider_manager = ProviderManager()
        
        # Initialize conversation handler
        self.handler = ConversationHandler(
            session_manager=None,  # Will be created internally
            provider_manager=self.provider_manager,
            memory_manager=self.memory_manager,
        )
        
        # Test client name
        self.client_name = "Test Conversation Client"

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
        """Test creating a new session."""
        # Create a session
        session_info = self.handler.create_new_session(
            client_name=self.client_name,
            persona_name=None,  # Use default
            session_type="initial",
            initial_message="Hello, I'm here for my first session.",
        )
        
        # Verify session creation
        self.assertIsNotNone(session_info, "Session info is None")
        self.assertEqual(session_info["client_name"], self.client_name)
        self.assertEqual(session_info["session_type"], "initial")
        
        print(f"Created session: {session_info['id']}")
        
        # Get the conversation history
        history = self.handler.get_conversation_history(session_info["id"])
        
        # Verify history
        self.assertIsNotNone(history, "Conversation history is None")
        self.assertEqual(len(history), 2, "History should have 2 messages (client + assistant)")
        
        # Check the first message
        self.assertEqual(history[0]["role"], "client")
        self.assertEqual(history[0]["content"], "Hello, I'm here for my first session.")
        
        # Check the assistant's response
        self.assertEqual(history[1]["role"], "assistant")
        self.assertTrue(len(history[1]["content"]) > 0, "Assistant response is empty")
        
        print(f"Client: {history[0]['content']}")
        print(f"Assistant: {history[1]['content']}")

    def test_send_message(self):
        """Test sending a message in a session."""
        # Create a session
        session_info = self.handler.create_new_session(
            client_name=self.client_name,
            persona_name=None,  # Use default
            session_type="standard",
        )
        
        # Send a message
        client_msg, assistant_msg = self.handler.send_message(
            session_id=session_info["id"],
            message="I've been feeling anxious about my job lately.",
            role=MessageRole.CLIENT,
            provider_name="mock",  # Explicitly use the mock provider
        )
        
        # Verify messages
        self.assertIsNotNone(client_msg, "Client message is None")
        self.assertIsNotNone(assistant_msg, "Assistant message is None")
        
        self.assertEqual(client_msg.role, MessageRole.CLIENT)
        self.assertEqual(assistant_msg.role, MessageRole.ASSISTANT)
        
        # Check message content
        self.assertEqual(client_msg.content, "I've been feeling anxious about my job lately.")
        self.assertTrue(len(assistant_msg.content) > 0, "Assistant response is empty")
        
        # Check message metadata
        self.assertTrue("provider" in assistant_msg.metadata, "Provider not in metadata")
        self.assertEqual(assistant_msg.metadata["provider"], "mock")
        
        print(f"Client: {client_msg.content}")
        print(f"Assistant: {assistant_msg.content}")
        print(f"Provider: {assistant_msg.metadata['provider']}")
        print(f"Model: {assistant_msg.metadata['model']}")

    def test_conversation_flow(self):
        """Test a complete conversation flow."""
        # Create a session
        session_info = self.handler.create_new_session(
            client_name=self.client_name,
            persona_name=None,  # Use default
            session_type="standard",
        )
        
        # Exchange multiple messages
        messages = [
            "I'm struggling with managing my time effectively.",
            "I have too many competing priorities and can't focus on what's important.",
            "Yes, I've tried making to-do lists, but I still get overwhelmed.",
            "I think I need a better system for prioritizing tasks.",
        ]
        
        # Send messages and verify responses
        for message in messages:
            client_msg, assistant_msg = self.handler.send_message(
                session_id=session_info["id"],
                message=message,
                provider_name="mock",
            )
            
            # Verify messages
            self.assertIsNotNone(client_msg, "Client message is None")
            self.assertIsNotNone(assistant_msg, "Assistant message is None")
            
            # Print the exchange
            print(f"Client: {client_msg.content}")
            print(f"Assistant: {assistant_msg.content}")
            print("-" * 50)
        
        # Get the complete conversation history
        history = self.handler.get_conversation_history(session_info["id"])
        
        # Verify history
        self.assertIsNotNone(history, "Conversation history is None")
        self.assertEqual(len(history), len(messages) * 2, "History should have all messages")
        
        print(f"Complete conversation has {len(history)} messages")


if __name__ == "__main__":
    unittest.main()
