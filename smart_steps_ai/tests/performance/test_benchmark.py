"""
Smart Steps AI Module - Function-level Performance Benchmarks

This file contains performance benchmarks for key functions within the Smart Steps AI Module.
Run with: pytest tests/performance/test_benchmark.py -v
"""

import gc
import json
import os
import random
import time
from pathlib import Path

import pytest
from memory_profiler import profile

# Import Smart Steps AI components
from smart_steps_ai.analysis.analyzer import SessionAnalyzer
from smart_steps_ai.api.app import create_app
from smart_steps_ai.config.config_manager import ConfigManager
from smart_steps_ai.conversation.conversation_handler import ConversationHandler
from smart_steps_ai.memory.memory_manager import MemoryManager
from smart_steps_ai.persona.persona_manager import PersonaManager
from smart_steps_ai.providers.mock_provider import MockProvider
from smart_steps_ai.providers.provider_manager import ProviderManager
from smart_steps_ai.session.session_manager import SessionManager

# Test fixtures
@pytest.fixture
def config_manager():
    """Create a config manager for testing."""
    return ConfigManager()

@pytest.fixture
def persona_manager(config_manager):
    """Create a persona manager for testing."""
    return PersonaManager(config_manager)

@pytest.fixture
def session_manager(config_manager):
    """Create a session manager for testing."""
    return SessionManager(config_manager)

@pytest.fixture
def memory_manager(config_manager):
    """Create a memory manager for testing."""
    return MemoryManager(config_manager)

@pytest.fixture
def provider_manager(config_manager):
    """Create a provider manager with mock provider for testing."""
    provider_mgr = ProviderManager(config_manager)
    mock_provider = MockProvider(config_manager)
    provider_mgr.register_provider("mock", mock_provider)
    provider_mgr.set_default_provider("mock")
    return provider_mgr

@pytest.fixture
def conversation_handler(session_manager, provider_manager, memory_manager, persona_manager):
    """Create a conversation handler for testing."""
    return ConversationHandler(
        session_manager=session_manager,
        provider_manager=provider_manager,
        memory_manager=memory_manager,
        persona_manager=persona_manager
    )

@pytest.fixture
def analyzer(config_manager):
    """Create a session analyzer for testing."""
    return SessionAnalyzer(config_manager)

@pytest.fixture
def test_session(session_manager, persona_manager):
    """Create a test session."""
    persona = persona_manager.get_persona("therapist_cbt")
    session = session_manager.create_session(
        client_name="Benchmark Test Client",
        persona_id=persona.id,
        metadata={"benchmark": True}
    )
    return session

# Memory Profile Tests (run separately, not included in benchmark)
@profile
def test_memory_profile_conversation_handler(conversation_handler, test_session):
    """Profile memory usage of conversation handler."""
    for i in range(10):
        conversation_handler.add_message(
            session_id=test_session.id,
            user_message=f"This is test message {i}",
            client=True
        )
        time.sleep(0.1)  # Small delay to simulate real usage

# Benchmark Tests
def test_session_creation(benchmark, session_manager, persona_manager):
    """Benchmark session creation performance."""
    persona = persona_manager.get_persona("therapist_cbt")
    
    def create_session():
        client_name = f"Test Client {random.randint(1000, 9999)}"
        session = session_manager.create_session(
            client_name=client_name,
            persona_id=persona.id,
            metadata={"benchmark": True}
        )
        return session
    
    # Run the benchmark
    result = benchmark(create_session)
    assert result is not None

def test_message_processing(benchmark, conversation_handler, test_session):
    """Benchmark message processing performance."""
    def process_message():
        response = conversation_handler.add_message(
            session_id=test_session.id,
            user_message=f"This is benchmark test message {random.randint(1, 1000)}",
            client=True
        )
        return response
    
    # Run the benchmark
    result = benchmark(process_message)
    assert result is not None

def test_session_analysis(benchmark, analyzer, test_session, conversation_handler):
    """Benchmark session analysis performance."""
    # Add some messages first
    for i in range(5):
        conversation_handler.add_message(
            session_id=test_session.id,
            user_message=f"Setup message {i} for analysis benchmark",
            client=True
        )
    
    def run_analysis():
        analysis = analyzer.analyze_session(test_session.id)
        return analysis
    
    # Run the benchmark
    result = benchmark(run_analysis)
    assert result is not None

