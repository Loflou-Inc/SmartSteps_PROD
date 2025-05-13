"""Session management commands for the CLI."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.prompt import Confirm, Prompt

from ...config import get_config_manager
from ...session import ConversationHandler, SessionManager, SessionState, SessionType
from ...persona import PersonaManager
from ...utils import get_logger
from ..console import (
    console,
    print_error,
    print_info,
    print_session_info,
    print_success,
    print_table,
    print_title,
    print_warning,
)

# Initialize logger
logger = get_logger(__name__)

# Create managers
session_manager = SessionManager()
persona_manager = PersonaManager()
conversation_handler = ConversationHandler(
    session_manager=session_manager,
    persona_manager=persona_manager,
)


def register(app: typer.Typer) -> None:
    """
    Register commands with the app.

    Args:
        app (typer.Typer): The typer app
    """
    
    @app.command("create")
    def create_session(
        client_name: str = typer.Option(
            ..., "--client", "-c", help="Name of the client"
        ),
        persona_name: Optional[str] = typer.Option(
            None, "--persona", "-p", help="Name of the persona to use"
        ),
        session_type: str = typer.Option(
            "standard", "--type", "-t", help="Type of session"
        ),
        initial_message: Optional[str] = typer.Option(
            None, "--message", "-m", help="Initial message to send"
        ),
        interactive: bool = typer.Option(
            False, "--interactive", "-i", help="Start interactive mode after creation"
        ),
    ) -> None:
        """
        Create a new session.
        """
        # Validate session type
        try:
            session_type_enum = SessionType(session_type)
        except ValueError:
            valid_types = [t.value for t in SessionType]
            print_error(f"Invalid session type: {session_type}")
            print_info(f"Valid types: {', '.join(valid_types)}")
            raise typer.Exit(1)
        
        # Check if persona exists
        if persona_name and not persona_manager.get_persona(persona_name):
            print_error(f"Persona not found: {persona_name}")
            available_personas = persona_manager.list_personas()
            if available_personas:
                print_info("Available personas:")
                for persona in available_personas:
                    print_info(f"  - {persona.name}: {persona.display_name}")
            raise typer.Exit(1)
        
        # Create the session
        print_info(f"Creating session for client: {client_name}")
        
        if initial_message:
            print_info(f"With initial message: {initial_message}")
        
        session_info = conversation_handler.create_new_session(
            client_name=client_name,
            persona_name=persona_name,
            session_type=session_type,
            initial_message=initial_message,
        )
        
        if not session_info:
            print_error("Failed to create session")
            raise typer.Exit(1)
        
        print_success("Session created successfully")
        print_session_info(session_info)
        
        # Store the session ID in an environment variable for other commands
        os.environ["SMART_STEPS_CURRENT_SESSION"] = session_info["id"]
        print_info("Session ID set as current session")
        
        # Start interactive mode if requested
        if interactive:
            from .conversation_commands import interactive_conversation
            interactive_conversation(session_info["id"])
    
    @app.command("list")
    def list_sessions(
        client_name: Optional[str] = typer.Option(
            None, "--client", "-c", help="Filter by client name"
        ),
        state: Optional[str] = typer.Option(
            None, "--state", "-s", help="Filter by session state"
        ),
        active_only: bool = typer.Option(
            False, "--active", "-a", help="Show only active sessions"
        ),
        format: str = typer.Option(
            "table", "--format", "-f", help="Output format (table, json)"
        ),
    ) -> None:
        """
        List all sessions.
        """
        # Validate state
        if state:
            try:
                state_enum = SessionState(state)
            except ValueError:
                valid_states = [s.value for s in SessionState]
                print_error(f"Invalid session state: {state}")
                print_info(f"Valid states: {', '.join(valid_states)}")
                raise typer.Exit(1)
        
        # Apply active-only filter
        if active_only:
            state = "active"
        
        # Get sessions
        sessions = session_manager.list_sessions(
            client_name=client_name,
            session_state=state,
        )
        
        if not sessions:
            print_info("No sessions found")
            return
        
        # Print sessions
        print_title(f"Sessions ({len(sessions)})")
        
        if format == "json":
            # Convert to JSON
            json_sessions = [
                {
                    "id": s.id,
                    "client_name": s.client_name,
                    "persona_name": s.persona_name,
                    "session_type": s.session_type,
                    "state": s.state,
                    "created_at": s.created_at.isoformat(),
                    "updated_at": s.updated_at.isoformat(),
                    "messages_count": s.messages_count,
                }
                for s in sessions
            ]
            console.print(json.dumps(json_sessions, indent=2))
        else:
            # Create table
            headers = ["ID", "Client", "Persona", "Type", "State", "Messages", "Last Updated"]
            rows = [
                [
                    s.id,
                    s.client_name,
                    s.persona_name,
                    s.session_type,
                    s.state,
                    s.messages_count,
                    s.updated_at.strftime("%Y-%m-%d %H:%M"),
                ]
                for s in sessions
            ]
            print_table(headers, rows)
    
    @app.command("info")
    def session_info(
        session_id: Optional[str] = typer.Argument(
            None, help="Session ID (defaults to current session)"
        ),
    ) -> None:
        """
        Show session information.
        """
        # Get session ID
        if not session_id:
            session_id = os.environ.get("SMART_STEPS_CURRENT_SESSION")
            if not session_id:
                print_error("No session ID provided and no current session set")
                print_info("Set a current session with: smart-steps-ai session set <id>")
                raise typer.Exit(1)
        
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            print_error(f"Session not found: {session_id}")
            raise typer.Exit(1)
        
        # Convert to session info
        session_info = {
            "id": session.id,
            "client_name": session.client_name,
            "persona_name": session.persona_name,
            "session_type": session.session_type.value,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages_count": session.messages_count,
            "duration_seconds": session.duration_seconds,
        }
        
        # Print session info
        print_session_info(session_info)
    
    @app.command("set")
    def set_session(
        session_id: str = typer.Argument(..., help="Session ID to set as current"),
    ) -> None:
        """
        Set the current session.
        """
        # Check if session exists
        session = session_manager.get_session(session_id)
        if not session:
            print_error(f"Session not found: {session_id}")
            raise typer.Exit(1)
        
        # Set as current session
        os.environ["SMART_STEPS_CURRENT_SESSION"] = session_id
        
        # Convert to session info
        session_info = {
            "id": session.id,
            "client_name": session.client_name,
            "persona_name": session.persona_name,
            "session_type": session.session_type.value,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
        }
        
        print_success(f"Current session set to: {session_id}")
        print_session_info(session_info)
    
    @app.command("state")
    def update_session_state(
        state: str = typer.Argument(..., help="New session state"),
        session_id: Optional[str] = typer.Option(
            None, "--session", "-s", help="Session ID (defaults to current session)"
        ),
    ) -> None:
        """
        Update the state of a session.
        """
        # Validate state
        try:
            state_enum = SessionState(state)
        except ValueError:
            valid_states = [s.value for s in SessionState]
            print_error(f"Invalid session state: {state}")
            print_info(f"Valid states: {', '.join(valid_states)}")
            raise typer.Exit(1)
        
        # Get session ID
        if not session_id:
            session_id = os.environ.get("SMART_STEPS_CURRENT_SESSION")
            if not session_id:
                print_error("No session ID provided and no current session set")
                print_info("Set a current session with: smart-steps-ai session set <id>")
                raise typer.Exit(1)
        
        # Update state
        success = session_manager.update_session_state(session_id, state)
        
        if not success:
            print_error(f"Failed to update session state: {session_id}")
            raise typer.Exit(1)
        
        print_success(f"Session state updated to: {state}")
    
    @app.command("export")
    def export_session(
        output_file: Path = typer.Argument(..., help="Path to export the session"),
        session_id: Optional[str] = typer.Option(
            None, "--session", "-s", help="Session ID (defaults to current session)"
        ),
        format: str = typer.Option(
            "json", "--format", "-f", help="Export format (json, markdown, text)"
        ),
        include_metadata: bool = typer.Option(
            True, "--metadata/--no-metadata", help="Include message metadata"
        ),
    ) -> None:
        """
        Export a session to a file.
        """
        # Get session ID
        if not session_id:
            session_id = os.environ.get("SMART_STEPS_CURRENT_SESSION")
            if not session_id:
                print_error("No session ID provided and no current session set")
                print_info("Set a current session with: smart-steps-ai session set <id>")
                raise typer.Exit(1)
        
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            print_error(f"Session not found: {session_id}")
            raise typer.Exit(1)
        
        # Check if file exists
        if output_file.exists():
            if not Confirm.ask(f"File exists: {output_file}. Overwrite?"):
                print_info("Operation cancelled")
                raise typer.Exit(0)
        
        # Get conversation history
        history = conversation_handler.get_conversation_history(session_id)
        if not history:
            print_error(f"Failed to get conversation history for session: {session_id}")
            raise typer.Exit(1)
        
        # Prepare session info
        session_info = {
            "id": session.id,
            "client_name": session.client_name,
            "persona_name": session.persona_name,
            "session_type": session.session_type.value,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages_count": session.messages_count,
            "duration_seconds": session.duration_seconds,
        }
        
        # Export based on format
        if format == "json":
            # Export as JSON
            export_data = {
                "session": session_info,
                "messages": history,
            }
            
            if not include_metadata:
                for message in export_data["messages"]:
                    if "metadata" in message:
                        del message["metadata"]
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)
        
        elif format == "markdown":
            # Export as Markdown
            lines = []
            
            # Add session info
            lines.append(f"# Session: {session.id}")
            lines.append(f"Client: {session.client_name}")
            lines.append(f"Persona: {session.persona_name}")
            lines.append(f"Type: {session.session_type.value}")
            lines.append(f"State: {session.state.value}")
            lines.append(f"Created: {session.created_at.isoformat()}")
            lines.append(f"Updated: {session.updated_at.isoformat()}")
            lines.append(f"Messages: {session.messages_count}")
            lines.append(f"Duration: {session.duration_seconds} seconds")
            lines.append("")
            
            # Add messages
            lines.append("## Conversation")
            lines.append("")
            
            for message in history:
                lines.append(f"### {message['role'].upper()}")
                lines.append(f"{message['content']}")
                
                if include_metadata and "metadata" in message:
                    lines.append("")
                    lines.append("*Metadata:*")
                    for key, value in message["metadata"].items():
                        lines.append(f"* {key}: {value}")
                
                lines.append("")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        
        elif format == "text":
            # Export as plain text
            lines = []
            
            # Add session info
            lines.append(f"Session: {session.id}")
            lines.append(f"Client: {session.client_name}")
            lines.append(f"Persona: {session.persona_name}")
            lines.append(f"Type: {session.session_type.value}")
            lines.append(f"State: {session.state.value}")
            lines.append(f"Created: {session.created_at.isoformat()}")
            lines.append(f"Updated: {session.updated_at.isoformat()}")
            lines.append(f"Messages: {session.messages_count}")
            lines.append(f"Duration: {session.duration_seconds} seconds")
            lines.append("")
            
            # Add messages
            lines.append("Conversation:")
            lines.append("")
            
            for message in history:
                lines.append(f"{message['role'].upper()}:")
                lines.append(f"{message['content']}")
                
                if include_metadata and "metadata" in message:
                    lines.append("")
                    lines.append("Metadata:")
                    for key, value in message["metadata"].items():
                        lines.append(f"  {key}: {value}")
                
                lines.append("")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        
        else:
            print_error(f"Invalid export format: {format}")
            print_info("Valid formats: json, markdown, text")
            raise typer.Exit(1)
        
        print_success(f"Session exported to: {output_file}")
    
    @app.command("delete")
    def delete_session(
        session_id: Optional[str] = typer.Argument(
            None, help="Session ID (defaults to current session)"
        ),
        force: bool = typer.Option(
            False, "--force", "-f", help="Skip confirmation"
        ),
    ) -> None:
        """
        Delete a session.
        """
        # Get session ID
        if not session_id:
            session_id = os.environ.get("SMART_STEPS_CURRENT_SESSION")
            if not session_id:
                print_error("No session ID provided and no current session set")
                print_info("Set a current session with: smart-steps-ai session set <id>")
                raise typer.Exit(1)
        
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            print_error(f"Session not found: {session_id}")
            raise typer.Exit(1)
        
        # Confirm deletion
        if not force:
            confirm_text = f"Delete session {session_id} for client {session.client_name}?"
            if not Confirm.ask(confirm_text):
                print_info("Operation cancelled")
                raise typer.Exit(0)
        
        # Delete session
        success = session_manager.delete_session(session_id)
        
        if not success:
            print_error(f"Failed to delete session: {session_id}")
            raise typer.Exit(1)
        
        print_success(f"Session deleted: {session_id}")
        
        # Clear current session if it was deleted
        if os.environ.get("SMART_STEPS_CURRENT_SESSION") == session_id:
            os.environ.pop("SMART_STEPS_CURRENT_SESSION")
            print_info("Current session cleared")
