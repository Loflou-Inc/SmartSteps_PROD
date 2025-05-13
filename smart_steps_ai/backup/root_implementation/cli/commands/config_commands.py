"""
Configuration commands for the Smart Steps AI CLI.

Provides commands for managing configuration settings,
viewing current configurations, and modifying values.
"""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from pathlib import Path

from smart_steps_ai.core.config_manager import ConfigManager

config_app = typer.Typer(
    help="Manage configuration settings",
    no_args_is_help=True,
)

console = Console()
config_manager = ConfigManager()

@config_app.callback()
def callback():
    """
    Manage configuration settings for Smart Steps AI.
    
    View, edit, and reset configuration values for the system.
    """
    pass

@config_app.command("list")
def list_config(
    section: Optional[str] = typer.Option(None, help="Filter by configuration section")
):
    """List all configuration settings."""
    config = config_manager.get_config()
    
    if section and section not in config:
        rprint(f"[bold red]Error:[/bold red] Section '{section}' not found in configuration.")
        raise typer.Exit(1)
    
    table = Table(title="Smart Steps AI Configuration")
    table.add_column("Section", style="cyan")
    table.add_column("Key", style="green")
    table.add_column("Value", style="yellow")
    
    sections = [section] if section else config.keys()
    
    for sect in sections:
        if isinstance(config[sect], dict):
            for key, value in config[sect].items():
                table.add_row(sect, key, str(value))
        else:
            table.add_row(sect, "", str(config[sect]))
    
    console.print(table)

@config_app.command("get")
def get_config(
    section: str = typer.Argument(..., help="Configuration section"),
    key: Optional[str] = typer.Argument(None, help="Configuration key")
):
    """Get a specific configuration value."""
    config = config_manager.get_config()
    
    if section not in config:
        rprint(f"[bold red]Error:[/bold red] Section '{section}' not found in configuration.")
        raise typer.Exit(1)
    
    if key:
        if key not in config[section]:
            rprint(f"[bold red]Error:[/bold red] Key '{key}' not found in section '{section}'.")
            raise typer.Exit(1)
        
        value = config[section][key]
        rprint(f"[cyan]{section}[/cyan].[green]{key}[/green] = [yellow]{value}[/yellow]")
    else:
        # Print the entire section
        table = Table(title=f"Configuration Section: {section}")
        table.add_column("Key", style="green")
        table.add_column("Value", style="yellow")
        
        for k, v in config[section].items():
            table.add_row(k, str(v))
        
        console.print(table)

@config_app.command("set")
def set_config(
    section: str = typer.Argument(..., help="Configuration section"),
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="New value to set")
):
    """Set a configuration value."""
    try:
        # Try to interpret the value as appropriate type (int, float, bool, etc.)
        if value.lower() == "true":
            typed_value = True
        elif value.lower() == "false":
            typed_value = False
        elif value.isdigit():
            typed_value = int(value)
        elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
            typed_value = float(value)
        else:
            typed_value = value
        
        config_manager.set_value(section, key, typed_value)
        rprint(f"[green]Configuration updated:[/green] [cyan]{section}[/cyan].[green]{key}[/green] = [yellow]{typed_value}[/yellow]")
    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@config_app.command("reset")
def reset_config(
    section: Optional[str] = typer.Option(None, help="Reset only a specific section"),
    force: bool = typer.Option(False, "--force", "-f", help="Don't ask for confirmation")
):
    """Reset configuration to default values."""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to reset {'the specified section' if section else 'all'} configuration to defaults?")
        if not confirm:
            rprint("[yellow]Operation cancelled.[/yellow]")
            raise typer.Exit()
    
    try:
        if section:
            config_manager.reset_section(section)
            rprint(f"[green]Section '{section}' reset to default values.[/green]")
        else:
            config_manager.reset_all()
            rprint(f"[green]All configuration reset to default values.[/green]")
    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@config_app.command("export")
def export_config(
    output_file: Path = typer.Argument(..., help="Path to save the configuration file"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file")
):
    """Export current configuration to a file."""
    if output_file.exists() and not force:
        confirm = typer.confirm(f"File {output_file} exists. Overwrite?")
        if not confirm:
            rprint("[yellow]Operation cancelled.[/yellow]")
            raise typer.Exit()
    
    try:
        config_manager.export_config(str(output_file))
        rprint(f"[green]Configuration exported to:[/green] {output_file}")
    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@config_app.command("import")
def import_config(
    input_file: Path = typer.Argument(..., help="Path to the configuration file to import"),
    force: bool = typer.Option(False, "--force", "-f", help="Don't ask for confirmation")
):
    """Import configuration from a file."""
    if not input_file.exists():
        rprint(f"[bold red]Error:[/bold red] File {input_file} does not exist.")
        raise typer.Exit(1)
    
    if not force:
        confirm = typer.confirm("This will overwrite current configuration. Continue?")
        if not confirm:
            rprint("[yellow]Operation cancelled.[/yellow]")
            raise typer.Exit()
    
    try:
        config_manager.import_config(str(input_file))
        rprint(f"[green]Configuration imported from:[/green] {input_file}")
    except Exception as e:
        rprint(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)
