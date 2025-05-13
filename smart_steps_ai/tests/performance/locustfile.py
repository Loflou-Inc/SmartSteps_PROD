"""
Smart Steps AI Module - Performance Testing with Locust

This file defines load tests for the Smart Steps AI Module's REST API.
Run with: locust -f locustfile.py
"""

import json
import random
import string
from pathlib import Path

from locust import HttpUser, between, task, tag
from locust.exception import RescheduleTask

# Constants
BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = None  # Will be set during setup


class APIUser(HttpUser):
    """Simulated user of the Smart Steps AI API."""
    
    wait_time = between(1, 5)  # Wait between 1-5 seconds between tasks
    
    def on_start(self):
        """Authenticate before starting tasks."""
        self.get_auth_token()
        self.client.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        self.session_id = None
        self.conversation_ids = []
    
    def get_auth_token(self):
        """Authenticate and get a token."""
        try:
            credentials = {
                "username": "performance_test_user",
                "password": "performance_test_password"
            }
            response = self.client.post(f"{BASE_URL}/auth/token", json=credentials)
            if response.status_code == 200:
                self.auth_token = response.json()["access_token"]
            else:
                # If auth fails, create a test user
                response = self.client.post(
                    f"{BASE_URL}/auth/register", 
                    json={
                        "username": "performance_test_user",
                        "password": "performance_test_password",
                        "email": "performance@test.com",
                        "full_name": "Performance Test User"
                    }
                )
                if response.status_code == 201:
                    self.get_auth_token()  # Try authentication again
                else:
                    print(f"Failed to create test user: {response.status_code}")
                    print(response.text)
        except Exception as e:
            print(f"Error during authentication: {e}")
    
    @tag("sessions")
    @task(10)
    def create_session(self):
        """Create a new session."""
        try:
            client_name = f"TestClient_{random.randint(1000, 9999)}"
            session_data = {
                "client_name": client_name,
                "persona_id": "therapist_cbt",  # Using default persona
                "metadata": {
                    "test_run": True,
                    "client_age": random.randint(18, 65),
                    "client_gender": random.choice(["male", "female", "other"]),
                }
            }
            
            response = self.client.post(f"{BASE_URL}/sessions", json=session_data)
            
            if response.status_code == 201:
                self.session_id = response.json()["id"]
            else:
                print(f"Failed to create session: {response.status_code}")
                print(response.text)
                raise RescheduleTask()
        except Exception as e:
            print(f"Error creating session: {e}")
            raise RescheduleTask()
    
    @tag("conversations")
    @task(30)
    def send_message(self):
        """Send a message in an existing session."""
        if not self.session_id:
            self.create_session()
            
        try:
            # Generate a random message
            test_messages = [
                "I've been feeling anxious lately.",
                "Work has been really stressful this week.",
                "I had a conflict with my friend yesterday.",
                "I'm having trouble sleeping at night.",
                "I don't know how to handle this situation.",
                "I feel like nobody understands me.",
                "I've been trying the techniques you suggested last time.",
                "I had a panic attack yesterday at work.",
                "My family is pressuring me about my career choices.",
                "I feel like I'm making progress but still struggle sometimes."
            ]
            
            message_data = {
                "content": random.choice(test_messages),
                "metadata": {
                    "test_run": True,
                    "timestamp": random.randint(1000000, 9999999)
                }
            }
            
            response = self.client.post(
                f"{BASE_URL}/sessions/{self.session_id}/conversations", 
                json=message_data
            )
            
            if response.status_code == 201:
                conversation_id = response.json()["id"]
                self.conversation_ids.append(conversation_id)
            else:
                print(f"Failed to send message: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    @tag("analysis")
    @task(5)
    def get_session_analysis(self):
        """Get analysis for a session."""
        if not self.session_id:
            self.create_session()
            self.send_message()  # Need at least one message for analysis
            
        try:
            response = self.client.get(f"{BASE_URL}/analysis/sessions/{self.session_id}")
            
            if response.status_code != 200:
                print(f"Failed to get analysis: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error getting analysis: {e}")
    
    @tag("personas")
    @task(2)
    def list_personas(self):
        """List available personas."""
        try:
            response = self.client.get(f"{BASE_URL}/personas")
            
            if response.status_code != 200:
                print(f"Failed to list personas: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error listing personas: {e}")
    
    @tag("sessions")
    @task(5)
    def list_sessions(self):
        """List all sessions for the user."""
        try:
            response = self.client.get(f"{BASE_URL}/sessions")
            
            if response.status_code != 200:
                print(f"Failed to list sessions: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error listing sessions: {e}")
    
    @tag("memory")
    @task(5)
    def get_session_memory(self):
        """Test memory retrieval performance."""
        if not self.session_id:
            self.create_session()
            self.send_message()
            
        try:
            response = self.client.get(f"{BASE_URL}/sessions/{self.session_id}/memory")
            
            if response.status_code != 200:
                print(f"Failed to get session memory: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Error getting session memory: {e}")
    
    @tag("batch")
    @task(1)
    def batch_message_test(self):
        """Send multiple messages in quick succession to test batch processing."""
        if not self.session_id:
            self.create_session()
            
        try:
            for _ in range(5):  # Send 5 messages in quick succession
                message_data = {
                    "content": f"Batch test message {random.randint(1, 1000)}",
                    "metadata": {
                        "test_run": True,
                        "batch_test": True
                    }
                }
                
                response = self.client.post(
                    f"{BASE_URL}/sessions/{self.session_id}/conversations", 
                    json=message_data
                )
                
                if response.status_code != 201:
                    print(f"Failed in batch message test: {response.status_code}")
                    print(response.text)
                    break
        except Exception as e:
            print(f"Error in batch message test: {e}")
