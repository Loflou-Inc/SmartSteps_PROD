"""
Integration tests for the Smart Steps AI API.

This script simulates a frontend client interacting with the API,
testing the full integration of all components.
"""

import os
import sys
import time
import json
import uuid
import requests
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configuration
API_URL = "http://localhost:8000"  # Update with your API URL
TEST_USERNAME = "admin"
TEST_PASSWORD = "password"

class APIClient:
    """Client for interacting with the Smart Steps AI API."""
    
    def __init__(self, base_url):
        """Initialize the client with the base URL."""
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def login(self, username, password):
        """Authenticate and get an access token."""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/token",
            data={"username": username, "password": password}
        )
        
        if response.status_code != 200:
            raise Exception(f"Login failed: {response.text}")
        
        self.token = response.json()["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        return response.json()
    
    def logout(self):
        """Log out and clear the session."""
        if self.token:
            response = self.session.post(f"{self.base_url}/api/v1/auth/logout")
            self.token = None
            self.session.headers.pop("Authorization", None)
            return response.status_code == 200
        return True
    
    def get_current_user(self):
        """Get the current authenticated user."""
        response = self.session.get(f"{self.base_url}/api/v1/auth/me")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get current user: {response.text}")
        
        return response.json()
    
    def create_persona(self, persona_data):
        """Create a new persona."""
        response = self.session.post(
            f"{self.base_url}/api/v1/personas/",
            json=persona_data
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create persona: {response.text}")
        
        return response.json()
    
    def get_persona(self, persona_id):
        """Get a persona by ID."""
        response = self.session.get(f"{self.base_url}/api/v1/personas/{persona_id}")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get persona: {response.text}")
        
        return response.json()
    
    def create_session(self, session_data):
        """Create a new session."""
        response = self.session.post(
            f"{self.base_url}/api/v1/sessions/",
            json=session_data
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create session: {response.text}")
        
        return response.json()
    
    def get_session(self, session_id):
        """Get a session by ID."""
        response = self.session.get(f"{self.base_url}/api/v1/sessions/{session_id}")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get session: {response.text}")
        
        return response.json()
    
    def add_message(self, session_id, message_data):
        """Add a message to a session."""
        response = self.session.post(
            f"{self.base_url}/api/v1/conversations/{session_id}/messages",
            json=message_data
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to add message: {response.text}")
        
        return response.json()
    
    def get_conversation_history(self, session_id):
        """Get the conversation history for a session."""
        response = self.session.get(
            f"{self.base_url}/api/v1/conversations/{session_id}/history"
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get conversation history: {response.text}")
        
        return response.json()


def run_integration_test():
    """Run a full integration test simulating client-API interaction."""
    print("Starting integration test for Smart Steps AI API...")
    
    # Initialize client
    client = APIClient(API_URL)
    
    try:
        # Step 1: Authenticate
        print("\n1. Authenticating...")
        client.login(TEST_USERNAME, TEST_PASSWORD)
        user = client.get_current_user()
        print(f"   Authenticated as: {user['username']} (role: {user['role']})")
        
        # Step 2: Create a persona
        print("\n2. Creating a persona...")
        persona_data = {
            "name": f"test-persona-{uuid.uuid4().hex[:8]}",
            "display_name": "Test Integration Persona",
            "version": "1.0.0",
            "description": "A test persona for integration testing",
            "system_prompt": "You are a test persona designed for integration testing.",
            "personality_traits": {
                "empathy": 7,
                "analytical": 8,
                "patience": 6,
                "directness": 5,
                "formality": 4,
                "warmth": 7,
                "curiosity": 9,
                "confidence": 8
            },
            "expertise_areas": ["testing", "integration", "psychology"],
            "conversation_style": {
                "greeting_format": "Hello {{client_name}}. How can I help you today?",
                "question_frequency": "medium",
                "session_structure": ["introduction", "assessment", "discussion", "summary"],
                "typical_phrases": ["Let's examine this further", "That's an interesting point"]
            },
            "rules": ["Be precise", "Provide examples", "Ask clarifying questions"]
        }
        persona = client.create_persona(persona_data)
        print(f"   Created persona: {persona['name']} (ID: {persona['id']})")
        
        # Step 3: Create a session
        print("\n3. Creating a session...")
        session_data = {
            "title": "Integration Test Session",
            "client_id": f"test-client-{uuid.uuid4().hex[:8]}",
            "persona_id": persona["id"],
            "provider_id": None,
            "metadata": {"purpose": "Integration test"}
        }
        session = client.create_session(session_data)
        print(f"   Created session: {session['title']} (ID: {session['id']})")
        
        # Step 4: Send messages in the conversation
        print("\n4. Simulating conversation...")
        messages = [
            {"role": "client", "content": "Hello, I'm here for our first session."},
            {"role": "client", "content": "I've been feeling stressed lately."},
            {"role": "client", "content": "I think it's related to my work situation."}
        ]
        
        for idx, msg in enumerate(messages):
            message = client.add_message(session["id"], msg)
            print(f"   Message {idx+1} sent: {msg['content'][:30]}...")
            
            # Simulate AI response (in a real integration, this would come from the server)
            ai_response = {
                "role": "assistant", 
                "content": f"Response to message {idx+1}. I understand your concerns about {msg['content'].split()[3]} and I'm here to help."
            }
            client.add_message(session["id"], ai_response)
            print(f"   AI responded: {ai_response['content'][:30]}...")
            
            # Small delay to simulate real conversation timing
            time.sleep(0.5)
        
        # Step 5: Get conversation history
        print("\n5. Retrieving conversation history...")
        history = client.get_conversation_history(session["id"])
        print(f"   Retrieved {len(history['messages'])} messages")
        
        # Step 6: Generate analysis (if implemented)
        print("\n6. Requesting session analysis...")
        try:
            response = client.session.post(
                f"{API_URL}/api/v1/analysis/sessions/{session['id']}/analyze"
            )
            if response.status_code == 200:
                analysis = response.json()
                print(f"   Analysis generated with {len(analysis['insights'])} insights")
            else:
                print(f"   Analysis endpoint not implemented: {response.status_code}")
        except Exception as e:
            print(f"   Analysis endpoint not implemented: {e}")
        
        # Step 7: Log out
        print("\n7. Logging out...")
        if client.logout():
            print("   Successfully logged out")
        
        print("\nIntegration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nIntegration test failed: {e}")
        return False


if __name__ == "__main__":
    run_integration_test()
