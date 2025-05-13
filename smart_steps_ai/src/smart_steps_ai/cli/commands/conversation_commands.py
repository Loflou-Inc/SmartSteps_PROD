"""Conversation commands for the Smart Steps AI CLI."""

import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, Confirm

from ...session import ConversationHandler, SessionManager, MessageRole
from ...config import get_config_manager
from ...utils import get_logger
from ..main import get_console

# Create Typer app for conversation commands
app = typer.Typer(help="Manage conversations with professional personas")

# Get console for rich output
console = get_console()

# Get logger
logger = get_logger(__name__)

# Get configuration
config = get_config_manager().get()

# Initialize managers
session_manager = SessionManager()
conversation_handler = ConversationHandler()


@app.command("send")
def send_message(
    session_id: str = typer.Option(
        ..., "--session", "-s", help="ID of the session to send the message to"
    ),
    message: str = typer.Option(
        ..., "--message", "-m", help="Message content to send"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", "-p", help="AI provider to use for the response"
    ),
):
    """
    Send a message in a session and get a response.
    """
    try:
        # Send the message
        client_msg, assistant_msg = conversation_handler.send_message(
            session_id=session_id,
            message=message,
            provider_name=provider,
        )
        
        if not client_msg or not assistant_msg:
            console.print("[bold red]Failed to send message or get response[/bold red]")
            return
        
        # Display the exchange
        console.print(Panel(
            client_msg.content,
            title="[bold blue]Client[/bold blue]",
            border_style="blue",
            box=box.ROUNDED,
            width=80,
        ))
        
        console.print(Panel(
            assistant_msg.content,
            title="[bold green]Assistant[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            width=80,
        ))
        
        # Display metadata
        if assistant_msg.metadata:
            provider_name = assistant_msg.metadata.get("provider", "unknown")
            model = assistant_msg.metadata.get("model", "unknown")
            tokens_in = assistant_msg.metadata.get("tokens_input", "?")
            tokens_out = assistant_msg.metadata.get("tokens_output", "?")
            latency = assistant_msg.metadata.get("latency_ms", "?")
            
            console.print(f"[dim]Provider: {provider_name}, Model: {model}[/dim]")
            console.print(f"[dim]Tokens: {tokens_in} in, {tokens_out} out, Latency: {latency}ms[/dim]")
    
    except Exception as e:
        console.print(f"[bold red]Error sending message:[/bold red] {str(e)}")
        logger.error(f"Error sending message: {str(e)}")


@app.command("interactive")
def interactive_conversation(
    session_id: Optional[str] = typer.Option(
        None, "--session", "-s", help="ID of an existing session (creates new if not provided)"
    ),
    client_name: Optional[str] = typer.Option(
        None, "--client", "-c", help="Name of the client (required for new sessions)"
    ),
    persona_name: Optional[str] = typer.Option(
        None, "--persona", "-p", help="Name of the persona to use"
    ),
    session_type: str = typer.Option(
        "standard", "--type", "-t", help="Type of session (standard, initial, followup, etc.)"
    ),
    provider: Optional[str] = typer.Option(
        None, "--provider", help="AI provider to use (e.g., mock, anthropic)"
    ),
):
    """
    Start an interactive conversation with a professional persona.
    """
    try:
        # Check if we need to create a new session
        if not session_id:
            if not client_name:
                console.print("[bold red]Client name is required for new sessions[/bold red]")
                client_name = Prompt.ask("[bold]Client name[/bold]")
            
            # Create a new session
            session_info = conversation_handler.create_new_session(
                client_name=client_name,
                persona_name=persona_name,
                session_type=session_type,
                provider_name=provider,
            )
            
            if not session_info:
                console.print("[bold red]Failed to create session[/bold red]")
                return
            
            session_id = session_info["id"]
            
            console.print(Panel(
                f"[bold]Client:[/bold] {session_info['client_name']}\n"
                f"[bold]Persona:[/bold] {session_info['persona_name']}\n"
                f"[bold]Type:[/bold] {session_info['session_type']}\n"
                f"[bold]Created:[/bold] {session_info['created_at']}\n"
                f"[bold]State:[/bold] {session_info['state']}",
                title=f"New Session Created: {session_id}",
                border_style="green",
                box=box.ROUNDED,
            ))
        
        # Verify the session exists
        session = session_manager.get_session(session_id)
        if not session:
            console.print(f"[bold red]Session not found:[/bold red] {session_id}")
            return
        
        # Start interactive loop
        _start_interactive_conversation(session_id, provider)
    
    except Exception as e:
        console.print(f"[bold red]Error in interactive conversation:[/bold red] {str(e)}")
        logger.error(f"Error in interactive conversation: {str(e)}")


