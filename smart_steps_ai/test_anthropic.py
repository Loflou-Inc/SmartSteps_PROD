"""Test script for Anthropic API integration."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.smart_steps_ai.session import ConversationHandler
from src.smart_steps_ai.provider import ProviderManager

# Print environment info
print("Testing Anthropic API integration...")
print(f"API key available: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")

# Create the provider manager
provider_manager = ProviderManager()
available_providers = provider_manager.list_providers()
print(f"Available providers: {available_providers}")

# Get the Anthropic provider
anthropic_provider = provider_manager.get_provider("anthropic")
print(f"Anthropic provider initialized: {anthropic_provider is not None}")
if anthropic_provider:
    print(f"Using model: {anthropic_provider.config.model}")
    print(f"Temperature: {anthropic_provider.config.temperature}")
    print(f"Max tokens: {anthropic_provider.config.max_tokens}")

# Create a conversation handler
conversation_handler = ConversationHandler(provider_manager=provider_manager)

# Create a new session
client_name = "API Test Client"
session_info = conversation_handler.create_new_session(
    client_name=client_name,
    persona_name="professional_therapist",
    session_type="initial",
    initial_message="Hello, I'm here for my first therapy session. I've been feeling anxious lately and wanted to talk to someone about it.",
)

print("\nCreated test session:")
print(f"Session ID: {session_info['id']}")
print(f"Client: {session_info['client_name']}")
print(f"Persona: {session_info['persona_name']}")
print(f"Session type: {session_info['session_type']}")
print(f"State: {session_info['state']}")

# Get the conversation history
history = conversation_handler.get_conversation_history(session_info["id"])
print("\nInitial conversation:")
for message in history:
    print(f"{message['role'].upper()}: {message['content']}")
    if 'metadata' in message and message['role'] == 'assistant':
        print(f"  Provider: {message['metadata'].get('provider')}")
        print(f"  Model: {message['metadata'].get('model')}")
        print(f"  Tokens: {message['metadata'].get('tokens_input', '?')} in, {message['metadata'].get('tokens_output', '?')} out")
        print(f"  Latency: {message['metadata'].get('latency_ms', '?')}ms")

# Send a follow-up message
print("\nSending follow-up message...")
client_msg, assistant_msg = conversation_handler.send_message(
    session_id=session_info["id"],
    message="I've been having trouble sleeping and find myself worrying about work constantly. Do you have any suggestions for managing anxiety?",
)

# Print the response
print(f"\nCLIENT: {client_msg.content}")
print(f"ASSISTANT: {assistant_msg.content}")
print(f"  Provider: {assistant_msg.metadata.get('provider')}")
print(f"  Model: {assistant_msg.metadata.get('model')}")
print(f"  Tokens: {assistant_msg.metadata.get('tokens_input', '?')} in, {assistant_msg.metadata.get('tokens_output', '?')} out")
print(f"  Latency: {assistant_msg.metadata.get('latency_ms', '?')}ms")

print("\nTest completed successfully!")
