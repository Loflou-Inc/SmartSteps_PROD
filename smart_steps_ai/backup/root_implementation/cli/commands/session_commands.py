"""
Session management commands for the Smart Steps AI CLI.

Provides commands for creating, listing, viewing, and managing
therapeutic sessions with AI professional personas.
"""

import typer
import os
import json
from typing import Optional, List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from pathlib import Path
from uuid import UUID

from smart_steps_ai.core.session_manager import SessionManager
from smart_steps_ai.core.persona_manager import PersonaManager
from smart_steps_ai.persistence.file_storage import FileStorage

session_app = typer.Typer(
    help="Manage therapy sessions",
    no_args_is_help=True,
)

console = Console()
session_manager = SessionManager()
persona_manager = PersonaManager()

@session_app.callback()
def callback():
    """
    Manage therapy sessions with AI professional personas.
    
    Create, list, view, and export sessions with different professional personas.
    """
    pass

@session_app.command("create")
def create_session(
    client_name: str = typer.Option(..., "--name", "-n", help="Name of the client"),
    persona_id: Optional[str] = typer.Option(None, "--persona", "-p", help="ID of the professional persona"),
    notes: Optional[str] = typer.Option(None, "--notes", help="Initial session notes"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags to associate with the session")
):
    """Create a new therapy session."""
    try:
        # If no persona ID is provided, list available personas and prompt for selection
        if not persona_id:
            personas = persona_manager.list_personas()
            
            table = Table(title="Available Professional Personas")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Type", style="yellow")
            
            for p in personas:
                table.add_row(p.id, p.name, p.type)
            
            console.print(table)
            
            persona_id = typer.prompt("Select persona ID")
        
        # Create the session
        session = session_manager.create_session(
            client_name=client_name,
            persona_id=persona_id,
            notes=notes or "",
            tags=tags or []
        )
        
        rprint(f"[green]Session created successfully![/green]")
        rprint(f"Session ID: [cyan]{session.id}[/cyan]")
        rprint(f"Client: [yellow]{session.client_name}[/yellow]")
        rprint(f"Persona: [yellow]{session.persona_id}[/yellow]")
        rprint(f"Created: [yellow]{session.created_at}[/yellow]")
        
        return session.id
    
    except Exception as e:
        rprint(f"[bold red]Error creating session:[/bold red] {str(e)}")
        raise typer.Exit(1)

@session_app.command("list")
def list_sessions(
    client: Optional[str] = typer.Option(None, "--client", "-c", help="Filter by client name"),
    persona: Optional[str] = typer.Option(None, "--persona", "-p", help="Filter by persona ID"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of sessions to show"),
    all_sessions: bool = typer.Option(False, "--all", "-a", help="Show all sessions")
):
    """List therapy sessions."""
    try:
        sessions = session_manager.list_sessions(
            client_name=client,
            persona_id=persona,
            tag=tag,
            limit=None if all_sessions else limit
        )
        
        if not sessions:
            rprint("[yellow]No sessions found.[/yellow]")
            return
        
        table = Table(title="Therapy Sessions")
        table.add_column("ID", style="cyan")
        table.add_column("Client", style="green")
        table.add_column("Persona", style="yellow")
        table.add_column("Created", style="magenta")
        table.add_column("Last Activity", style="blue")
        table.add_column("Messages", style="red")
        table.add_column("Status", style="green")
        
        for session in sessions:
            persona = persona_manager.get_persona(session.persona_id)
            persona_name = persona.name if persona else session.persona_id
            
            # Calculate message count
            message_count = len(session.messages) if hasattr(session, 'messages') else 0
            
            # Determine status
            status = "Active" if not session.ended_at else "Ended"
            
            table.add_row(
                str(session.id)[:8] + "...",  # Truncated ID for readability
                session.client_name,
                persona_name,
                session.created_at.strftime("%Y-%m-%d %H:%M"),
                session.updated_at.strftime("%Y-%m-%d %H:%M") if session.updated_at else "-",
                str(message_count),
                status
            )
        
        console.print(table)
    
    except Exception as e:
        rprint(f"[bold red]Error listing sessions:[/bold red] {str(e)}")
        raise typer.Exit(1)

@session_app.command("info")
def session_info(
    session_id: UUID = typer.Argument(..., help="ID of the session"),
    show_messages: bool = typer.Option(False, "--messages", "-m", help="Show session messages")
):
    """Show detailed information about a session."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        persona = persona_manager.get_persona(session.persona_id)
        persona_name = persona.name if persona else session.persona_id
        
        console.print(Panel.fit(
            f"[bold]Session Details[/bold]\n\n"
            f"[cyan]ID:[/cyan] {session.id}\n"
            f"[cyan]Client:[/cyan] {session.client_name}\n"
            f"[cyan]Persona:[/cyan] {persona_name}\n"
            f"[cyan]Created:[/cyan] {session.created_at}\n"
            f"[cyan]Last Activity:[/cyan] {session.updated_at or '-'}\n"
            f"[cyan]Status:[/cyan] {'Active' if not session.ended_at else 'Ended'}\n"
            f"[cyan]Tags:[/cyan] {', '.join(session.tags) if session.tags else 'None'}\n"
            f"[cyan]Notes:[/cyan] {session.notes or 'None'}",
            title=f"Session {session_id}",
            border_style="blue"
        ))
        
        # Show messages if requested
        if show_messages and hasattr(session, 'messages') and session.messages:
            table = Table(title="Session Messages")
            table.add_column("Time", style="cyan")
            table.add_column("From", style="green")
            table.add_column("Message", style="white")
            
            for msg in session.messages:
                table.add_row(
                    msg.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "Client" if msg.is_user else persona_name,
                    msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                )
            
            console.print(table)
    
    except Exception as e:
        rprint(f"[bold red]Error getting session info:[/bold red] {str(e)}")
        raise typer.Exit(1)

@session_app.command("export")
def export_session(
    session_id: UUID = typer.Argument(..., help="ID of the session to export"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, markdown, text, html, csv)")
):
    """Export a session to a file."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        # If no output file specified, use a default based on session ID and format
        if not output_file:
            output_file = Path(f"session_{session_id}.{format}")
        
        # Export based on format
        if format.lower() == "json":
            session_data = session.to_dict() if hasattr(session, 'to_dict') else session.__dict__
            with open(output_file, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
        
        elif format.lower() == "markdown":
            from smart_steps_ai.analysis.export import export_to_markdown
            content = export_to_markdown(session)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "text":
            from smart_steps_ai.analysis.export import export_to_text
            content = export_to_text(session)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "html":
            from smart_steps_ai.analysis.export import export_to_html
            content = export_to_html(session)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "csv":
            from smart_steps_ai.analysis.export import export_to_csv
            content = export_to_csv(session)
            with open(output_file, 'w') as f:
                f.write(content)
        
        else:
            rprint(f"[bold red]Error:[/bold red] Unsupported export format: {format}")
            raise typer.Exit(1)
        
        rprint(f"[green]Session exported successfully to:[/green] {output_file}")
    
    except Exception as e:
        rprint(f"[bold red]Error exporting session:[/bold red] {str(e)}")
        raise typer.Exit(1)

@session_app.command("end")
def end_session(
    session_id: UUID = typer.Argument(..., help="ID of the session to end"),
    summary: Optional[str] = typer.Option(None, "--summary", "-s", help="Session summary"),
    generate_summary: bool = typer.Option(False, "--generate", "-g", help="Generate summary automatically")
):
    """End an active therapy session."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        if session.ended_at:
            rprint(f"[yellow]Warning:[/yellow] Session is already ended.")
            raise typer.Exit()
        
        # Generate summary if requested
        if generate_summary:
            from smart_steps_ai.analysis.insights import generate_session_summary
            summary = generate_session_summary(session)
        
        # End the session
        session_manager.end_session(session_id, summary=summary)
        
        rprint(f"[green]Session ended successfully![/green]")
        if summary:
            rprint(f"[cyan]Summary:[/cyan] {summary}")
    
    except Exception as e:
        rprint(f"[bold red]Error ending session:[/bold red] {str(e)}")
        raise typer.Exit(1)

@session_app.command("delete")
def delete_session(
    session_id: UUID = typer.Argument(..., help="ID of the session to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation")
):
    """Delete a therapy session."""
    try:
        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete session {session_id}? This cannot be undone.")
            if not confirm:
                rprint("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit()
        
        session_manager.delete_session(session_id)
        rprint(f"[green]Session deleted successfully![/green]")
    
    except Exception as e:
        rprint(f"[bold red]Error deleting session:[/bold red] {str(e)}")
        raise typer.Exit(1)
