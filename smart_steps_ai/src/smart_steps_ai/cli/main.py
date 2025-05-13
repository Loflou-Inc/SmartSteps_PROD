"""Main CLI application for Smart Steps AI."""

import os
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.theme import Theme
from typing import Optional

from ..config import get_config_manager
from ..utils import get_logger, load_dotenv

# Create custom theme for rich console output
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "title": "bold blue",
    "prompt": "bold cyan",
    "input": "green",
    "command": "magenta",
    "param": "cyan",
    "path": "yellow",
    "highlight": "bold white on blue",
})

# Create console for rich output
console = Console(theme=custom_theme)

# Create logger
logger = get_logger("cli")

# Create Typer application
app = typer.Typer(
    name="smart-steps-ai",
    help="CLI for Smart Steps AI Professional Persona module",
    add_completion=True,
)

# Callback for CLI initialization
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Path to configuration file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    version: bool = typer.Option(
        False, "--version", help="Show the version and exit"
    ),
) -> None:
    """
    Smart Steps AI Professional Persona CLI.
    
    This tool provides a command-line interface for interacting with the
    Smart Steps AI Professional Persona module, allowing management of
    personas, sessions, and conversations.
    """
    # Load environment variables
    load_dotenv()
    
    # Set up configuration
    try:
        config_manager = get_config_manager(config_path=config_file)
        config = config_manager.get_config()
    except Exception as e:
        console.print(f"[error]Error loading configuration: {str(e)}")
        sys.exit(1)
    
    # Store config and console in context
    ctx.obj = {
        "config": config,
        "console": console,
        "verbose": verbose,
    }
    
    # Show version if requested
    if version:
        from .. import __version__
        console.print(f"Smart Steps AI v{__version__}")
        raise typer.Exit()
    
    # If no subcommand provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()
