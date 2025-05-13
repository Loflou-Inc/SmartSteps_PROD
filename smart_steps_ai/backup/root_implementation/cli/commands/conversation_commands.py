"""
Conversation commands for the Smart Steps AI CLI.

Provides commands for sending messages, viewing conversation history,
and interactive conversation mode with AI professional personas.
"""

import typer
import json
import os
import sys
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint
from pathlib import Path
from uuid import UUID

from smart_steps_ai.core.session_manager import SessionManager
from smart_steps_ai.core.persona_manager import PersonaManager
from smart_steps_ai.core.memory_manager import MemoryManager
from smart_steps_ai.ai_providers.conversation_handler import ConversationHandler

conversation_app = typer.Typer(
    help="Manage conversations with AI personas",
    no_args_is_help=True,
)

console = Console()
session_manager = SessionManager()
persona_manager = PersonaManager()
conversation_handler = ConversationHandler()

@conversation_app.callback()
def callback():
    """
    Manage conversations with AI professional personas.
    
    Send messages, view conversation history, and engage in
    interactive conversations with AI professional personas.
    """
    pass

@conversation_app.command("send")
def send_message(
    session_id: UUID = typer.Argument(..., help="ID of the session"),
    message: str = typer.Argument(..., help="Message to send"),
    show_context: bool = typer.Option(False, "--context", "-c", help="Show context information used for the response")
):
    """Send a message to the AI professional persona."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        if session.ended_at:
            rprint(f"[bold red]Error:[/bold red] Cannot send message to ended session.")
            raise typer.Exit(1)
        
        # Get the persona for this session
        persona = persona_manager.get_persona(session.persona_id)
        persona_name = persona.name if persona else session.persona_id
        
        # Display the sent message
        console.print(Panel(
            message,
            title="Client Message",
            border_style="green"
        ))
        
        # Send message and get response
        response, context = conversation_handler.send_message(session_id, message, return_context=show_context)
        
        # Display the response
        console.print(Panel(
            response,
            title=f"Response from {persona_name}",
            border_style="blue"
        ))
        
        # Show context if requested
        if show_context and context:
            console.print(Panel(
                json.dumps(context, indent=2),
                title="Context Information",
                border_style="yellow"
            ))
    
    except Exception as e:
        rprint(f"[bold red]Error sending message:[/bold red] {str(e)}")
        raise typer.Exit(1)

@conversation_app.command("history")
def view_history(
    session_id: UUID = typer.Argument(..., help="ID of the session"),
    limit: int = typer.Option(None, "--limit", "-l", help="Maximum number of messages to show"),
    export_file: Optional[Path] = typer.Option(None, "--export", "-e", help="Export conversation to file"),
    format: str = typer.Option("text", "--format", "-f", help="Export format (text, markdown, json)")
):
    """View conversation history for a session."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        # Get the persona for this session
        persona = persona_manager.get_persona(session.persona_id)
        persona_name = persona.name if persona else session.persona_id
        
        # Get messages
        messages = conversation_handler.get_messages(session_id, limit=limit)
        
        if not messages:
            rprint("[yellow]No messages found for this session.[/yellow]")
            return
        
        # If exporting to file
        if export_file:
            if format.lower() == "text":
                with open(export_file, 'w') as f:
                    f.write(f"Conversation with {persona_name} - Session {session_id}\n\n")
                    for msg in messages:
                        sender = "Client" if msg.is_user else persona_name
                        f.write(f"{msg.timestamp} - {sender}:\n")
                        f.write(f"{msg.content}\n\n")
            
            elif format.lower() == "markdown":
                with open(export_file, 'w') as f:
                    f.write(f"# Conversation with {persona_name}\n\n")
                    f.write(f"Session ID: {session_id}\n\n")
                    for msg in messages:
                        sender = "Client" if msg.is_user else persona_name
                        f.write(f"### {sender} ({msg.timestamp})\n\n")
                        f.write(f"{msg.content}\n\n")
            
            elif format.lower() == "json":
                with open(export_file, 'w') as f:
                    json_data = {
                        "session_id": str(session_id),
                        "persona": persona_name,
                        "client": session.client_name,
                        "messages": [
                            {
                                "timestamp": msg.timestamp.isoformat(),
                                "sender": "client" if msg.is_user else "persona",
                                "content": msg.content
                            }
                            for msg in messages
                        ]
                    }
                    json.dump(json_data, f, indent=2)
            
            else:
                rprint(f"[bold red]Error:[/bold red] Unsupported export format: {format}")
                raise typer.Exit(1)
            
            rprint(f"[green]Conversation exported to:[/green] {export_file}")
        
        # Display on console
        else:
            rprint(f"[bold]Conversation History for Session {session_id}[/bold]\n")
            rprint(f"Client: [green]{session.client_name}[/green]")
            rprint(f"Persona: [blue]{persona_name}[/blue]\n")
            
            for msg in messages:
                if msg.is_user:
                    console.print(Panel(
                        msg.content,
                        title=f"Client ({msg.timestamp.strftime('%Y-%m-%d %H:%M')})",
                        border_style="green"
                    ))
                else:
                    console.print(Panel(
                        msg.content,
                        title=f"{persona_name} ({msg.timestamp.strftime('%Y-%m-%d %H:%M')})",
                        border_style="blue"
                    ))
    
    except Exception as e:
        rprint(f"[bold red]Error viewing conversation history:[/bold red] {str(e)}")
        raise typer.Exit(1)

