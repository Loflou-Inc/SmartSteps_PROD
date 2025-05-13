"""
Unit tests for the cache_manager module.

This module contains tests for the caching system, including memory and disk caches,
batch processing, and performance monitoring.
"""

import os
import time
import json
import shutil
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from smart_steps_ai.core.cache_manager import (
    Cache,
    MemoryCache,
    DiskCache,
    CacheManager,
    VectorCacheOptimizer,
    BatchProcessor,
    PerformanceMonitor
)

class TestMemoryCache(unittest.TestCase):
    """Tests for the MemoryCache class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.cache = MemoryCache(max_size=5)
    
    def test_set_get(self):
        """Test setting and getting items from the cache."""
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertIsNone(self.cache.get("nonexistent_key"))
    
    def test_delete(self):
        """Test deleting items from the cache."""
        self.cache.set("key1", "value1")
        self.assertTrue(self.cache.delete("key1"))
        self.assertIsNone(self.cache.get("key1"))
        self.assertFalse(self.cache.delete("nonexistent_key"))
    
    def test_clear(self):
        """Test clearing the cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.assertTrue(self.cache.clear())
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_expiry(self):
        """Test item expiry."""
        self.cache.set("key1", "value1", ttl=0.1)  # 100ms TTL
        self.assertEqual(self.cache.get("key1"), "value1")
        time.sleep(0.2)  # Wait for expiry
        self.assertIsNone(self.cache.get("key1"))
    
    def test_max_size(self):
        """Test that the cache respects max_size."""
        # Fill the cache to max_size
        for i in range(5):
            self.cache.set(f"key{i}", f"value{i}")
        
        # Add one more item
        self.cache.set("key5", "value5")
        
        # One of the previous items should have been evicted
        count = sum(1 for i in range(6) if self.cache.get(f"key{i}") is not None)
        self.assertEqual(count, 5)


class TestDiskCache(unittest.TestCase):
    """Tests for the DiskCache class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = DiskCache(cache_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_set_get(self):
        """Test setting and getting items from the cache."""
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertIsNone(self.cache.get("nonexistent_key"))
    
    def test_delete(self):
        """Test deleting items from the cache."""
        self.cache.set("key1", "value1")
        self.assertTrue(self.cache.delete("key1"))
        self.assertIsNone(self.cache.get("key1"))
        self.assertFalse(self.cache.delete("nonexistent_key"))
    
    def test_clear(self):
        """Test clearing the cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.assertTrue(self.cache.clear())
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_expiry(self):
        """Test item expiry."""
        self.cache.set("key1", "value1", ttl=0.1)  # 100ms TTL
        self.assertEqual(self.cache.get("key1"), "value1")
        time.sleep(0.2)  # Wait for expiry
        self.assertIsNone(self.cache.get("key1"))
    
    def test_complex_objects(self):
        """Test caching complex objects."""
        obj = {
            "name": "Test",
            "nested": {
                "list": [1, 2, 3],
                "dict": {"a": 1, "b": 2}
            }
        }
        self.cache.set("complex", obj)
        self.assertEqual(self.cache.get("complex"), obj)


