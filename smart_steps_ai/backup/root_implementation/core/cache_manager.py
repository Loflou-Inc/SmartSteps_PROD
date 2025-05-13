"""
Cache management system for the Smart Steps AI module.

This module provides caching mechanisms to improve performance
for frequently accessed data and operations.
"""

import os
import json
import time
import hashlib
import pickle
from typing import Dict, Any, Optional, Callable, TypeVar, List, Union
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
import threading
import numpy as np

# Type variable for generic function
T = TypeVar('T')
R = TypeVar('R')

class Cache:
    """Base cache interface."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get an item from the cache."""
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set an item in the cache with optional TTL in seconds."""
        raise NotImplementedError
    
    def delete(self, key: str) -> bool:
        """Delete an item from the cache."""
        raise NotImplementedError
    
    def clear(self) -> bool:
        """Clear all cache entries."""
        raise NotImplementedError


class MemoryCache(Cache):
    """In-memory cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the memory cache.
        
        Args:
            max_size: Maximum number of items in the cache
        """
        self.max_size = max_size
        self.cache = {}  # key -> (value, expiry)
        self.access_times = {}  # key -> last access time
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            value, expiry = self.cache[key]
            
            # Check if expired
            if expiry is not None and time.time() > expiry:
                self.delete(key)
                return None
            
            # Update access time
            self.access_times[key] = time.time()
            
            return value
    
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
        with self.lock:
            # Calculate expiry time
            expiry = None
            if ttl is not None:
                expiry = time.time() + ttl
            
            # Check if cache is full
            if len(self.cache) >= self.max_size and key not in self.cache:
                # Evict least recently used item
                self._evict_lru()
            
            # Set cache entry
            self.cache[key] = (value, expiry)
            self.access_times[key] = time.time()
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                return True
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful
        """
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            return True
    
    def _evict_lru(self):
        """Evict the least recently used cache entry."""
        if not self.access_times:
            return
        
        # Find oldest entry
        oldest_key = min(self.access_times, key=self.access_times.get)
        
        # Delete it
        self.delete(oldest_key)


class DiskCache(Cache):
    """Disk-based cache implementation."""
    
    def __init__(self, cache_dir: Optional[str] = None, max_size_mb: int = 500):
        """
        Initialize the disk cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache')
        self.max_size_mb = max_size_mb
        self.metadata_file = os.path.join(self.cache_dir, 'metadata.json')
        self.metadata = self._load_metadata()
        self.lock = threading.RLock()
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata from file."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache metadata: {str(e)}")
        
        # Return default structure
        return {
            "entries": {},
            "size_bytes": 0,
            "last_cleanup": time.time()
        }
    
    def _save_metadata(self):
        """Save cache metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f)
    
    def _get_cache_path(self, key: str) -> str:
        """Get file path for a cache key."""
        # Use hash for filename to avoid invalid characters
        filename = hashlib.md5(key.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, filename)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        with self.lock:
            # Check if key exists in metadata
            if key not in self.metadata["entries"]:
                return None
            
            entry = self.metadata["entries"][key]
            cache_path = self._get_cache_path(key)
            
            # Check if file exists
            if not os.path.exists(cache_path):
                # File missing, remove from metadata
                self.delete(key)
                return None
            
            # Check if expired
            if entry.get("expiry") is not None and time.time() > entry["expiry"]:
                self.delete(key)
                return None
            
            # Load value from file
            try:
                with open(cache_path, 'rb') as f:
                    value = pickle.load(f)
                
                # Update access time
                self.metadata["entries"][key]["last_access"] = time.time()
                self._save_metadata()
                
                return value
            
            except Exception as e:
                print(f"Error loading cache entry {key}: {str(e)}")
                self.delete(key)
                return None
    
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
        with self.lock:
            # Calculate expiry time
            expiry = None
            if ttl is not None:
                expiry = time.time() + ttl
            
            # Get cache path
            cache_path = self._get_cache_path(key)
            
            # Save value to file
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(value, f)
                
                # Get file size
                file_size = os.path.getsize(cache_path)
                
                # Update metadata
                is_update = key in self.metadata["entries"]
                old_size = self.metadata["entries"].get(key, {}).get("size", 0) if is_update else 0
                
                self.metadata["entries"][key] = {
                    "size": file_size,
                    "created": time.time(),
                    "last_access": time.time(),
                    "expiry": expiry
                }
                
                # Update total size
                self.metadata["size_bytes"] = self.metadata["size_bytes"] - old_size + file_size
                
                # Save metadata
                self._save_metadata()
                
                # Check if cache is too large
                max_bytes = self.max_size_mb * 1024 * 1024
                if self.metadata["size_bytes"] > max_bytes:
                    self._cleanup(max_bytes * 0.8)  # Clean up to 80% of max size
                
                return True
            
            except Exception as e:
                print(f"Error saving cache entry {key}: {str(e)}")
                return False
    
    def delete(self, key: str) -> bool:
        """
        Delete an item from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            if key not in self.metadata["entries"]:
                return False
            
            # Get file path
            cache_path = self._get_cache_path(key)
            
            # Delete file if exists
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except Exception as e:
                    print(f"Error deleting cache file for {key}: {str(e)}")
            
            # Update metadata
            old_size = self.metadata["entries"][key].get("size", 0)
            self.metadata["size_bytes"] = max(0, self.metadata["size_bytes"] - old_size)
            del self.metadata["entries"][key]
            
            # Save metadata
            self._save_metadata()
            
            return True
    
    def clear(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if successful
        """
        with self.lock:
            try:
                # Delete all cache files
                for entry_key in list(self.metadata["entries"].keys()):
                    self.delete(entry_key)
                
                # Reset metadata
                self.metadata = {
                    "entries": {},
                    "size_bytes": 0,
                    "last_cleanup": time.time()
                }
                
                # Save metadata
                self._save_metadata()
                
                return True
            
            except Exception as e:
                print(f"Error clearing cache: {str(e)}")
                return False
    
    def _cleanup(self, target_size: float):
        """
        Clean up cache to target size.
        
        Args:
            target_size: Target size in bytes
        """
        # Check if cleanup needed
        if self.metadata["size_bytes"] <= target_size:
            return
        
        # Get entries sorted by last access time
        entries = list(self.metadata["entries"].items())
        entries.sort(key=lambda x: x[1].get("last_access", 0))
        
        # Delete oldest entries until target size is reached
        for key, entry in entries:
            self.delete(key)
            
            if self.metadata["size_bytes"] <= target_size:
                break
        
        # Update last cleanup time
        self.metadata["last_cleanup"] = time.time()
        self._save_metadata()


