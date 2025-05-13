"""
Vector-based knowledge store for the Smart Steps AI module.

This module implements a vector-based knowledge storage and retrieval system
for persona documents and knowledge sources with performance optimizations.
"""

import os
import json
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
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

class EmbeddingManager:
    """
    Manages text embeddings for semantic search.
    
    This class provides functionality to generate and store embeddings
    for text documents, chunks, and queries.
    """
    
    def __init__(self, model_name: str = "default"):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        # In a production environment, we would load actual embedding models here
        # For now, we'll simulate embeddings with random vectors to demonstrate the architecture
        self.vector_dimension = 384  # Typical dimension for sentence embeddings
    
    @performance_monitor.timed("embed_text")
    def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for a text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Vector embedding as a list of floats
        """
        # In production, this would call a proper embedding model
        # For now, simulate an embedding with a random vector
        # This method is wrapped with our vector cache optimizer
        
        # Create a deterministic but random-looking embedding based on the text hash
        text_hash = hash(text) % 10000
        np.random.seed(text_hash)
        embedding = np.random.normal(0, 1, self.vector_dimension).tolist()
        
        return embedding
    
    # Create cached version of the embed_text method
    embed_text = vector_cache_optimizer.cached_embed_text(embed_text)
    
    @performance_monitor.timed("embed_document")
    def embed_document(self, document: str, chunk_size: int = 512, overlap: int = 100) -> List[Dict]:
        """
        Split a document into chunks and embed each chunk.
        
        Args:
            document: Text document to embed
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of chunk dictionaries with text, embedding, and metadata
        """
        # Split document into chunks
        chunks = self._split_into_chunks(document, chunk_size, overlap)
        
        # Create a function to process each chunk
        def process_chunk(chunk_data):
            i, chunk_text = chunk_data
            embedding = self.embed_text(chunk_text)
            return {
                "id": str(uuid.uuid4()),
                "text": chunk_text,
                "embedding": embedding,
                "position": i,
                "created_at": datetime.now().isoformat()
            }
        
        # Process chunks in batches for better performance
        chunk_data = list(enumerate(chunks))
        embedded_chunks = batch_processor.process_batch(chunk_data, process_chunk)
        
        return embedded_chunks
    
    def _split_into_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        # Simple chunking by characters
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + chunk_size, len(text))
            
            # Find a good breaking point (sentence or paragraph)
            if end < len(text):
                # Try to break at paragraph
                paragraph_break = text.rfind('\n\n', start, end)
                if paragraph_break != -1 and paragraph_break > start + (chunk_size // 2):
                    end = paragraph_break + 2
                else:
                    # Try to break at sentence
                    sentence_break = max(
                        text.rfind('. ', start, end),
                        text.rfind('? ', start, end),
                        text.rfind('! ', start, end)
                    )
                    if sentence_break != -1 and sentence_break > start + (chunk_size // 2):
                        end = sentence_break + 2
            
            # Add chunk
            chunks.append(text[start:end])
            
            # Move start position for next chunk
            start = end - overlap
        
        return chunks
    
    @performance_monitor.timed("calculate_similarity")
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity (between -1 and 1)
        """
        # Check if either embedding is compressed
        embedding1_compressed = isinstance(embedding1[0], int) if embedding1 else False
        embedding2_compressed = isinstance(embedding2[0], int) if embedding2 else False
        
        # Decompress if needed
        if embedding1_compressed:
            embedding1 = vector_compressor.decompress(embedding1)
        if embedding2_compressed:
            embedding2 = vector_compressor.decompress(embedding2)
        
        # Convert to numpy arrays for efficient computation
        v1 = np.array(embedding1)
        v2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    # Create cached version of the similarity method
    similarity = vector_cache_optimizer.cached_similarity(similarity)