class TestCacheManager(unittest.TestCase):
    """Tests for the CacheManager class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.cache_manager = CacheManager()
    
    def test_get_cache(self):
        """Test getting different cache types."""
        memory_cache = self.cache_manager.get_cache("memory")
        self.assertIsInstance(memory_cache, MemoryCache)
        
        disk_cache = self.cache_manager.get_cache("disk")
        self.assertIsInstance(disk_cache, DiskCache)
        
        # Default to memory cache for unknown type
        default_cache = self.cache_manager.get_cache("unknown")
        self.assertIsInstance(default_cache, MemoryCache)
    
    def test_cached_decorator(self):
        """Test the cached decorator."""
        counter = [0]
        
        @self.cache_manager.cached(cache_type="memory")
        def test_function(arg):
            counter[0] += 1
            return f"result_{arg}"
        
        # First call should execute the function
        self.assertEqual(test_function("test"), "result_test")
        self.assertEqual(counter[0], 1)
        
        # Second call with same args should use cached result
        self.assertEqual(test_function("test"), "result_test")
        self.assertEqual(counter[0], 1)  # Counter shouldn't increment
        
        # Call with different args should execute the function again
        self.assertEqual(test_function("other"), "result_other")
        self.assertEqual(counter[0], 2)


class TestVectorCacheOptimizer(unittest.TestCase):
    """Tests for the VectorCacheOptimizer class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.cache_manager = CacheManager()
        self.vector_cache = VectorCacheOptimizer(self.cache_manager)
    
    def test_cached_embed_text(self):
        """Test the cached_embed_text method."""
        counter = [0]
        
        def embed_text(text):
            counter[0] += 1
            return [0.1, 0.2, 0.3]
        
        cached_embed = self.vector_cache.cached_embed_text(embed_text)
        
        # First call should execute the function
        self.assertEqual(cached_embed("test"), [0.1, 0.2, 0.3])
        self.assertEqual(counter[0], 1)
        
        # Second call with same args should use cached result
        self.assertEqual(cached_embed("test"), [0.1, 0.2, 0.3])
        self.assertEqual(counter[0], 1)  # Counter shouldn't increment
        
        # Call with different args should execute the function again
        self.assertEqual(cached_embed("other"), [0.1, 0.2, 0.3])
        self.assertEqual(counter[0], 2)
    
    def test_cached_similarity(self):
        """Test the cached_similarity method."""
        counter = [0]
        
        def similarity(embedding1, embedding2):
            counter[0] += 1
            return 0.75
        
        cached_similarity = self.vector_cache.cached_similarity(similarity)
        
        # First call should execute the function
        embedding1 = [0.1, 0.2, 0.3]
        embedding2 = [0.4, 0.5, 0.6]
        self.assertEqual(cached_similarity(embedding1, embedding2), 0.75)
        self.assertEqual(counter[0], 1)
        
        # Second call with same args should use cached result
        self.assertEqual(cached_similarity(embedding1, embedding2), 0.75)
        self.assertEqual(counter[0], 1)  # Counter shouldn't increment
        
        # Call with different args should execute the function again
        embedding3 = [0.7, 0.8, 0.9]
        self.assertEqual(cached_similarity(embedding1, embedding3), 0.75)
        self.assertEqual(counter[0], 2)


class TestBatchProcessor(unittest.TestCase):
    """Tests for the BatchProcessor class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.batch_processor = BatchProcessor(batch_size=2)
    
    def test_process_batch(self):
        """Test processing items in batches."""
        items = [1, 2, 3, 4, 5]
        
        # Define a function that squares the input
        def square(x):
            return x * x
        
        # Process the batch
        results = self.batch_processor.process_batch(items, square)
        
        # Check the results
        self.assertEqual(results, [1, 4, 9, 16, 25])
    
    def test_map_async(self):
        """Test asynchronous processing."""
        items = [1, 2, 3, 4, 5]
        
        # Define a function that squares the input
        def square(x):
            return x * x
        
        # Process the batch asynchronously
        results = self.batch_processor.map_async(items, square)
        
        # Check the results
        self.assertEqual(results, [1, 4, 9, 16, 25])


class TestPerformanceMonitor(unittest.TestCase):
    """Tests for the PerformanceMonitor class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.performance_monitor = PerformanceMonitor()
    
    def test_timed_decorator(self):
        """Test the timed decorator."""
        @self.performance_monitor.timed("test_operation")
        def test_function():
            time.sleep(0.1)  # Sleep for 100ms
            return "result"
        
        # Execute the function
        self.assertEqual(test_function(), "result")
        
        # Check that the timing was recorded
        self.assertIn("test_operation", self.performance_monitor.timings)
        self.assertEqual(self.performance_monitor.get_execution_count("test_operation"), 1)
        
        # Check that the average time is reasonable
        avg_time = self.performance_monitor.get_average_time("test_operation")
        self.assertGreaterEqual(avg_time, 0.05)  # Should be at least 50ms
        self.assertLessEqual(avg_time, 0.2)  # Should be at most 200ms
    
    def test_get_performance_report(self):
        """Test generating a performance report."""
        @self.performance_monitor.timed("test_operation")
        def test_function():
            time.sleep(0.01)  # Sleep for 10ms
            return "result"
        
        # Execute the function multiple times
        for _ in range(3):
            test_function()
        
        # Get the performance report
        report = self.performance_monitor.get_performance_report()
        
        # Check the report structure
        self.assertIn("test_operation", report)
        self.assertIn("average_time", report["test_operation"])
        self.assertIn("min_time", report["test_operation"])
        self.assertIn("max_time", report["test_operation"])
        self.assertIn("execution_count", report["test_operation"])
        
        # Check the execution count
        self.assertEqual(report["test_operation"]["execution_count"], 3)


if __name__ == "__main__":
    unittest.main()
