"""
Unit tests for the memory_optimizer module.

This module contains tests for memory optimization components, including
vector compression, memory-optimized collections, and memory monitoring.
"""

import os
import gc
import sys
import json
import shutil
import unittest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

from smart_steps_ai.core.memory_optimizer import (
    CompressedVector,
    MemoryOptimizedCollection,
    MemoryMonitor
)

class TestCompressedVector(unittest.TestCase):
    """Tests for the CompressedVector class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.compressor = CompressedVector(original_dim=10, compressed_dim=5)
    
    def test_compress_decompress(self):
        """Test compressing and decompressing vectors."""
        # Create a test vector
        original_vector = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        # Compress the vector
        compressed = self.compressor.compress(original_vector)
        
        # Verify the compressed vector has the right dimension
        self.assertEqual(len(compressed), 5)
        
        # Decompress the vector
        decompressed = self.compressor.decompress(compressed)
        
        # Verify the decompressed vector has the original dimension
        self.assertEqual(len(decompressed), 10)
        
        # Note: The decompressed vector won't be exactly the same as the original
        # but we can verify it's a reasonable approximation
        if isinstance(compressed[0], int):
            # If quantization was used, values will be very different
            # Just check dimensions
            pass
        else:
            # If no quantization, the values should be somewhat close
            # Calculate cosine similarity between original and decompressed
            original_norm = np.linalg.norm(original_vector)
            decompressed_norm = np.linalg.norm(decompressed)
            
            dot_product = sum(o * d for o, d in zip(original_vector, decompressed))
            similarity = dot_product / (original_norm * decompressed_norm) if original_norm * decompressed_norm > 0 else 0
            
            # Similarity should be above a certain threshold
            # This is a loose check since we're using a random projection
            self.assertGreaterEqual(abs(similarity), 0.1)
    
    def test_quantization(self):
        """Test vector quantization."""
        # Create a compressor with quantization
        compressor = CompressedVector(original_dim=10, compressed_dim=5, quantize=True)
        
        # Create a test vector
        original_vector = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        # Compress the vector with quantization
        compressed = compressor.compress(original_vector)
        
        # Verify the compressed vector contains integers
        self.assertTrue(all(isinstance(val, int) for val in compressed))
        
        # Verify values are in the expected range (-128 to 127)
        self.assertTrue(all(-128 <= val <= 127 for val in compressed))
        
        # Decompress the vector
        decompressed = compressor.decompress(compressed)
        
        # Verify the decompressed vector has the original dimension
        self.assertEqual(len(decompressed), 10)


class TestMemoryOptimizedCollection(unittest.TestCase):
    """Tests for the MemoryOptimizedCollection class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.collection = MemoryOptimizedCollection(
            max_memory_items=3,
            disk_cache_path=self.temp_dir
        )
    
    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_set_get(self):
        """Test setting and getting items."""
        self.collection["key1"] = "value1"
        self.assertEqual(self.collection["key1"], "value1")
        
        with self.assertRaises(KeyError):
            _ = self.collection["nonexistent_key"]
    
    def test_contains(self):
        """Test the contains operator."""
        self.collection["key1"] = "value1"
        self.assertTrue("key1" in self.collection)
        self.assertFalse("nonexistent_key" in self.collection)
    
    def test_length(self):
        """Test the length operator."""
        self.assertEqual(len(self.collection), 0)
        
        self.collection["key1"] = "value1"
        self.collection["key2"] = "value2"
        
        self.assertEqual(len(self.collection), 2)
    
    def test_delete(self):
        """Test deleting items."""
        self.collection["key1"] = "value1"
        del self.collection["key1"]
        
        self.assertFalse("key1" in self.collection)
        
        with self.assertRaises(KeyError):
            _ = self.collection["key1"]
    
    def test_items_keys_values(self):
        """Test items(), keys(), and values() methods."""
        self.collection["key1"] = "value1"
        self.collection["key2"] = "value2"
        
        # Test keys()
        keys = set(self.collection.keys())
        self.assertEqual(keys, {"key1", "key2"})
        
        # Test values()
        values = list(self.collection.values())
        self.assertEqual(sorted(values), ["value1", "value2"])
        
        # Test items()
        items = dict(self.collection.items())
        self.assertEqual(items, {"key1": "value1", "key2": "value2"})
    
    def test_memory_eviction(self):
        """Test that items are evicted from memory when max_memory_items is reached."""
        # Add items up to max_memory_items
        self.collection["key1"] = "value1"
        self.collection["key2"] = "value2"
        self.collection["key3"] = "value3"
        
        # Access key1 to update its access time
        _ = self.collection["key1"]
        
        # Add one more item to trigger eviction
        self.collection["key4"] = "value4"
        
        # key2 should be evicted from memory but still accessible
        self.assertEqual(self.collection["key2"], "value2")
        
        # But it should have been loaded from disk
        # This is hard to test directly, so we just verify all items are still accessible
        self.assertEqual(len(self.collection), 4)
        for key in ["key1", "key2", "key3", "key4"]:
            self.assertTrue(key in self.collection)
            self.assertEqual(self.collection[key], f"value{key[-1]}")
    
    def test_clear(self):
        """Test clearing the collection."""
        self.collection["key1"] = "value1"
        self.collection["key2"] = "value2"
        
        self.collection.clear()
        
        self.assertEqual(len(self.collection), 0)
        self.assertFalse("key1" in self.collection)
        self.assertFalse("key2" in self.collection)
    
    def test_optimize_memory(self):
        """Test optimize_memory method."""
        self.collection["key1"] = "value1"
        self.collection["key2"] = "value2"
        
        # Before optimization, items should be in memory
        self.assertTrue("key1" in self.collection.memory_items)
        self.assertTrue("key2" in self.collection.memory_items)
        
        # Optimize memory
        self.collection.optimize_memory()
        
        # After optimization, items should be moved to disk and memory cleared
        self.assertEqual(len(self.collection.memory_items), 0)
        
        # But items should still be accessible
        self.assertEqual(self.collection["key1"], "value1")
        self.assertEqual(self.collection["key2"], "value2")


class TestMemoryMonitor(unittest.TestCase):
    """Tests for the MemoryMonitor class."""
    
    def test_get_memory_usage(self):
        """Test get_memory_usage method."""
        memory_usage = MemoryMonitor.get_memory_usage()
        
        # Check that the result has the expected structure
        self.assertIn("total_objects", memory_usage)
        self.assertIn("total_size_mb", memory_usage)
        
        # Check that the values are reasonable
        self.assertGreater(memory_usage["total_objects"], 0)
        self.assertGreater(memory_usage["total_size_mb"], 0)
    
    def test_optimize_memory(self):
        """Test optimize_memory method."""
        # Create some objects to potentially be cleaned up
        objects = [list(range(1000)) for _ in range(100)]
        
        # Get the result of optimization
        result = MemoryMonitor.optimize_memory()
        
        # Check that the result has the expected structure
        self.assertIn("objects_before", result)
        self.assertIn("objects_after", result)
        self.assertIn("objects_cleaned", result)
        
        # Verify that objects_cleaned is non-negative
        self.assertGreaterEqual(result["objects_cleaned"], 0)
        
        # Clean up the test objects
        del objects
        gc.collect()


if __name__ == "__main__":
    unittest.main()
