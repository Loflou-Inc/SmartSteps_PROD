"""
Enhanced persona management commands for the Smart Steps AI CLI.

This module provides command-line tools for creating, editing, testing,
and analyzing enhanced personas with layered memory capabilities.
"""

import os
import json
import typer
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from uuid import UUID
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint

from smart_steps_ai.core.enhanced_persona import EnhancedPersonaManager, PersonaSchema
from smart_steps_ai.core.layered_memory import LayeredMemoryManager

persona_app = typer.Typer(
    help="Manage enhanced AI professional personas",
    no_args_is_help=True,
)

console = Console()
enhanced_persona_manager = EnhancedPersonaManager()

@persona_app.callback()
def callback():
    """
    Manage enhanced AI professional personas with advanced capabilities.
    
    Create, edit, test, and analyze complex personas with layered memory
    and knowledge integration for therapeutic applications.
    """
    pass

@persona_app.command("create")
def create_persona(
    name: str = typer.Argument(..., help="Name of the persona"),
    persona_type: str = typer.Argument(..., help="Type of professional persona"),
    education: List[str] = typer.Option([], "--education", "-e", help="Educational background"),
    specializations: List[str] = typer.Option([], "--specialization", "-s", help="Professional specializations"),
    experience: List[str] = typer.Option([], "--experience", "-x", help="Professional experience"),
    definition_file: Optional[Path] = typer.Option(None, "--definition", "-d", help="Path to persona definition file")
):
    """Create a new enhanced professional persona."""
    try:
        # Check if importing from file
        if definition_file:
            if not definition_file.exists():
                rprint(f"[bold red]Error:[/bold red] Definition file not found: {definition_file}")
                raise typer.Exit(1)
            
            persona_id = enhanced_persona_manager.import_from_file(str(definition_file))
            if not persona_id:
                rprint("[bold red]Error:[/bold red] Failed to import persona from file.")
                raise typer.Exit(1)
            
            persona = enhanced_persona_manager.get_persona(persona_id)
            rprint(f"[green]Successfully imported persona:[/green] {persona['name']} ({persona_id})")
            return
        
        # Create new persona
        personality_traits = {
            "empathy": 0.7,
            "analytical": 0.7,
            "resilience": 0.7
        }
        
        persona_id = enhanced_persona_manager.create_persona(
            name=name,
            persona_type=persona_type,
            core_attributes={
                "education": education,
                "specializations": specializations,
                "professional_experience": experience,
                "personality_traits": personality_traits
            }
        )
        
        rprint(f"[green]Successfully created persona:[/green] {name} ({persona_id})")
        rprint("Use the following commands to enhance this persona:")
        rprint(f"  [cyan]smart-steps-ai persona edit {persona_id} --traits[/cyan]")
        rprint(f"  [cyan]smart-steps-ai persona import {persona_id} --document /path/to/document.txt[/cyan]")
    
    except Exception as e:
        rprint(f"[bold red]Error creating persona:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("list")
def list_personas():
    """List all available enhanced personas."""
    try:
        personas = enhanced_persona_manager.list_personas()
        
        if not personas:
            rprint("[yellow]No enhanced personas found.[/yellow]")
            return
        
        table = Table(title="Enhanced Professional Personas")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Created", style="magenta")
        table.add_column("Updated", style="blue")
        table.add_column("Version", style="red")
        
        for persona in personas:
            created_at = persona.get("created_at", "Unknown")
            if created_at and created_at != "Unknown":
                created_at = datetime.fromisoformat(created_at).strftime("%Y-%m-%d")
            
            updated_at = persona.get("updated_at", "Unknown")
            if updated_at and updated_at != "Unknown":
                updated_at = datetime.fromisoformat(updated_at).strftime("%Y-%m-%d")
            
            table.add_row(
                persona["id"],
                persona["name"],
                persona["type"],
                created_at,
                updated_at,
                str(persona.get("version", 1))
            )
        
        console.print(table)
    
    except Exception as e:
        rprint(f"[bold red]Error listing personas:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("info")
def persona_info(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed information")
):
    """Show information about an enhanced persona."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        # Basic info panel
        console.print(Panel.fit(
            f"[bold]{persona['name']}[/bold] ({persona['id']})\n"
            f"Type: {persona['type']}\n"
            f"Created: {datetime.fromisoformat(persona.get('created_at', datetime.now().isoformat())).strftime('%Y-%m-%d')}\n"
            f"Updated: {datetime.fromisoformat(persona.get('updated_at', datetime.now().isoformat())).strftime('%Y-%m-%d')}\n"
            f"Version: {persona.get('version', 1)}",
            title="Persona Information",
            border_style="blue"
        ))
        
        # Core attributes
        core_attrs = persona.get("core_attributes", {})
        
        # Education
        if "education" in core_attrs and core_attrs["education"]:
            rprint("[bold cyan]Education:[/bold cyan]")
            for edu in core_attrs["education"]:
                rprint(f"  • [green]{edu}[/green]")
            rprint("")
        
        # Specializations
        if "specializations" in core_attrs and core_attrs["specializations"]:
            rprint("[bold cyan]Specializations:[/bold cyan]")
            for spec in core_attrs["specializations"]:
                rprint(f"  • [green]{spec}[/green]")
            rprint("")
        
        # Professional experience
        if "professional_experience" in core_attrs and core_attrs["professional_experience"]:
            rprint("[bold cyan]Professional Experience:[/bold cyan]")
            for exp in core_attrs["professional_experience"]:
                rprint(f"  • [green]{exp}[/green]")
            rprint("")
        
        # Personality traits
        if "personality_traits" in core_attrs:
            traits = core_attrs["personality_traits"]
            rprint("[bold cyan]Personality Traits:[/bold cyan]")
            for trait, value in traits.items():
                rprint(f"  • [green]{trait}:[/green] {value:.2f}")
            rprint("")
        
        # Knowledge sources
        if "knowledge_sources" in persona and persona["knowledge_sources"]:
            sources = persona["knowledge_sources"]
            
            table = Table(title="Knowledge Sources")
            table.add_column("ID", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Path", style="yellow")
            table.add_column("Period", style="magenta")
            
            for source in sources:
                table.add_row(
                    source["id"],
                    source["type"],
                    source["path"],
                    source["metadata"].get("period", "Unknown")
                )
            
            console.print(table)
        
        # Detailed information
        if detailed:
            # Memory configuration
            if "memory_configuration" in persona:
                memory_config = persona["memory_configuration"]
                
                console.print(Panel.fit(
                    f"Reflection Frequency: {memory_config.get('reflection_frequency', 5)}\n"
                    f"Learning Rate: {memory_config.get('learning_rate', 0.3)}\n"
                    f"Confidence Threshold: {memory_config.get('confidence_threshold', 0.7)}",
                    title="Memory Configuration",
                    border_style="yellow"
                ))
            
            # Growth boundaries
            if "growth_boundaries" in persona:
                growth = persona["growth_boundaries"]
                
                rprint("[bold cyan]Growth Boundaries:[/bold cyan]")
                rprint(f"  • [green]Personality Variance:[/green] {growth.get('personality_variance', 0.2)}")
                
                if "allowed_domains" in growth and growth["allowed_domains"]:
                    rprint("  • [green]Allowed Domains:[/green]")
                    for domain in growth["allowed_domains"]:
                        rprint(f"    - [yellow]{domain}[/yellow]")
    
    except Exception as e:
        rprint(f"[bold red]Error getting persona info:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("edit")
def edit_persona(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New name for the persona"),
    persona_type: Optional[str] = typer.Option(None, "--type", "-t", help="New type for the persona"),
    add_education: List[str] = typer.Option([], "--add-education", help="Add educational background"),
    add_specialization: List[str] = typer.Option([], "--add-specialization", help="Add specialization"),
    add_experience: List[str] = typer.Option([], "--add-experience", help="Add professional experience"),
    traits: bool = typer.Option(False, "--traits", help="Edit personality traits interactively")
):
    """Edit an existing enhanced persona."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        # Prepare updates
        updates = {}
        
        # Basic properties
        if name:
            updates["name"] = name
        
        if persona_type:
            updates["type"] = persona_type
        
        # Core attributes
        core_updates = {}
        
        # Add education
        if add_education:
            current_education = persona.get("core_attributes", {}).get("education", [])
            core_updates["education"] = current_education + [edu for edu in add_education if edu not in current_education]
        
        # Add specialization
        if add_specialization:
            current_specs = persona.get("core_attributes", {}).get("specializations", [])
            core_updates["specializations"] = current_specs + [spec for spec in add_specialization if spec not in current_specs]
        
        # Add experience
        if add_experience:
            current_exp = persona.get("core_attributes", {}).get("professional_experience", [])
            core_updates["professional_experience"] = current_exp + [exp for exp in add_experience if exp not in current_exp]
        
        # Edit personality traits
        if traits:
            current_traits = persona.get("core_attributes", {}).get("personality_traits", {})
            new_traits = {}
            
            rprint("[bold cyan]Edit Personality Traits[/bold cyan]")
            rprint("Enter values between 0.0 and 1.0 for each trait:")
            
            # Get existing traits
            for trait, value in current_traits.items():
                new_value = float(typer.prompt(f"{trait} (current: {value:.2f})", default=str(value)))
                new_traits[trait] = max(0.0, min(1.0, new_value))  # Clamp to 0-1
            
            # Ask if user wants to add new traits
            if typer.confirm("Add additional personality traits?", default=False):
                while True:
                    trait_name = typer.prompt("Trait name (or leave empty to finish)")
                    if not trait_name:
                        break
                    
                    trait_value = float(typer.prompt(f"{trait_name} value (0.0-1.0)", default="0.7"))
                    new_traits[trait_name] = max(0.0, min(1.0, trait_value))  # Clamp to 0-1
            
            core_updates["personality_traits"] = new_traits
        
        # Apply core attribute updates
        if core_updates:
            updates["core_attributes"] = core_updates
        
        # Apply updates
        if updates:
            success = enhanced_persona_manager.update_persona(persona_id, updates)
            
            if success:
                rprint(f"[green]Successfully updated persona:[/green] {persona_id}")
            else:
                rprint(f"[bold red]Error:[/bold red] Failed to update persona.")
                raise typer.Exit(1)
        else:
            rprint("[yellow]No updates specified.[/yellow]")
    
    except Exception as e:
        rprint(f"[bold red]Error editing persona:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("import")
def import_document(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    document: Path = typer.Argument(..., help="Path to the document file"),
    document_id: Optional[str] = typer.Option(None, "--id", help="ID for the document"),
    document_type: str = typer.Option("biography", "--type", "-t", help="Type of document"),
    period: str = typer.Option("unknown", "--period", "-p", help="Time period the document covers"),
    relevance: List[str] = typer.Option([], "--relevance", "-r", help="Relevance tags for the document")
):
    """Import a knowledge document for a persona."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        if not document.exists():
            rprint(f"[bold red]Error:[/bold red] Document file not found: {document}")
            raise typer.Exit(1)
        
        # Generate document ID if not provided
        if not document_id:
            document_id = document.stem.lower().replace(" ", "_")
        
        # Create memory manager for this persona
        memory_manager = LayeredMemoryManager(persona_id)
        
        # Import document to foundation layer
        chunk_ids = memory_manager.foundation.import_document(
            document_id=document_id,
            file_path=str(document),
            metadata={
                "type": document_type,
                "period": period,
                "relevance": relevance or ["general"],
                "imported_at": datetime.now().isoformat()
            }
        )
        
        if not chunk_ids:
            rprint(f"[bold red]Error:[/bold red] Failed to import document.")
            raise typer.Exit(1)
        
        # Add knowledge source to persona definition
        enhanced_persona_manager.add_knowledge_source(
            persona_id=persona_id,
            source_id=document_id,
            source_type=document_type,
            source_path=str(document),
            metadata={
                "period": period,
                "relevance": relevance or ["general"]
            }
        )
        
        rprint(f"[green]Successfully imported document:[/green] {document.name}")
        rprint(f"Document ID: [cyan]{document_id}[/cyan]")
        rprint(f"Created [cyan]{len(chunk_ids)}[/cyan] knowledge chunks")
    
    except Exception as e:
        rprint(f"[bold red]Error importing document:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("validate")
def validate_persona(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    report_file: Optional[Path] = typer.Option(None, "--report", "-r", help="Path to save validation report")
):
    """Validate an enhanced persona for consistency and completeness."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        # Validate persona
        errors = enhanced_persona_manager.validate_persona(persona_id)
        
        # Check knowledge sources
        knowledge_warnings = []
        if "knowledge_sources" in persona and persona["knowledge_sources"]:
            for source in persona["knowledge_sources"]:
                source_path = source.get("path")
                if not os.path.exists(source_path):
                    knowledge_warnings.append(f"Knowledge source file not found: {source_path}")
        
        # Display results
        if not errors and not knowledge_warnings:
            rprint(f"[green]Persona validation successful![/green] {persona['name']} ({persona_id}) is valid.")
        else:
            rprint(f"[bold yellow]Validation issues found for[/bold yellow] {persona['name']} ({persona_id}):")
            
            if errors:
                rprint("[bold red]Schema Errors:[/bold red]")
                for error in errors:
                    rprint(f"  • [red]{error}[/red]")
            
            if knowledge_warnings:
                rprint("[bold yellow]Knowledge Source Warnings:[/bold yellow]")
                for warning in knowledge_warnings:
                    rprint(f"  • [yellow]{warning}[/yellow]")
        
        # Save report if requested
        if report_file:
            with open(report_file, 'w') as f:
                f.write(f"Validation Report for {persona['name']} ({persona_id})\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                
                if not errors and not knowledge_warnings:
                    f.write("VALIDATION SUCCESSFUL: No issues found.\n")
                else:
                    if errors:
                        f.write("SCHEMA ERRORS:\n")
                        for error in errors:
                            f.write(f"- {error}\n")
                        f.write("\n")
                    
                    if knowledge_warnings:
                        f.write("KNOWLEDGE SOURCE WARNINGS:\n")
                        for warning in knowledge_warnings:
                            f.write(f"- {warning}\n")
                        f.write("\n")
            
            rprint(f"[green]Validation report saved to:[/green] {report_file}")
    
    except Exception as e:
        rprint(f"[bold red]Error validating persona:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("test")
def test_persona(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    scenario: str = typer.Option("general", "--scenario", "-s", help="Test scenario"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Run tests interactively"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Path to save test results")
):
    """Test an enhanced persona against defined scenarios."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        # Create memory manager for this persona
        memory_manager = LayeredMemoryManager(persona_id)
        
        # Define test scenarios
        scenarios = {
            "general": [
                "Can you introduce yourself and your background?",
                "What is your approach to therapy?",
                "How do you handle difficult clients?"
            ],
            "trauma": [
                "How does trauma affect development?",
                "What are effective approaches for treating PTSD?",
                "How do you distinguish between different types of trauma responses?"
            ],
            "ethical": [
                "How do you handle confidentiality issues?",
                "What would you do if a client reported self-harm thoughts?",
                "How do you maintain professional boundaries?"
            ]
        }
        
        # Use specified scenario or default to general
        test_questions = scenarios.get(scenario, scenarios["general"])
        
        # Interactive mode
        if interactive:
            rprint(f"[bold cyan]Interactive Testing: {persona['name']}[/bold cyan]")
            rprint("[yellow]Enter test questions or 'exit' to quit.[/yellow]\n")
            
            while True:
                question = typer.prompt("Test Question")
                if question.lower() in ["exit", "quit", "q"]:
                    break
                
                # Retrieve context for question
                context = memory_manager.retrieve_context(question)
                formatted_context = memory_manager.format_context(context)
                
                # Display context
                console.print(Panel(
                    formatted_context,
                    title="Retrieved Context",
                    border_style="blue"
                ))
        
        # Automated testing
        else:
            rprint(f"[bold cyan]Testing Persona:[/bold cyan] {persona['name']} ({persona_id})")
            rprint(f"[bold cyan]Scenario:[/bold cyan] {scenario}")
            
            results = []
            
            for question in test_questions:
                rprint(f"\n[bold green]Test Question:[/bold green] {question}")
                
                # Retrieve context for question
                context = memory_manager.retrieve_context(question)
                formatted_context = memory_manager.format_context(context)
                
                # Calculate context quality metrics
                foundation_words = len(context.get("foundation", "").split())
                experience_words = len(context.get("experience", "").split())
                synthesis_words = len(context.get("synthesis", "").split())
                
                # Display metrics
                rprint("[bold]Context Metrics:[/bold]")
                rprint(f"  • Foundation: [cyan]{foundation_words}[/cyan] words")
                rprint(f"  • Experience: [cyan]{experience_words}[/cyan] words")
                rprint(f"  • Synthesis: [cyan]{synthesis_words}[/cyan] words")
                
                # Store result
                results.append({
                    "question": question,
                    "metrics": {
                        "foundation_words": foundation_words,
                        "experience_words": experience_words,
                        "synthesis_words": synthesis_words,
                        "total_words": foundation_words + experience_words + synthesis_words
                    },
                    "context": formatted_context
                })
            
            # Save results if requested
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump({
                        "persona_id": persona_id,
                        "persona_name": persona["name"],
                        "scenario": scenario,
                        "timestamp": datetime.now().isoformat(),
                        "results": results
                    }, f, indent=2)
                
                rprint(f"\n[green]Test results saved to:[/green] {output_file}")
    
    except Exception as e:
        rprint(f"[bold red]Error testing persona:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("reflect")
def persona_reflect(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    topic: Optional[str] = typer.Option(None, "--topic", "-t", help="Topic for reflection"),
    session_id: Optional[str] = typer.Option(None, "--session", "-s", help="Session ID to base reflection on")
):
    """Generate reflections and insights for a persona."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        # Create memory manager for this persona
        memory_manager = LayeredMemoryManager(persona_id)
        
        # Prepare reflection context
        context = {
            "session_id": session_id,
            "topic": topic
        }
        
        # Generate reflection prompt
        reflection_prompt = memory_manager.prepare_reflection_prompt(context)
        
        rprint("[bold cyan]Reflection Prompt:[/bold cyan]")
        rprint(reflection_prompt)
        
        # In a complete implementation, this would call an AI model 
        # to generate the actual reflection. For now, we'll just show the prompt.
        rprint("\n[yellow]This command would normally send the prompt to an AI model[/yellow]")
        rprint("[yellow]to generate a reflection that would be stored in the synthesis layer.[/yellow]")
    
    except Exception as e:
        rprint(f"[bold red]Error generating reflection:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("analyze")
def analyze_persona(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Path to save analysis report")
):
    """Analyze a persona's knowledge structure and growth."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        # Create memory manager for this persona
        memory_manager = LayeredMemoryManager(persona_id)
        
        # Get meta-cognitive data
        metacog_context = memory_manager.meta_cognitive.get_self_awareness_context()
        
        # Display analysis
        console.print(Panel.fit(
            f"[bold]{persona['name']} ({persona_id})[/bold]\n\n"
            f"{metacog_context}",
            title="Persona Analysis",
            border_style="blue"
        ))
        
        # In a complete implementation, this would analyze the persona's
        # knowledge structure and growth in more detail.
        
        # Save report if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"Analysis Report for {persona['name']} ({persona_id})\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n\n")
                f.write(metacog_context.replace("[Self-Awareness]", "Self-Awareness").replace("[", "").replace("]", ""))
            
            rprint(f"[green]Analysis report saved to:[/green] {output_file}")
    
    except Exception as e:
        rprint(f"[bold red]Error analyzing persona:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("export")
def export_persona(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    output_file: Path = typer.Argument(..., help="Path to save the persona definition"),
    include_memory: bool = typer.Option(False, "--memory", "-m", help="Include memory data in export")
):
    """Export a persona definition to a file."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        # Export persona definition
        success = enhanced_persona_manager.export_to_file(persona_id, str(output_file))
        
        if not success:
            rprint(f"[bold red]Error:[/bold red] Failed to export persona.")
            raise typer.Exit(1)
        
        rprint(f"[green]Successfully exported persona definition to:[/green] {output_file}")
        
        # Export memory data if requested
        if include_memory:
            # This would export the memory data in a complete implementation
            rprint("[yellow]Memory data export is not implemented in this version.[/yellow]")
    
    except Exception as e:
        rprint(f"[bold red]Error exporting persona:[/bold red] {str(e)}")
        raise typer.Exit(1)

@persona_app.command("delete")
def delete_persona(
    persona_id: str = typer.Argument(..., help="ID of the persona"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation")
):
    """Delete an enhanced persona."""
    try:
        persona = enhanced_persona_manager.get_persona(persona_id)
        
        if not persona:
            rprint(f"[bold red]Error:[/bold red] Persona not found: {persona_id}")
            raise typer.Exit(1)
        
        # Confirm deletion
        if not force:
            confirm = typer.confirm(f"Are you sure you want to delete persona '{persona['name']}' ({persona_id})?")
            if not confirm:
                rprint("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit()
        
        # Delete persona
        success = enhanced_persona_manager.delete_persona(persona_id)
        
        if success:
            rprint(f"[green]Successfully deleted persona:[/green] {persona_id}")
        else:
            rprint(f"[bold red]Error:[/bold red] Failed to delete persona.")
            raise typer.Exit(1)
    
    except Exception as e:
        rprint(f"[bold red]Error deleting persona:[/bold red] {str(e)}")
        raise typer.Exit(1)
