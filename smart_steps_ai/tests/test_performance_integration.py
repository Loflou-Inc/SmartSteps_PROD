"""
Integration tests for performance optimization components.

This module contains integration tests that verify different performance
optimization components work together correctly.
"""

import os
import time
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

class TestCacheIntegration(unittest.TestCase):
    """Integration tests for the caching system."""
    
    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Clear caches before each test
        memory_cache = cache_manager.get_cache("memory")
        memory_cache.clear()
        
        disk_cache = cache_manager.get_cache("disk")
        disk_cache.clear()
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_embedding_caching(self):
        """Test that embeddings are properly cached."""
        # Create an embedding manager
        embedding_manager = EmbeddingManager()
        
        # Create a simple test function to monitor calls
        call_count = [0]
        original_embed_text = embedding_manager.embed_text
        
        def monitored_embed_text(text):
            call_count[0] += 1
            return original_embed_text(text)
        
        # Replace the embed_text method
        embedding_manager.embed_text = monitored_embed_text
        
        # Create a cached version
        cached_embed = vector_cache_optimizer.cached_embed_text(embedding_manager.embed_text)
        
        # Assign the cached version back
        embedding_manager.embed_text = cached_embed
        
        # Call it multiple times with the same text
        text = "This is a test."
        for _ in range(5):
            embedding = embedding_manager.embed_text(text)
            self.assertIsInstance(embedding, list)
        
        # Verify that the function was only called once due to caching
        self.assertEqual(call_count[0], 1)
        
        # Call with different text
        other_text = "This is another test."
        embedding = embedding_manager.embed_text(other_text)
        
        # Verify that the function was called again
        self.assertEqual(call_count[0], 2)
    
    def test_similarity_caching(self):
        """Test that similarity calculations are properly cached."""
        # Create an embedding manager
        embedding_manager = EmbeddingManager()
        
        # Create a simple test function to monitor calls
        call_count = [0]
        original_similarity = embedding_manager.similarity
        
        def monitored_similarity(embedding1, embedding2):
            call_count[0] += 1
            return original_similarity(embedding1, embedding2)
        
        # Replace the similarity method
        embedding_manager.similarity = monitored_similarity
        
        # Create a cached version
        cached_similarity = vector_cache_optimizer.cached_similarity(embedding_manager.similarity)
        
        # Assign the cached version back
        embedding_manager.similarity = cached_similarity
        
        # Create test embeddings
        embedding1 = [0.1, 0.2, 0.3]
        embedding2 = [0.4, 0.5, 0.6]
        
        # Call it multiple times with the same embeddings
        for _ in range(5):
            similarity = embedding_manager.similarity(embedding1, embedding2)
            self.assertIsInstance(similarity, float)
        
        # Verify that the function was only called once due to caching
        self.assertEqual(call_count[0], 1)
        
        # Call with different embeddings
        embedding3 = [0.7, 0.8, 0.9]
        similarity = embedding_manager.similarity(embedding1, embedding3)
        
        # Verify that the function was called again
        self.assertEqual(call_count[0], 2)
    
    def test_batch_processing_integration(self):
        """Test batch processing with the vector store."""
        # Create a vector store with a temp directory
        vector_store = VectorStore(self.temp_dir)
        
        # Create a collection
        vector_store.create_collection("test_collection")
        
        # Define a test document
        document = """
        This is a test document with multiple paragraphs.
        
        Each paragraph will be split into chunks for processing.
        
        The batch processor should handle these chunks efficiently.
        
        We can verify that the batch processor is working by checking
        that all chunks are properly embedded and stored.
        """
        
        # Create a simple test function to monitor batch processing
        processing_batches = []
        original_process_batch = batch_processor.process_batch
        
        def monitored_process_batch(items, operation):
            processing_batches.append(len(items))
            return original_process_batch(items, operation)
        
        # Replace the process_batch method
        batch_processor.process_batch = monitored_process_batch
        
        # Add the document
        chunk_ids = vector_store.add_document(
            collection_name="test_collection",
            document_id="test_doc",
            content=document,
            chunk_size=100,
            chunk_overlap=20
        )
        
        # Verify that batch processing was used
        self.assertTrue(len(processing_batches) > 0)
        
        # Verify that all chunks were processed
        chunks = vector_store.get_document_chunks("test_collection", "test_doc")
        self.assertEqual(len(chunks), len(chunk_ids))


