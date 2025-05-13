"""
Command-line entry point for the Smart Steps AI module.
"""

import sys
import typer
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Create CLI app
app = typer.Typer(
    name="smart-steps-ai",
    help="Smart Steps AI Professional Persona Module",
    no_args_is_help=True,
)

console = Console()

@app.callback()
def callback():
    """
    Smart Steps AI Professional Persona Module

    A system for providing AI professional personas, session management,
    and analysis capabilities for therapeutic applications.
    """
    pass

@app.command("version")
def version():
    """Display the current version of the Smart Steps AI module."""
    from smart_steps_ai import __version__
    console.print(f"Smart Steps AI v{__version__}")

@app.command("info")
def info():
    """Display information about the Smart Steps AI module."""
    from smart_steps_ai import __version__
    
    console.print(Panel.fit(
        f"[bold]Smart Steps AI v{__version__}[/bold]\n\n"
        "Professional AI persona module for therapeutic applications.\n"
        "Provides configurable personas, session management, and analysis capabilities.",
        title="Smart Steps AI",
        border_style="blue"
    ))

@app.command("run-api")
def run_api():
    """Start the Smart Steps AI API server."""
    from smart_steps_ai.api.main import main
    console.print("[bold green]Starting Smart Steps AI API server...[/bold green]")
    main()

# Import and add other commands as they exist
try:
    # Import commands if they exist
    from smart_steps_ai.cli.commands import (
        session_app,
        conversation_app,
        analysis_app,
        config_app,
        persona_app,
        performance_app
    )
    
    # Add subcommands
    app.add_typer(session_app, name="session")
    app.add_typer(conversation_app, name="conversation")
    app.add_typer(analysis_app, name="analysis")
    app.add_typer(config_app, name="config")
    app.add_typer(persona_app, name="persona")
    app.add_typer(performance_app, name="performance")
except ImportError as e:
    console.print(f"[yellow]Note: Some CLI commands are not available: {e}[/yellow]")

if __name__ == "__main__":
    app()
