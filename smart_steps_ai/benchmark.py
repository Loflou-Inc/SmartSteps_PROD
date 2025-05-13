"""Benchmark suite for the Smart Steps AI module."""

import sys
import time
import json
import uuid
import random
import statistics
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Callable

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import required modules
from src.smart_steps_ai.config import get_config_manager
from src.smart_steps_ai.utils import get_logger, StructuredLogger
from src.smart_steps_ai.persona import PersonaManager
from src.smart_steps_ai.session import SessionManager, Session, MessageRole
from src.smart_steps_ai.provider import ProviderManager
from src.smart_steps_ai.analysis import SessionAnalyzer


@dataclass
class BenchmarkResult:
    """Result of a benchmark."""
    name: str
    iterations: int
    duration: float
    operation_count: int = 1
    operations_per_second: float = 0.0
    avg_duration_per_op: float = 0.0
    min_duration: float = 0.0
    max_duration: float = 0.0
    median_duration: float = 0.0
    std_deviation: float = 0.0
    percentile_90: float = 0.0
    percentile_95: float = 0.0
    percentile_99: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

    def calculate_stats(self, durations: List[float]) -> None:
        """
        Calculate statistics from a list of operation durations.
        
        Args:
            durations (List[float]): List of operation durations in seconds
        """
        if not durations:
            return
            
        # Sort durations for percentile calculations
        sorted_durations = sorted(durations)
        
        # Calculate basic statistics
        self.min_duration = min(durations)
        self.max_duration = max(durations)
        self.median_duration = statistics.median(durations)
        
        # Calculate standard deviation if we have enough data
        if len(durations) > 1:
            self.std_deviation = statistics.stdev(durations)
            
        # Calculate percentiles
        self.percentile_90 = sorted_durations[int(0.9 * len(sorted_durations))]
        self.percentile_95 = sorted_durations[int(0.95 * len(sorted_durations))]
        self.percentile_99 = sorted_durations[int(0.99 * len(sorted_durations))]
        
        # Calculate overall metrics
        self.avg_duration_per_op = self.duration / self.operation_count
        self.operations_per_second = self.operation_count / self.duration


