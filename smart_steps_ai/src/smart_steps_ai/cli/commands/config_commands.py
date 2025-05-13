"""Configuration commands for the CLI."""

import json
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.prompt import Confirm, Prompt

from ...config import get_config_manager
from ...utils import get_logger
from ..console import console, print_error, print_info, print_success, print_table, print_title

# Initialize logger
logger = get_logger(__name__)


def register(app: typer.Typer) -> None:
    """
    Register commands with the app.

    Args:
        app (typer.Typer): The typer app
    """
    
    @app.command("show")
    def show_config(
        section: Optional[str] = typer.Argument(
            None, help="Section to show (e.g., 'app', 'paths', 'ai')"
        ),
        format: str = typer.Option(
            "table", "--format", "-f", help="Output format (table, json)"
        ),
    ) -> None:
        """
        Show the current configuration.
        """
        config_manager = get_config_manager()
        config = config_manager.get_config()
        
        if section:
            if not hasattr(config, section):
                print_error(f"Section not found: {section}")
                raise typer.Exit(1)
            
            # Get the section
            section_data = getattr(config, section)
            section_dict = section_data.model_dump()
            
            # Print the section
            print_title(f"Configuration: {section}")
            
            if format == "json":
                console.print(json.dumps(section_dict, indent=2))
            else:
                # Convert to list of rows
                rows = [[key, str(value)] for key, value in section_dict.items()]
                print_table(["Key", "Value"], rows)
        else:
            # Print the complete configuration
            print_title("Configuration")
            
            if format == "json":
                console.print(json.dumps(config.model_dump(), indent=2))
            else:
                # Print each section
                for section_name in ["app", "paths", "ai", "memory", "session", "analysis", "api"]:
                    section_data = getattr(config, section_name)
                    section_dict = section_data.model_dump()
                    
                    print_info(f"\n[bold]{section_name.upper()}[/bold]")
                    rows = [[key, str(value)] for key, value in section_dict.items()]
                    print_table(["Key", "Value"], rows)
    
    @app.command("set")
    def set_config(
        key: str = typer.Argument(..., help="Configuration key (e.g., 'app.log_level')"),
        value: str = typer.Argument(..., help="Value to set"),
    ) -> None:
        """
        Set a configuration value.
        """
        config_manager = get_config_manager()
        config_dict = config_manager.get_config().model_dump()
        
        # Split the key into sections
        sections = key.split(".")
        
        # Validate the key
        if len(sections) < 2:
            print_error(f"Invalid key format: {key} (should be 'section.key')")
            raise typer.Exit(1)
        
        # Check if the section exists
        if sections[0] not in config_dict:
            print_error(f"Section not found: {sections[0]}")
            raise typer.Exit(1)
        
        # Navigate to the target section
        target = config_dict
        for section in sections[:-1]:
            if section not in target:
                print_error(f"Section not found: {section}")
                raise typer.Exit(1)
            target = target[section]
        
        # Check if the key exists
        if sections[-1] not in target:
            print_error(f"Key not found: {sections[-1]}")
            raise typer.Exit(1)
        
        # Get the current value
        current_value = target[sections[-1]]
        print_info(f"Current value: {current_value}")
        
        # Convert the value to the appropriate type
        if isinstance(current_value, bool):
            value = value.lower() in ("true", "1", "yes", "y", "on", "t")
        elif isinstance(current_value, int):
            try:
                value = int(value)
            except ValueError:
                print_error(f"Invalid integer value: {value}")
                raise typer.Exit(1)
        elif isinstance(current_value, float):
            try:
                value = float(value)
            except ValueError:
                print_error(f"Invalid float value: {value}")
                raise typer.Exit(1)
        
        # Update the value
        target[sections[-1]] = value
        
        # Create a new configuration
        config_manager._set_nested_value(config_dict, sections, value)
        
        # Save to environment variable
        env_key = "SMART_STEPS_" + "_".join(sections).upper()
        print_info(f"Setting environment variable: {env_key}={value}")
        
        # Confirm success
        print_success(f"Configuration updated: {key} = {value}")
    
    @app.command("save")
    def save_config(
        output_file: Path = typer.Argument(
            ..., help="Path to save the configuration file"
        ),
        overwrite: bool = typer.Option(
            False, "--overwrite", "-o", help="Overwrite existing file"
        ),
    ) -> None:
        """
        Save the current configuration to a file.
        """
        # Check if the file exists
        if output_file.exists() and not overwrite:
            if not Confirm.ask(f"File exists: {output_file}. Overwrite?"):
                print_info("Operation cancelled")
                raise typer.Exit(0)
        
        # Save the configuration
        config_manager = get_config_manager()
        success = config_manager.save_config(output_file)
        
        if success:
            print_success(f"Configuration saved to {output_file}")
        else:
            print_error(f"Failed to save configuration to {output_file}")
            raise typer.Exit(1)
    
    @app.command("load")
    def load_config(
        input_file: Path = typer.Argument(
            ..., help="Path to the configuration file to load"
        ),
    ) -> None:
        """
        Load a configuration file.
        """
        # Check if the file exists
        if not input_file.exists():
            print_error(f"File not found: {input_file}")
            raise typer.Exit(1)
        
        # Load the configuration
        config_manager = get_config_manager(config_path=input_file, force_reload=True)
        
        print_success(f"Configuration loaded from {input_file}")
