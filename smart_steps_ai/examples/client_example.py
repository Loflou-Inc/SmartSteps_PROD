"""
Smart Steps AI Python Client Example

This script demonstrates how to use the Smart Steps AI Python client library
to interact with the API and conduct a therapy session.
"""

import os
import sys
import logging
import json
from pathlib import Path
from uuid import uuid4

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.smart_steps_ai.client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run a complete workflow example with the client library."""
    # Create client with API key
    api_key = os.environ.get("SMART_STEPS_API_KEY")
    if not api_key:
        logger.error("No API key provided. Please set the SMART_STEPS_API_KEY environment variable.")
        logger.info("For testing purposes, you can try to log in with username and password.")
        
        try:
            username = input("Enter username: ")
            password = input("Enter password: ")
            
            # Create client without API key
            client = APIClient(base_url="http://127.0.0.1:9500")
            
            # Try to log in
            login_result = client.login(username, password)
            logger.info(f"Login successful. Token: {login_result.get('access_token')[:10]}...")
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return
    else:
        # Create client with API key
        client = APIClient(
            base_url="http://127.0.0.1:9500",
            api_key=api_key,
        )
    
    # Step 1: Get available personas
    try:
        logger.info("Getting available personas...")
        persona_response = client.list_personas()
        personas = persona_response.get("personas", [])
        
        if not personas:
            logger.error("No personas found.")
            return
        
        logger.info(f"Found {len(personas)} personas:")
        for i, persona in enumerate(personas, 1):
            logger.info(f"{i}. {persona.get('name')} - {persona.get('display_name')}")
        
        # Select a persona
        if len(personas) == 1:
            persona = personas[0]
        else:
            persona_idx = int(input(f"Select a persona (1-{len(personas)}): ")) - 1
            persona = personas[persona_idx]
        
        logger.info(f"Selected persona: {persona.get('display_name')}")
    except Exception as e:
        logger.error(f"Error getting personas: {str(e)}")
        return
    
    # Step 2: Create a new session
    try:
        logger.info("Creating a new session...")
        client_id = f"test_client_{uuid4().hex[:8]}"
        
        session_response = client.create_session(
            client_id=client_id,
            persona_id=persona.get("id"),
            title="Test Session",
            metadata={
                "purpose": "Testing the Python client library",
                "notes": "This is a test session created by the example script.",
            },
        )
        
        session_id = session_response.get("id")
        logger.info(f"Created session with ID: {session_id}")
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return
    
    # Step 3: Send an initial message
    try:
        logger.info("Sending an initial message...")
        initial_message = "Hello! This is my first time talking to a therapist. I'm not sure where to start."
        
        message_response = client.send_message(
            session_id=session_id,
            message=initial_message,
        )
        
        assistant_message = message_response.get("assistant_message", {}).get("content", "")
        logger.info("Assistant's response:")
        logger.info(f"\n{assistant_message}\n")
    except Exception as e:
        logger.error(f"Error sending initial message: {str(e)}")
    
    # Step 4: Continue the conversation
    try:
        continue_conversation = True
        while continue_conversation:
            user_message = input("\nYour message (type 'exit' to end): ")
            
            if user_message.lower() in ["exit", "quit", "bye"]:
                continue_conversation = False
                continue
            
            logger.info("Sending message...")
            message_response = client.send_message(
                session_id=session_id,
                message=user_message,
            )
            
            assistant_message = message_response.get("assistant_message", {}).get("content", "")
            logger.info("Assistant's response:")
            logger.info(f"\n{assistant_message}\n")
    except Exception as e:
        logger.error(f"Error in conversation: {str(e)}")
    
    # Step 5: Get conversation history
    try:
        logger.info("Getting conversation history...")
        history_response = client.get_conversation_history(session_id)
        
        messages = history_response.get("messages", [])
        logger.info(f"Found {len(messages)} messages in the conversation.")
        
        # Save conversation to file
        output_file = f"conversation_{session_id}.json"
        with open(output_file, "w") as f:
            json.dump(history_response, f, indent=2)
        
        logger.info(f"Saved conversation history to {output_file}")
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
    
    # Step 6: Analyze the session
    try:
        logger.info("Analyzing the session...")
        analysis_response = client.analyze_session(session_id)
        
        # Check if analysis is available
        if "error" in analysis_response:
            logger.warning(f"Analysis not available: {analysis_response.get('error')}")
        else:
            # Get the analysis report
            logger.info("Getting analysis report...")
            report_response = client.get_session_report(session_id, format="markdown")
            
            # Save report to file
            output_file = f"analysis_{session_id}.md"
            with open(output_file, "w") as f:
                f.write(report_response.get("report", ""))
            
            logger.info(f"Saved analysis report to {output_file}")
    except Exception as e:
        logger.error(f"Error analyzing session: {str(e)}")
    
    logger.info("Example completed.")

if __name__ == "__main__":
    main()