@conversation_app.command("interactive")
def interactive_conversation(
    session_id: UUID = typer.Argument(..., help="ID of the session"),
    markdown: bool = typer.Option(True, help="Render markdown in responses")
):
    """Start an interactive conversation session."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        if session.ended_at:
            rprint(f"[bold red]Error:[/bold red] Cannot start interactive conversation with ended session.")
            raise typer.Exit(1)
        
        # Get the persona for this session
        persona = persona_manager.get_persona(session.persona_id)
        persona_name = persona.name if persona else session.persona_id
        
        rprint(f"[bold green]Starting interactive conversation with {persona_name}[/bold green]")
        rprint(f"[yellow]Type 'exit', 'quit', or press Ctrl+C to end the conversation[/yellow]\n")
        
        # Show the last few messages for context
        last_messages = conversation_handler.get_messages(session_id, limit=3)
        if last_messages:
            rprint("[cyan]Last few messages:[/cyan]")
            for msg in last_messages:
                sender = "You" if msg.is_user else persona_name
                console.print(f"[{'green' if msg.is_user else 'blue'}]{sender}:[/{'green' if msg.is_user else 'blue'}] {msg.content[:50]}...")
            rprint("")
        
        # Interactive loop
        while True:
            try:
                # Get user input
                user_message = typer.prompt("You")
                
                # Check for exit commands
                if user_message.lower() in ["exit", "quit", "bye", "goodbye"]:
                    rprint("[yellow]Ending conversation session.[/yellow]")
                    break
                
                # Send message and get response
                response = conversation_handler.send_message(session_id, user_message)
                
                # Display the response
                if markdown:
                    console.print(f"[blue]{persona_name}:[/blue]")
                    console.print(Markdown(response))
                else:
                    console.print(f"[blue]{persona_name}:[/blue] {response}")
                
                rprint("")  # Add a blank line for readability
            
            except KeyboardInterrupt:
                rprint("\n[yellow]Conversation ended by user.[/yellow]")
                break
    
    except Exception as e:
        rprint(f"[bold red]Error in interactive conversation:[/bold red] {str(e)}")
        raise typer.Exit(1)

@conversation_app.command("export")
def export_conversation(
    session_id: UUID = typer.Argument(..., help="ID of the session"),
    output_file: Path = typer.Argument(..., help="Output file path"),
    format: str = typer.Option("text", "--format", "-f", help="Export format (text, markdown, json, html)"),
    include_metadata: bool = typer.Option(False, "--metadata", "-m", help="Include session metadata in export")
):
    """Export a conversation to a file in various formats."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        # Get the persona for this session
        persona = persona_manager.get_persona(session.persona_id)
        persona_name = persona.name if persona else session.persona_id
        
        # Get all messages
        messages = conversation_handler.get_messages(session_id)
        
        if not messages:
            rprint("[yellow]No messages found for this session.[/yellow]")
            return
        
        # Export based on format
        if format.lower() == "text":
            from smart_steps_ai.analysis.export import export_conversation_to_text
            content = export_conversation_to_text(session, messages, include_metadata)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "markdown":
            from smart_steps_ai.analysis.export import export_conversation_to_markdown
            content = export_conversation_to_markdown(session, messages, include_metadata)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "json":
            from smart_steps_ai.analysis.export import export_conversation_to_json
            content = export_conversation_to_json(session, messages, include_metadata)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "html":
            from smart_steps_ai.analysis.export import export_conversation_to_html
            content = export_conversation_to_html(session, messages, include_metadata)
            with open(output_file, 'w') as f:
                f.write(content)
        
        else:
            rprint(f"[bold red]Error:[/bold red] Unsupported export format: {format}")
            raise typer.Exit(1)
        
        rprint(f"[green]Conversation exported to:[/green] {output_file}")
    
    except Exception as e:
        rprint(f"[bold red]Error exporting conversation:[/bold red] {str(e)}")
        raise typer.Exit(1)
