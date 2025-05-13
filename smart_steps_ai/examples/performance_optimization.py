#!/usr/bin/env python
"""
Performance Optimization Example

This script demonstrates how to optimize performance in the Smart Steps AI module
through caching, memory optimization, batch processing, and performance monitoring.
"""

import os
import time
import json
from pathlib import Path

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


def setup_example_environment():
    """Set up an example environment for the demonstration."""
    # Create temporary directories
    base_dir = Path("./example_data")
    base_dir.mkdir(exist_ok=True)
    
    config_dir = base_dir / "config"
    data_dir = base_dir / "data"
    personas_dir = base_dir / "personas"
    sessions_dir = base_dir / "sessions"
    
    config_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)
    personas_dir.mkdir(exist_ok=True)
    sessions_dir.mkdir(exist_ok=True)
    
    # Create example persona
    persona_dir = personas_dir / "example_therapist"
    persona_dir.mkdir(exist_ok=True)
    
    persona_data = {
        "id": "example_therapist",
        "name": "Dr. Example Therapist",
        "type": "therapist",
        "background": "An example therapist persona for performance testing.",
        "education": ["Example University"],
        "specialties": ["Cognitive Behavioral Therapy", "Performance Anxiety"],
        "approach": "Evidence-based therapy"
    }
    
    with open(persona_dir / "persona.json", "w") as f:
        json.dump(persona_data, f, indent=2)
    
    return {
        "base_dir": base_dir,
        "config_dir": config_dir,
        "data_dir": data_dir,
        "personas_dir": personas_dir,
        "sessions_dir": sessions_dir
    }


def example_1_basic_caching():
    """Demonstrate basic caching."""
    print("\n=== Example 1: Basic Caching ===\n")
    
    # Clear caches
    memory_cache = cache_manager.get_cache("memory")
    memory_cache.clear()
    
    disk_cache = cache_manager.get_cache("disk")
    disk_cache.clear()
    
    # Define a function that simulates an expensive operation
    def expensive_operation(key):
        print(f"Performing expensive operation for {key}...")
        time.sleep(1)  # Simulate expensive computation
        return f"Result for {key}"
    
    # Create a cached version
    @cache_manager.cached(cache_type="memory", ttl=60)
    def cached_operation(key):
        return expensive_operation(key)
    
    # First call: should execute the function
    print("First call:")
    result1 = cached_operation("test")
    print(f"Result: {result1}")
    
    # Second call: should use cached result
    print("\nSecond call (should use cache):")
    result2 = cached_operation("test")
    print(f"Result: {result2}")
    
    # Call with different parameter: should execute the function again
    print("\nCall with different parameter:")
    result3 = cached_operation("other")
    print(f"Result: {result3}")
    
    print("\nCache statistics:")
    print(f"Memory cache size: {len(memory_cache.cache)} items")


def example_2_vector_caching():
    """Demonstrate vector caching for embeddings."""
    print("\n=== Example 2: Vector Caching ===\n")
    
    # Create an embedding manager
    embedding_manager = EmbeddingManager()
    
    # Create a simple test function to monitor calls
    call_count = [0]
    original_embed_text = embedding_manager.embed_text
    
    def monitored_embed_text(text):
        call_count[0] += 1
        print(f"Generating embedding for: {text}")
        return original_embed_text(text)
    
    # Replace the embed_text method
    embedding_manager.embed_text = monitored_embed_text
    
    # Create a cached version
    cached_embed = vector_cache_optimizer.cached_embed_text(embedding_manager.embed_text)
    
    # Assign the cached version back
    embedding_manager.embed_text = cached_embed
    
    # First call: should execute the function
    print("First call:")
    embedding1 = embedding_manager.embed_text("This is a test document.")
    print(f"Generated embedding with {len(embedding1)} dimensions")
    
    # Second call: should use cached result
    print("\nSecond call (should use cache):")
    embedding2 = embedding_manager.embed_text("This is a test document.")
    print(f"Retrieved embedding with {len(embedding2)} dimensions")
    
    # Call with different text: should execute the function again
    print("\nCall with different text:")
    embedding3 = embedding_manager.embed_text("This is another document.")
    print(f"Generated embedding with {len(embedding3)} dimensions")
    
    print(f"\nTotal function calls: {call_count[0]}")


def example_3_batch_processing():
    """Demonstrate batch processing for multiple items."""
    print("\n=== Example 3: Batch Processing ===\n")
    
    # Configure batch processor
    batch_processor.batch_size = 3
    
    # Create example items
    items = [f"item_{i}" for i in range(10)]
    
    # Define a processing function
    def process_item(item):
        print(f"Processing {item}...")
        time.sleep(0.5)  # Simulate processing time
        return f"Processed {item}"
    
    # Process items in batches
    print("Processing items in batches:")
    start_time = time.time()
    results = batch_processor.process_batch(items, process_item)
    batch_time = time.time() - start_time
    
    print(f"\nProcessed {len(results)} items in {batch_time:.2f} seconds")
    
    # Process items one by one for comparison
    print("\nProcessing items one by one for comparison:")
    start_time = time.time()
    individual_results = [process_item(item) for item in items]
    individual_time = time.time() - start_time
    
    print(f"\nProcessed {len(individual_results)} items in {individual_time:.2f} seconds")
    
    # Compare times
    speedup = individual_time / batch_time if batch_time > 0 else 0
    print(f"\nBatch processing speedup: {speedup:.2f}x")


