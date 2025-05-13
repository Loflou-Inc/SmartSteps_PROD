"""
Memory profiling script for the Smart Steps AI application.

This script analyzes memory usage patterns and identifies memory leaks
in the Smart Steps AI application.
"""

import os
import sys
import gc
import time
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import random
import string

import matplotlib.pyplot as plt
import numpy as np
import psutil
import tracemalloc
import linecache
from memory_profiler import profile

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from smart_steps_ai.config import ConfigManager
from smart_steps_ai.persistence import PersistenceManager
from smart_steps_ai.session import SessionManager
from smart_steps_ai.persona import PersonaManager
from smart_steps_ai.memory import MemoryManager
from smart_steps_ai.provider import ProviderManager
from smart_steps_ai.analysis import AnalysisManager
from smart_steps_ai.utils.logging import setup_logger

# Configure logging
logger = setup_logger(__name__)

def random_string(length=10):
    """Generate a random string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def display_top(snapshot, key_type='lineno', limit=10):
    """
    Display the top memory-consuming objects.
    
    Args:
        snapshot: tracemalloc snapshot
        key_type: type of key for grouping ('lineno', 'traceback', 'filename')
        limit: maximum number of entries to display
    """
    if key_type == 'lineno':
        snapshot = snapshot.filter_traces((
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        ))
        top_stats = snapshot.statistics('lineno')
    elif key_type == 'traceback':
        top_stats = snapshot.statistics('traceback')
    elif key_type == 'filename':
        top_stats = snapshot.statistics('filename')
    else:
        raise ValueError(f"Unknown key_type: {key_type}")
    
    print(f"Top {limit} memory-consuming objects:")
    for index, stat in enumerate(top_stats[:limit], 1):
        if key_type == 'traceback':
            frame = stat.traceback[0]
            filename = os.path.basename(frame.filename)
            print(f"#{index}: {stat.size / 1024:.1f} KiB - {filename}:{frame.lineno}")
            print("".join(tracemalloc.format_traceback(stat.traceback)))
        elif key_type == 'lineno':
            frame = stat.traceback[0]
            filename = os.path.basename(frame.filename)
            line = linecache.getline(frame.filename, frame.lineno).strip()
            print(f"#{index}: {stat.size / 1024:.1f} KiB - {filename}:{frame.lineno}: {line}")
        else:
            print(f"#{index}: {stat.size / 1024:.1f} KiB - {stat.traceback}")
    
    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print(f"{len(other)} other: {size / 1024:.1f} KiB")
    
    total = sum(stat.size for stat in top_stats)
    print(f"Total allocated size: {total / 1024:.1f} KiB")

class MemoryProfiler:
    """
    Memory profiler for the Smart Steps AI application.
    """
    
    def __init__(
        self,
        results_dir: str = "results",
        config_path: Optional[str] = None,
    ):
        """
        Initialize the memory profiler.
        
        Args:
            results_dir: Directory to store test results
            config_path: Path to configuration file
        """
        self.results_dir = Path(results_dir)
        self.config_path = config_path
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Initialize components
        self.config_manager = ConfigManager(config_path=config_path)
        self.persistence_manager = PersistenceManager(self.config_manager)
        self.memory_manager = MemoryManager(self.config_manager, self.persistence_manager)
        self.persona_manager = PersonaManager(self.config_manager, self.persistence_manager)
        self.session_manager = SessionManager(self.config_manager, self.persistence_manager, self.memory_manager)
        self.provider_manager = ProviderManager(self.config_manager, self.persona_manager)
        self.analysis_manager = AnalysisManager(self.config_manager, self.session_manager, self.provider_manager)
        
        # Initialize variables for tracking memory usage
        self.memory_usage_data = []
        self.snapshots = []
        self.process = psutil.Process(os.getpid())
    
    def take_memory_snapshot(self, label: str) -> Tuple[int, int]:
        """
        Take a memory snapshot.
        
        Args:
            label: Label for the snapshot
            
        Returns:
            Tuple[int, int]: (tracemalloc size, process RSS)
        """
        # Take tracemalloc snapshot
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append((label, snapshot))
        
        # Get process memory info
        memory_info = self.process.memory_info()
        rss = memory_info.rss / 1024 / 1024  # MB
        
        # Get tracemalloc memory info
        traced_memory = sum(stat.size for stat in snapshot.statistics('filename'))
        traced_memory_mb = traced_memory / 1024 / 1024  # MB
        
        # Log memory usage
        logger.info(f"Memory usage ({label}): {rss:.2f} MB (total), {traced_memory_mb:.2f} MB (traced)")
        
        # Record memory usage
        self.memory_usage_data.append({
            "label": label,
            "timestamp": time.time(),
            "total_memory_mb": rss,
            "traced_memory_mb": traced_memory_mb
        })
        
        return traced_memory, memory_info.rss
    
    @profile
    def run_session_creation_test(self, num_sessions: int = 100) -> None:
        """
        Test memory usage during session creation.
        
        Args:
            num_sessions: Number of sessions to create
        """
        logger.info(f"Running session creation test ({num_sessions} sessions)")
        
        # Take initial snapshot
        self.take_memory_snapshot("before_session_creation")
        
        # Create sessions
        for i in range(num_sessions):
            session_id = self.session_manager.create_session(
                title=f"Memory Test Session {i}",
                client_id=f"memory_test_client_{i % 10}",
                persona_id="cbt_therapist",
                metadata={"test": True, "index": i}
            )
            
            # Take snapshot every 10 sessions
            if (i + 1) % 10 == 0:
                self.take_memory_snapshot(f"after_creating_{i+1}_sessions")
        
        # Take final snapshot
        self.take_memory_snapshot("after_session_creation")
        
        # Force garbage collection
        gc.collect()
        
        # Take post-gc snapshot
        self.take_memory_snapshot("after_session_creation_gc")
    
    @profile
    def run_message_exchange_test(self, num_messages: int = 100) -> None:
        """
        Test memory usage during message exchange.
        
        Args:
            num_messages: Number of messages to exchange
        """
        logger.info(f"Running message exchange test ({num_messages} messages)")
        
        # Create a test session
        session_id = self.session_manager.create_session(
            title="Memory Test Message Session",
            client_id="memory_test_client",
            persona_id="cbt_therapist",
            metadata={"test": True}
        )
        
        # Take initial snapshot
        self.take_memory_snapshot("before_message_exchange")
        
        # Exchange messages
        for i in range(num_messages):
            # Add client message
            self.session_manager.add_message(
                session_id=session_id,
                sender_type="client",
                content=f"Test message {i} from client: {random_string(50)}",
                metadata={"test": True, "index": i}
            )
            
            # Add AI response
            self.session_manager.add_message(
                session_id=session_id,
                sender_type="ai",
                content=f"Test response {i} from AI: {random_string(100)}",
                metadata={"test": True, "index": i}
            )
            
            # Take snapshot every 10 messages
            if (i + 1) % 10 == 0:
                self.take_memory_snapshot(f"after_exchanging_{i+1}_messages")
        
        # Take final snapshot
        self.take_memory_snapshot("after_message_exchange")
        
        # Force garbage collection
        gc.collect()
        
        # Take post-gc snapshot
        self.take_memory_snapshot("after_message_exchange_gc")
    
    @profile
    def run_analysis_test(self, num_analyses: int = 20) -> None:
        """
        Test memory usage during session analysis.
        
        Args:
            num_analyses: Number of analyses to perform
        """
        logger.info(f"Running analysis test ({num_analyses} analyses)")
        
        # Create test sessions with messages
        session_ids = []
        for i in range(5):
            session_id = self.session_manager.create_session(
                title=f"Memory Test Analysis Session {i}",
                client_id="memory_test_client",
                persona_id="cbt_therapist",
                metadata={"test": True, "index": i}
            )
            
            session_ids.append(session_id)
            
            # Add messages to session
            for j in range(10):
                self.session_manager.add_message(
                    session_id=session_id,
                    sender_type="client",
                    content=f"Test message {j} from client in session {i}: {random_string(50)}",
                    metadata={"test": True, "index": j}
                )
                
                self.session_manager.add_message(
                    session_id=session_id,
                    sender_type="ai",
                    content=f"Test response {j} from AI in session {i}: {random_string(100)}",
                    metadata={"test": True, "index": j}
                )
        
        # Take initial snapshot
        self.take_memory_snapshot("before_analysis")
        
        # Perform analyses
        for i in range(num_analyses):
            # Select a random session
            session_id = random.choice(session_ids)
            
            # Analyze session
            self.analysis_manager.analyze_session(
                session_id=session_id,
                depth="standard"
            )
            
            # Take snapshot every 5 analyses
            if (i + 1) % 5 == 0:
                self.take_memory_snapshot(f"after_performing_{i+1}_analyses")
        
        # Take final snapshot
        self.take_memory_snapshot("after_analysis")
        
        # Force garbage collection
        gc.collect()
        
        # Take post-gc snapshot
        self.take_memory_snapshot("after_analysis_gc")
    
    @profile
    def run_memory_integration_test(self, num_operations: int = 50) -> None:
        """
        Test memory usage during memory integration operations.
        
        Args:
            num_operations: Number of memory operations to perform
        """
        logger.info(f"Running memory integration test ({num_operations} operations)")
        
        # Take initial snapshot
        self.take_memory_snapshot("before_memory_integration")
        
        # Perform memory operations
        for i in range(num_operations):
            # Add memory
            self.memory_manager.add_memory(
                text=f"Test memory {i}: {random_string(100)}",
                metadata={"test": True, "index": i}
            )
            
            # Take snapshot every 10 operations
            if (i + 1) % 10 == 0:
                self.take_memory_snapshot(f"after_performing_{i+1}_memory_operations")
        
        # Perform memory retrievals
        for i in range(num_operations):
            # Get memories
            self.memory_manager.get_memories(limit=10)
            
            # Take snapshot every 10 operations
            if (i + 1) % 10 == 0:
                self.take_memory_snapshot(f"after_performing_{i+1}_memory_retrievals")
        
        # Take final snapshot
        self.take_memory_snapshot("after_memory_integration")
        
        # Force garbage collection
        gc.collect()
        
        # Take post-gc snapshot
        self.take_memory_snapshot("after_memory_integration_gc")
    
    def compare_snapshots(self, label1: str, label2: str, limit: int = 10) -> None:
        """
        Compare two memory snapshots.
        
        Args:
            label1: Label of the first snapshot
            label2: Label of the second snapshot
            limit: Maximum number of entries to display
        """
        logger.info(f"Comparing snapshots: {label1} vs {label2}")
        
        # Find snapshots by label
        snapshot1 = None
        snapshot2 = None
        
        for label, snapshot in self.snapshots:
            if label == label1:
                snapshot1 = snapshot
            elif label == label2:
                snapshot2 = snapshot
        
        if not snapshot1 or not snapshot2:
            logger.error(f"Could not find snapshots: {label1}, {label2}")
            return
        
        # Compare snapshots
        diff = snapshot2.compare_to(snapshot1, 'lineno')
        
        print(f"Top {limit} memory changes between {label1} and {label2}:")
        for index, stat in enumerate(diff[:limit], 1):
            frame = stat.traceback[0]
            filename = os.path.basename(frame.filename)
            line = linecache.getline(frame.filename, frame.lineno).strip()
            print(f"#{index}: {stat.size_diff / 1024:.1f} KiB {stat.count_diff:+d} - {filename}:{frame.lineno}: {line}")
    
    def generate_memory_usage_chart(self) -> str:
        """
        Generate a chart of memory usage over time.
        
        Returns:
            str: Path to the chart file
        """
        logger.info("Generating memory usage chart")
        
        # Extract data
        labels = [entry["label"] for entry in self.memory_usage_data]
        total_memory = [entry["total_memory_mb"] for entry in self.memory_usage_data]
        traced_memory = [entry["traced_memory_mb"] for entry in self.memory_usage_data]
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Create x-axis ticks at label positions
        x = range(len(labels))
        
        # Plot data
        plt.plot(x, total_memory, 'b-', label='Total Memory (RSS)')
        plt.plot(x, traced_memory, 'r-', label='Traced Memory')
        
        # Set x-axis labels
        plt.xticks(x, labels, rotation=45, ha='right')
        
        # Set labels and title
        plt.xlabel('Test Phase')
        plt.ylabel('Memory (MB)')
        plt.title('Memory Usage During Tests')
        plt.grid(True)
        plt.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save chart
        chart_path = self.results_dir / "memory_usage_chart.png"
        plt.savefig(chart_path)
        plt.close()
        
        logger.info(f"Memory usage chart saved to: {chart_path}")
        
        return str(chart_path)
    
    def save_results(self) -> str:
        """
        Save test results to a file.
        
        Returns:
            str: Path to the results file
        """
        # Create filename
        timestamp = int(time.time())
        filename = f"memory_profile_results_{timestamp}.json"
        
        # Prepare data
        results = {
            "timestamp": timestamp,
            "memory_usage": self.memory_usage_data,
        }
        
        # Save to file
        results_path = self.results_dir / filename
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {results_path}")
        
        return str(results_path)
    
    def generate_report(self) -> str:
        """
        Generate a HTML report from the test results.
        
        Returns:
            str: Path to the report file
        """
        # Create filename
        timestamp = int(time.time())
        filename = f"memory_profile_report_{timestamp}.html"
        
        # Generate chart
        chart_filename = os.path.basename(self.generate_memory_usage_chart())
        
        # Create HTML content
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Smart Steps AI Memory Profile Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .section {{ margin-bottom: 30px; }}
                .chart {{ margin: 20px 0; text-align: center; }}
                .chart img {{ max-width: 100%; }}
            </style>
        </head>
        <body>
            <h1>Smart Steps AI Memory Profile Report</h1>
            
            <div class="section">
                <h2>Memory Usage Chart</h2>
                <div class="chart">
                    <img src="{chart_filename}" alt="Memory Usage Chart">
                </div>
            </div>
            
            <div class="section">
                <h2>Memory Usage Data</h2>
                <table>
                    <tr>
                        <th>Phase</th>
                        <th>Total Memory (MB)</th>
                        <th>Traced Memory (MB)</th>
                    </tr>
        """
        
        # Add memory usage data
        for entry in self.memory_usage_data:
            html += f"""
                    <tr>
                        <td>{entry["label"]}</td>
                        <td>{entry["total_memory_mb"]:.2f}</td>
                        <td>{entry["traced_memory_mb"]:.2f}</td>
                    </tr>
            """
        
        html += f"""
                </table>
            </div>
            
            <div class="section">
                <h2>Key Findings</h2>
                <p>The memory profile shows the following key observations:</p>
                <ul>
        """
        
        # Add key findings
        if len(self.memory_usage_data) >= 2:
            initial_memory = self.memory_usage_data[0]["total_memory_mb"]
            final_memory = self.memory_usage_data[-1]["total_memory_mb"]
            memory_diff = final_memory - initial_memory
            
            html += f"""
                    <li>Initial memory usage: {initial_memory:.2f} MB</li>
                    <li>Final memory usage: {final_memory:.2f} MB</li>
                    <li>Memory change: {memory_diff:.2f} MB ({(memory_diff / initial_memory) * 100:.2f}%)</li>
            """
            
            # Check for potential memory leaks
            if memory_diff > 10 and (memory_diff / initial_memory) > 0.2:
                html += f"""
                    <li class="warning">Potential memory leak detected: Memory usage increased significantly.</li>
                """
            else:
                html += f"""
                    <li class="success">No significant memory leaks detected.</li>
                """
        
        html += f"""
                </ul>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    <li>Consider implementing a cache cleanup mechanism for long-running processes.</li>
                    <li>Monitor memory usage in production environments, especially after handling large datasets.</li>
                    <li>Implement memory limits for per-client operations to prevent resource exhaustion.</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        # Save to file
        report_path = self.results_dir / filename
        with open(report_path, "w") as f:
            f.write(html)
        
        logger.info(f"Report saved to: {report_path}")
        
        return str(report_path)
    
    def run_all_tests(self) -> None:
        """
        Run all memory profiling tests.
        """
        # Start tracemalloc
        tracemalloc.start()
        
        # Take initial snapshot
        self.take_memory_snapshot("initial")
        
        try:
            # Run tests
            self.run_session_creation_test(num_sessions=50)
            self.run_message_exchange_test(num_messages=50)
            self.run_analysis_test(num_analyses=10)
            self.run_memory_integration_test(num_operations=25)
            
            # Take final snapshot
            self.take_memory_snapshot("final")
            
            # Force garbage collection
            gc.collect()
            
            # Take post-gc snapshot
            self.take_memory_snapshot("final_after_gc")
            
            # Compare initial and final snapshots
            self.compare_snapshots("initial", "final", limit=20)
            self.compare_snapshots("final", "final_after_gc", limit=10)
            
            # Generate report
            self.save_results()
            self.generate_report()
        finally:
            # Stop tracemalloc
            tracemalloc.stop()


def main():
    """
    Main function.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(description="Memory profile the Smart Steps AI application")
    parser.add_argument("--config", type=str, help="Path to the configuration file")
    parser.add_argument("--results-dir", type=str, help="Directory to store test results", default="results")
    args = parser.parse_args()
    
    # Create profiler
    profiler = MemoryProfiler(
        results_dir=args.results_dir,
        config_path=args.config,
    )
    
    # Run tests
    profiler.run_all_tests()


if __name__ == "__main__":
    main()
