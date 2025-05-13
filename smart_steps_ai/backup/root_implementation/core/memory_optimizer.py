"""
Memory usage optimization for the Smart Steps AI module.

This module provides tools to optimize memory usage in the Smart Steps AI module,
particularly for vector operations and large datasets.
"""

import os
import gc
import sys
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, TypeVar, Generic

# Type variable for generic types
T = TypeVar('T')

class CompressedVector:
    """
    Memory-efficient vector representation using dimensionality reduction.
    
    This class provides a compressed representation of high-dimensional vectors
    using techniques like quantization and dimensionality reduction.
    """
    
    def __init__(self, original_dim: int = 384, compressed_dim: int = 128, quantize: bool = True):
        """
        Initialize the vector compressor.
        
        Args:
            original_dim: Original dimensionality of vectors
            compressed_dim: Compressed dimensionality
            quantize: Whether to quantize values for additional compression
        """
        self.original_dim = original_dim
        self.compressed_dim = compressed_dim
        self.quantize = quantize
        
        # Create random projection matrix
        # In a production system, we would use a more sophisticated method like PCA
        np.random.seed(42)  # Fixed seed for reproducibility
        self.projection_matrix = np.random.normal(0, 1/np.sqrt(compressed_dim), (original_dim, compressed_dim))
    
    def compress(self, vector: List[float]) -> Union[List[float], List[int]]:
        """
        Compress a vector to a lower-dimensional representation.
        
        Args:
            vector: Original vector
            
        Returns:
            Compressed representation
        """
        # Convert to numpy array
        vec = np.array(vector)
        
        # Project to lower dimension
        projected = np.dot(vec, self.projection_matrix)
        
        if self.quantize:
            # Quantize to 8-bit integers (-128 to 127)
            min_val = projected.min()
            max_val = projected.max()
            scale = 255.0 / (max_val - min_val) if max_val > min_val else 1.0
            quantized = np.round((projected - min_val) * scale - 128).astype(np.int8)
            
            # Store metadata for decompression
            self.min_val = min_val
            self.max_val = max_val
            
            return quantized.tolist()
        else:
            return projected.tolist()
    
    def decompress(self, compressed: Union[List[float], List[int]]) -> List[float]:
        """
        Decompress a vector back to its approximate original form.
        
        Args:
            compressed: Compressed vector
            
        Returns:
            Decompressed vector (approximate reconstruction)
        """
        # Convert to numpy array
        comp = np.array(compressed)
        
        if self.quantize:
            # Dequantize
            scale = (self.max_val - self.min_val) / 255.0
            dequantized = (comp + 128) * scale + self.min_val
            
            # Project back to original space (approximate)
            # Note: This is not a perfect reconstruction, but works for similarity calculations
            return np.dot(dequantized, self.projection_matrix.T).tolist()
        else:
            # Project back to original space
            return np.dot(comp, self.projection_matrix.T).tolist()