def example_4_performance_monitoring():
    """Demonstrate performance monitoring."""
    print("\n=== Example 4: Performance Monitoring ===\n")
    
    # Clear performance monitor data
    performance_monitor.timings.clear()
    performance_monitor.execution_counts.clear()
    
    # Create monitored functions
    @performance_monitor.timed("fast_operation")
    def fast_operation():
        time.sleep(0.01)  # 10ms
        return "Fast result"
    
    @performance_monitor.timed("medium_operation")
    def medium_operation():
        time.sleep(0.05)  # 50ms
        return "Medium result"
    
    @performance_monitor.timed("slow_operation")
    def slow_operation():
        time.sleep(0.1)  # 100ms
        return "Slow result"
    
    # Execute functions multiple times
    print("Executing functions...")
    for _ in range(5):
        fast_operation()
    
    for _ in range(3):
        medium_operation()
    
    for _ in range(2):
        slow_operation()
    
    # Get performance report
    report = performance_monitor.get_performance_report()
    
    print("\nPerformance Report:")
    print("------------------")
    for operation, metrics in report.items():
        print(f"Operation: {operation}")
        print(f"  Average time: {metrics['average_time'] * 1000:.2f} ms")
        print(f"  Min time: {metrics['min_time'] * 1000:.2f} ms")
        print(f"  Max time: {metrics['max_time'] * 1000:.2f} ms")
        print(f"  Execution count: {metrics['execution_count']}")
        print()


def example_5_memory_optimization():
    """Demonstrate memory optimization."""
    print("\n=== Example 5: Memory Optimization ===\n")
    
    # Get initial memory usage
    initial_usage = memory_monitor.get_memory_usage()
    print("Initial memory usage:")
    print(f"  Total objects: {initial_usage['total_objects']}")
    print(f"  Total size (MB): {initial_usage['total_size_mb']:.2f}")
    
    # Create some objects to increase memory usage
    print("\nCreating objects...")
    objects = []
    for i in range(1000):
        objects.append([i] * 1000)  # Each list is about 8KB
    
    # Get memory usage after object creation
    mid_usage = memory_monitor.get_memory_usage()
    print("Memory usage after object creation:")
    print(f"  Total objects: {mid_usage['total_objects']}")
    print(f"  Total size (MB): {mid_usage['total_size_mb']:.2f}")
    
    # Optimize memory
    print("\nOptimizing memory...")
    result = memory_monitor.optimize_memory()
    print(f"Objects cleaned: {result['objects_cleaned']}")
    
    # Delete objects to free memory
    print("\nDeleting objects...")
    del objects
    
    # Optimize memory again
    result = memory_monitor.optimize_memory()
    print(f"Objects cleaned: {result['objects_cleaned']}")
    
    # Get final memory usage
    final_usage = memory_monitor.get_memory_usage()
    print("\nFinal memory usage:")
    print(f"  Total objects: {final_usage['total_objects']}")
    print(f"  Total size (MB): {final_usage['total_size_mb']:.2f}")


def example_6_vector_compression():
    """Demonstrate vector compression."""
    print("\n=== Example 6: Vector Compression ===\n")
    
    # Create original vectors
    print("Creating vectors...")
    dimensions = 384
    num_vectors = 1000
    
    original_vectors = []
    for i in range(num_vectors):
        vector = [0.1] * dimensions  # Each vector is about 3KB
        original_vectors.append(vector)
    
    # Get memory usage before compression
    before_usage = memory_monitor.get_memory_usage()
    print("Memory usage before compression:")
    print(f"  Total objects: {before_usage['total_objects']}")
    print(f"  Total size (MB): {before_usage['total_size_mb']:.2f}")
    
    # Compress vectors
    print("\nCompressing vectors...")
    compressed_vectors = []
    for vector in original_vectors:
        compressed = vector_compressor.compress(vector)
        compressed_vectors.append(compressed)
    
    # Free original vectors
    del original_vectors
    memory_monitor.optimize_memory()
    
    # Get memory usage after compression
    after_usage = memory_monitor.get_memory_usage()
    print("Memory usage after compression:")
    print(f"  Total objects: {after_usage['total_objects']}")
    print(f"  Total size (MB): {after_usage['total_size_mb']:.2f}")
    
    # Test decompression and similarity
    print("\nTesting decompression and similarity...")
    decompressed = vector_compressor.decompress(compressed_vectors[0])
    
    # Convert to numpy arrays for cosine similarity
    import numpy as np
    v1 = np.array([0.1] * dimensions)  # Original vector
    v2 = np.array(decompressed)  # Decompressed vector
    
    # Calculate cosine similarity
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    similarity = dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
    
    print(f"Original dimensions: {dimensions}")
    print(f"Compressed dimensions: {len(compressed_vectors[0])}")
    print(f"Decompressed dimensions: {len(decompressed)}")
    print(f"Similarity between original and decompressed: {similarity:.4f}")
    
    # Free compressed vectors
    del compressed_vectors
    memory_monitor.optimize_memory()


