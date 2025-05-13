# Cache Manager API Reference

The `cache_manager` module provides a comprehensive caching system for the Smart Steps AI module.

## Overview

The caching system includes:

- Memory-based caching for fast, in-memory storage
- Disk-based caching for persistent storage
- Decorator-based caching for easy integration
- Specialized vector caching for embedding operations

## Classes

### Cache

Abstract base class for cache implementations.

```python
class Cache:
    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache."""
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set an item in the cache with optional TTL in seconds."""
        
    def delete(self, key: str) -> bool:
        """Delete an item from the cache."""
        
    def clear(self) -> bool:
        """Clear all cache entries."""
```

### MemoryCache

In-memory cache implementation.

```python
class MemoryCache(Cache):
    def __init__(self, max_size: int = 1000):
        """
        Initialize the memory cache.
        
        Args:
            max_size: Maximum number of items in the cache
        """
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set an item in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiry)
            
        Returns:
            True if successful
        """
        
    def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful
        """
```

### DiskCache

Disk-based cache implementation.

```python
class DiskCache(Cache):
    def __init__(self, cache_dir: Optional[str] = None, max_size_mb: int = 500):
        """
        Initialize the disk cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in megabytes
        """
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set an item in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiry)
            
        Returns:
            True if successful
        """
        
    def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful
        """
        
    def _cleanup(self, target_size: float):
        """
        Clean up cache to target size.
        
        Args:
            target_size: Target size in bytes
        """
```

### CacheManager

Manager for different cache implementations.

```python
class CacheManager:
    def __init__(self):
        """Initialize the cache manager."""
        
    def get_cache(self, cache_type: str) -> Cache:
        """
        Get a cache instance by type.
        
        Args:
            cache_type: Type of cache ('memory' or 'disk')
            
        Returns:
            Cache instance
        """
        
    def cached(self, 
              cache_type: str = "memory", 
              ttl: Optional[int] = None,
              key_prefix: str = "",
              hash_args: bool = True):
        """
        Decorator for caching function results.
        
        Args:
            cache_type: Type of cache ('memory' or 'disk')
            ttl: Time to live in seconds (None for no expiry)
            key_prefix: Prefix for cache keys
            hash_args: Whether to hash function arguments
            
        Returns:
            Decorated function
        """
```

### VectorCacheOptimizer

Optimizes vector operations using caching.

```python
class VectorCacheOptimizer:
    def __init__(self, cache_manager: CacheManager):
        """
        Initialize the vector cache optimizer.
        
        Args:
            cache_manager: Cache manager instance
        """
        
    def cached_embed_text(self, embed_func: Callable[[str], List[float]]) -> Callable[[str], List[float]]:
        """
        Create a cached version of an embedding function.
        
        Args:
            embed_func: Function that generates embeddings
            
        Returns:
            Cached embedding function
        """
        
    def cached_similarity(self, similarity_func: Callable[[List[float], List[float]], float]) -> Callable[[List[float], List[float]], float]:
        """
        Create a cached version of a similarity function.
        
        Args:
            similarity_func: Function that calculates similarity
            
        Returns:
            Cached similarity function
        """
```

### BatchProcessor

Batch processor for optimizing operations on multiple items.

```python
class BatchProcessor:
    def __init__(self, batch_size: int = 10):
        """
        Initialize the batch processor.
        
        Args:
            batch_size: Size of processing batches
        """
        
    def process_batch(self, items: List[T], operation: Callable[[T], R]) -> List[R]:
        """
        Process a list of items in batches.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            List of operation results
        """
        
    def map_async(self, items: List[T], operation: Callable[[T], R]) -> List[R]:
        """
        Process a list of items in parallel threads.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            List of operation results
        """
```

### PerformanceMonitor

Monitor and optimize performance of AI operations.

```python
class PerformanceMonitor:
    def __init__(self):
        """Initialize the performance monitor."""
        
    def timed(self, name: str):
        """
        Decorator for timing function execution.
        
        Args:
            name: Name of the operation
            
        Returns:
            Decorated function
        """
        
    def get_average_time(self, name: str) -> float:
        """
        Get average execution time for an operation.
        
        Args:
            name: Name of the operation
            
        Returns:
            Average execution time in seconds
        """
        
    def get_execution_count(self, name: str) -> int:
        """
        Get execution count for an operation.
        
        Args:
            name: Name of the operation
            
        Returns:
            Number of executions
        """
        
    def get_performance_report(self) -> Dict[str, Dict[str, Union[float, int]]]:
        """
        Generate a performance report.
        
        Returns:
            Dictionary with performance metrics for each operation
        """
```

## Global Instances

The module provides the following global instances:

```python
cache_manager = CacheManager()
vector_cache_optimizer = VectorCacheOptimizer(cache_manager)
batch_processor = BatchProcessor()
performance_monitor = PerformanceMonitor()
```

## Usage Examples

### Basic Caching

```python
from smart_steps_ai.core.cache_manager import cache_manager

# Get a cache
memory_cache = cache_manager.get_cache("memory")

# Store a value
memory_cache.set("key", "value", ttl=300)  # 5 minutes TTL

# Retrieve a value
value = memory_cache.get("key")

# Delete a value
memory_cache.delete("key")

# Clear the cache
memory_cache.clear()
```

### Decorator-based Caching

```python
from smart_steps_ai.core.cache_manager import cache_manager

@cache_manager.cached(cache_type="memory", ttl=300)
def expensive_operation(arg):
    # Perform expensive computation
    return result
```

### Vector Caching

```python
from smart_steps_ai.core.cache_manager import vector_cache_optimizer

# Define embedding function
def embed_text(text):
    # Generate embedding
    return embedding

# Create cached version
cached_embed = vector_cache_optimizer.cached_embed_text(embed_text)

# Use cached version
embedding = cached_embed("text")
```

### Batch Processing

```python
from smart_steps_ai.core.cache_manager import batch_processor

# Define operation
def process_item(item):
    # Process item
    return result

# Process items in batches
items = [item1, item2, item3, ...]
results = batch_processor.process_batch(items, process_item)
```

### Performance Monitoring

```python
from smart_steps_ai.core.cache_manager import performance_monitor

@performance_monitor.timed("operation_name")
def my_function():
    # Function code here

# Get performance report
report = performance_monitor.get_performance_report()
```