class VectorStore:
    """
    Vector-based storage for document chunks and embeddings.
    
    This class provides functionality to store and retrieve document chunks
    based on semantic similarity with memory optimization.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the vector store.
        
        Args:
            data_dir: Directory to store vector data
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'vectors')
        self.embedding_manager = EmbeddingManager()
        
        # Use memory-optimized collection for collections
        cache_dir = os.path.join(self.data_dir, 'cache')
        self.collections = MemoryOptimizedCollection(
            max_memory_items=10,  # Keep only 10 collections in memory
            disk_cache_path=cache_dir
        )
        
        # Memory optimization settings
        self.use_compressed_vectors = True
        self.memory_check_counter = 0
        self.memory_check_frequency = 100  # Check memory after this many operations
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing collections
        self._load_collections()
    
    def _load_collections(self):
        """Load all collections from the data directory."""
        collection_files = os.path.join(self.data_dir, '*.json')
        for collection_file in Path(self.data_dir).glob('*.json'):
            try:
                collection_name = os.path.splitext(os.path.basename(collection_file))[0]
                with open(collection_file, 'r') as f:
                    collection_data = json.load(f)
                    
                self.collections[collection_name] = collection_data
            except Exception as e:
                print(f"Error loading collection from {collection_file}: {str(e)}")
    
    def create_collection(self, name: str, description: Optional[str] = None) -> bool:
        """
        Create a new collection for storing documents.
        
        Args:
            name: Name of the collection
            description: Description of the collection
            
        Returns:
            True if successful, False if collection already exists
        """
        if name in self.collections:
            return False
        
        # Create collection
        self.collections[name] = {
            "name": name,
            "description": description or "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "documents": [],
            "chunks": []
        }
        
        # Save collection
        self._save_collection(name)
        
        return True
    
    def add_document(self, 
                    collection_name: str, 
                    document_id: str,
                    content: str,
                    metadata: Optional[Dict] = None,
                    chunk_size: int = 512,
                    chunk_overlap: int = 100) -> List[str]:
        """
        Add a document to a collection and generate chunk embeddings.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document
            content: Text content of the document
            metadata: Document metadata
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            List of generated chunk IDs or empty list if collection not found
        """
        if collection_name not in self.collections:
            return []
        
        # Create document entry
        document = {
            "id": document_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "size": len(content)
        }
        
        # Check if document already exists
        for i, doc in enumerate(self.collections[collection_name]["documents"]):
            if doc["id"] == document_id:
                # Update existing document
                self.collections[collection_name]["documents"][i] = document
                
                # Remove existing chunks for this document
                self.collections[collection_name]["chunks"] = [
                    chunk for chunk in self.collections[collection_name]["chunks"]
                    if chunk.get("document_id") != document_id
                ]
                
                break
        else:
            # Add new document
            self.collections[collection_name]["documents"].append(document)
        
        # Create and embed chunks
        embedded_chunks = self.embedding_manager.embed_document(content, chunk_size, chunk_overlap)
        
        # Add document reference to chunks
        chunk_ids = []
        for chunk in embedded_chunks:
            chunk_id = chunk["id"]
            chunk["document_id"] = document_id
            chunk_ids.append(chunk_id)
            self.collections[collection_name]["chunks"].append(chunk)
        
        # Update collection metadata
        self.collections[collection_name]["updated_at"] = datetime.now().isoformat()
        
        # Save collection
        self._save_collection(collection_name)
        
        return chunk_ids
    
    @performance_monitor.timed("search")
    @cache_manager.cached(cache_type="memory", ttl=300, key_prefix="vector_search")
    def search(self, 
              collection_name: str, 
              query: str,
              limit: int = 5,
              threshold: float = 0.5,
              filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar chunks in a collection.
        
        Args:
            collection_name: Name of the collection
            query: Search query
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            filter_metadata: Filter results by metadata
            
        Returns:
            List of matching chunks with similarity scores
        """
        if collection_name not in self.collections:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_manager.embed_text(query)
        
        # Get all chunks from collection
        chunks = self.collections[collection_name]["chunks"]
        
        # Define processing function for each chunk
        def process_chunk(chunk):
            # Check if chunk has embedding
            if "embedding" not in chunk:
                return None
                
            # Apply metadata filter if provided
            if filter_metadata and not self._matches_filter(chunk, filter_metadata):
                return None
                
            # Calculate similarity
            similarity = self.embedding_manager.similarity(query_embedding, chunk["embedding"])
                
            # Return None if below threshold
            if similarity < threshold:
                return None
                
            # Get document metadata
            document_id = chunk.get("document_id")
            document_metadata = {}
            for doc in self.collections[collection_name]["documents"]:
                if doc["id"] == document_id:
                    document_metadata = doc.get("metadata", {})
                    break
                    
            # Return result
            return {
                "chunk_id": chunk["id"],
                "document_id": document_id,
                "text": chunk["text"],
                "similarity": similarity,
                "position": chunk.get("position"),
                "document_metadata": document_metadata
            }
        
        # Process chunks in batches
        raw_results = batch_processor.process_batch(chunks, process_chunk)
        
        # Filter out None results
        results = [r for r in raw_results if r is not None]
        
        # Sort results by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Limit results
        results = results[:limit]
        
        return results
    
    def _matches_filter(self, chunk: Dict, filter_metadata: Dict) -> bool:
        """Check if a chunk matches the metadata filter."""
        # Get document metadata
        document_id = chunk.get("document_id")
        if not document_id:
            return False
        
        document_metadata = {}
        for doc in self.collections[chunk.get("collection_name", "")]["documents"]:
            if doc["id"] == document_id:
                document_metadata = doc.get("metadata", {})
                break
        
        # Check if all filter conditions match
        for key, value in filter_metadata.items():
            if key not in document_metadata:
                return False
            
            if isinstance(value, list):
                # Check if document value is in the filter list
                if document_metadata[key] not in value:
                    return False
            else:
                # Direct comparison
                if document_metadata[key] != value:
                    return False
        
        return True
    
    def get_document_chunks(self, collection_name: str, document_id: str) -> List[Dict]:
        """
        Get all chunks for a document.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document
            
        Returns:
            List of chunks
        """
        if collection_name not in self.collections:
            return []
        
        return [
            chunk for chunk in self.collections[collection_name]["chunks"]
            if chunk.get("document_id") == document_id
        ]
    
    def delete_document(self, collection_name: str, document_id: str) -> bool:
        """
        Delete a document and its chunks from a collection.
        
        Args:
            collection_name: Name of the collection
            document_id: ID of the document
            
        Returns:
            True if successful, False if collection or document not found
        """
        if collection_name not in self.collections:
            return False
        
        # Find document
        for i, doc in enumerate(self.collections[collection_name]["documents"]):
            if doc["id"] == document_id:
                # Remove document
                del self.collections[collection_name]["documents"][i]
                
                # Remove chunks
                self.collections[collection_name]["chunks"] = [
                    chunk for chunk in self.collections[collection_name]["chunks"]
                    if chunk.get("document_id") != document_id
                ]
                
                # Update collection metadata
                self.collections[collection_name]["updated_at"] = datetime.now().isoformat()
                
                # Save collection
                self._save_collection(collection_name)
                
                return True
        
        return False
    
    def _save_collection(self, collection_name: str):
        """Save collection to disk."""
        if collection_name not in self.collections:
            return
        
        collection_file = os.path.join(self.data_dir, f"{collection_name}.json")
        with open(collection_file, 'w') as f:
            json.dump(self.collections[collection_name], f, indent=2)
        
        # Increment memory check counter
        self.memory_check_counter += 1
        
        # Check if memory optimization is needed
        if self.memory_check_counter >= self.memory_check_frequency:
            self.optimize_memory()
            self.memory_check_counter = 0
    
    def optimize_memory(self):
        """
        Optimize memory usage.
        
        This method optimizes memory usage by compressing vectors,
        moving collections to disk, and forcing garbage collection.
        """
        # Compress vectors if enabled
        if self.use_compressed_vectors:
            compressed_count = 0
            # Iterate through collections and compress vectors
            for collection_name in self.collections.keys():
                collection = self.collections[collection_name]
                if "chunks" in collection:
                    for chunk in collection["chunks"]:
                        # Check if embedding exists and is not already compressed
                        if "embedding" in chunk and "compressed" not in chunk:
                            # Compress embedding
                            original_embedding = chunk["embedding"]
                            compressed_embedding = vector_compressor.compress(original_embedding)
                            
                            # Store compressed embedding
                            chunk["embedding"] = compressed_embedding
                            chunk["compressed"] = True
                            
                            compressed_count += 1
            
            print(f"Compressed {compressed_count} vectors")
        
        # Optimize collection storage
        self.collections.optimize_memory()
        
        # Force garbage collection
        memory_stats = memory_monitor.optimize_memory()
        
        print(f"Memory optimization completed: {memory_stats['objects_cleaned']} objects cleaned")
        return {
            "compressed_vectors": self.use_compressed_vectors,
            "memory_stats": memory_stats
        }