def example_7_end_to_end_optimization(dirs):
    """Demonstrate an end-to-end optimization scenario."""
    print("\n=== Example 7: End-to-End Optimization ===\n")
    
    # Initialize components
    persona_manager = PersonaManager(personas_dir=dirs["personas_dir"])
    session_manager = SessionManager(
        sessions_dir=dirs["sessions_dir"],
        persona_manager=persona_manager
    )
    
    # Load persona
    print("Loading persona...")
    persona = persona_manager.load_persona("example_therapist")
    
    # Create session
    print("Creating session...")
    session = session_manager.create_session(
        persona_id="example_therapist",
        client_name="Example Client",
        session_type="performance_testing"
    )
    session_id = session["id"]
    
    # Create layered memory manager
    print("Creating layered memory manager...")
    memory_manager = LayeredMemoryManager(
        persona_id="example_therapist",
        data_dir=Path(dirs["data_dir"]) / "memory"
    )
    
    # Add a document to foundation layer
    print("Adding document to foundation layer...")
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
    
    # Record some interactions
    print("Recording interactions...")
    conversations = [
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
    
    for exchange in conversations:
        memory_manager.record_interaction(
            session_id=session_id,
            client_message=exchange["client"],
            persona_response=exchange["persona"]
        )
        
        session_manager.add_message(
            session_id=session_id,
            speaker="client",
            content=exchange["client"]
        )
        
        session_manager.add_message(
            session_id=session_id,
            speaker="persona",
            content=exchange["persona"]
        )
    
    # Generate an insight
    print("Generating insight...")
    memory_manager.generate_insight(
        content="Performance issues often manifest as scalability problems when user load increases.",
        domain="performance_optimization",
        sources={
            "foundation": ["performance_knowledge"],
            "experience": [session_id]
        },
        confidence=0.9
    )
    
    # Measure initial context retrieval time
    print("\nTesting context retrieval without optimization...")
    start_time = time.time()
    context = memory_manager.retrieve_context(
        query="How can I improve database performance?",
        session_id=session_id
    )
    initial_retrieval_time = time.time() - start_time
    print(f"Initial retrieval time: {initial_retrieval_time * 1000:.2f} ms")
    
    # Now let's apply optimizations
    print("\nApplying optimizations...")
    
    # 1. Enable vector compression
    vector_compressor.compressed_dim = 128
    vector_compressor.quantize = True
    
    # 2. Optimize memory usage
    memory_monitor.optimize_memory()
    
    # 3. Configure caching
    memory_cache = cache_manager.get_cache("memory")
    memory_cache.max_size = 2000
    
    disk_cache = cache_manager.get_cache("disk")
    disk_cache.max_size_mb = 500
    
    # 4. Configure batch processing
    batch_processor.batch_size = 20
    
    # Now measure optimized context retrieval time
    print("\nTesting context retrieval with optimization...")
    start_time = time.time()
    optimized_context = memory_manager.retrieve_context(
        query="How can I improve database performance?",
        session_id=session_id
    )
    optimized_retrieval_time = time.time() - start_time
    print(f"Optimized retrieval time: {optimized_retrieval_time * 1000:.2f} ms")
    
    # Compare performance
    improvement = (initial_retrieval_time - optimized_retrieval_time) / initial_retrieval_time * 100
    print(f"\nPerformance improvement: {improvement:.2f}%")
    
    # Get performance report
    report = performance_monitor.get_performance_report()
    
    print("\nPerformance Report:")
    print("------------------")
    for operation, metrics in report.items():
        if operation == "retrieve_context":
            print(f"Operation: {operation}")
            print(f"  Average time: {metrics['average_time'] * 1000:.2f} ms")
            print(f"  Min time: {metrics['min_time'] * 1000:.2f} ms")
            print(f"  Max time: {metrics['max_time'] * 1000:.2f} ms")
            print(f"  Execution count: {metrics['execution_count']}")
            print()
    
    print("Optimization completed successfully!")


def cleanup_example_environment(dirs):
    """Clean up the example environment."""
    import shutil
    
    print("\nCleaning up example environment...")
    
    try:
        shutil.rmtree(dirs["base_dir"])
        print("Cleanup completed successfully!")
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


def main():
    """Main function to run all examples."""
    print("=== Smart Steps AI Performance Optimization Examples ===\n")
    
    # Setup example environment
    dirs = setup_example_environment()
    
    try:
        # Run examples
        example_1_basic_caching()
        example_2_vector_caching()
        example_3_batch_processing()
        example_4_performance_monitoring()
        example_5_memory_optimization()
        example_6_vector_compression()
        example_7_end_to_end_optimization(dirs)
        
        print("\n=== All examples completed successfully! ===")
    
    finally:
        # Clean up
        cleanup_example_environment(dirs)


if __name__ == "__main__":
    main()
