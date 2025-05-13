"""Console output formatting for the CLI."""

from typing import Any, Dict, List, Optional, Union

import rich.box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Create a console instance
console = Console()


def print_title(title: str) -> None:
    """
    Print a title with decoration.

    Args:
        title (str): Title to print
    """
    console.print(f"\n[bold blue]{title}[/bold blue]")
    console.print("=" * len(title), style="blue")


def print_section(title: str) -> None:
    """
    Print a section title.

    Args:
        title (str): Section title to print
    """
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print("-" * len(title), style="cyan")


def print_success(message: str) -> None:
    """
    Print a success message.

    Args:
        message (str): Success message to print
    """
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """
    Print an error message.

    Args:
        message (str): Error message to print
    """
    console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str) -> None:
    """
    Print a warning message.

    Args:
        message (str): Warning message to print
    """
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str) -> None:
    """
    Print an info message.

    Args:
        message (str): Info message to print
    """
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_session_info(session_info: Dict[str, Any]) -> None:
    """
    Print session information.

    Args:
        session_info (Dict[str, Any]): Session information
    """
    panel = Panel(
        "\n".join([
            f"[bold]Session ID:[/bold] {session_info['id']}",
            f"[bold]Client:[/bold] {session_info['client_name']}",
            f"[bold]Persona:[/bold] {session_info['persona_name']}",
            f"[bold]Type:[/bold] {session_info['session_type']}",
            f"[bold]State:[/bold] {session_info['state']}",
            f"[bold]Created:[/bold] {session_info['created_at']}",
        ]),
        title="Session Information",
        border_style="blue",
    )
    console.print(panel)


def print_message(role: str, content: str, metadata: Optional[Dict[str, str]] = None) -> None:
    """
    Print a conversation message.

    Args:
        role (str): Message role
        content (str): Message content
        metadata (Optional[Dict[str, str]]): Message metadata
    """
    # Format the role
    if role.lower() == "client":
        formatted_role = "[bold green]Client[/bold green]"
    elif role.lower() == "assistant":
        formatted_role = "[bold blue]Assistant[/bold blue]"
    elif role.lower() == "system":
        formatted_role = "[bold yellow]System[/bold yellow]"
    else:
        formatted_role = f"[bold]{role.capitalize()}[/bold]"
    
    # Print the message
    console.print(f"\n{formatted_role}:", style="bold")
    console.print(f"  {content}")
    
    # Print metadata if available
    if metadata:
        metadata_text = []
        if "provider" in metadata:
            metadata_text.append(f"Provider: {metadata['provider']}")
        if "model" in metadata:
            metadata_text.append(f"Model: {metadata['model']}")
        if "tokens_input" in metadata and "tokens_output" in metadata:
            metadata_text.append(f"Tokens: {metadata['tokens_input']} in, {metadata['tokens_output']} out")
        if "latency_ms" in metadata:
            metadata_text.append(f"Latency: {metadata['latency_ms']}ms")
        
        if metadata_text:
            console.print("  [dim]" + ", ".join(metadata_text) + "[/dim]")


def print_conversation(messages: List[Dict[str, Any]]) -> None:
    """
    Print a conversation history.

    Args:
        messages (List[Dict[str, Any]]): List of messages
    """
    for message in messages:
        print_message(
            role=message["role"],
            content=message["content"],
            metadata=message.get("metadata"),
        )


def print_table(
    headers: List[str],
    rows: List[List[Any]],
    title: Optional[str] = None,
    show_lines: bool = False,
) -> None:
    """
    Print a table.

    Args:
        headers (List[str]): Table headers
        rows (List[List[Any]]): Table rows
        title (Optional[str]): Table title
        show_lines (bool): Whether to show lines between rows
    """
    table = Table(
        title=title,
        show_header=True,
        header_style="bold",
        box=rich.box.ROUNDED if show_lines else None,
    )
    
    # Add columns
    for header in headers:
        table.add_column(header)
    
    # Add rows
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    
    console.print(table)


def print_markdown(markdown_text: str) -> None:
    """
    Print markdown text.

    Args:
        markdown_text (str): Markdown text to print
    """
    md = Markdown(markdown_text)
    console.print(md)


def progress_bar(description: str = "Processing") -> Any:
    """
    Create a progress bar.

    Args:
        description (str): Progress bar description

    Returns:
        Any: Progress bar
    """
    return console.status(f"[bold blue]{description}...[/bold blue]")