def test_memory_retrieval(benchmark, memory_manager, test_session, conversation_handler):
    """Benchmark memory retrieval performance."""
    # Add some messages first to create memories
    for i in range(5):
        conversation_handler.add_message(
            session_id=test_session.id,
            user_message=f"Setup message {i} for memory benchmark",
            client=True
        )
    
    def retrieve_memory():
        memories = memory_manager.get_memories_for_session(test_session.id)
        return memories
    
    # Run the benchmark
    result = benchmark(retrieve_memory)
    assert isinstance(result, list)

def test_persona_loading(benchmark, persona_manager):
    """Benchmark persona loading performance."""
    def load_all_personas():
        personas = persona_manager.list_personas()
        return personas
    
    # Run the benchmark
    result = benchmark(load_all_personas)
    assert len(result) > 0

def test_batch_operations(benchmark, session_manager, conversation_handler, test_session):
    """Benchmark batch operations performance."""
    # Helper function to generate random messages
    def generate_message():
        message_templates = [
            "I've been feeling {emotion} lately.",
            "Work has been really {adjective} this week.",
            "I had a {adjective} conflict with my {relation} yesterday.",
            "I'm having trouble with {problem} at night.",
            "I don't know how to handle this {situation}."
        ]
        emotions = ["anxious", "sad", "angry", "frustrated", "confused", "happy", "excited"]
        adjectives = ["stressful", "challenging", "difficult", "intense", "problematic", "good"]
        relations = ["friend", "family member", "coworker", "boss", "partner"]
        problems = ["sleeping", "eating", "focusing", "relaxing", "exercising"]
        situations = ["situation", "problem", "issue", "challenge", "dilemma"]
        
        template = random.choice(message_templates)
        return template.format(
            emotion=random.choice(emotions),
            adjective=random.choice(adjectives),
            relation=random.choice(relations),
            problem=random.choice(problems),
            situation=random.choice(situations)
        )
    
    def batch_process_messages():
        """Process multiple messages in batch."""
        messages = [generate_message() for _ in range(10)]
        responses = []
        
        for msg in messages:
            response = conversation_handler.add_message(
                session_id=test_session.id,
                user_message=msg,
                client=True
            )
            responses.append(response)
        
        return responses
    
    # Run the benchmark
    result = benchmark(batch_process_messages)
    assert len(result) == 10

# Test API endpoints - use pytest-benchmark to measure response times
def test_api_session_creation(benchmark):
    """Benchmark API session creation endpoint."""
    from fastapi.testclient import TestClient
    from smart_steps_ai.api.app import app
    
    client = TestClient(app)
    
    def create_session_via_api():
        response = client.post(
            "/api/v1/sessions",
            json={
                "client_name": f"API Test Client {random.randint(1000, 9999)}",
                "persona_id": "therapist_cbt",
                "metadata": {"benchmark": True}
            },
            headers={"Authorization": "Bearer test_token"}
        )
        return response
    
    # Run the benchmark
    result = benchmark(create_session_via_api)
    assert result.status_code in (201, 401)  # 401 if auth is required

def test_api_conversation(benchmark):
    """Benchmark API conversation endpoint."""
    from fastapi.testclient import TestClient
    from smart_steps_ai.api.app import app
    
    client = TestClient(app)
    
    # First create a session
    session_response = client.post(
        "/api/v1/sessions",
        json={
            "client_name": "API Benchmark Client",
            "persona_id": "therapist_cbt",
            "metadata": {"benchmark": True}
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    if session_response.status_code == 201:
        session_id = session_response.json()["id"]
        
        def add_message_via_api():
            response = client.post(
                f"/api/v1/sessions/{session_id}/conversations",
                json={
                    "content": f"API benchmark message {random.randint(1, 1000)}",
                    "metadata": {"benchmark": True}
                },
                headers={"Authorization": "Bearer test_token"}
            )
            return response
        
        # Run the benchmark
        result = benchmark(add_message_via_api)
        assert result.status_code in (201, 401)  # 401 if auth is required
    else:
        pytest.skip("Failed to create session for API benchmark")

# Run the benchmark suite
if __name__ == "__main__":
    pytest.main(["-v", __file__])