@app.command("history")
def view_history(
    session_id: str = typer.Argument(
        ..., help="ID of the session to view history for"
    ),
    limit: int = typer.Option(
        None, "--limit", "-l", help="Maximum number of messages to show"
    ),
    format: str = typer.Option(
        "rich", "--format", "-f", help="Display format (rich, text, simple)"
    ),
):
    """
    View the conversation history for a session.
    """
    try:
        # Get the conversation history
        history = conversation_handler.get_conversation_history(session_id)
        
        if not history:
            console.print("[yellow]No conversation history found[/yellow]")
            return
        
        # Apply limit if specified
        if limit is not None and limit > 0:
            history = history[-limit:]
        
        # Display history based on format
        if format.lower() == "text":
            for message in history:
                role = message["role"].upper()
                content = message["content"]
                timestamp = datetime.fromisoformat(message["timestamp"]).strftime("%H:%M:%S")
                console.print(f"{role} ({timestamp}):\n{content}\n")
        
        elif format.lower() == "simple":
            for message in history:
                role = message["role"].upper()
                content = message["content"]
                console.print(f"{role}: {content}")
        
        else:  # Default to rich
            for message in history:
                role = message["role"].upper()
                content = message["content"]
                timestamp = datetime.fromisoformat(message["timestamp"]).strftime("%H:%M:%S")
                
                if role == "ASSISTANT":
                    console.print(Panel(
                        content,
                        title=f"{role} ({timestamp})",
                        border_style="green",
                        box=box.ROUNDED,
                        width=80,
                    ))
                elif role == "CLIENT":
                    console.print(Panel(
                        content,
                        title=f"{role} ({timestamp})",
                        border_style="blue",
                        box=box.ROUNDED,
                        width=80,
                    ))
                else:
                    console.print(Panel(
                        content,
                        title=f"{role} ({timestamp})",
                        border_style="yellow",
                        box=box.ROUNDED,
                        width=80,
                    ))
    
    except Exception as e:
        console.print(f"[bold red]Error viewing history:[/bold red] {str(e)}")
        logger.error(f"Error viewing history: {str(e)}")


def _start_interactive_conversation(session_id: str, provider_name: Optional[str] = None):
    """Start an interactive conversation session."""
    console.print("\n[bold]Starting interactive conversation...[/bold]")
    console.print("[italic]Type 'exit' or 'quit' to end the conversation[/italic]\n")
    
    # Show conversation history
    history = conversation_handler.get_conversation_history(session_id)
    
    if history:
        console.print("[bold]Conversation History:[/bold]")
        for message in history:
            role = message["role"].upper()
            content = message["content"]
            
            if role == "ASSISTANT":
                console.print(Panel(
                    content,
                    title="[bold green]AI[/bold green]",
                    border_style="green",
                    box=box.ROUNDED,
                    width=80,
                ))
            elif role == "CLIENT":
                console.print(Panel(
                    content,
                    title="[bold blue]You[/bold blue]",
                    border_style="blue",
                    box=box.ROUNDED,
                    width=80,
                ))
            else:
                console.print(Panel(
                    content,
                    title=role,
                    border_style="yellow",
                    box=box.ROUNDED,
                    width=80,
                ))
    
    # Enter interactive loop
    while True:
        # Get user input
        user_message = Prompt.ask("\n[bold blue]You[/bold blue]")
        
        # Check for exit command
        if user_message.lower() in ["exit", "quit", "bye", "goodbye"]:
            if Confirm.ask("End the conversation?"):
                console.print("[green]Conversation ended[/green]")
                break
            else:
                continue
        
        # Send message to AI
        client_msg, assistant_msg = conversation_handler.send_message(
            session_id=session_id,
            message=user_message,
            provider_name=provider_name,
        )
        
        # Check for errors
        if not assistant_msg:
            console.print("[bold red]Error getting response from AI[/bold red]")
            continue
        
        # Display AI response
        console.print(Panel(
            assistant_msg.content,
            title="[bold green]AI[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            width=80,
        ))
        
        # Display metadata
        if assistant_msg.metadata:
            provider = assistant_msg.metadata.get("provider", "unknown")
            model = assistant_msg.metadata.get("model", "unknown")
            tokens_in = assistant_msg.metadata.get("tokens_input", "?")
            tokens_out = assistant_msg.metadata.get("tokens_output", "?")
            
            console.print(f"[dim]Provider: {provider}, Model: {model}, Tokens: {tokens_in} in, {tokens_out} out[/dim]")


if __name__ == "__main__":
    app()
