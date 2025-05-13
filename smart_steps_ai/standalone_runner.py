#!/usr/bin/env python
"""
Smart Steps AI Standalone Runner

This script provides a standalone runner for the Smart Steps AI system.
It starts the API server and provides a simple interface for interacting with it.

Usage:
    python standalone_runner.py

Author: Smart Steps Team
Date: May 13, 2025
"""

import argparse
import json
import os
import sys
import time
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.smart_steps_ai.api.direct_controller import SmartStepsController

def start_server(port: int = 9500) -> subprocess.Popen:
    """
    Start the API server.
    
    Args:
        port: Port to listen on
        
    Returns:
        Server process
    """
    print(f"Starting API server on port {port}...")
    
    # Start the server in a new process
    server_process = subprocess.Popen(
        [sys.executable, "run_api_server.bat"],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    return server_process

def stop_server(server_process):
    """
    Stop the API server.
    
    Args:
        server_process: Server process
    """
    print("Stopping API server...")
    server_process.terminate()
    
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print("Server not responding to terminate, forcing kill...")
        server_process.kill()

def run_interactive_session(controller: SmartStepsController):
    """
    Run an interactive session with the API.
    
    Args:
        controller: API controller
    """
    print("\nWelcome to Smart Steps AI Interactive Session")
    print("=============================================")
    print("Type 'help' for a list of commands, 'exit' to quit.")
    
    session_id = None
    
    while True:
        command = input("\n> ").strip().lower()
        
        if command == "exit":
            print("Exiting interactive session.")
            break
        
        elif command == "help":
            print("\nAvailable commands:")
            print("  help              - Show this help message")
            print("  exit              - Exit the interactive session")
            print("  health            - Get system health")
            print("  auth              - Authenticate with the API")
            print("  sessions          - Get list of sessions")
            print("  create            - Create a new session")
            print("  personas          - Get list of personas")
            print("  use <session_id>  - Use a specific session")
            print("  send <message>    - Send a message to the current session")
            print("  messages          - Get messages for the current session")
        
        elif command == "health":
            health = controller.get_system_health()
            print("\nSystem Health:")
            print(json.dumps(health, indent=2))
        
        elif command == "auth":
            username = input("Username: ")
            password = input("Password: ")
            if controller.authenticate(username, password):
                print(f"Authenticated as {username}")
            else:
                print("Authentication failed")
        
        elif command == "sessions":
            sessions = controller.get_sessions()
            print("\nSessions:")
            print(json.dumps(sessions, indent=2))
        
        elif command == "create":
            client_id = input("Client ID: ")
            persona_id = input("Persona ID: ")
            session = controller.create_session(client_id, persona_id)
            if session:
                print("\nCreated Session:")
                print(json.dumps(session, indent=2))
                session_id = session.get("id")
                print(f"Using session {session_id}")
        
        elif command == "personas":
            personas = controller.get_personas()
            print("\nPersonas:")
            print(json.dumps(personas, indent=2))
        
        elif command.startswith("use "):
            session_id = command[4:].strip()
            print(f"Using session {session_id}")
        
        elif command.startswith("send "):
            if not session_id:
                print("No session selected. Use 'use <session_id>' or 'create' first.")
                continue
            
            message = command[5:].strip()
            result = controller.add_message(session_id, "user", message)
            if result:
                print("\nSent message")
                
                # Get response
                time.sleep(1)  # Wait for processing
                messages = controller.get_messages(session_id)
                if messages:
                    # Find the latest assistant message
                    assistant_messages = [m for m in messages if m.get("role") == "assistant"]
                    if assistant_messages:
                        latest = assistant_messages[-1]
                        print(f"\nAssistant: {latest.get('content')}")
        
        elif command == "messages":
            if not session_id:
                print("No session selected. Use 'use <session_id>' or 'create' first.")
                continue
            
            messages = controller.get_messages(session_id)
            print("\nMessages:")
            for message in messages:
                role = message.get("role")
                content = message.get("content")
                print(f"\n{role.capitalize()}: {content}")
        
        else:
            print(f"Unknown command: {command}. Type 'help' for available commands.")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Smart Steps AI Standalone Runner")
    parser.add_argument("--port", type=int, default=9500, help="Port to listen on")
    parser.add_argument("--api-url", default="http://localhost:9500", help="URL of the API server")
    parser.add_argument("--username", default="admin", help="Username for authentication")
    parser.add_argument("--password", default="password", help="Password for authentication")
    parser.add_argument("--no-server", action="store_true", help="Don't start the API server (connect to existing server)")
    
    args = parser.parse_args()
    
    # Start the server if requested
    server_process = None
    if not args.no_server:
        server_process = start_server(args.port)
    
    # Create controller
    controller = SmartStepsController(args.api_url)
    
    # Check if server is available
    health = controller.get_system_health()
    if health:
        print("API server is available")
    else:
        print("API server not available. Please check server status.")
        if server_process:
            stop_server(server_process)
        return
    
    # Run interactive session
    try:
        run_interactive_session(controller)
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
    
    # Stop the server if we started it
    if server_process:
        stop_server(server_process)

if __name__ == "__main__":
    main()
