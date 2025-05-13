"""
Direct API controller for the Smart Steps AI system.
This module provides a simple wrapper around the API for direct access.

Usage:
    from smart_steps_ai.api.direct_controller import SmartStepsController
    
    controller = SmartStepsController()
    controller.authenticate("admin", "password")
    sessions = controller.get_sessions()

Author: Smart Steps Team
Date: May 13, 2025
"""

import os
import sys
import json
import requests
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

class SmartStepsController:
    """Controller for the Smart Steps AI API."""
    
    def __init__(self, api_url: str = "http://localhost:9500"):
        """
        Initialize the controller.
        
        Args:
            api_url: URL of the API server
        """
        self.api_url = api_url
        self.session = requests.Session()
        self.access_token = None
        self.user_info = None
    
    def start_server(self, port: int = 9500, config_path: Optional[str] = None) -> bool:
        """
        Start the API server.
        
        Args:
            port: Port to listen on
            config_path: Path to configuration file
            
        Returns:
            True if the server was started successfully, False otherwise
        """
        import subprocess
        import time
        
        env = os.environ.copy()
        if config_path:
            env["CONFIG_PATH"] = config_path
        
        # Start the server
        try:
            server_process = subprocess.Popen(
                [sys.executable, "-m", "smart_steps_ai.api"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for the server to start
            time.sleep(2)
            
            # Check if server is running
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=5)
                if response.status_code == 200:
                    print(f"API server running on port {port}")
                    return True
            except:
                pass
            
            print("Failed to start API server")
            return False
        except Exception as e:
            print(f"Error starting API server: {str(e)}")
            return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate with the API server.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            url = f"{self.api_url}/api/v1/auth/token"
            response = self.session.post(
                url, 
                data={
                    "username": username,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                # Get user info
                self.user_info = self._get_current_user()
                
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            return False
    
    def _get_current_user(self) -> Dict[str, Any]:
        """
        Get information about the current user.
        
        Returns:
            User information
        """
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return {}
        
        try:
            url = f"{self.api_url}/api/v1/auth/me"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user information: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error getting user information: {str(e)}")
            return {}
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health information.
        
        Returns:
            System health information
        """
        try:
            url = f"{self.api_url}/health"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get system health: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error getting system health: {str(e)}")
            return {}
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Get list of sessions.
        
        Returns:
            List of sessions
        """
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return []
        
        try:
            url = f"{self.api_url}/api/v1/sessions"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get sessions: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error getting sessions: {str(e)}")
            return []
    
    def create_session(self, client_id: str, persona_id: str, 
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            client_id: Client ID
            persona_id: Persona ID
            metadata: Session metadata
            
        Returns:
            Session information
        """
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return {}
        
        metadata = metadata or {
            "client_name": "Test Client",
            "therapist_name": "Test Therapist",
            "session_type": "api_test"
        }
        
        try:
            url = f"{self.api_url}/api/v1/sessions"
            response = self.session.post(
                url, 
                json={
                    "client_id": client_id,
                    "persona_id": persona_id,
                    "metadata": metadata
                },
                timeout=10
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Failed to create session: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            return {}
    
    def get_personas(self) -> List[Dict[str, Any]]:
        """
        Get list of personas.
        
        Returns:
            List of personas
        """
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return []
        
        try:
            url = f"{self.api_url}/api/v1/personas"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get personas: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error getting personas: {str(e)}")
            return []
    
    def add_message(self, session_id: str, role: str, content: str) -> Dict[str, Any]:
        """
        Add a message to a session.
        
        Args:
            session_id: Session ID
            role: Message role ("user" or "assistant")
            content: Message content
            
        Returns:
            Message information
        """
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return {}
        
        try:
            url = f"{self.api_url}/api/v1/sessions/{session_id}/messages"
            response = self.session.post(
                url, 
                json={
                    "role": role,
                    "content": content
                },
                timeout=10
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Failed to add message: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error adding message: {str(e)}")
            return {}
    
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get messages for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of messages
        """
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return []
        
        try:
            url = f"{self.api_url}/api/v1/sessions/{session_id}/messages"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get messages: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []
    
    def run_maintenance(self, tasks: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run maintenance tasks.
        
        Args:
            tasks: List of tasks to run
            
        Returns:
            Maintenance results
        """
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return {}
        
        try:
            url = f"{self.api_url}/api/v1/admin/maintenance"
            response = self.session.post(
                url, 
                json={
                    "tasks": tasks or ["clean_temp_files"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to run maintenance tasks: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error running maintenance tasks: {str(e)}")
            return {}

def start_controller(api_url: str = "http://localhost:9500", 
                    username: str = "admin", 
                    password: str = "password") -> SmartStepsController:
    """
    Create and authenticate a controller.
    
    Args:
        api_url: URL of the API server
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        Authenticated controller
    """
    controller = SmartStepsController(api_url)
    
    # Check if server is available
    health = controller.get_system_health()
    if not health:
        print("API server not available. Starting server...")
        controller.start_server()
    
    # Authenticate
    if controller.authenticate(username, password):
        print(f"Authenticated as {username}")
        return controller
    else:
        print("Authentication failed")
        return controller

if __name__ == "__main__":
    # Example usage
    controller = start_controller()
    health = controller.get_system_health()
    print(json.dumps(health, indent=2))
