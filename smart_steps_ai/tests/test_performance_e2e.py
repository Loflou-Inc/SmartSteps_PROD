"""
End-to-end tests for performance optimization components.

This module contains end-to-end tests that simulate realistic usage scenarios
for the performance optimization components.
"""

import os
import time
import json
import shutil
import unittest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

from smart_steps_ai.core.cache_manager import (
    cache_manager,
    vector_cache_optimizer,
    batch_processor,
    performance_monitor
)
from smart_steps_ai.core.memory_optimizer import (
    vector_compressor,
    memory_monitor,
    MemoryOptimizedCollection
)
from smart_steps_ai.core.knowledge_store import (
    EmbeddingManager,
    VectorStore,
    KnowledgeStore
)
from smart_steps_ai.core.layered_memory import (
    LayeredMemoryManager
)
from smart_steps_ai.core.session_manager import (
    SessionManager
)
from smart_steps_ai.core.persona_manager import (
    PersonaManager
)
from smart_steps_ai.core.config_manager import (
    ConfigManager
)

class TestPerformanceE2E(unittest.TestCase):
    """End-to-end tests for performance optimization."""
    
    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create directories for test data
        self.config_dir = os.path.join(self.temp_dir, "config")
        self.data_dir = os.path.join(self.temp_dir, "data")
        self.personas_dir = os.path.join(self.temp_dir, "personas")
        self.sessions_dir = os.path.join(self.temp_dir, "sessions")
        
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.personas_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Create test persona
        self.create_test_persona()
        
        # Initialize components
        self.config_manager = ConfigManager(config_dir=self.config_dir)
        self.persona_manager = PersonaManager(personas_dir=self.personas_dir)
        self.session_manager = SessionManager(
            sessions_dir=self.sessions_dir,
            persona_manager=self.persona_manager
        )
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_persona(self):
        """Create a test persona."""
        persona_data = {
            "id": "test_therapist",
            "name": "Dr. Test Therapist",
            "type": "therapist",
            "background": "A test therapist persona for performance testing.",
            "education": ["Test University"],
            "specialties": ["Testing", "Performance Optimization"],
            "approach": "Test-driven therapy"
        }
        
        os.makedirs(os.path.join(self.personas_dir, "test_therapist"), exist_ok=True)
        
        # Write persona file
        with open(os.path.join(self.personas_dir, "test_therapist", "persona.json"), "w") as f:
            json.dump(persona_data, f, indent=2)
    
    def test_complete_workflow(self):
        """
        Test a complete workflow with performance optimization.
        
        This test simulates a realistic usage scenario with:
        1. Loading a persona
        2. Creating a session
        3. Adding knowledge to the layered memory system
        4. Simulating conversations
        5. Generating insights
        6. Retrieving context multiple times
        7. Verifying performance improvements from caching
        """
        # Clear caches and performance data
        memory_cache = cache_manager.get_cache("memory")
        memory_cache.clear()
        
        disk_cache = cache_manager.get_cache("disk")
        disk_cache.clear()
        
        performance_monitor.timings.clear()
        performance_monitor.execution_counts.clear()
        
        # 1. Load persona
        persona = self.persona_manager.load_persona("test_therapist")
        self.assertEqual(persona["name"], "Dr. Test Therapist")
        
        # 2. Create session
        session = self.session_manager.create_session(
            persona_id="test_therapist",
            client_name="Test Client",
            session_type="performance_testing"
        )
        session_id = session["id"]
        
        # 3. Create layered memory manager
        memory_manager = LayeredMemoryManager(
            persona_id="test_therapist",
            data_dir=os.path.join(self.data_dir, "memory")
        )
        
        # Add knowledge to foundation layer
        document = """
        Performance optimization is a critical aspect of software development.
        It involves improving the efficiency, speed, and resource usage of applications.
        Techniques include caching, batch processing, memory optimization, and more.
        Proper performance testing is essential to identify bottlenecks and validate optimizations.
        
        Key performance metrics include:
        - Response time: How quickly the system responds to requests
        - Throughput: How many operations can be completed in a given time period
        - Resource usage: CPU, memory, disk, and network utilization
        - Scalability: How well the system handles increased load
        
        Performance optimization should be an ongoing process, with regular monitoring
        and improvements based on real-world usage patterns.
        """
        
        memory_manager.foundation.add_document(
            document_id="performance_knowledge",
            content=document,
            metadata={"type": "reference", "topic": "performance_optimization"}
        )
        
        # 4. Simulate conversations
        conversation = [
            {
                "client": "I'm concerned about the performance of my application.",
                "persona": "I understand your concern. Performance issues can significantly impact user experience. Can you tell me more about what you're observing?"
            },
            {
                "client": "The application becomes slower as more users are added.",
                "persona": "That sounds like a scalability issue. We should look at how resources are being used and identify potential bottlenecks."
            },
            {
                "client": "I think it might be related to database queries.",
                "persona": "Database performance is often a common bottleneck. We should examine query execution plans, indexing strategies, and connection pooling."
            }
        ]
        
        # Record conversations
        for exchange in conversation:
            memory_manager.record_interaction(
                session_id=session_id,
                client_message=exchange["client"],
                persona_response=exchange["persona"]
            )
            
            # Update session history
            self.session_manager.add_message(
                session_id=session_id,
                speaker="client",
                content=exchange["client"]
            )
            
            self.session_manager.add_message(
                session_id=session_id,
                speaker="persona",
                content=exchange["persona"]
            )
        
        # 5. Generate insights
        memory_manager.generate_insight(
            content="Performance issues often manifest as scalability problems when user load increases.",
            domain="performance_optimization",
            sources={
                "foundation": ["performance_knowledge"],
                "experience": [session_id]
            },
            confidence=0.9
        )
        
        memory_manager.generate_insight(
            content="Database optimization is a common first step in addressing application performance issues.",
            domain="database_performance",
            sources={
                "foundation": ["performance_knowledge"],
                "experience": [session_id]
            },
            confidence=0.85
        )
        
        # 6. Measure initial context retrieval time
        start_time = time.time()
        context = memory_manager.retrieve_context(
            query="How can I improve database performance?",
            session_id=session_id
        )
        initial_retrieval_time = time.time() - start_time
        
        # Verify that context was retrieved successfully
        self.assertIn("foundation", context)
        self.assertIn("experience", context)
        self.assertIn("synthesis", context)
        self.assertIn("meta_cognitive", context)
        
        # Verify context contains relevant information
        formatted_context = memory_manager.format_context(context)
        self.assertIn("database", formatted_context.lower())
        self.assertIn("performance", formatted_context.lower())
        
        # 7. Measure cached context retrieval time
        start_time = time.time()
        cached_context = memory_manager.retrieve_context(
            query="How can I improve database performance?",
            session_id=session_id
        )
        cached_retrieval_time = time.time() - start_time
        
        # Verify that cached retrieval is faster
        self.assertLessEqual(cached_retrieval_time, initial_retrieval_time * 0.8)
        
        # Verify that the cached context is the same
        self.assertEqual(context, cached_context)
        
        # 8. Check performance report
        report = performance_monitor.get_performance_report()
        
        # Verify that performance data was collected
        self.assertTrue(len(report) > 0)
        
        # Verify that retrieve_context was monitored
        self.assertIn("retrieve_context", report)
        
        # Check execution count
        self.assertEqual(report["retrieve_context"]["execution_count"], 2)
        
        # 9. Test memory optimization
        memory_stats_before = memory_monitor.get_memory_usage()
        
        # Optimize memory
        optimization_result = memory_monitor.optimize_memory()
        
        # Verify that optimization completed successfully
        self.assertIsInstance(optimization_result, dict)
        self.assertIn("objects_cleaned", optimization_result)
        
        # 10. Verify that the system still works after optimization
        context_after_optimization = memory_manager.retrieve_context(
            query="What are key performance metrics?",
            session_id=session_id
        )
        
        # Verify that context retrieval still works
        self.assertIn("foundation", context_after_optimization)
        self.assertIn("experience", context_after_optimization)
        
        # Verify that the context contains relevant information
        formatted_context = memory_manager.format_context(context_after_optimization)
        self.assertIn("metrics", formatted_context.lower())
        self.assertIn("performance", formatted_context.lower())


if __name__ == "__main__":
    unittest.main()
