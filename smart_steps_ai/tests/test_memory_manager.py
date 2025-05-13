"""Test the MemoryManager class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_steps_ai.memory import MemoryManager
from src.smart_steps_ai.memory.models import MemoryType
from src.smart_steps_ai.config import get_config_manager


class TestMemoryManager(unittest.TestCase):
    """Test the MemoryManager class."""

    def setUp(self):
        """Set up the test environment."""
        # Initialize memory manager
        self.memory_manager = MemoryManager()
        
        # Test client name
        self.client_name = "Test Client"

    def test_memory_integration(self):
        """Test basic memory integration functionality."""
        # Check if memory integration is enabled
        if not self.memory_manager.enabled:
            self.skipTest("Memory integration is disabled")
        
        # Try to store a memory
        memory_text = "This is a test memory for the Smart Steps AI module."
        success = self.memory_manager.store_memory(
            text=memory_text,
            client_name=self.client_name,
            memory_type=MemoryType.CLIENT_INFORMATION,
            source_type="test",
            source_id="test_memory_manager",
            importance=5,
        )
        
        # Verify storage
        self.assertTrue(success, "Failed to store memory")
        
        print(f"Successfully stored memory: {memory_text[:30]}...")

    def test_retrieve_memories(self):
        """Test retrieving memories."""
        # Check if memory integration is enabled
        if not self.memory_manager.enabled:
            self.skipTest("Memory integration is disabled")
        
        # Store a memory
        memory_text = "The client mentioned having difficulty with time management skills."
        self.memory_manager.store_memory(
            text=memory_text,
            client_name=self.client_name,
            memory_type=MemoryType.OBSERVATION,
            source_type="test",
            source_id="test_retrieve",
            importance=6,
        )
        
        # Retrieve memories
        memories = self.memory_manager.retrieve_memories(
            query="time management",
            client_name=self.client_name,
        )
        
        # Verify retrieval
        self.assertTrue(len(memories) > 0, "No memories retrieved")
        
        print(f"Retrieved {len(memories)} memories")
        for i, memory in enumerate(memories):
            print(f"{i+1}. {memory[:50]}...")

    def test_get_memory_context(self):
        """Test getting a memory context."""
        # Check if memory integration is enabled
        if not self.memory_manager.enabled:
            self.skipTest("Memory integration is disabled")
        
        # Store a memory
        memory_text = "The client expressed interest in developing better communication strategies."
        self.memory_manager.store_memory(
            text=memory_text,
            client_name=self.client_name,
            memory_type=MemoryType.PREFERENCE,
            source_type="test",
            source_id="test_context",
            importance=7,
        )
        
        # Get a memory context
        context = self.memory_manager.get_memory_context(
            query="communication strategies",
            client_name=self.client_name,
        )
        
        # Verify context
        self.assertTrue(len(context) > 0, "No memory context retrieved")
        
        print(f"Retrieved memory context ({len(context)} characters)")
        print(context[:100] + "..." if len(context) > 100 else context)


if __name__ == "__main__":
    unittest.main()
