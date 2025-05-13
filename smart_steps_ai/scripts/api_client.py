#!/usr/bin/env python
"""
Smart Steps API Test Client

This script provides a standalone client for testing the Smart Steps API.
It includes authentication, session management, and basic API operations.

Usage:
    python api_client.py auth
    python api_client.py sessions
    python api_client.py personas
    python api_client.py monitoring

Author: Smart Steps Team
Date: May 13, 2025
"""

import argparse
import json
import os
import sys
import requests
from typing import Dict, List, Optional, Any

# Configuration
API_URL = "http://localhost:9500"
USERNAME = "admin"
PASSWORD = "password"
REQUEST_TIMEOUT = 10  # seconds

class SmartStepsClient:
    """Client for interacting with the Smart Steps API."""
    
    def __init__(self, api_url: str = API_URL, 
                 username: str = USERNAME, 
                 password: str = PASSWORD):
        """
        Initialize the client.
        
        Args:
            api_url: URL of the API server
            username: Username for authentication
            password: Password for authentication
        """
        self.api_url = api_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.access_token = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with the API server.
        
        Returns:
            True if authentication was successful, False otherwise
        """
        print(f"Authenticating as {self.username}...")
        
        try:
            url = f"{self.api_url}/api/v1/auth/token"
            response = self.session.post(
                url, 
                data={
                    "username": self.username,
                    "password": self.password
                },
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                print("Authentication successful!")
                return True
            else:
                print(f"Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Error during authentication: {str(e)}")
            return False
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        Get information about the current user.
        
        Returns:
            User information
        """
        print("Getting current user information...")
        
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return {}
        
        try:
            url = f"{self.api_url}/api/v1/auth/me"
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                user_data = response.json()
                print("User information retrieved successfully!")
                return user_data
            else:
                print(f"Failed to get user information: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error getting user information: {str(e)}")
            return {}
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Get list of sessions.
        
        Returns:
            List of sessions
        """
        print("Getting sessions...")
        
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return []
        
        try:
            url = f"{self.api_url}/api/v1/sessions"
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                sessions = response.json()
                print(f"Retrieved {len(sessions)} sessions")
                return sessions
            else:
                print(f"Failed to get sessions: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error getting sessions: {str(e)}")
            return []
    
    def create_session(self, client_id: str, persona_id: str) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            client_id: Client ID
            persona_id: Persona ID
            
        Returns:
            Session information
        """
        print(f"Creating session for client {client_id} with persona {persona_id}...")
        
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return {}
        
        try:
            url = f"{self.api_url}/api/v1/sessions"
            response = self.session.post(
                url, 
                json={
                    "client_id": client_id,
                    "persona_id": persona_id,
                    "metadata": {
                        "client_name": "Test Client",
                        "therapist_name": "Test Therapist",
                        "session_type": "testing"
                    }
                },
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 201:
                session_data = response.json()
                print(f"Session created successfully with ID: {session_data.get('id')}")
                return session_data
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
        print("Getting personas...")
        
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return []
        
        try:
            url = f"{self.api_url}/api/v1/personas"
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                personas = response.json()
                print(f"Retrieved {len(personas)} personas")
                return personas
            else:
                print(f"Failed to get personas: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error getting personas: {str(e)}")
            return []
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health information.
        
        Returns:
            System health information
        """
        print("Getting system health...")
        
        try:
            url = f"{self.api_url}/health"
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                health_data = response.json()
                print("System health retrieved successfully!")
                return health_data
            else:
                print(f"Failed to get system health: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error getting system health: {str(e)}")
            return {}
    
    def get_admin_metrics(self) -> Dict[str, Any]:
        """
        Get admin metrics.
        
        Returns:
            Admin metrics
        """
        print("Getting admin metrics...")
        
        if not self.access_token:
            print("Not authenticated. Authenticate first.")
            return {}
        
        try:
            url = f"{self.api_url}/api/v1/admin/metrics"
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                metrics = response.json()
                print("Admin metrics retrieved successfully!")
                return metrics
            else:
                print(f"Failed to get admin metrics: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error getting admin metrics: {str(e)}")
            return {}
    
    def run_maintenance(self, tasks: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run maintenance tasks.
        
        Args:
            tasks: List of tasks to run
            
        Returns:
            Maintenance results
        """
        print("Running maintenance tasks...")
        
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
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                maintenance_data = response.json()
                print("Maintenance tasks completed successfully!")
                return maintenance_data
            else:
                print(f"Failed to run maintenance tasks: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"Error running maintenance tasks: {str(e)}")
            return {}

def format_json(data: Any) -> str:
    """
    Format JSON data for display.
    
    Args:
        data: Data to format
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=2)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Smart Steps API Test Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Authentication command
    auth_parser = subparsers.add_parser("auth", help="Test authentication")
    
    # Sessions command
    sessions_parser = subparsers.add_parser("sessions", help="Test session management")
    sessions_parser.add_argument("--create", action="store_true", help="Create a new session")
    sessions_parser.add_argument("--client", default="test_client", help="Client ID for new session")
    sessions_parser.add_argument("--persona", default="test_therapist", help="Persona ID for new session")
    
    # Personas command
    personas_parser = subparsers.add_parser("personas", help="Test persona management")
    
    # Monitoring command
    monitoring_parser = subparsers.add_parser("monitoring", help="Test monitoring features")
    monitoring_parser.add_argument("--health", action="store_true", help="Get system health")
    monitoring_parser.add_argument("--metrics", action="store_true", help="Get admin metrics")
    monitoring_parser.add_argument("--maintenance", action="store_true", help="Run maintenance tasks")
    
    args = parser.parse_args()
    
    # Create client
    client = SmartStepsClient()
    
    if args.command == "auth":
        # Test authentication
        if client.authenticate():
            user_info = client.get_current_user()
            print("\nUser Information:")
            print(format_json(user_info))
    
    elif args.command == "sessions":
        # Test session management
        if client.authenticate():
            if args.create:
                # Create a new session
                session = client.create_session(args.client, args.persona)
                print("\nCreated Session:")
                print(format_json(session))
            
            # Get sessions
            sessions = client.get_sessions()
            print("\nSessions:")
            print(format_json(sessions))
    
    elif args.command == "personas":
        # Test persona management
        if client.authenticate():
            personas = client.get_personas()
            print("\nPersonas:")
            print(format_json(personas))
    
    elif args.command == "monitoring":
        # Test monitoring features
        if args.health or not (args.metrics or args.maintenance):
            # Get system health
            health = client.get_system_health()
            print("\nSystem Health:")
            print(format_json(health))
        
        if args.metrics or args.maintenance:
            # Need authentication for admin features
            if client.authenticate():
                if args.metrics:
                    # Get admin metrics
                    metrics = client.get_admin_metrics()
                    print("\nAdmin Metrics:")
                    print(format_json(metrics))
                
                if args.maintenance:
                    # Run maintenance tasks
                    results = client.run_maintenance()
                    print("\nMaintenance Results:")
                    print(format_json(results))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
