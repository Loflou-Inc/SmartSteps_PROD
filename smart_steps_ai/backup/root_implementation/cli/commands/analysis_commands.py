"""
Analysis commands for the Smart Steps AI CLI.

Provides commands for analyzing sessions, generating insights,
creating reports, and visualizing progress data.
"""

import typer
import json
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint
from pathlib import Path
from uuid import UUID
from datetime import datetime, timedelta

from smart_steps_ai.core.session_manager import SessionManager
from smart_steps_ai.core.persona_manager import PersonaManager
from smart_steps_ai.analysis.insights import (
    generate_session_insights,
    generate_progress_report,
    extract_key_themes,
    analyze_sentiment_trends
)

analysis_app = typer.Typer(
    help="Analyze therapy sessions and generate reports",
    no_args_is_help=True,
)

console = Console()
session_manager = SessionManager()
persona_manager = PersonaManager()

@analysis_app.callback()
def callback():
    """
    Analyze therapy sessions and generate reports.
    
    Generate insights, identify patterns, and create various
    reports based on session content and progress data.
    """
    pass

@analysis_app.command("insights")
def generate_insights(
    session_id: UUID = typer.Argument(..., help="ID of the session to analyze"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for the insights"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, markdown, json, html)"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Generate detailed insights")
):
    """Generate insights from a therapy session."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        # Get the persona for this session
        persona = persona_manager.get_persona(session.persona_id)
        persona_name = persona.name if persona else session.persona_id
        
        rprint(f"[cyan]Generating insights for session {session_id}...[/cyan]")
        
        # Generate insights
        insights = generate_session_insights(session, detailed=detailed)
        
        if not insights:
            rprint("[yellow]No significant insights generated for this session.[/yellow]")
            return
        
        # Output to file if specified
        if output_file:
            if format.lower() == "text":
                with open(output_file, 'w') as f:
                    f.write(f"Session Insights - {session_id}\n")
                    f.write(f"Client: {session.client_name}\n")
                    f.write(f"Persona: {persona_name}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    
                    for category, items in insights.items():
                        f.write(f"{category}:\n")
                        for item in items:
                            f.write(f"- {item}\n")
                        f.write("\n")
            
            elif format.lower() == "markdown":
                with open(output_file, 'w') as f:
                    f.write(f"# Session Insights - {session_id}\n\n")
                    f.write(f"**Client:** {session.client_name}\n\n")
                    f.write(f"**Persona:** {persona_name}\n\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    
                    for category, items in insights.items():
                        f.write(f"## {category}\n\n")
                        for item in items:
                            f.write(f"* {item}\n")
                        f.write("\n")
            
            elif format.lower() == "json":
                with open(output_file, 'w') as f:
                    json_data = {
                        "session_id": str(session_id),
                        "client": session.client_name,
                        "persona": persona_name,
                        "date": datetime.now().isoformat(),
                        "insights": insights
                    }
                    json.dump(json_data, f, indent=2)
            
            elif format.lower() == "html":
                from smart_steps_ai.analysis.export import export_insights_to_html
                content = export_insights_to_html(session, insights)
                with open(output_file, 'w') as f:
                    f.write(content)
            
            else:
                rprint(f"[bold red]Error:[/bold red] Unsupported output format: {format}")
                raise typer.Exit(1)
            
            rprint(f"[green]Insights saved to:[/green] {output_file}")
        
        # Display on console
        else:
            console.print(Panel(
                f"[bold]Session Insights[/bold]\n"
                f"Client: {session.client_name}\n"
                f"Persona: {persona_name}\n",
                title=f"Session {session_id}",
                border_style="blue"
            ))
            
            for category, items in insights.items():
                rprint(f"[bold cyan]{category}:[/bold cyan]")
                for item in items:
                    rprint(f"  • [yellow]{item}[/yellow]")
                rprint("")
    
    except Exception as e:
        rprint(f"[bold red]Error generating insights:[/bold red] {str(e)}")
        raise typer.Exit(1)

@analysis_app.command("themes")
def extract_themes(
    session_id: UUID = typer.Argument(..., help="ID of the session to analyze"),
    count: int = typer.Option(5, "--count", "-c", help="Number of themes to extract"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for the themes")
):
    """Extract key themes from session conversations."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        rprint(f"[cyan]Extracting key themes from session {session_id}...[/cyan]")
        
        # Extract themes
        themes = extract_key_themes(session, count=count)
        
        if not themes:
            rprint("[yellow]No significant themes identified for this session.[/yellow]")
            return
        
        # Output to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"Key Themes - Session {session_id}\n")
                f.write(f"Client: {session.client_name}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                
                for theme, score in themes:
                    f.write(f"{theme} (Relevance: {score:.2f})\n")
            
            rprint(f"[green]Themes saved to:[/green] {output_file}")
        
        # Display on console
        else:
            table = Table(title=f"Key Themes - Session {session_id}")
            table.add_column("Theme", style="cyan")
            table.add_column("Relevance", style="yellow")
            
            for theme, score in themes:
                table.add_row(theme, f"{score:.2f}")
            
            console.print(table)
    
    except Exception as e:
        rprint(f"[bold red]Error extracting themes:[/bold red] {str(e)}")
        raise typer.Exit(1)

@analysis_app.command("sentiment")
def analyze_sentiment(
    session_id: UUID = typer.Argument(..., help="ID of the session to analyze"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for sentiment analysis"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="Generate visualization")
):
    """Analyze sentiment trends in a session."""
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
            raise typer.Exit(1)
        
        rprint(f"[cyan]Analyzing sentiment in session {session_id}...[/cyan]")
        
        # Analyze sentiment
        sentiment_data = analyze_sentiment_trends(session)
        
        if not sentiment_data:
            rprint("[yellow]Not enough data for sentiment analysis in this session.[/yellow]")
            return
        
        # Output to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"Sentiment Analysis - Session {session_id}\n")
                f.write(f"Client: {session.client_name}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                
                f.write("Overall Sentiment:\n")
                f.write(f"- Average: {sentiment_data['overall']['average']:.2f}\n")
                f.write(f"- Trend: {sentiment_data['overall']['trend']}\n\n")
                
                f.write("Sentiment Progression:\n")
                for entry in sentiment_data['progression']:
                    f.write(f"- {entry['position']}: {entry['score']:.2f} ({entry['label']})\n")
            
            rprint(f"[green]Sentiment analysis saved to:[/green] {output_file}")
        
        # Visualize if requested
        if visualize:
            try:
                from smart_steps_ai.analysis.visualization import create_sentiment_chart
                chart_path = Path(f"sentiment_{session_id}.png")
                create_sentiment_chart(sentiment_data, str(chart_path))
                rprint(f"[green]Sentiment visualization saved to:[/green] {chart_path}")
            except ImportError:
                rprint("[yellow]Visualization requires matplotlib to be installed.[/yellow]")
        
        # Display on console
        if not output_file or not visualize:
            console.print(Panel(
                f"[bold]Overall Sentiment:[/bold]\n"
                f"Average: {sentiment_data['overall']['average']:.2f}\n"
                f"Trend: {sentiment_data['overall']['trend']}",
                title=f"Sentiment Analysis - Session {session_id}",
                border_style="blue"
            ))
            
            table = Table(title="Sentiment Progression")
            table.add_column("Position", style="cyan")
            table.add_column("Score", style="yellow")
            table.add_column("Label", style="green")
            
            for entry in sentiment_data['progression']:
                table.add_row(str(entry['position']), f"{entry['score']:.2f}", entry['label'])
            
            console.print(table)
    
    except Exception as e:
        rprint(f"[bold red]Error analyzing sentiment:[/bold red] {str(e)}")
        raise typer.Exit(1)

@analysis_app.command("progress")
def generate_progress(
    client_name: str = typer.Argument(..., help="Name of the client"),
    period: str = typer.Option("all", "--period", "-p", help="Time period (week, month, all)"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for progress report"),
    format: str = typer.Option("text", "--format", "-f", help="Output format (text, markdown, json, html)"),
    visualize: bool = typer.Option(False, "--visualize", "-v", help="Generate visualizations")
):
    """Generate a progress report for a client."""
    try:
        # Determine date range based on period
        end_date = datetime.now()
        if period.lower() == "week":
            start_date = end_date - timedelta(days=7)
        elif period.lower() == "month":
            start_date = end_date - timedelta(days=30)
        else:  # all
            start_date = None
        
        rprint(f"[cyan]Generating progress report for {client_name}...[/cyan]")
        
        # Get client sessions
        sessions = session_manager.list_sessions(client_name=client_name)
        
        if not sessions:
            rprint(f"[yellow]No sessions found for client: {client_name}[/yellow]")
            return
        
        # Filter by date range if needed
        if start_date:
            sessions = [s for s in sessions if s.created_at >= start_date]
            
            if not sessions:
                rprint(f"[yellow]No sessions found for client {client_name} in the specified period.[/yellow]")
                return
        
        # Generate progress report
        progress_report = generate_progress_report(sessions)
        
        if not progress_report:
            rprint("[yellow]Not enough data to generate a meaningful progress report.[/yellow]")
            return
        
        # Output to file if specified
        if output_file:
            if format.lower() == "text":
                with open(output_file, 'w') as f:
                    f.write(f"Progress Report - {client_name}\n")
                    f.write(f"Period: {period.capitalize()}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    
                    f.write("SUMMARY\n")
                    f.write(progress_report['summary'] + "\n\n")
                    
                    f.write("KEY AREAS OF PROGRESS\n")
                    for area in progress_report['areas_of_progress']:
                        f.write(f"- {area}\n")
                    f.write("\n")
                    
                    f.write("CHALLENGES\n")
                    for challenge in progress_report['challenges']:
                        f.write(f"- {challenge}\n")
                    f.write("\n")
                    
                    f.write("RECOMMENDATIONS\n")
                    for rec in progress_report['recommendations']:
                        f.write(f"- {rec}\n")
            
            elif format.lower() == "markdown":
                with open(output_file, 'w') as f:
                    f.write(f"# Progress Report - {client_name}\n\n")
                    f.write(f"**Period:** {period.capitalize()}\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                    
                    f.write("## Summary\n\n")
                    f.write(progress_report['summary'] + "\n\n")
                    
                    f.write("## Key Areas of Progress\n\n")
                    for area in progress_report['areas_of_progress']:
                        f.write(f"* {area}\n")
                    f.write("\n")
                    
                    f.write("## Challenges\n\n")
                    for challenge in progress_report['challenges']:
                        f.write(f"* {challenge}\n")
                    f.write("\n")
                    
                    f.write("## Recommendations\n\n")
                    for rec in progress_report['recommendations']:
                        f.write(f"* {rec}\n")
            
            elif format.lower() == "json":
                with open(output_file, 'w') as f:
                    json_data = {
                        "client": client_name,
                        "period": period,
                        "date": datetime.now().isoformat(),
                        "report": progress_report
                    }
                    json.dump(json_data, f, indent=2)
            
            elif format.lower() == "html":
                from smart_steps_ai.analysis.export import export_progress_to_html
                content = export_progress_to_html(client_name, period, progress_report)
                with open(output_file, 'w') as f:
                    f.write(content)
            
            else:
                rprint(f"[bold red]Error:[/bold red] Unsupported output format: {format}")
                raise typer.Exit(1)
            
            rprint(f"[green]Progress report saved to:[/green] {output_file}")
        
        # Visualize if requested
        if visualize:
            try:
                from smart_steps_ai.analysis.visualization import create_progress_charts
                chart_path = Path(f"progress_{client_name.replace(' ', '_')}.png")
                create_progress_charts(sessions, str(chart_path))
                rprint(f"[green]Progress visualization saved to:[/green] {chart_path}")
            except ImportError:
                rprint("[yellow]Visualization requires matplotlib to be installed.[/yellow]")
        
        # Display on console
        if not output_file:
            console.print(Panel(
                f"[bold]Client:[/bold] {client_name}\n"
                f"[bold]Period:[/bold] {period.capitalize()}\n"
                f"[bold]Sessions analyzed:[/bold] {len(sessions)}",
                title="Progress Report",
                border_style="blue"
            ))
            
            console.print(Panel(progress_report['summary'], title="Summary", border_style="green"))
            
            rprint("[bold cyan]Key Areas of Progress:[/bold cyan]")
            for area in progress_report['areas_of_progress']:
                rprint(f"  • [yellow]{area}[/yellow]")
            rprint("")
            
            rprint("[bold cyan]Challenges:[/bold cyan]")
            for challenge in progress_report['challenges']:
                rprint(f"  • [yellow]{challenge}[/yellow]")
            rprint("")
            
            rprint("[bold cyan]Recommendations:[/bold cyan]")
            for rec in progress_report['recommendations']:
                rprint(f"  • [yellow]{rec}[/yellow]")
    
    except Exception as e:
        rprint(f"[bold red]Error generating progress report:[/bold red] {str(e)}")
        raise typer.Exit(1)

@analysis_app.command("report")
def generate_report(
    session_id: Optional[UUID] = typer.Option(None, "--session", "-s", help="ID of a specific session"),
    client_name: Optional[str] = typer.Option(None, "--client", "-c", help="Name of the client for multi-session report"),
    period: str = typer.Option("all", "--period", "-p", help="Time period (week, month, all)"),
    output_file: Path = typer.Argument(..., help="Output file for the report"),
    format: str = typer.Option("html", "--format", "-f", help="Output format (text, markdown, json, html, pdf)"),
    comprehensive: bool = typer.Option(False, "--comprehensive", help="Generate a comprehensive report with all analyses")
):
    """Generate a comprehensive therapy report."""
    try:
        # Validate that either session_id or client_name is provided
        if not session_id and not client_name:
            rprint("[bold red]Error:[/bold red] Either a session ID or client name must be provided.")
            raise typer.Exit(1)
        
        # Determine date range based on period
        end_date = datetime.now()
        if period.lower() == "week":
            start_date = end_date - timedelta(days=7)
        elif period.lower() == "month":
            start_date = end_date - timedelta(days=30)
        else:  # all
            start_date = None
        
        # Get sessions
        if session_id:
            session = session_manager.get_session(session_id)
            if not session:
                rprint(f"[bold red]Error:[/bold red] Session with ID {session_id} not found.")
                raise typer.Exit(1)
            sessions = [session]
            client_name = session.client_name
        else:
            sessions = session_manager.list_sessions(client_name=client_name)
            if not sessions:
                rprint(f"[yellow]No sessions found for client: {client_name}[/yellow]")
                return
            
            # Filter by date range if needed
            if start_date:
                sessions = [s for s in sessions if s.created_at >= start_date]
                
                if not sessions:
                    rprint(f"[yellow]No sessions found for client {client_name} in the specified period.[/yellow]")
                    return
        
        rprint(f"[cyan]Generating {'comprehensive ' if comprehensive else ''}report for {client_name}...[/cyan]")
        
        # Generate the report
        from smart_steps_ai.analysis.reporting import generate_comprehensive_report
        
        report_data = generate_comprehensive_report(
            sessions=sessions,
            client_name=client_name,
            period=period,
            comprehensive=comprehensive
        )
        
        # Output based on format
        if format.lower() == "text":
            from smart_steps_ai.analysis.export import export_report_to_text
            content = export_report_to_text(report_data)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "markdown":
            from smart_steps_ai.analysis.export import export_report_to_markdown
            content = export_report_to_markdown(report_data)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "json":
            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
        
        elif format.lower() == "html":
            from smart_steps_ai.analysis.export import export_report_to_html
            content = export_report_to_html(report_data)
            with open(output_file, 'w') as f:
                f.write(content)
        
        elif format.lower() == "pdf":
            try:
                from smart_steps_ai.analysis.export import export_report_to_pdf
                export_report_to_pdf(report_data, str(output_file))
            except ImportError:
                rprint("[bold red]Error:[/bold red] PDF export requires weasyprint to be installed.")
                rprint("Try installing it with: pip install weasyprint")
                raise typer.Exit(1)
        
        else:
            rprint(f"[bold red]Error:[/bold red] Unsupported output format: {format}")
            raise typer.Exit(1)
        
        rprint(f"[green]Report generated and saved to:[/green] {output_file}")
    
    except Exception as e:
        rprint(f"[bold red]Error generating report:[/bold red] {str(e)}")
        raise typer.Exit(1)
