# Memory Optimizer API Reference

The `memory_optimizer` module provides tools to optimize memory usage in the Smart Steps AI module, particularly for vector operations and large datasets.

## Overview

Memory optimization components include:

- Vector compression for reducing the memory footprint of embeddings
- Memory-optimized collections for efficient storage of large datasets
- Memory monitoring for tracking and optimizing memory usage

## Classes

### CompressedVector

Memory-efficient vector representation using dimensionality reduction.

```python
class CompressedVector:
    def __init__(self, original_dim: int = 384, compressed_dim: int = 128, quantize: bool = True):
        """
        Initialize the vector compressor.
        
        Args:
            original_dim: Original dimensionality of vectors
            compressed_dim: Compressed dimensionality
            quantize: Whether to quantize values for additional compression
        """
        
    def compress(self, vector: List[float]) -> Union[List[float], List[int]]:
        """
        Compress a vector to a lower-dimensional representation.
        
        Args:
            vector: Original vector
            
        Returns:
            Compressed representation
        """
        
    def decompress(self, compressed: Union[List[float], List[int]]) -> List[float]:
        """
        Decompress a vector back to its approximate original form.
        
        Args:
            compressed: Compressed vector
            
        Returns:
            Decompressed vector (approximate reconstruction)
        """
```

### MemoryOptimizedCollection

Memory-optimized collection for storing large datasets.

```python
class MemoryOptimizedCollection(Generic[T]):
    def __init__(self, max_memory_items: int = 1000, disk_cache_path: Optional[str] = None):
        """
        Initialize the memory-optimized collection.
        
        Args:
            max_memory_items: Maximum number of items to keep in memory
            disk_cache_path: Path to disk cache directory
        """
        
    def __len__(self) -> int:
        """Get the number of items in the collection."""
        
    def __contains__(self, key: str) -> bool:
        """Check if the collection contains an item."""
        
    def __getitem__(self, key: str) -> T:
        """Get an item from the collection."""
        
    def __setitem__(self, key: str, value: T):
        """Set an item in the collection."""
        
    def __delitem__(self, key: str):
        """Delete an item from the collection."""
        
    def items(self):
        """Get all items in the collection."""
        
    def keys(self):
        """Get all keys in the collection."""
        
    def values(self):
        """Get all values in the collection."""
        
    def clear(self):
        """Clear the collection."""
        
    def optimize_memory(self):
        """
        Optimize memory usage by moving items to disk.
        
        This method moves all items to disk and clears memory,
        forcing garbage collection to free up memory.
        """
```

### MemoryMonitor

Monitor and optimize memory usage.

```python
class MemoryMonitor:
    @staticmethod
    def get_memory_usage() -> Dict[str, Union[int, float]]:
        """
        Get current memory usage information.
        
        Returns:
            Dictionary with memory usage metrics
        """
        
    @staticmethod
    def optimize_memory():
        """
        Optimize memory usage by cleaning up and forcing garbage collection.
        
        Returns:
            Dictionary with optimization results
        """
```

## Global Instances

The module provides the following global instances:

```python
vector_compressor = CompressedVector()
memory_monitor = MemoryMonitor()
```

## Usage Examples

### Vector Compression

```python
from smart_steps_ai.core.memory_optimizer import vector_compressor

# Compress a vector
original_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
compressed_vector = vector_compressor.compress(original_vector)

# Decompress the vector
decompressed_vector = vector_compressor.decompress(compressed_vector)
```

### Memory-Optimized Collection

```python
from smart_steps_ai.core.memory_optimizer import MemoryOptimizedCollection

# Create a memory-optimized collection
collection = MemoryOptimizedCollection(
    max_memory_items=1000,
    disk_cache_path="path/to/cache"
)

# Use like a dictionary
collection["key"] = value
item = collection["key"]

# Check if key exists
if "key" in collection:
    # Do something

# Get the number of items
num_items = len(collection)

# Iterate over items
for key, value in collection.items():
    # Do something

# Optimize memory usage
collection.optimize_memory()
```

### Memory Monitoring

```python
from smart_steps_ai.core.memory_optimizer import memory_monitor

# Get memory usage
memory_usage = memory_monitor.get_memory_usage()
print(f"Total objects: {memory_usage['total_objects']}")
print(f"Total size (MB): {memory_usage['total_size_mb']:.2f}")

# Optimize memory
result = memory_monitor.optimize_memory()
print(f"Objects cleaned: {result['objects_cleaned']}")
```

## Integration with VectorStore

The `MemoryOptimizedCollection` is used in the `VectorStore` to efficiently manage collections:

```python
from smart_steps_ai.core.knowledge_store import VectorStore

# Create a vector store
vector_store = VectorStore()

# Collections are stored in a memory-optimized collection
collections = vector_store.collections

# Optimize memory usage
vector_store.optimize_memory()
```

## Best Practices

1. **Use Vector Compression**: Enable vector compression for large vector datasets.

```python
vector_compressor = CompressedVector(
    original_dim=384,  # Original dimension
    compressed_dim=128,  # Compressed dimension
    quantize=True  # Enable quantization
)
```

2. **Adjust Memory-Optimized Collection Parameters**: Based on available memory and dataset size.

```python
collection = MemoryOptimizedCollection(
    max_memory_items=5000,  # Keep more items in memory
    disk_cache_path="path/to/cache"  # Use disk cache
)
```

3. **Regularly Optimize Memory**: For long-running processes or large datasets.

```python
# Optimize after processing large batches
vector_store.optimize_memory()
memory_monitor.optimize_memory()
```

4. **Monitor Memory Usage**: To identify memory leaks or excessive usage.

```python
# Regularly check memory usage
memory_usage = memory_monitor.get_memory_usage()
if memory_usage["total_size_mb"] > threshold:
    # Take action
    memory_monitor.optimize_memory()
```