class MemoryOptimizedCollection(Generic[T]):
    """
    Memory-optimized collection for storing large datasets.
    
    This class provides a memory-efficient way to store and access
    large collections of items, with automatic memory management.
    """
    
    def __init__(self, max_memory_items: int = 1000, disk_cache_path: Optional[str] = None):
        """
        Initialize the memory-optimized collection.
        
        Args:
            max_memory_items: Maximum number of items to keep in memory
            disk_cache_path: Path to disk cache directory
        """
        self.max_memory_items = max_memory_items
        self.disk_cache_path = disk_cache_path
        
        # If disk cache path is provided, ensure it exists
        if disk_cache_path:
            os.makedirs(disk_cache_path, exist_ok=True)
        
        # Initialize collections
        self.memory_items = {}  # Items currently in memory
        self.access_times = {}  # Last access time for each item
        self.disk_items = set()  # Items stored on disk
    
    def __len__(self) -> int:
        """Get the number of items in the collection."""
        return len(self.memory_items) + len(self.disk_items)
    
    def __contains__(self, key: str) -> bool:
        """Check if the collection contains an item."""
        return key in self.memory_items or key in self.disk_items
    
    def __getitem__(self, key: str) -> T:
        """Get an item from the collection."""
        # Check if item is in memory
        if key in self.memory_items:
            # Update access time
            self.access_times[key] = os.path.getmtime(__file__)
            return self.memory_items[key]
        
        # Check if item is on disk
        if key in self.disk_items and self.disk_cache_path:
            # Load from disk
            item_path = os.path.join(self.disk_cache_path, f"{key}.json")
            if os.path.exists(item_path):
                with open(item_path, 'r') as f:
                    item = json.load(f)
                
                # Store in memory
                self._add_to_memory(key, item)
                
                return item
        
        # Item not found
        raise KeyError(f"Item {key} not found in collection")
    
    def __setitem__(self, key: str, value: T):
        """Set an item in the collection."""
        # Add to memory
        self._add_to_memory(key, value)
        
        # Save to disk if disk cache is enabled
        if self.disk_cache_path:
            item_path = os.path.join(self.disk_cache_path, f"{key}.json")
            try:
                with open(item_path, 'w') as f:
                    json.dump(value, f)
                
                # Add to disk items set
                self.disk_items.add(key)
            except Exception as e:
                print(f"Error saving item {key} to disk: {str(e)}")
    
    def __delitem__(self, key: str):
        """Delete an item from the collection."""
        # Remove from memory if present
        if key in self.memory_items:
            del self.memory_items[key]
            if key in self.access_times:
                del self.access_times[key]
        
        # Remove from disk if present
        if key in self.disk_items and self.disk_cache_path:
            item_path = os.path.join(self.disk_cache_path, f"{key}.json")
            if os.path.exists(item_path):
                try:
                    os.remove(item_path)
                except Exception as e:
                    print(f"Error removing item {key} from disk: {str(e)}")
            
            # Remove from disk items set
            self.disk_items.remove(key)
    
    def _add_to_memory(self, key: str, value: T):
        """Add an item to memory, managing memory usage."""
        # Check if we need to evict items from memory
        if len(self.memory_items) >= self.max_memory_items and key not in self.memory_items:
            # Evict least recently used item
            self._evict_lru()
        
        # Add item to memory
        self.memory_items[key] = value
        self.access_times[key] = os.path.getmtime(__file__)
    
    def _evict_lru(self):
        """Evict the least recently used item from memory."""
        if not self.access_times:
            return
        
        # Find oldest item
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        
        # Remove from memory
        if oldest_key in self.memory_items:
            del self.memory_items[oldest_key]
        
        # Remove from access times
        if oldest_key in self.access_times:
            del self.access_times[oldest_key]
    
    def items(self):
        """Get all items in the collection."""
        # First yield memory items
        for key, value in self.memory_items.items():
            yield key, value
        
        # Then load and yield disk items not already in memory
        if self.disk_cache_path:
            for key in self.disk_items:
                if key not in self.memory_items:
                    try:
                        yield key, self[key]
                    except Exception as e:
                        print(f"Error loading disk item {key}: {str(e)}")
    
    def keys(self):
        """Get all keys in the collection."""
        # Combine memory and disk keys
        return set(self.memory_items.keys()).union(self.disk_items)
    
    def values(self):
        """Get all values in the collection."""
        # Use items() to yield values
        for _, value in self.items():
            yield value
    
    def clear(self):
        """Clear the collection."""
        # Clear memory items
        self.memory_items.clear()
        self.access_times.clear()
        
        # Clear disk items
        if self.disk_cache_path:
            for key in list(self.disk_items):
                item_path = os.path.join(self.disk_cache_path, f"{key}.json")
                if os.path.exists(item_path):
                    try:
                        os.remove(item_path)
                    except Exception as e:
                        print(f"Error removing item {key} from disk: {str(e)}")
            
            # Clear disk items set
            self.disk_items.clear()
    
    def optimize_memory(self):
        """
        Optimize memory usage by moving items to disk.
        
        This method moves all items to disk and clears memory,
        forcing garbage collection to free up memory.
        """
        if not self.disk_cache_path:
            return
        
        # Save all memory items to disk
        for key, value in list(self.memory_items.items()):
            item_path = os.path.join(self.disk_cache_path, f"{key}.json")
            try:
                with open(item_path, 'w') as f:
                    json.dump(value, f)
                
                # Add to disk items set
                self.disk_items.add(key)
            except Exception as e:
                print(f"Error saving item {key} to disk: {str(e)}")
        
        # Clear memory items
        self.memory_items.clear()
        self.access_times.clear()
        
        # Force garbage collection
        gc.collect()


class MemoryMonitor:
    """
    Monitor and optimize memory usage.
    
    This class provides functionality to monitor and manage memory usage
    in the system, preventing out-of-memory errors.
    """
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Union[int, float]]:
        """
        Get current memory usage information.
        
        Returns:
            Dictionary with memory usage metrics
        """
        if hasattr(sys, 'getsizeof'):
            # Get total objects size
            total_size = 0
            objects = gc.get_objects()
            for obj in objects:
                try:
                    if hasattr(obj, '__sizeof__'):
                        total_size += sys.getsizeof(obj)
                except (TypeError, OverflowError):
                    continue
            
            return {
                "total_objects": len(objects),
                "total_size_mb": total_size / (1024 * 1024)
            }
        else:
            return {
                "total_objects": 0,
                "total_size_mb": 0
            }
    
    @staticmethod
    def optimize_memory():
        """
        Optimize memory usage by cleaning up and forcing garbage collection.
        
        Returns:
            Dictionary with optimization results
        """
        # Record objects before cleanup
        objects_before = len(gc.get_objects())
        
        # Collect all generations
        gc.collect()
        
        # Record objects after cleanup
        objects_after = len(gc.get_objects())
        
        return {
            "objects_before": objects_before,
            "objects_after": objects_after,
            "objects_cleaned": objects_before - objects_after
        }


# Create global instances
vector_compressor = CompressedVector()
memory_monitor = MemoryMonitor()
