"""
Smart Steps AI Module - Performance Test Runner

This script runs all performance tests for the Smart Steps AI Module and
generates a comprehensive report.

Usage:
    python -m tests.performance.run_performance_tests [--full] [--scenarios SCENARIOS]
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

# Initialize console
console = Console()

class PerformanceTestRunner:
    """Runs the performance test suite and generates reports."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.root_dir = Path("G:/My Drive/Deftech/SmartSteps/smart_steps_ai")
        self.tests_dir = self.root_dir / "tests" / "performance"
        self.results_dir = self.tests_dir / "results"
        self.report_template = self.root_dir / "docs" / "templates" / "performance_report_template.md"
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Test timestamp and ID
        self.timestamp = datetime.datetime.now()
        self.test_id = self.timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Results dictionary
        self.results = {
            "test_id": self.test_id,
            "timestamp": self.timestamp.isoformat(),
            "scenarios": {},
            "summary": {}
        }
    
    def run_benchmark_tests(self):
        """Run pytest-benchmark tests."""
        console.print("\n[bold blue]Running Benchmark Tests[/bold blue]")
        
        try:
            # Run the benchmark tests
            result = subprocess.run(
                ["pytest", str(self.tests_dir / "test_benchmark.py"), "-v", "--benchmark-json", 
                 str(self.results_dir / f"benchmark_{self.test_id}.json")],
                capture_output=True,
                text=True,
                check=False  # Don't raise an exception on non-zero exit
            )
            
            console.print(result.stdout)
            
            if result.returncode != 0:
                console.print(f"[bold red]Benchmark tests failed with code {result.returncode}[/bold red]")
                console.print(result.stderr)
                self.results["scenarios"]["benchmark"] = {
                    "status": "failed",
                    "exit_code": result.returncode,
                    "error": result.stderr
                }
            else:
                console.print("[bold green]Benchmark tests completed successfully[/bold green]")
                
                # Load the benchmark results
                benchmark_file = self.results_dir / f"benchmark_{self.test_id}.json"
                if benchmark_file.exists():
                    with open(benchmark_file, "r") as f:
                        benchmark_data = json.load(f)
                    
                    self.results["scenarios"]["benchmark"] = {
                        "status": "success",
                        "data": benchmark_data
                    }
                else:
                    console.print("[bold yellow]Warning: Benchmark results file not found[/bold yellow]")
                    self.results["scenarios"]["benchmark"] = {
                        "status": "warning",
                        "message": "Results file not found"
                    }
        
        except Exception as e:
            console.print(f"[bold red]Error running benchmark tests: {str(e)}[/bold red]")
            self.results["scenarios"]["benchmark"] = {
                "status": "error",
                "error": str(e)
            }
    
    def run_memory_profiling(self):
        """Run memory profiling tests."""
        console.print("\n[bold blue]Running Memory Profiling Tests[/bold blue]")
        
        try:
            # Run the memory profiler
            memory_output_file = self.results_dir / f"memory_profile_{self.test_id}.txt"
            
            # Redirect output to file
            with open(memory_output_file, "w") as f:
                result = subprocess.run(
                    ["python", "-m", "tests.performance.memory_profiler"],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            
            # Display the output
            with open(memory_output_file, "r") as f:
                console.print(f.read())
            
            if result.returncode != 0:
                console.print(f"[bold red]Memory profiling failed with code {result.returncode}[/bold red]")
                console.print(result.stderr)
                self.results["scenarios"]["memory_profiling"] = {
                    "status": "failed",
                    "exit_code": result.returncode,
                    "error": result.stderr
                }
            else:
                console.print("[bold green]Memory profiling completed successfully[/bold green]")
                self.results["scenarios"]["memory_profiling"] = {
                    "status": "success",
                    "output_file": str(memory_output_file)
                }
        
        except Exception as e:
            console.print(f"[bold red]Error running memory profiling: {str(e)}[/bold red]")
            self.results["scenarios"]["memory_profiling"] = {
                "status": "error",
                "error": str(e)
            }
    
    def run_load_test_scenario(self, name, num_users, messages_per_user, include_analysis=True):
        """Run a specific load test scenario."""
        console.print(f"\n[bold blue]Running Load Test Scenario: {name}[/bold blue]")
        console.print(f"Users: {num_users}, Messages/User: {messages_per_user}, Analysis: {include_analysis}")
        
        try:
            # Build command arguments
            cmd = [
                "python", "-m", "tests.performance.load_test",
                "--num-users", str(num_users),
                "--messages-per-user", str(messages_per_user)
            ]
            
            if not include_analysis:
                cmd.append("--no-include-analysis")
            
            # Run the load test
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            console.print(result.stdout)
            
            if result.returncode != 0:
                console.print(f"[bold red]Load test scenario '{name}' failed with code {result.returncode}[/bold red]")
                console.print(result.stderr)
                self.results["scenarios"][f"load_test_{name}"] = {
                    "status": "failed",
                    "exit_code": result.returncode,
                    "error": result.stderr
                }
            else:
                console.print(f"[bold green]Load test scenario '{name}' completed successfully[/bold green]")
                
                # Find the most recent load test results file
                load_test_files = list(self.results_dir.glob("loadtest_results_*.json"))
                if load_test_files:
                    # Sort by modification time (newest first)
                    newest_file = sorted(load_test_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
                    
                    # Load the results
                    with open(newest_file, "r") as f:
                        load_test_data = json.load(f)
                    
                    self.results["scenarios"][f"load_test_{name}"] = {
                        "status": "success",
                        "data": load_test_data,
                        "file": str(newest_file)
                    }
                else:
                    console.print("[bold yellow]Warning: Load test results file not found[/bold yellow]")
                    self.results["scenarios"][f"load_test_{name}"] = {
                        "status": "warning",
                        "message": "Results file not found"
                    }
        
        except Exception as e:
            console.print(f"[bold red]Error running load test scenario '{name}': {str(e)}[/bold red]")
            self.results["scenarios"][f"load_test_{name}"] = {
                "status": "error",
                "error": str(e)
            }
    
    def run_api_stress_test(self):
        """Run API stress test with Locust."""
        console.print("\n[bold blue]Running API Stress Test with Locust[/bold blue]")
        
        try:
            # Run Locust in headless mode
            locust_output_file = self.results_dir / f"locust_{self.test_id}.txt"
            
            # Redirect output to file
            with open(locust_output_file, "w") as f:
                result = subprocess.run(
                    [
                        "locust", "-f", str(self.tests_dir / "locustfile.py"),
                        "--headless", "--users", "100", "--spawn-rate", "10",
                        "--run-time", "2m", "--host", "http://localhost:8000",
                        "--csv", str(self.results_dir / f"locust_{self.test_id}")
                    ],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
            
            # Display the output
            with open(locust_output_file, "r") as f:
                console.print(f.read())
            
            if result.returncode != 0:
                console.print(f"[bold red]API stress test failed with code {result.returncode}[/bold red]")
                console.print(result.stderr)
                self.results["scenarios"]["api_stress"] = {
                    "status": "failed",
                    "exit_code": result.returncode,
                    "error": result.stderr
                }
            else:
                console.print("[bold green]API stress test completed successfully[/bold green]")
                
                # Check if CSV files were generated
                stats_file = self.results_dir / f"locust_{self.test_id}_stats.csv"
                if stats_file.exists():
                    self.results["scenarios"]["api_stress"] = {
                        "status": "success",
                        "output_file": str(locust_output_file),
                        "stats_file": str(stats_file),
                        "requests_file": str(self.results_dir / f"locust_{self.test_id}_stats_history.csv"),
                        "failures_file": str(self.results_dir / f"locust_{self.test_id}_failures.csv")
                    }
                else:
                    console.print("[bold yellow]Warning: Locust CSV results files not found[/bold yellow]")
                    self.results["scenarios"]["api_stress"] = {
                        "status": "warning",
                        "message": "Results files not found",
                        "output_file": str(locust_output_file)
                    }
        
        except Exception as e:
            console.print(f"[bold red]Error running API stress test: {str(e)}[/bold red]")
            self.results["scenarios"]["api_stress"] = {
                "status": "error",
                "error": str(e)
            }
    
    def check_server_running(self):
        """Check if the API server is running."""
        console.print("\n[bold blue]Checking if API server is running[/bold blue]")
        
        try:
            import requests
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                console.print("[bold green]API server is running.[/bold green]")
                return True
            else:
                console.print(f"[bold yellow]API server responded with status {response.status_code}[/bold yellow]")
                return False
        except Exception as e:
            console.print(f"[bold red]API server does not appear to be running: {str(e)}[/bold red]")
            console.print("Please start the API server with 'python run_api_server.bat' before running load tests.")
            return False
    
    def start_api_server(self):
        """Start the API server if it's not running."""
        console.print("\n[bold blue]Starting API server[/bold blue]")
        
        try:
            # Check if server is already running
            if self.check_server_running():
                return True
            
            # Start the server
            server_process = subprocess.Popen(
                ["python", str(self.root_dir / "run_api_server.bat")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start (max 30 seconds)
            console.print("Waiting for server to start...")
            for _ in range(30):
                if self.check_server_running():
                    console.print("[bold green]API server started successfully.[/bold green]")
                    return True
                time.sleep(1)
            
            console.print("[bold red]Failed to start API server within timeout period.[/bold red]")
            return False
        
        except Exception as e:
            console.print(f"[bold red]Error starting API server: {str(e)}[/bold red]")
            return False
            
    def generate_report(self):
        """Generate a comprehensive performance test report."""
        console.print("\n[bold blue]Generating Performance Test Report[/bold blue]")
        
        # Calculate summary statistics
        self._calculate_summary()
        
        # Save results JSON
        results_file = self.results_dir / f"performance_results_{self.test_id}.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        console.print(f"Results saved to: [bold]{results_file}[/bold]")
        
        # Generate markdown report
        report_file = self.results_dir / f"performance_report_{self.test_id}.md"
        self._generate_markdown_report(report_file)
        
        console.print(f"Report generated: [bold]{report_file}[/bold]")
        
        # Display summary
        self._display_summary()
    
    def _calculate_summary(self):
        """Calculate summary statistics from all test results."""
        summary = {
            "overall_status": "success",
            "metrics": {},
            "targets": {
                "response_time": {
                    "target": "< 500ms for simple operations, < 2s for complex operations",
                    "status": "unknown",
                    "actual": "Not measured"
                },
                "throughput": {
                    "target": "50+ concurrent users, 100+ messages per minute",
                    "status": "unknown",
                    "actual": "Not measured"
                },
                "memory_usage": {
                    "target": "< 200MB base, < 50% growth after 1000 operations",
                    "status": "unknown",
                    "actual": "Not measured"
                },
                "error_rate": {
                    "target": "< 1% under normal load",
                    "status": "unknown",
                    "actual": "Not measured"
                }
            }
        }
        
        # Check if any scenario failed
        for scenario, data in self.results["scenarios"].items():
            if data["status"] in ["failed", "error"]:
                summary["overall_status"] = "failed"
                break
            elif data["status"] == "warning" and summary["overall_status"] != "failed":
                summary["overall_status"] = "warning"
        
        # Store summary
        self.results["summary"] = summary
    
    def _generate_markdown_report(self, report_file):
        """Generate a markdown report from the template."""
        try:
            # Generate a basic report
            with open(report_file, "w") as f:
                f.write(f"# Performance Test Report - {self.test_id}\n\n")
                f.write(f"Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Test Results\n\n")
                for scenario, data in self.results["scenarios"].items():
                    f.write(f"### {scenario}: {data['status']}\n\n")
                    
                    if data["status"] == "success":
                        if scenario in ["benchmark", "memory_profiling"] or scenario.startswith("load_test_"):
                            f.write("See detailed results in the accompanying JSON files.\n\n")
                    else:
                        if "error" in data:
                            f.write(f"Error: {data['error']}\n\n")
                
                f.write("## Performance Summary\n\n")
                f.write(f"Overall Status: {self.results['summary']['overall_status']}\n\n")
                
                if "targets" in self.results["summary"]:
                    f.write("### Performance Targets\n\n")
                    for target, data in self.results["summary"]["targets"].items():
                        f.write(f"- {target.replace('_', ' ').title()}: {data['status']} ({data['actual']} vs target {data['target']})\n")
                
        except Exception as e:
            console.print(f"[bold red]Error generating report: {str(e)}[/bold red]")
    
    def _display_summary(self):
        """Display a summary of the test results."""
        console.print("\n[bold green]Performance Test Summary[/bold green]")
        
        # Create a table for scenario results
        table = Table(title="Test Scenarios")
        table.add_column("Scenario", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        for scenario, data in self.results["scenarios"].items():
            status = data["status"]
            status_style = {
                "success": "green",
                "warning": "yellow",
                "failed": "red",
                "error": "red bold"
            }.get(status, "white")
            
            details = "See report for details"
            if status in ["failed", "error"] and "error" in data:
                details = data["error"][:50] + ("..." if len(data["error"]) > 50 else "")
            
            table.add_row(scenario, f"[{status_style}]{status}[/{status_style}]", details)
        
        console.print(table)
        
        # Overall result
        overall_status = self.results["summary"]["overall_status"]
        status_style = {
            "success": "green bold",
            "warning": "yellow bold",
            "failed": "red bold"
        }.get(overall_status, "white bold")
        
        console.print(f"\nOverall Result: [{status_style}]{overall_status.upper()}[/{status_style}]")
        console.print(f"Report: [bold]{self.results_dir / f'performance_report_{self.test_id}.md'}[/bold]")
    
    def run_all_tests(self):
        """Run all performance tests."""
        console.print("[bold blue]Running All Performance Tests[/bold blue]")
        
        # Start with benchmark tests (don't require server)
        self.run_benchmark_tests()
        
        # Run memory profiling (doesn't require server)
        self.run_memory_profiling()
        
        # Check if server is running, start if needed
        server_running = self.check_server_running() or self.start_api_server()
        
        if server_running:
            # Run load test scenarios
            self.run_load_test_scenario("scenario1", 1, 100)  # Single user intensive
            self.run_load_test_scenario("scenario2", 50, 10)  # Multi-user concurrent
            self.run_load_test_scenario("scenario3", 10, 20, False)  # No analysis
            self.run_load_test_scenario("scenario4", 5, 50)  # Long session analysis
            
            # Run API stress test
            self.run_api_stress_test()
        else:
            console.print("[bold red]Skipping tests that require API server.[/bold red]")
        
        # Generate report
        self.generate_report()
        
        console.print("\n[bold green]All performance tests completed![/bold green]")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run performance tests for Smart Steps AI Module")
    
    parser.add_argument(
        "--full", action="store_true",
        help="Run full suite of tests including long-running tests"
    )
    
    parser.add_argument(
        "--scenarios", type=str, choices=["benchmark", "memory", "load", "api", "all"],
        default="all", help="Specify which test scenarios to run"
    )
    
    args = parser.parse_args()
    
    # Create and run the test runner
    runner = PerformanceTestRunner()
    
    if args.scenarios == "benchmark":
        runner.run_benchmark_tests()
    elif args.scenarios == "memory":
        runner.run_memory_profiling()
    elif args.scenarios == "load":
        if runner.check_server_running() or runner.start_api_server():
            runner.run_load_test_scenario("scenario1", 1, 50)
            runner.run_load_test_scenario("scenario2", 20, 5)
    elif args.scenarios == "api":
        if runner.check_server_running() or runner.start_api_server():
            runner.run_api_stress_test()
    else:
        # Run all tests
        runner.run_all_tests()
    
    # Generate report
    runner.generate_report()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Performance tests interrupted by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error during performance tests: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)