class KnowledgeStore:
    """
    Knowledge store for persona documents and information.
    
    This class provides a high-level interface for managing persona knowledge
    using the vector store for efficient retrieval.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the knowledge store.
        
        Args:
            data_dir: Directory to store knowledge data
        """
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'knowledge')
        self.vector_store = VectorStore(os.path.join(self.data_dir, 'vectors'))
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def initialize_persona_knowledge(self, persona_id: str, description: Optional[str] = None) -> bool:
        """
        Initialize knowledge collection for a persona.
        
        Args:
            persona_id: ID of the persona
            description: Description of the persona knowledge
            
        Returns:
            True if successful, False if collection already exists
        """
        return self.vector_store.create_collection(
            name=f"persona_{persona_id}",
            description=description or f"Knowledge collection for persona {persona_id}"
        )
    
    def add_document(self, 
                   persona_id: str, 
                   document_id: str,
                   content: str,
                   metadata: Optional[Dict] = None) -> List[str]:
        """
        Add a document to a persona's knowledge.
        
        Args:
            persona_id: ID of the persona
            document_id: ID of the document
            content: Text content of the document
            metadata: Document metadata
            
        Returns:
            List of generated chunk IDs
        """
        collection_name = f"persona_{persona_id}"
        
        # Ensure collection exists
        if collection_name not in self.vector_store.collections:
            self.initialize_persona_knowledge(persona_id)
        
        return self.vector_store.add_document(
            collection_name=collection_name,
            document_id=document_id,
            content=content,
            metadata=metadata
        )
    
    def import_document_from_file(self, 
                                persona_id: str, 
                                document_id: str,
                                file_path: str,
                                metadata: Optional[Dict] = None) -> List[str]:
        """
        Import a document from a file to a persona's knowledge.
        
        Args:
            persona_id: ID of the persona
            document_id: ID of the document
            file_path: Path to the document file
            metadata: Document metadata
            
        Returns:
            List of generated chunk IDs
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add document
            return self.add_document(
                persona_id=persona_id,
                document_id=document_id,
                content=content,
                metadata=metadata or {
                    "source_file": os.path.basename(file_path),
                    "imported_at": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            print(f"Error importing document: {str(e)}")
            return []
    
    def search(self, 
              persona_id: str, 
              query: str,
              limit: int = 5,
              filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Search a persona's knowledge for relevant information.
        
        Args:
            persona_id: ID of the persona
            query: Search query
            limit: Maximum number of results
            filter_metadata: Filter results by metadata
            
        Returns:
            List of matching chunks with similarity scores
        """
        collection_name = f"persona_{persona_id}"
        
        return self.vector_store.search(
            collection_name=collection_name,
            query=query,
            limit=limit,
            filter_metadata=filter_metadata
        )
    
    def get_knowledge_context(self, 
                            persona_id: str, 
                            query: str,
                            max_tokens: int = 2000) -> str:
        """
        Get relevant knowledge context for a query.
        
        Args:
            persona_id: ID of the persona
            query: Context query
            max_tokens: Maximum number of tokens in the context
            
        Returns:
            Formatted context string
        """
        # Search for relevant chunks
        results = self.search(
            persona_id=persona_id,
            query=query,
            limit=10
        )
        
        if not results:
            return ""
        
        # Prepare context
        context_parts = []
        total_length = 0
        
        for result in results:
            # Extract document information
            doc_id = result.get("document_id", "unknown")
            text = result.get("text", "")
            
            # Estimate token count (rough approximation: 4 chars = 1 token)
            text_tokens = len(text) // 4
            
            # Check if adding this chunk would exceed the limit
            if total_length + text_tokens > max_tokens and context_parts:
                # We already have some context and adding more would exceed limit
                break
            
            # Add chunk to context
            context_parts.append(f"[Document: {doc_id}]\n{text}\n")
            total_length += text_tokens
        
        # Join context parts
        return "\n".join(context_parts)


# Example usage
if __name__ == "__main__":
    # Create knowledge store
    store = KnowledgeStore()
    
    # Initialize persona knowledge
    store.initialize_persona_knowledge("jane_stevens")
    
    # Add a document
    store.add_document(
        persona_id="jane_stevens",
        document_id="early-trauma",
        content="Early Trauma and Giftedness in Context\nJane's early years (ages 0–6) can plausibly include both exposure to family conflict and emerging giftedness...",
        metadata={
            "type": "biography",
            "period": "early-childhood",
            "topics": ["trauma", "giftedness", "development"]
        }
    )
    
    # Search for relevant information
    results = store.search(
        persona_id="jane_stevens",
        query="How did childhood trauma affect development?",
        limit=3
    )
    
    # Print results
    for i, result in enumerate(results):
        print(f"Result {i+1} (similarity: {result['similarity']:.4f}):")
        print(f"Document: {result['document_id']}")
        print(f"Text: {result['text'][:100]}...")
        print()
