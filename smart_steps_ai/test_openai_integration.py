"""
OpenAI Integration Test for Smart Steps AI

This script tests the Smart Steps AI system with a real OpenAI API key.
It creates a session, has a conversation, and verifies that OpenAI is being used.
"""

import os
import sys
import time
import json
import logging
import requests
from pathlib import Path
from uuid import uuid4

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.smart_steps_ai.client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configure API details
API_URL = "http://127.0.0.1:9500"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
API_KEY = os.environ.get("API_SECRET_KEY", "development_secret_key")

def check_server_running():
    """Check if the API server is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.info(f"API server is running: {response.json()}")
            return True
        else:
            logger.error(f"API server returned unexpected status: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"API server is not running: {str(e)}")
        return False

def main():
    """Run a real OpenAI integration test."""
    # Check for OpenAI API key
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not found in environment variables!")
        logger.error("Please set the OPENAI_API_KEY environment variable.")
        return

    logger.info("=== OpenAI Integration Test ===")
    logger.info(f"Using OpenAI API key: {OPENAI_API_KEY[:5]}...")
    
    # Check if server is running
    if not check_server_running():
        logger.error("API server is not running! Please start the server before running this test.")
        logger.info("You can start the server with: python run_src_server.py")
        return
    
    # Create client
    client = APIClient(base_url=API_URL, api_key=API_KEY)
    
    # Step 1: List personas and find the therapist
    try:
        personas = client.list_personas()
        persona_list = personas.get('personas', [])
        
        if not persona_list:
            logger.error("No personas found. Cannot continue test.")
            return
        
        # Find a therapist persona
        therapist_persona = None
        for persona in persona_list:
            if 'therapist' in persona.get('name', '').lower() or 'therapist' in persona.get('display_name', '').lower():
                therapist_persona = persona
                break
        
        # If no therapist persona, use the first one
        if not therapist_persona and persona_list:
            therapist_persona = persona_list[0]
            
        if not therapist_persona:
            logger.error("No suitable persona found. Cannot continue test.")
            return
            
        logger.info(f"Using persona: {therapist_persona.get('display_name')}")
        
    except Exception as e:
        logger.error(f"Error listing personas: {str(e)}")
        return
    
    # Step 2: Create a session explicitly specifying OpenAI provider
    try:
        client_id = f"test_client_{uuid4().hex[:8]}"
        
        session_data = {
            "client_id": client_id,
            "persona_id": therapist_persona.get("id"),
            "title": "OpenAI Integration Test",
            "provider_id": "openai",  # Explicitly use OpenAI provider
            "metadata": {
                "test_type": "openai_integration",
                "timestamp": time.time()
            }
        }
        
        session = client.post("/api/v1/sessions", session_data)
        session_id = session.get("id")
        
        if not session_id:
            logger.error("Failed to create session. Cannot continue test.")
            return
            
        logger.info(f"Created session: {session_id}")
        
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return
    
    # Step 3: Start a conversation
    try:
        # Initial message
        initial_msg = "Hello, I'm feeling anxious about a presentation I have to give next week. I keep worrying that I'll mess up and everyone will judge me."
        
        logger.info("Sending initial message...")
        response = client.send_message(session_id, initial_msg)
        
        # Get assistant response and metadata
        assistant_message = response.get("assistant_message", {})
        content = assistant_message.get("content", "")
        metadata = assistant_message.get("metadata", {})
        
        logger.info("=== Initial Response ===")
        logger.info(f"Provider: {metadata.get('provider')}")
        logger.info(f"Model: {metadata.get('model')}")
        logger.info(f"Tokens: {metadata.get('tokens_input')} in, {metadata.get('tokens_output')} out")
        logger.info(f"Latency: {metadata.get('latency_ms')}ms")
        logger.info("=== Content ===")
        logger.info(content)
        
        # Continue the conversation
        follow_up = "What techniques can I use to calm myself down before the presentation?"
        
        logger.info("\nSending follow-up message...")
        response = client.send_message(session_id, follow_up)
        
        # Get assistant response and metadata
        assistant_message = response.get("assistant_message", {})
        content = assistant_message.get("content", "")
        metadata = assistant_message.get("metadata", {})
        
        logger.info("=== Follow-up Response ===")
        logger.info(f"Provider: {metadata.get('provider')}")
        logger.info(f"Model: {metadata.get('model')}")
        logger.info(f"Tokens: {metadata.get('tokens_input')} in, {metadata.get('tokens_output')} out")
        logger.info(f"Latency: {metadata.get('latency_ms')}ms")
        logger.info("=== Content ===")
        logger.info(content)
        
    except Exception as e:
        logger.error(f"Error during conversation: {str(e)}")
        return
    
    # Step 4: Verify API is working with full conversation history
    try:
        logger.info("\nFetching conversation history...")
        history = client.get_conversation_history(session_id)
        
        messages = history.get("messages", [])
        logger.info(f"Found {len(messages)} messages in conversation")
        
        # Save the conversation history for review
        with open(f"openai_test_{session_id}.json", "w") as f:
            json.dump(history, f, indent=2)
            
        logger.info(f"Saved conversation history to openai_test_{session_id}.json")
    
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
    
    logger.info("=== OpenAI Integration Test Complete ===")
    if metadata.get('provider') == 'openai':
        logger.info("✅ SUCCESS: OpenAI provider confirmed working!")
    else:
        logger.warning(f"⚠️ TEST INCONCLUSIVE: Provider was {metadata.get('provider')}, not 'openai'")

if __name__ == "__main__":
    main()