class BenchmarkSuite:
    """
    Benchmark suite for measuring performance of the Smart Steps AI module.
    
    This class provides functionality for running various benchmarks to measure
    the performance of different components of the Smart Steps AI module.
    """
    
    def __init__(self, config_path: Optional[Path] = None, use_mock: bool = True):
        """
        Initialize the benchmark suite.
        
        Args:
            config_path (Optional[Path]): Path to configuration file (default: None)
            use_mock (bool): Whether to use mock providers (default: True)
        """
        # Initialize logger
        self.logger = StructuredLogger('benchmark_suite')
        
        # Load configuration
        self.config_manager = get_config_manager()
        if config_path and config_path.exists():
            self.config_manager.reload()
        
        # Set up components
        self.persona_manager = PersonaManager()
        self.session_manager = SessionManager()
        self.provider_manager = ProviderManager()
        
        if use_mock:
            # Configure to use mock provider
            self.config_manager.set("providers.use_mock", True)
            self.config_manager.set("providers.mock.enabled", True)
            self.logger.info("Using mock provider for benchmarking")
        
        # Create output directory
        self.output_dir = Path("./output/benchmarks")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize benchmark results
        self.results = {}
    
    def run_all_benchmarks(self) -> Dict[str, BenchmarkResult]:
        """
        Run all benchmarks.
        
        Returns:
            Dict[str, BenchmarkResult]: Benchmark results
        """
        self.logger.info("Starting benchmarks")
        
        # Run individual benchmarks
        self.benchmark_persona_loading()
        self.benchmark_session_creation()
        self.benchmark_message_processing()
        self.benchmark_session_persistence()
        self.benchmark_session_analysis()
        self.benchmark_report_generation()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def benchmark_function(
        self, 
        name: str, 
        func: Callable, 
        iterations: int,
        operation_count: int = 1,
        warmup_iterations: int = 1
    ) -> BenchmarkResult:
        """
        Benchmark a function.
        
        Args:
            name (str): Benchmark name
            func (Callable): Function to benchmark
            iterations (int): Number of benchmark iterations
            operation_count (int): Number of operations per iteration (default: 1)
            warmup_iterations (int): Number of warmup iterations (default: 1)
            
        Returns:
            BenchmarkResult: Benchmark result
        """
        self.logger.info(f"Running benchmark: {name} ({iterations} iterations)")
        
        # Run warmup iterations
        for _ in range(warmup_iterations):
            func()
        
        # Measure performance
        start_time = time.time()
        durations = []
        
        for i in range(iterations):
            iter_start = time.time()
            func()
            iter_duration = time.time() - iter_start
            durations.append(iter_duration)
            
        total_duration = time.time() - start_time
        
        # Create result
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            duration=total_duration,
            operation_count=iterations * operation_count
        )
        
        # Calculate statistics
        result.calculate_stats(durations)
        
        # Log result
        self.logger.info(
            f"Benchmark '{name}' completed: "
            f"{result.operations_per_second:.2f} ops/sec, "
            f"avg: {result.avg_duration_per_op * 1000:.2f} ms, "
            f"p95: {result.percentile_95 * 1000:.2f} ms"
        )
        
        # Store result
        self.results[name] = result
        
        return result
    
    def benchmark_persona_loading(self, iterations: int = 10) -> BenchmarkResult:
        """
        Benchmark persona loading performance.
        
        Args:
            iterations (int): Number of benchmark iterations (default: 10)
            
        Returns:
            BenchmarkResult: Benchmark result
        """
        # Get all persona ids for benchmark
        persona_ids = self.persona_manager.get_available_personas()
        if not persona_ids:
            # Create mock persona for benchmark
            persona_ids = ["test_persona"]
            
        # Define benchmark function
        def benchmark_func():
            for persona_id in persona_ids:
                self.persona_manager.get_persona(persona_id)
        
        # Run benchmark
        result = self.benchmark_function(
            name="persona_loading",
            func=benchmark_func,
            iterations=iterations,
            operation_count=len(persona_ids)
        )
        
        # Add details
        result.details = {
            "persona_count": len(persona_ids),
            "persona_ids": persona_ids
        }
        
        return result
    
    def benchmark_session_creation(self, iterations: int = 10) -> BenchmarkResult:
        """
        Benchmark session creation performance.
        
        Args:
            iterations (int): Number of benchmark iterations (default: 10)
            
        Returns:
            BenchmarkResult: Benchmark result
        """
        # Get a persona id for benchmark
        persona_ids = self.persona_manager.get_available_personas()
        if not persona_ids:
            # Use mock persona
            persona_id = "test_persona"
        else:
            persona_id = persona_ids[0]
            
        session_ids = []
        
        # Define benchmark function
        def benchmark_func():
            session_id = str(uuid.uuid4())
            session_ids.append(session_id)
            
            self.session_manager.create_session(
                session_id=session_id,
                client_name="Benchmark Client",
                persona_id=persona_id
            )
        
        # Run benchmark
        result = self.benchmark_function(
            name="session_creation",
            func=benchmark_func,
            iterations=iterations
        )
        
        # Clean up created sessions
        for session_id in session_ids:
            self.session_manager.delete_session(session_id)
        
        # Add details
        result.details = {
            "persona_id": persona_id,
            "sessions_created": len(session_ids),
            "sessions_deleted": len(session_ids)
        }
        
        return result
    
    def benchmark_message_processing(self, iterations: int = 5) -> BenchmarkResult:
        """
        Benchmark message processing performance.
        
        Args:
            iterations (int): Number of benchmark iterations (default: 5)
            
        Returns:
            BenchmarkResult: Benchmark result
        """
        # Get a mock provider
        provider = self.provider_manager.get_provider("mock")
        if not provider:
            self.logger.warning("Mock provider not available, skipping benchmark")
            
            # Create empty result
            result = BenchmarkResult(
                name="message_processing",
                iterations=0,
                duration=0
            )
            
            self.results[result.name] = result
            return result
            
        # Create a session for benchmark
        session_id = str(uuid.uuid4())
        session = self.session_manager.create_session(
            session_id=session_id,
            client_name="Benchmark Client",
            persona_id="test_persona"
        )
        
        if not session:
            self.logger.warning("Failed to create session, skipping benchmark")
            
            # Create empty result
            result = BenchmarkResult(
                name="message_processing",
                iterations=0,
                duration=0
            )
            
            self.results[result.name] = result
            return result
            
        # Add system message
        session.add_message({
            "role": MessageRole.SYSTEM.value,
            "content": "You are a helpful assistant."
        })
        
        # Prepare test messages
        test_messages = [
            "Hello, how are you today?",
            "Can you tell me about anxiety?",
            "What are some coping strategies for stress?",
            "I've been feeling overwhelmed at work lately.",
            "What are some relaxation techniques I can try?"
        ]
        
        processed_count = 0
        
        # Define benchmark function
        def benchmark_func():
            nonlocal processed_count
            
            # Add client message
            message = test_messages[processed_count % len(test_messages)]
            session.add_message({
                "role": MessageRole.CLIENT.value,
                "content": message
            })
            
            # Get messages
            messages = session.get_messages()
            
            # Generate response
            response = provider.generate_response(messages)
            
            # Add response to session
            session.add_message({
                "role": MessageRole.PERSONA.value,
                "content": response.content
            })
            
            processed_count += 1
        
        # Run benchmark
        result = self.benchmark_function(
            name="message_processing",
            func=benchmark_func,
            iterations=iterations
        )
        
        # Clean up
        self.session_manager.delete_session(session_id)
        
        # Add details
        result.details = {
            "provider": "mock",
            "session_id": session_id,
            "messages_processed": processed_count,
            "avg_response_length": session.get_messages()[-1]["content"] if session.messages_count > 0 else 0
        }
        
        return result
    
    def benchmark_session_persistence(self, iterations: int = 10) -> BenchmarkResult:
        """
        Benchmark session persistence performance.
        
        Args:
            iterations (int): Number of benchmark iterations (default: 10)
            
        Returns:
            BenchmarkResult: Benchmark result
        """
        # Create a session for benchmark
        session_id = str(uuid.uuid4())
        session = self.session_manager.create_session(
            session_id=session_id,
            client_name="Benchmark Client",
            persona_id="test_persona"
        )
        
        if not session:
            self.logger.warning("Failed to create session, skipping benchmark")
            
            # Create empty result
            result = BenchmarkResult(
                name="session_persistence",
                iterations=0,
                duration=0
            )
            
            self.results[result.name] = result
            return result
            
        # Add system message
        session.add_message({
            "role": MessageRole.SYSTEM.value,
            "content": "You are a helpful assistant."
        })
        
        # Define benchmark function
        def benchmark_func():
            # Add a new message
            session.add_message({
                "role": MessageRole.CLIENT.value,
                "content": f"Test message {session.messages_count}"
            })
            
            # Save the session
            self.session_manager.save_session(session)
            
            # Retrieve the session
            retrieved_session = self.session_manager.get_session(session_id)
            
            # Add a persona message
            retrieved_session.add_message({
                "role": MessageRole.PERSONA.value,
                "content": f"Response to message {retrieved_session.messages_count - 1}"
            })
            
            # Save again
            self.session_manager.save_session(retrieved_session)
        
        # Run benchmark
        result = self.benchmark_function(
            name="session_persistence",
            func=benchmark_func,
            iterations=iterations,
            operation_count=4  # Add message, save, retrieve, save again
        )
        
        # Clean up
        self.session_manager.delete_session(session_id)
        
        # Add details
        result.details = {
            "session_id": session_id,
            "final_message_count": session.messages_count
        }
        
        return result
    
    def benchmark_session_analysis(self, iterations: int = 5) -> BenchmarkResult:
        """
        Benchmark session analysis performance.
        
        Args:
            iterations (int): Number of benchmark iterations (default: 5)
            
        Returns:
            BenchmarkResult: Benchmark result
        """
        # Create a session for benchmark
        session_id = str(uuid.uuid4())
        session = self.session_manager.create_session(
            session_id=session_id,
            client_name="Benchmark Client",
            persona_id="test_persona"
        )
        
        if not session:
            self.logger.warning("Failed to create session, skipping benchmark")
            
            # Create empty result
            result = BenchmarkResult(
                name="session_analysis",
                iterations=0,
                duration=0
            )
            
            self.results[result.name] = result
            return result
            
        # Add test conversation
        session.add_message({
            "role": MessageRole.SYSTEM.value,
            "content": "You are a professional therapist."
        })
        
        session.add_message({
            "role": MessageRole.PERSONA.value,
            "content": "Hello! How are you feeling today?"
        })
        
        session.add_message({
            "role": MessageRole.CLIENT.value,
            "content": "I've been feeling anxious about work lately. I can't seem to focus."
        })
        
        session.add_message({
            "role": MessageRole.PERSONA.value,
            "content": "I'm sorry to hear you're feeling anxious. Can you tell me more about what's happening at work?"
        })
        
        session.add_message({
            "role": MessageRole.CLIENT.value,
            "content": "I have a big project due next week and I keep procrastinating. Then I panic and feel overwhelmed."
        })
        
        session.add_message({
            "role": MessageRole.PERSONA.value,
            "content": "That sounds challenging. The cycle of procrastination and panic can be difficult to break. Let's discuss some strategies to help you manage this situation."
        })
        
        # Save the session
        self.session_manager.save_session(session)
        
        # Create analyzer
        analyzer = SessionAnalyzer(
            session_manager=self.session_manager
        )
        
        # Define benchmark function
        def benchmark_func():
            analyzer.analyze_session(session_id)
        
        # Run benchmark
        result = self.benchmark_function(
            name="session_analysis",
            func=benchmark_func,
            iterations=iterations
        )
        
        # Clean up
        self.session_manager.delete_session(session_id)
        
        # Add details
        result.details = {
            "session_id": session_id,
            "message_count": session.messages_count
        }
        
        return result
    
    def benchmark_report_generation(self, iterations: int = 5) -> BenchmarkResult:
        """
        Benchmark report generation performance.
        
        Args:
            iterations (int): Number of benchmark iterations (default: 5)
            
        Returns:
            BenchmarkResult: Benchmark result
        """
        # Create a session for benchmark
        session_id = str(uuid.uuid4())
        session = self.session_manager.create_session(
            session_id=session_id,
            client_name="Benchmark Client",
            persona_id="test_persona"
        )
        
        if not session:
            self.logger.warning("Failed to create session, skipping benchmark")
            
            # Create empty result
            result = BenchmarkResult(
                name="report_generation",
                iterations=0,
                duration=0
            )
            
            self.results[result.name] = result
            return result
            
        # Add test conversation
        session.add_message({
            "role": MessageRole.SYSTEM.value,
            "content": "You are a professional therapist."
        })
        
        session.add_message({
            "role": MessageRole.PERSONA.value,
            "content": "Hello! How are you feeling today?"
        })
        
        session.add_message({
            "role": MessageRole.CLIENT.value,
            "content": "I've been feeling anxious about work lately. I can't seem to focus."
        })
        
        # Save the session
        self.session_manager.save_session(session)
        
        # Create analyzer
        analyzer = SessionAnalyzer(
            session_manager=self.session_manager
        )
        
        # Analyze the session
        analysis_result = analyzer.analyze_session(session_id)
        if not analysis_result:
            self.logger.warning("Failed to analyze session, skipping benchmark")
            
            # Create empty result
            result = BenchmarkResult(
                name="report_generation",
                iterations=0,
                duration=0
            )
            
            self.results[result.name] = result
            return result
            
        # Import report generator
        from src.smart_steps_ai.analysis import ReportGenerator, ReportFormat
        
        report_generator = ReportGenerator()
        
        # Define benchmark function
        def benchmark_func():
            # Generate reports in different formats
            report_generator.generate_report(
                analysis_result=analysis_result,
                format=ReportFormat.TEXT,
                include_visualizations=False,
                level_of_detail="standard"
            )
            
            report_generator.generate_report(
                analysis_result=analysis_result,
                format=ReportFormat.MARKDOWN,
                include_visualizations=False,
                level_of_detail="standard"
            )
            
            report_generator.generate_report(
                analysis_result=analysis_result,
                format=ReportFormat.HTML,
                include_visualizations=False,
                level_of_detail="standard"
            )
        
        # Run benchmark
        result = self.benchmark_function(
            name="report_generation",
            func=benchmark_func,
            iterations=iterations,
            operation_count=3  # Three report formats
        )
        
        # Clean up
        self.session_manager.delete_session(session_id)
        
        # Add details
        result.details = {
            "session_id": session_id,
            "analysis_result_insights": len(analysis_result.insights) if analysis_result else 0,
            "formats": ["text", "markdown", "html"]
        }
        
        return result
    
    def save_results(self, output_path: Optional[Path] = None) -> Path:
        """
        Save benchmark results to a file.
        
        Args:
            output_path (Optional[Path]): Output file path (default: None)
                If None, a default path in the output directory will be used
                
        Returns:
            Path: Path to the saved results file
        """
        if not output_path:
            # Generate default output path
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"benchmark_results_{timestamp}.json"
        
        # Create result dictionary
        result_dict = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "benchmarks": {name: asdict(result) for name, result in self.results.items()}
        }
        
        # Save to file
        try:
            # Create directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write results
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2)
                
            self.logger.info(f"Benchmark results saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save benchmark results: {str(e)}")
        
        return output_path
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """
        Generate a human-readable report of benchmark results.
        
        Args:
            output_path (Optional[Path]): Output file path (default: None)
                If None, a default path in the output directory will be used
                
        Returns:
            str: Report content
        """
        if not self.results:
            return "No benchmark results available."
            
        # Generate report content
        report = [
            "# Smart Steps AI Benchmark Report",
            f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"Total benchmarks: {len(self.results)}",
            "",
            "| Benchmark | Ops/Sec | Avg (ms) | p95 (ms) | Min (ms) | Max (ms) |",
            "|-----------|---------|----------|----------|----------|----------|"
        ]
        
        # Add result summary rows
        for name, result in self.results.items():
            report.append(
                f"| {name} | "
                f"{result.operations_per_second:.2f} | "
                f"{result.avg_duration_per_op * 1000:.2f} | "
                f"{result.percentile_95 * 1000:.2f} | "
                f"{result.min_duration * 1000:.2f} | "
                f"{result.max_duration * 1000:.2f} |"
            )
            
        report.append("")
        
        # Add detailed sections for each benchmark
        report.append("## Detailed Results")
        
        for name, result in self.results.items():
            report.append(f"### {name}")
            report.append(f"- Operations per second: {result.operations_per_second:.2f}")
            report.append(f"- Average duration: {result.avg_duration_per_op * 1000:.2f} ms")
            report.append(f"- Median duration: {result.median_duration * 1000:.2f} ms")
            report.append(f"- 90th percentile: {result.percentile_90 * 1000:.2f} ms")
            report.append(f"- 95th percentile: {result.percentile_95 * 1000:.2f} ms")
            report.append(f"- 99th percentile: {result.percentile_99 * 1000:.2f} ms")
            report.append(f"- Standard deviation: {result.std_deviation * 1000:.2f} ms")
            report.append(f"- Iterations: {result.iterations}")
            report.append(f"- Total operations: {result.operation_count}")
            report.append(f"- Total duration: {result.duration:.2f} seconds")
            
            if result.details:
                report.append("- Details:")
                for key, value in result.details.items():
                    report.append(f"  - {key}: {value}")
                    
            report.append("")
        
        # Add performance insights
        report.append("## Performance Insights")
        
        # Identify slowest operations
        sorted_by_avg = sorted(
            self.results.items(), 
            key=lambda x: x[1].avg_duration_per_op, 
            reverse=True
        )
        
        report.append("### Slowest Operations")
        for name, result in sorted_by_avg[:3]:
            report.append(f"- {name}: {result.avg_duration_per_op * 1000:.2f} ms per operation")
            
        report.append("")
        
        # Identify most variable operations
        sorted_by_std = sorted(
            self.results.items(), 
            key=lambda x: x[1].std_deviation, 
            reverse=True
        )
        
        report.append("### Most Variable Operations")
        for name, result in sorted_by_std[:3]:
            variation_pct = (result.std_deviation / result.avg_duration_per_op) * 100 if result.avg_duration_per_op > 0 else 0
            report.append(f"- {name}: ±{variation_pct:.1f}% variation (std dev: {result.std_deviation * 1000:.2f} ms)")
            
        report.append("")
        
        # Join report lines
        report_content = "\n".join(report)
        
        # Save report if output path provided
        if output_path:
            try:
                # Create directory if it doesn't exist
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write report
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                    
                self.logger.info(f"Benchmark report saved to {output_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to save benchmark report: {str(e)}")
        
        return report_content


if __name__ == "__main__":
    # Run benchmarks
    benchmark_suite = BenchmarkSuite(use_mock=True)
    results = benchmark_suite.run_all_benchmarks()
    
    # Generate and save reports
    output_dir = Path("./output/benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # Save raw results
    json_path = output_dir / f"benchmark_results_{timestamp}.json"
    benchmark_suite.save_results(json_path)
    
    # Save human-readable report
    report_path = output_dir / f"benchmark_report_{timestamp}.md"
    report = benchmark_suite.generate_report(report_path)
    
    print(f"\nBenchmarks completed. Results saved to:")
    print(f"- Raw results: {json_path}")
    print(f"- Report: {report_path}")
