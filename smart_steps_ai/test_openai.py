"""Test script for OpenAI API integration."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import provider components
from src.smart_steps_ai.provider import manager
from src.smart_steps_ai.provider.interface import ProviderConfig, MessageFormat
from src.smart_steps_ai.session.models import Message, MessageRole

def test_openai_provider():
    """Test OpenAI provider functionality."""
    print("\n===== Testing OpenAI Provider =====")
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    print(f"OpenAI API key available: {bool(api_key)}")
    
    if not api_key:
        print("ERROR: OpenAI API key not found in environment variables")
        print("Please set the OPENAI_API_KEY environment variable")
        return False
    
    # Create provider manager
    provider_manager = manager.ProviderManager()
    
    # Get the list of available providers
    providers = provider_manager.list_providers()
    print(f"Available providers: {providers}")
    
    # Check if OpenAI provider is registered
    if "openai" not in providers:
        print("ERROR: OpenAI provider not registered")
        return False
    
    # Get OpenAI provider
    openai_provider = provider_manager.get_provider("openai")
    
    if not openai_provider:
        print("ERROR: Failed to get OpenAI provider")
        return False
    
    print(f"Provider name: {openai_provider.name}")
    print(f"Available models: {openai_provider.available_models}")
    
    # Update provider config to use a valid model
    custom_config = ProviderConfig(
        model="gpt-3.5-turbo",  # Use a valid model
        max_tokens=500,
        temperature=0.7,
        message_format=MessageFormat.OPENAI,
        api_key=api_key
    )
    
    # Re-initialize with custom config
    openai_provider.initialize(custom_config)
    print(f"Using model: {custom_config.model}")
    
    # Create test messages
    messages = [
        Message(
            role=MessageRole.SYSTEM,
            content="You are a helpful, professional assistant for a mental health professional."
        ),
        Message(
            role=MessageRole.CLIENT,
            content="I've been feeling anxious lately. Can you help me understand what might be causing this?"
        )
    ]
    
    # Generate a response
    print("\nGenerating response...")
    start_time = time.time()
    response = openai_provider.generate_response(messages)
    elapsed_time = time.time() - start_time
    
    print(f"Response generated in {elapsed_time:.2f} seconds")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.usage.get('prompt_tokens', '?')} (prompt) + {response.usage.get('completion_tokens', '?')} (completion) = {response.usage.get('total_tokens', '?')} (total)")
    print(f"Finish reason: {response.finish_reason}")
    print(f"Response content: {response.content[:150]}...")
    
    # Test token counting
    sample_text = "This is a sample text to test token counting functionality."
    token_count = openai_provider.get_token_count(sample_text)
    print(f"\nToken count for sample text: {token_count}")
    
    print("\nOpenAI provider test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_openai_provider()
    sys.exit(0 if success else 1)
