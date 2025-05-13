"""
CLI commands for performance optimization and monitoring.

This module provides CLI commands for performance optimization,
configuration, and monitoring.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from smart_steps_ai.core.cache_manager import (
    cache_manager, 
    performance_monitor
)
from smart_steps_ai.core.memory_optimizer import memory_monitor
from smart_steps_ai.core.knowledge_store import KnowledgeStore

# Create Typer app
app = typer.Typer(help="Performance optimization and monitoring commands")
console = Console()

@app.command("optimize")
def optimize_performance(
    clear_cache: bool = typer.Option(False, "--clear-cache", "-c", help="Clear all caches"),
    compress_vectors: bool = typer.Option(True, "--compress-vectors", "-v", help="Compress vector embeddings"),
    optimize_memory: bool = typer.Option(True, "--optimize-memory", "-m", help="Optimize memory usage"),
    report_file: Optional[Path] = typer.Option(None, "--report", "-r", help="Save optimization report to file")
):
    """
    Optimize system performance.
    
    This command runs various performance optimizations including
    caching, memory usage, and vector compression.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        console=console
    ) as progress:
        # Create overall task
        optimize_task = progress.add_task("[bold blue]Optimizing performance...", total=4)
        results = {}
        
        # Step 1: Clear cache if requested
        progress.update(optimize_task, advance=1, description="Clearing caches...")
        if clear_cache:
            memory_cache = cache_manager.get_cache("memory")
            disk_cache = cache_manager.get_cache("disk")
            
            memory_cleared = memory_cache.clear()
            disk_cleared = disk_cache.clear()
            
            results["cache_clearing"] = {
                "memory_cache_cleared": memory_cleared,
                "disk_cache_cleared": disk_cleared
            }
        
        # Step 2: Compress vectors if requested
        progress.update(optimize_task, advance=1, description="Compressing vectors...")
        if compress_vectors:
            # Create knowledge store
            store = KnowledgeStore()
            
            # Get all collections
            vector_results = store.vector_store.optimize_memory()
            results["vector_compression"] = vector_results
        
        # Step 3: Optimize memory if requested
        progress.update(optimize_task, advance=1, description="Optimizing memory usage...")
        if optimize_memory:
            memory_results = memory_monitor.optimize_memory()
            results["memory_optimization"] = memory_results
        
        # Step 4: Generate report
        progress.update(optimize_task, advance=1, description="Generating report...")
        
        # Add timestamp
        results["timestamp"] = datetime.now().isoformat()
        results["system_info"] = {
            "platform": sys.platform,
            "python_version": sys.version
        }
        
        # Save report if requested
        if report_file:
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2)
        
        # Complete task
        progress.update(optimize_task, completed=True, description="Optimization complete!")
    
    # Display results
    console.print("\n[bold green]Performance Optimization Results:[/bold green]")
    
    # Display cache clearing results
    if clear_cache:
        console.print("\n[bold]Cache Clearing:[/bold]")
        console.print(f"Memory cache cleared: {results['cache_clearing']['memory_cache_cleared']}")
        console.print(f"Disk cache cleared: {results['cache_clearing']['disk_cache_cleared']}")
    
    # Display vector compression results
    if compress_vectors and "vector_compression" in results:
        console.print("\n[bold]Vector Compression:[/bold]")
        if "memory_stats" in results["vector_compression"]:
            stats = results["vector_compression"]["memory_stats"]
            console.print(f"Objects before: {stats['objects_before']}")
            console.print(f"Objects after: {stats['objects_after']}")
            console.print(f"Objects cleaned: {stats['objects_cleaned']}")
    
    # Display memory optimization results
    if optimize_memory:
        console.print("\n[bold]Memory Optimization:[/bold]")
        console.print(f"Objects cleaned: {results['memory_optimization']['objects_cleaned']}")
    
    # Display report path if saved
    if report_file:
        console.print(f"\nFull report saved to: {report_file}")


