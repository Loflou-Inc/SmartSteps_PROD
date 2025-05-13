"""Benchmarking suite for the Smart Steps AI Professional Persona module."""

import os
import sys
import json
import time
import statistics
import argparse
import tracemalloc
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import the Smart Steps AI module components
from src.smart_steps_ai.utils import get_logger, StructuredLogger
from src.smart_steps_ai.config import get_config_manager
from src.smart_steps_ai.provider import ProviderManager
from src.smart_steps_ai.provider.mock import MockProvider
from src.smart_steps_ai.persona import PersonaManager
from src.smart_steps_ai.session import SessionManager, Session, Message, MessageRole
from src.smart_steps_ai.memory import MemoryManager
from src.smart_steps_ai.analysis import SessionAnalyzer


class BenchmarkSuite:
    """
    Benchmarking suite for the Smart Steps AI module.
    
    This class provides functionality for running performance benchmarks
    on various components and functions of the Smart Steps AI module.
    """
    
    def __init__(
        self,
        output_dir: Optional[Union[str, Path]] = None,
        log_level: str = "info",
        use_mock: bool = True,
    ):
        """
        Initialize the benchmark suite.
        
        Args:
            output_dir (Optional[Union[str, Path]]): Directory for benchmark outputs (default: None)
                If None, uses ./tests/benchmarks
            log_level (str): Log level for the benchmark suite (default: "info")
            use_mock (bool): Whether to use mock providers (default: True)
        """
        # Set up directories
        self.output_dir = Path(output_dir) if output_dir else project_root / "tests" / "benchmarks"
        
        # Create directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = StructuredLogger(
            name="benchmarks",
            level=log_level,
            context={"module": "benchmarks", "use_mock": use_mock}
        )
        
        # Benchmark configuration
        self.use_mock = use_mock
        self.benchmark_results = {}
        
        # Initialize components
        self.config_manager = get_config_manager()
        self.memory_manager = MemoryManager()
        self.provider_manager = ProviderManager()
        self.persona_manager = PersonaManager()
        self.session_manager = SessionManager()
        
        # Ensure mock provider is registered for testing
        if self.use_mock:
            if "mock" not in self.provider_manager.available_providers:
                self.provider_manager.register_provider("mock", MockProvider())
            self.config_manager.set("providers.default", "mock")
            
        self.logger.info("Benchmark suite initialized")
    
    def benchmark_function(
        self,
        func: Callable[..., Any],
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        iterations: int = 10,
        warmup_iterations: int = 2,
        track_memory: bool = True,
    ) -> Dict[str, Any]:
        """
        Benchmark a function.
        
        Args:
            func (Callable[..., Any]): Function to benchmark
            args (Optional[List[Any]]): Positional arguments to pass to the function (default: None)
            kwargs (Optional[Dict[str, Any]]): Keyword arguments to pass to the function (default: None)
            name (Optional[str]): Name for the benchmark (default: None)
                If None, uses the function name
            iterations (int): Number of iterations to run (default: 10)
            warmup_iterations (int): Number of warmup iterations (default: 2)
            track_memory (bool): Whether to track memory usage (default: True)
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        # Get name from function if not provided
        if name is None:
            name = func.__name__
            
        self.logger.info(f"Benchmarking function: {name}")
        
        # Run warmup iterations
        if warmup_iterations > 0:
            self.logger.debug(f"Running {warmup_iterations} warmup iterations")
            for _ in range(warmup_iterations):
                func(*args, **kwargs)
        
        # Track time
        self.logger.debug(f"Running {iterations} benchmark iterations")
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            func(*args, **kwargs)
            end_time = time.time()
            elapsed = end_time - start_time
            times.append(elapsed)
            self.logger.debug(f"Iteration {i+1}/{iterations}: {elapsed:.6f} seconds")
        
        # Track memory if requested
        memory_before = None
        memory_after = None
        memory_diff = None
        
        if track_memory:
            tracemalloc.start()
            memory_before = tracemalloc.get_traced_memory()
            
            func(*args, **kwargs)
            
            memory_after = tracemalloc.get_traced_memory()
            memory_diff = memory_after[0] - memory_before[0]
            tracemalloc.stop()
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        try:
            stdev_time = statistics.stdev(times)
        except statistics.StatisticsError:
            stdev_time = 0.0
            
        median_time = statistics.median(times)
        
        # Prepare results
        results = {
            "name": name,
            "iterations": iterations,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "median_time": median_time,
            "stdev_time": stdev_time,
            "times": times
        }
        
        if track_memory:
            results["memory_before"] = memory_before[0] if memory_before else None
            results["memory_peak_before"] = memory_before[1] if memory_before else None
            results["memory_after"] = memory_after[0] if memory_after else None
            results["memory_peak_after"] = memory_after[1] if memory_after else None
            results["memory_diff"] = memory_diff
        
        # Store results
        self.benchmark_results[name] = results
        
        # Log results
        self.logger.info(
            f"Benchmark {name} completed: avg={avg_time:.6f}s, min={min_time:.6f}s, max={max_time:.6f}s",
            context={
                "benchmark": name,
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "median_time": median_time,
                "stdev_time": stdev_time,
                "memory_diff": memory_diff
            }
        )
        
        return results
    
    def benchmark_session_creation(
        self, iterations: int = 10, warmup_iterations: int = 2
    ) -> Dict[str, Any]:
        """
        Benchmark session creation.
        
        Args:
            iterations (int): Number of iterations to run (default: 10)
            warmup_iterations (int): Number of warmup iterations (default: 2)
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        def create_session():
            session = Session(
                client_name="Benchmark Client",
                persona_name="dr_hayes",
                tags=["benchmark", "test"]
            )
            session.add_message(Message(
                role=MessageRole.SYSTEM,
                content="You are a professional therapist helping a client with anxiety."
            ))
            session.add_message(Message(
                role=MessageRole.CLIENT,
                content="I've been feeling really anxious about work lately."
            ))
            return session
        
        return self.benchmark_function(
            func=create_session,
            name="session_creation",
            iterations=iterations,
            warmup_iterations=warmup_iterations
        )
    
    def benchmark_message_processing(
        self, iterations: int = 10, warmup_iterations: int = 2
    ) -> Dict[str, Any]:
        """
        Benchmark message processing with a provider.
        
        Args:
            iterations (int): Number of iterations to run (default: 10)
            warmup_iterations (int): Number of warmup iterations (default: 2)
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        # Create a session
        session = Session(
            client_name="Benchmark Client",
            persona_name="dr_hayes",
            tags=["benchmark", "test"]
        )
        session.add_message(Message(
            role=MessageRole.SYSTEM,
            content="You are a professional therapist helping a client with anxiety."
        ))
        
        # Define function to benchmark
        def process_message():
            # Create new message
            message = Message(
                role=MessageRole.CLIENT,
                content="I've been feeling really anxious about work lately."
            )
            
            # Add to session
            session.add_message(message)
            
            # Get provider
            provider = self.provider_manager.get_provider("mock")
            
            # Generate response
            provider_response = provider.generate_response(session.messages)
            
            # Add response to session
            session.add_message(Message(
                role=MessageRole.PERSONA,
                content=provider_response.content
            ))
            
            return provider_response
        
        return self.benchmark_function(
            func=process_message,
            name="message_processing",
            iterations=iterations,
            warmup_iterations=warmup_iterations
        )
    
    def benchmark_session_analysis(
        self, iterations: int = 5, warmup_iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Benchmark session analysis.
        
        Args:
            iterations (int): Number of iterations to run (default: 5)
            warmup_iterations (int): Number of warmup iterations (default: 1)
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        # Create a session with messages
        session = Session(
            client_name="Benchmark Client",
            persona_name="dr_hayes",
            tags=["benchmark", "test"]
        )
        session.add_message(Message(
            role=MessageRole.SYSTEM,
            content="You are a professional therapist helping a client with anxiety."
        ))
        session.add_message(Message(
            role=MessageRole.CLIENT,
            content="I've been feeling really anxious about work lately."
        ))
        
        # Add some back-and-forth messages
        for i in range(3):
            # Add persona response
            session.add_message(Message(
                role=MessageRole.PERSONA,
                content=f"I understand that anxiety. Can you tell me more about what's happening at work? (message {i+1})"
            ))
            
            # Add client response
            session.add_message(Message(
                role=MessageRole.CLIENT,
                content=f"Well, there's a lot of pressure to perform and I'm worried about meeting expectations. (message {i+1})"
            ))
        
        # Save session
        self.session_manager.save_session(session)
        session_id = session.id
        
        # Define function to benchmark
        def analyze_session():
            analyzer = SessionAnalyzer(
                session_manager=self.session_manager,
                memory_manager=self.memory_manager,
                persona_manager=self.persona_manager
            )
            return analyzer.analyze_session(session_id)
        
        return self.benchmark_function(
            func=analyze_session,
            name="session_analysis",
            iterations=iterations,
            warmup_iterations=warmup_iterations
        )
    
    def benchmark_memory_operations(
        self, iterations: int = 20, warmup_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Benchmark memory operations.
        
        Args:
            iterations (int): Number of iterations to run (default: 20)
            warmup_iterations (int): Number of warmup iterations (default: 5)
            
        Returns:
            Dict[str, Any]: Benchmark results
        """
        # Define function to benchmark
        def memory_operations():
            # Store a memory
            memory_id = self.memory_manager.store_memory(
                text="This is a benchmark memory about anxiety at work.",
                client_name="Benchmark Client",
                source_type="benchmark",
                source_id="benchmark_test",
                importance=5,
                tags=["benchmark", "anxiety", "work"]
            )
            
            # Retrieve the memory
            memory = self.memory_manager.get_memory(memory_id)
            
            # Search for memories
            search_results = self.memory_manager.search_memories(
                client_name="Benchmark Client",
                query="anxiety work",
                limit=5
            )
            
            return len(search_results)
        
        return self.benchmark_function(
            func=memory_operations,
            name="memory_operations",
            iterations=iterations,
            warmup_iterations=warmup_iterations
        )
    
    def run_all_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """
        Run all benchmarks.
        
        Returns:
            Dict[str, Dict[str, Any]]: All benchmark results
        """
        self.logger.info("Running all benchmarks")
        
        # Start timing
        self.logger.start_timer("all_benchmarks")
        
        # Run benchmarks
        self.benchmark_session_creation()
        self.benchmark_message_processing()
        self.benchmark_session_analysis()
        self.benchmark_memory_operations()
        
        # Stop timing
        total_elapsed = self.logger.stop_timer("all_benchmarks", level="info")
        
        # Log summary
        self.logger.info(
            f"All benchmarks completed in {total_elapsed:.2f} seconds",
            context={"total_elapsed": total_elapsed}
        )
        
        # Return results
        return self.benchmark_results
    
    def generate_report(self, results: Optional[Dict[str, Dict[str, Any]]] = None) -> str:
        """
        Generate a report of benchmark results.
        
        Args:
            results (Optional[Dict[str, Dict[str, Any]]]): Benchmark results to report (default: None)
                If None, uses the stored results
                
        Returns:
            str: Benchmark report in Markdown format
        """
        if results is None:
            results = self.benchmark_results
            
        if not results:
            return "# Benchmark Report\n\nNo benchmark results available."
        
        # Generate report
        report = [
            "# Smart Steps AI Benchmark Report",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Benchmarks:** {len(results)}",
            "",
            "## Results Summary",
            "",
            "| Benchmark | Iterations | Avg Time (s) | Min Time (s) | Max Time (s) | Std Dev (s) |",
            "| --------- | ---------- | ------------ | ------------ | ------------ | ----------- |",
        ]
        
        # Add summary for each benchmark
        for name, result in results.items():
            report.append(
                f"| {name} | {result['iterations']} | "
                f"{result['avg_time']:.6f} | {result['min_time']:.6f} | "
                f"{result['max_time']:.6f} | {result['stdev_time']:.6f} |"
            )
        
        # Add detailed results for each benchmark
        report.append("")
        report.append("## Detailed Results")
        
        for name, result in results.items():
            report.append("")
            report.append(f"### {name}")
            report.append("")
            report.append(f"- **Iterations:** {result['iterations']}")
            report.append(f"- **Average Time:** {result['avg_time']:.6f} seconds")
            report.append(f"- **Median Time:** {result['median_time']:.6f} seconds")
            report.append(f"- **Min Time:** {result['min_time']:.6f} seconds")
            report.append(f"- **Max Time:** {result['max_time']:.6f} seconds")
            report.append(f"- **Standard Deviation:** {result['stdev_time']:.6f} seconds")
            
            if "memory_diff" in result and result["memory_diff"] is not None:
                report.append(f"- **Memory Usage:** {result['memory_diff'] / 1024:.2f} KB")
            
            report.append("")
            report.append("#### Time Distribution")
            report.append("")
            report.append("```")
            report.append("Iteration | Time (seconds)")
            report.append("--------- | --------------")
            
            for i, t in enumerate(result["times"], 1):
                report.append(f"{i:9d} | {t:.6f}")
                
            report.append("```")
        
        # Add recommendations
        report.append("")
        report.append("## Recommendations")
        report.append("")
        
        if "session_analysis" in results and results["session_analysis"]["avg_time"] > 1.0:
            report.append("- **Session Analysis Performance:** Consider optimizing the analysis process, as it currently takes more than 1 second on average.")
            
        if "message_processing" in results and results["message_processing"]["avg_time"] > 0.5:
            report.append("- **Message Processing Performance:** Consider optimizing the message processing flow to improve response times.")
            
        if any(result.get("memory_diff", 0) and result["memory_diff"] > 1024 * 1024 for result in results.values()):
            report.append("- **Memory Usage:** Some operations are using more than 1 MB of memory. Consider optimizing memory usage for better scalability.")
            
        if not report[-1].startswith("-"):
            report.append("- No specific performance issues identified. All benchmarks are within acceptable ranges.")
        
        return "\n".join(report)
    
    def save_report(self, report: str, filename: Optional[str] = None) -> Optional[Path]:
        """
        Save a benchmark report to a file.
        
        Args:
            report (str): Benchmark report to save
            filename (Optional[str]): Filename to use (default: None)
                If None, generates a filename based on the current date and time
                
        Returns:
            Optional[Path]: Path to the saved report, or None if save failed
        """
        if filename is None:
            filename = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
        output_file = self.output_dir / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"Benchmark report saved to {output_file}")
            return output_file
        except Exception as e:
            self.logger.error(f"Error saving benchmark report: {str(e)}")
            return None
    
    def save_results(self, results: Optional[Dict[str, Dict[str, Any]]] = None, filename: Optional[str] = None) -> Optional[Path]:
        """
        Save benchmark results to a JSON file.
        
        Args:
            results (Optional[Dict[str, Dict[str, Any]]]): Benchmark results to save (default: None)
                If None, uses the stored results
            filename (Optional[str]): Filename to use (default: None)
                If None, generates a filename based on the current date and time
                
        Returns:
            Optional[Path]: Path to the saved results, or None if save failed
        """
        if results is None:
            results = self.benchmark_results
            
        if filename is None:
            filename = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        output_file = self.output_dir / filename
        
        try:
            # Process results to ensure JSON serialization
            processed_results = {}
            
            for name, result in results.items():
                processed_result = dict(result)
                
                # Remove any non-serializable values
                for key in list(processed_result.keys()):
                    try:
                        json.dumps({key: processed_result[key]})
                    except (TypeError, OverflowError):
                        del processed_result[key]
                
                processed_results[name] = processed_result
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "use_mock": self.use_mock,
                    "results": processed_results
                }, f, indent=2)
                
            self.logger.info(f"Benchmark results saved to {output_file}")
            return output_file
        except Exception as e:
            self.logger.error(f"Error saving benchmark results: {str(e)}")
            return None


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Run benchmarks for Smart Steps AI")
    parser.add_argument("--output-dir", type=str, help="Directory for benchmark outputs")
    parser.add_argument("--log-level", type=str, default="info", help="Log level (debug, info, warning, error)")
    parser.add_argument("--use-real-provider", action="store_true", help="Use real providers instead of mock")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations for each benchmark")
    parser.add_argument("--warmup", type=int, default=2, help="Number of warmup iterations")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create benchmark suite
    suite = BenchmarkSuite(
        output_dir=args.output_dir,
        log_level=args.log_level,
        use_mock=not args.use_real_provider
    )
    
    # Run benchmarks
    results = suite.run_all_benchmarks()
    
    # Generate and save report and results
    report = suite.generate_report(results)
    suite.save_report(report)
    suite.save_results(results)
