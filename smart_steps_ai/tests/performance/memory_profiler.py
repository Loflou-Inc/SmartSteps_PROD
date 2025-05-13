"""
Smart Steps AI Module - Memory Usage Profiling

This script profiles memory usage in the Smart Steps AI Module during various operations.
Run with: python -m tests.performance.memory_profiler
"""

import gc
import os
import random
import time
from pathlib import Path

import psutil
from memory_profiler import profile

# Import Smart Steps AI components
from smart_steps_ai.config.config_manager import ConfigManager
from smart_steps_ai.conversation.conversation_handler import ConversationHandler
from smart_steps_ai.memory.memory_manager import MemoryManager
from smart_steps_ai.persona.persona_manager import PersonaManager
from smart_steps_ai.providers.mock_provider import MockProvider
from smart_steps_ai.providers.provider_manager import ProviderManager
from smart_steps_ai.session.session_manager import SessionManager


class MemoryProfiler:
    """Memory profiling for Smart Steps AI components."""
    
    def __init__(self):
        """Initialize profiler with necessary components."""
        self.process = psutil.Process(os.getpid())
        self.config_manager = ConfigManager()
        self.persona_manager = PersonaManager(self.config_manager)
        self.session_manager = SessionManager(self.config_manager)
        self.memory_manager = MemoryManager(self.config_manager)
        self.provider_manager = ProviderManager(self.config_manager)
        
        # Register mock provider for testing
        mock_provider = MockProvider(self.config_manager)
        self.provider_manager.register_provider("mock", mock_provider)
        self.provider_manager.set_default_provider("mock")
        
        self.conversation_handler = ConversationHandler(
            session_manager=self.session_manager,
            provider_manager=self.provider_manager,
            memory_manager=self.memory_manager,
            persona_manager=self.persona_manager
        )
        
        # Clean up before starting
        gc.collect()
        self.base_memory = self.get_memory_usage()
        print(f"Initial memory usage: {self.base_memory:.2f} MB")
    
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def print_memory_delta(self, operation_name):
        """Print memory usage delta from baseline."""
        current = self.get_memory_usage()
        delta = current - self.base_memory
        print(f"Memory after {operation_name}: {current:.2f} MB (Delta: {delta:+.2f} MB)")
    
    @profile
    def profile_session_creation(self, num_sessions=10):
        """Profile memory usage during session creation."""
        print("\n=== Profiling Session Creation ===")
        sessions = []
        
        for i in range(num_sessions):
            persona = self.persona_manager.get_persona("therapist_cbt")
            session = self.session_manager.create_session(
                client_name=f"Memory Test Client {i}",
                persona_id=persona.id,
                metadata={"memory_profile": True}
            )
            sessions.append(session)
            
            if (i + 1) % 5 == 0 or i == num_sessions - 1:
                self.print_memory_delta(f"creating {i+1} sessions")
        
        return sessions
    
    @profile
    def profile_conversation(self, session_id, num_messages=20):
        """Profile memory usage during conversation."""
        print("\n=== Profiling Conversation ===")
        
        for i in range(num_messages):
            self.conversation_handler.add_message(
                session_id=session_id,
                user_message=f"This is memory profile test message {i}",
                client=True
            )
            
            if (i + 1) % 5 == 0 or i == num_messages - 1:
                self.print_memory_delta(f"sending {i+1} messages")
        
        # Trigger garbage collection and check memory
        gc.collect()
        self.print_memory_delta("garbage collection after conversation")
    
    @profile
    def profile_memory_retrieval(self, session_id, num_retrievals=10):
        """Profile memory usage during memory retrieval."""
        print("\n=== Profiling Memory Retrieval ===")
        
        for i in range(num_retrievals):
            memories = self.memory_manager.get_memories_for_session(session_id)
            
            if (i + 1) % 5 == 0 or i == num_retrievals - 1:
                self.print_memory_delta(f"retrieving memories {i+1} times")
    
    @profile
    def profile_batch_operations(self, session_id, batch_size=10, num_batches=5):
        """Profile memory usage during batch operations."""
        print("\n=== Profiling Batch Operations ===")
        
        for batch in range(num_batches):
            for i in range(batch_size):
                self.conversation_handler.add_message(
                    session_id=session_id,
                    user_message=f"Batch {batch}, message {i}: Memory profiling test",
                    client=True
                )
            
            self.print_memory_delta(f"processing batch {batch+1}/{num_batches}")
            
            # Pause between batches to see memory changes
            time.sleep(1)
        
        # Trigger garbage collection and check memory
        gc.collect()
        self.print_memory_delta("garbage collection after batch operations")
    
    @profile
    def profile_multiple_concurrent_sessions(self, num_sessions=5, messages_per_session=10):
        """Profile memory usage with multiple active sessions."""
        print("\n=== Profiling Multiple Concurrent Sessions ===")
        
        # Create sessions
        sessions = []
        for i in range(num_sessions):
            persona = self.persona_manager.get_persona("therapist_cbt")
            session = self.session_manager.create_session(
                client_name=f"Concurrent Test Client {i}",
                persona_id=persona.id,
                metadata={"concurrent_profile": True}
            )
            sessions.append(session)
        
        self.print_memory_delta(f"creating {num_sessions} concurrent sessions")
        
        # Simulate concurrent usage by interleaving messages
        for msg_idx in range(messages_per_session):
            for session in sessions:
                self.conversation_handler.add_message(
                    session_id=session.id,
                    user_message=f"Concurrent message {msg_idx} for session {session.client_name}",
                    client=True
                )
            
            self.print_memory_delta(f"sending message {msg_idx+1} to all {num_sessions} sessions")
        
        # Trigger garbage collection and check memory
        gc.collect()
        self.print_memory_delta("garbage collection after concurrent sessions")
    
    @profile
    def profile_persona_loading(self, load_iterations=10):
        """Profile memory usage during persona loading."""
        print("\n=== Profiling Persona Loading ===")
        
        for i in range(load_iterations):
            personas = self.persona_manager.list_personas()
            for persona_id in personas:
                self.persona_manager.get_persona(persona_id)
            
            self.print_memory_delta(f"loading all personas (iteration {i+1})")
    
    def run_all_profiles(self):
        """Run all memory profiling tests."""
        print("\n===== Starting Memory Profiling =====")
        
        # Profile session creation
        sessions = self.profile_session_creation(num_sessions=5)
        test_session_id = sessions[0].id
        
        # Profile conversation
        self.profile_conversation(test_session_id, num_messages=15)
        
        # Profile memory retrieval
        self.profile_memory_retrieval(test_session_id, num_retrievals=10)
        
        # Profile batch operations
        self.profile_batch_operations(test_session_id, batch_size=5, num_batches=3)
        
        # Profile concurrent sessions
        self.profile_multiple_concurrent_sessions(num_sessions=3, messages_per_session=5)
        
        # Profile persona loading
        self.profile_persona_loading(load_iterations=5)
        
        print("\n===== Memory Profiling Complete =====")
        final_memory = self.get_memory_usage()
        print(f"Final memory usage: {final_memory:.2f} MB (Delta from start: {final_memory - self.base_memory:+.2f} MB)")
        
        # Final garbage collection
        gc.collect()
        post_gc_memory = self.get_memory_usage()
        print(f"Memory after final garbage collection: {post_gc_memory:.2f} MB (Delta from start: {post_gc_memory - self.base_memory:+.2f} MB)")


if __name__ == "__main__":
    profiler = MemoryProfiler()
    profiler.run_all_profiles()