@app.command("status")
def performance_status(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed performance metrics"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch performance metrics in real time"),
    interval: int = typer.Option(2, "--interval", "-i", help="Update interval in seconds (for watch mode)")
):
    """
    Display current performance status.
    
    This command shows performance metrics like operation timings,
    memory usage, and cache statistics.
    """
    def display_status():
        # Clear screen in watch mode
        if watch:
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print(f"[bold]Performance Status[/bold] (Updated: {datetime.now().strftime('%H:%M:%S')})")
            console.print("[dim]Press Ctrl+C to exit watch mode[/dim]\n")
        
        # Get performance report
        perf_report = performance_monitor.get_performance_report()
        
        # Create performance table
        perf_table = Table(title="Operation Performance", box=box.MINIMAL)
        perf_table.add_column("Operation", style="bold")
        perf_table.add_column("Avg Time (ms)", justify="right")
        perf_table.add_column("Min Time (ms)", justify="right")
        perf_table.add_column("Max Time (ms)", justify="right")
        perf_table.add_column("Count", justify="right")
        
        for op_name, metrics in perf_report.items():
            perf_table.add_row(
                op_name,
                f"{metrics['average_time'] * 1000:.2f}",
                f"{metrics['min_time'] * 1000:.2f}",
                f"{metrics['max_time'] * 1000:.2f}",
                str(metrics['execution_count'])
            )
        
        console.print(perf_table)
        
        # Get memory usage
        memory_usage = memory_monitor.get_memory_usage()
        
        # Create memory table
        memory_table = Table(title="Memory Usage", box=box.MINIMAL)
        memory_table.add_column("Metric", style="bold")
        memory_table.add_column("Value", justify="right")
        
        memory_table.add_row("Total Objects", str(memory_usage["total_objects"]))
        memory_table.add_row("Total Size (MB)", f"{memory_usage['total_size_mb']:.2f}")
        
        console.print(memory_table)
        
        # Show detailed metrics if requested
        if detailed:
            # Get memory cache info
            memory_cache = cache_manager.get_cache("memory")
            
            # Create cache table
            cache_table = Table(title="Cache Status", box=box.MINIMAL)
            cache_table.add_column("Cache Type", style="bold")
            cache_table.add_column("Items", justify="right")
            cache_table.add_column("Hit Rate", justify="right")
            
            # This is a simplified approach since we don't track hit rate yet
            # In a real implementation, we would track hits and misses
            cache_table.add_row(
                "Memory Cache",
                str(len(memory_cache.cache)),
                "N/A"
            )
            
            console.print(cache_table)
    
    # Single display mode
    if not watch:
        display_status()
        return
    
    # Watch mode
    try:
        while True:
            display_status()
            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[bold green]Exiting watch mode[/bold green]")


@app.command("configure")
def configure_performance(
    cache_size: Optional[int] = typer.Option(None, "--cache-size", "-c", help="Maximum memory cache size"),
    disk_cache_size: Optional[int] = typer.Option(None, "--disk-cache-size", "-d", help="Maximum disk cache size (MB)"),
    compression: Optional[bool] = typer.Option(None, "--compression", "-v", help="Enable vector compression"),
    batch_size: Optional[int] = typer.Option(None, "--batch-size", "-b", help="Batch processing size")
):
    """
    Configure performance settings.
    
    This command allows configuring various performance settings
    like cache sizes, compression, and batch processing.
    """
    changes_made = []
    
    # Update memory cache size
    if cache_size is not None:
        memory_cache = cache_manager.get_cache("memory")
        memory_cache.max_size = cache_size
        changes_made.append(f"Memory cache size set to {cache_size} items")
    
    # Update disk cache size
    if disk_cache_size is not None:
        disk_cache = cache_manager.get_cache("disk")
        disk_cache.max_size_mb = disk_cache_size
        changes_made.append(f"Disk cache size set to {disk_cache_size} MB")
    
    # Update vector compression setting
    if compression is not None:
        # Create knowledge store
        store = KnowledgeStore()
        store.vector_store.use_compressed_vectors = compression
        changes_made.append(f"Vector compression {'enabled' if compression else 'disabled'}")
    
    # Update batch size
    if batch_size is not None:
        batch_processor.batch_size = batch_size
        changes_made.append(f"Batch processing size set to {batch_size}")
    
    # Display results
    if changes_made:
        console.print("[bold green]Performance configuration updated:[/bold green]")
        for change in changes_made:
            console.print(f"• {change}")
    else:
        console.print("[yellow]No changes were made to performance configuration.[/yellow]")
        console.print("Use --help to see available options.")


@app.command("reset")
def reset_performance_metrics(
    confirm: bool = typer.Option(False, "--confirm", "-c", help="Confirm reset without prompt")
):
    """
    Reset all performance metrics.
    
    This command clears performance counters, timings, and statistics.
    """
    if not confirm:
        confirmed = typer.confirm("Are you sure you want to reset all performance metrics?")
        if not confirmed:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
    
    # Clear performance monitor
    performance_monitor.timings.clear()
    performance_monitor.execution_counts.clear()
    
    console.print("[bold green]All performance metrics reset successfully.[/bold green]")
    

if __name__ == "__main__":
    app()