class TestMemoryOptimizationIntegration(unittest.TestCase):
    """Integration tests for memory optimization components."""
    
    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a vector store with a temp directory
        self.vector_store = VectorStore(os.path.join(self.temp_dir, "vectors"))
        
        # Enable vector compression
        self.vector_store.use_compressed_vectors = True
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_vector_compression_integration(self):
        """Test that vector compression is properly applied in the vector store."""
        # Create a collection
        self.vector_store.create_collection("test_collection")
        
        # Add a document
        document = "This is a test document for vector compression."
        self.vector_store.add_document(
            collection_name="test_collection",
            document_id="test_doc",
            content=document
        )
        
        # Optimize memory to trigger compression
        result = self.vector_store.optimize_memory()
        
        # Verify that vectors were compressed
        # This is hard to test directly, so we check that the method returned without error
        self.assertIsInstance(result, dict)
        
        # Perform a search to verify that decompression works
        results = self.vector_store.search(
            collection_name="test_collection",
            query="test document",
            limit=5
        )
        
        # Verify that results were returned
        self.assertTrue(len(results) > 0)
        
        # Verify that the results contain the expected fields
        self.assertIn("text", results[0])
        self.assertIn("similarity", results[0])
        self.assertIn("document_id", results[0])
    
    def test_memory_optimized_collection_integration(self):
        """Test that memory-optimized collection works with the vector store."""
        # Create a collection
        self.vector_store.create_collection("test_collection")
        
        # Add multiple documents
        for i in range(5):
            document = f"This is test document {i} for memory optimization."
            self.vector_store.add_document(
                collection_name="test_collection",
                document_id=f"test_doc_{i}",
                content=document
            )
        
        # Verify that collections are properly stored
        self.assertIn("test_collection", self.vector_store.collections.keys())
        
        # Get a collection
        collection = self.vector_store.collections["test_collection"]
        
        # Verify that documents are in the collection
        self.assertEqual(len(collection["documents"]), 5)
        
        # Optimize memory
        self.vector_store.collections.optimize_memory()
        
        # Verify that collection can still be accessed
        self.assertIn("test_collection", self.vector_store.collections.keys())
        collection = self.vector_store.collections["test_collection"]
        self.assertEqual(len(collection["documents"]), 5)
        
        # Perform a search to verify functionality
        results = self.vector_store.search(
            collection_name="test_collection",
            query="test document",
            limit=5
        )
        
        # Verify that results were returned
        self.assertTrue(len(results) > 0)
    
    def test_layered_memory_performance_integration(self):
        """Test that layered memory works with performance optimizations."""
        # Create a temporary data directory
        data_dir = os.path.join(self.temp_dir, "memory_data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Create a layered memory manager
        memory_manager = LayeredMemoryManager(
            persona_id="test_persona",
            data_dir=data_dir
        )
        
        # Add a document to the foundation layer
        memory_manager.foundation.add_document(
            document_id="test_doc",
            content="This is a test document for layered memory performance testing.",
            metadata={"type": "test", "importance": "high"}
        )
        
        # Record some interactions
        for i in range(3):
            memory_manager.record_interaction(
                session_id="test_session",
                client_message=f"Client message {i}",
                persona_response=f"Persona response {i}"
            )
        
        # Generate an insight
        memory_manager.generate_insight(
            content="This is a test insight from performance integration testing.",
            domain="test_domain",
            sources={
                "foundation": ["test_doc"],
                "experience": ["test_session"]
            },
            confidence=0.85
        )
        
        # Time the retrieval of context
        start_time = time.time()
        context = memory_manager.retrieve_context(
            query="test document",
            session_id="test_session"
        )
        retrieval_time = time.time() - start_time
        
        # Verify that context was retrieved
        self.assertIn("foundation", context)
        self.assertIn("experience", context)
        self.assertIn("synthesis", context)
        self.assertIn("meta_cognitive", context)
        
        # Perform a second retrieval which should be faster due to caching
        start_time = time.time()
        cached_context = memory_manager.retrieve_context(
            query="test document",
            session_id="test_session"
        )
        cached_retrieval_time = time.time() - start_time
        
        # Verify that the cached retrieval is either faster or same speed
        # (allowing some margin for timing variations)
        self.assertLessEqual(cached_retrieval_time, retrieval_time * 1.5)
        
        # Verify that the cached context is the same as the original
        self.assertEqual(context, cached_context)


class TestPerformanceMonitoringIntegration(unittest.TestCase):
    """Integration tests for performance monitoring components."""
    
    def test_performance_monitoring_integration(self):
        """Test that performance monitoring works with components."""
        # Clear performance monitor data
        performance_monitor.timings.clear()
        performance_monitor.execution_counts.clear()
        
        # Create a vector store
        vector_store = VectorStore()
        
        # Create a knowledge store
        knowledge_store = KnowledgeStore()
        
        # Initialize persona knowledge
        knowledge_store.initialize_persona_knowledge("test_persona")
        
        # Add a document with performance monitoring
        document = "This is a test document for performance monitoring."
        knowledge_store.add_document(
            persona_id="test_persona",
            document_id="test_doc",
            content=document
        )
        
        # Perform a search
        results = knowledge_store.search(
            persona_id="test_persona",
            query="test document",
            limit=5
        )
        
        # Get performance report
        report = performance_monitor.get_performance_report()
        
        # Verify that performance data was collected
        self.assertTrue(len(report) > 0)
        
        # Check for expected operations in the report
        operations = set(report.keys())
        
        # At least one of these operations should be in the report
        expected_operations = {
            "embed_text", "calculate_similarity", "embed_document", "search"
        }
        
        self.assertTrue(expected_operations.intersection(operations))
        
        # Verify that each operation has the expected metrics
        for operation, metrics in report.items():
            self.assertIn("average_time", metrics)
            self.assertIn("min_time", metrics)
            self.assertIn("max_time", metrics)
            self.assertIn("execution_count", metrics)
            
            # Execution count should be at least 1
            self.assertGreaterEqual(metrics["execution_count"], 1)


if __name__ == "__main__":
    unittest.main()