"""
Command-line entry point for the Smart Steps AI module.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

# Import commands
from smart_steps_ai.cli.commands import (
    session_app,
    conversation_app,
    analysis_app,
    config_app,
    persona_app,
    performance_app
)

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

# Add subcommands
app.add_typer(session_app, name="session")
app.add_typer(conversation_app, name="conversation")
app.add_typer(analysis_app, name="analysis")
app.add_typer(config_app, name="config")
app.add_typer(persona_app, name="persona")
app.add_typer(performance_app, name="performance")

if __name__ == "__main__":
    app()