class CacheManager:
    """
    Manager for different cache implementations.
    
    This class provides a unified interface for managing different
    cache backends (memory, disk, etc.).
    """
    
    def __init__(self):
        """Initialize the cache manager."""
        self.caches = {
            "memory": MemoryCache(),
            "disk": DiskCache()
        }
    
    def get_cache(self, cache_type: str) -> Cache:
        """
        Get a cache instance by type.
        
        Args:
            cache_type: Type of cache ('memory' or 'disk')
            
        Returns:
            Cache instance
        """
        return self.caches.get(cache_type, self.caches["memory"])
    
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
        cache = self.get_cache(cache_type)
        
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> R:
                # Generate cache key
                if hash_args:
                    key_args = pickle.dumps((args, kwargs))
                    key_hash = hashlib.md5(key_args).hexdigest()
                    key = f"{key_prefix}:{func.__name__}:{key_hash}"
                else:
                    # Use args directly in key
                    key_parts = [str(arg) for arg in args]
                    key_parts.extend(f"{k}={v}" for k, v in kwargs.items())
                    key = f"{key_prefix}:{func.__name__}:{','.join(key_parts)}"
                
                # Try to get from cache
                result = cache.get(key)
                if result is not None:
                    return result
                
                # Call function
                result = func(*args, **kwargs)
                
                # Store in cache
                cache.set(key, result, ttl)
                
                return result
            
            return wrapper
        
        return decorator


class VectorCacheOptimizer:
    """
    Optimizes vector operations using caching.
    
    This class provides specialized caching for vector operations
    like embeddings and similarity calculations.
    """
    
    def __init__(self, cache_manager: CacheManager):
        """
        Initialize the vector cache optimizer.
        
        Args:
            cache_manager: Cache manager instance
        """
        self.cache_manager = cache_manager
        self.embedding_cache = cache_manager.get_cache("memory")
        self.similarity_cache = cache_manager.get_cache("memory")
    
    def cached_embed_text(self, embed_func: Callable[[str], List[float]]) -> Callable[[str], List[float]]:
        """
        Create a cached version of an embedding function.
        
        Args:
            embed_func: Function that generates embeddings
            
        Returns:
            Cached embedding function
        """
        @wraps(embed_func)
        def cached_func(text: str) -> List[float]:
            # Generate cache key
            key = f"embedding:{hashlib.md5(text.encode('utf-8')).hexdigest()}"
            
            # Try to get from cache
            embedding = self.embedding_cache.get(key)
            if embedding is not None:
                return embedding
            
            # Generate embedding
            embedding = embed_func(text)
            
            # Store in cache (1 day TTL)
            self.embedding_cache.set(key, embedding, ttl=86400)
            
            return embedding
        
        return cached_func
    
    def cached_similarity(self, similarity_func: Callable[[List[float], List[float]], float]) -> Callable[[List[float], List[float]], float]:
        """
        Create a cached version of a similarity function.
        
        Args:
            similarity_func: Function that calculates similarity
            
        Returns:
            Cached similarity function
        """
        @wraps(similarity_func)
        def cached_func(embedding1: List[float], embedding2: List[float]) -> float:
            # Generate cache key (use vectors as keys, hashed for efficiency)
            key1 = hashlib.md5(str(embedding1[:10]).encode('utf-8')).hexdigest()
            key2 = hashlib.md5(str(embedding2[:10]).encode('utf-8')).hexdigest()
            
            # Ensure consistent order for cache key
            if key1 > key2:
                key1, key2 = key2, key1
            
            cache_key = f"similarity:{key1}:{key2}"
            
            # Try to get from cache
            similarity = self.similarity_cache.get(cache_key)
            if similarity is not None:
                return similarity
            
            # Calculate similarity
            similarity = similarity_func(embedding1, embedding2)
            
            # Store in cache (1 day TTL)
            self.similarity_cache.set(cache_key, similarity, ttl=86400)
            
            return similarity
        
        return cached_func


class BatchProcessor:
    """
    Batch processor for optimizing operations on multiple items.
    
    This class provides functionality to process operations in batches,
    improving performance for CPU-bound tasks.
    """
    
    def __init__(self, batch_size: int = 10):
        """
        Initialize the batch processor.
        
        Args:
            batch_size: Size of processing batches
        """
        self.batch_size = batch_size
    
    def process_batch(self, items: List[T], operation: Callable[[T], R]) -> List[R]:
        """
        Process a list of items in batches.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            List of operation results
        """
        results = []
        
        # Process items in batches
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i+self.batch_size]
            batch_results = [operation(item) for item in batch]
            results.extend(batch_results)
        
        return results
    
    def map_async(self, items: List[T], operation: Callable[[T], R]) -> List[R]:
        """
        Process a list of items in parallel threads.
        
        Args:
            items: List of items to process
            operation: Function to apply to each item
            
        Returns:
            List of operation results
        """
        # For simplicity, we're using threading here
        # In production, you might want to use a more sophisticated approach
        # with a thread pool or multiprocessing
        
        results = [None] * len(items)
        threads = []
        
        def process_item(index, item):
            results[index] = operation(item)
        
        # Create threads
        for i, item in enumerate(items):
            thread = threading.Thread(target=process_item, args=(i, item))
            threads.append(thread)
            thread.start()
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()
        
        return results


class PerformanceMonitor:
    """
    Monitor and optimize performance of AI operations.
    
    This class provides functionality for tracking and improving
    performance of AI operations.
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.timings = {}
        self.execution_counts = {}
        self.lock = threading.RLock()
    
    def timed(self, name: str):
        """
        Decorator for timing function execution.
        
        Args:
            name: Name of the operation
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable[..., R]) -> Callable[..., R]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> R:
                start_time = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    execution_time = time.time() - start_time
                    
                    with self.lock:
                        # Update timings
                        if name not in self.timings:
                            self.timings[name] = []
                        
                        self.timings[name].append(execution_time)
                        
                        # Keep only the last 100 timings
                        if len(self.timings[name]) > 100:
                            self.timings[name] = self.timings[name][-100:]
                        
                        # Update execution count
                        self.execution_counts[name] = self.execution_counts.get(name, 0) + 1
            
            return wrapper
        
        return decorator
    
    def get_average_time(self, name: str) -> float:
        """
        Get average execution time for an operation.
        
        Args:
            name: Name of the operation
            
        Returns:
            Average execution time in seconds
        """
        with self.lock:
            timings = self.timings.get(name, [])
            if not timings:
                return 0.0
            
            return sum(timings) / len(timings)
    
    def get_execution_count(self, name: str) -> int:
        """
        Get execution count for an operation.
        
        Args:
            name: Name of the operation
            
        Returns:
            Number of executions
        """
        with self.lock:
            return self.execution_counts.get(name, 0)
    
    def get_performance_report(self) -> Dict[str, Dict[str, Union[float, int]]]:
        """
        Generate a performance report.
        
        Returns:
            Dictionary with performance metrics for each operation
        """
        with self.lock:
            report = {}
            
            for name in self.timings:
                timings = self.timings[name]
                count = self.execution_counts.get(name, 0)
                
                if not timings:
                    continue
                
                avg_time = sum(timings) / len(timings)
                min_time = min(timings)
                max_time = max(timings)
                
                report[name] = {
                    "average_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "execution_count": count
                }
            
            return report


# Create global instances
cache_manager = CacheManager()
vector_cache_optimizer = VectorCacheOptimizer(cache_manager)
batch_processor = BatchProcessor()
performance_monitor = PerformanceMonitor()
