"""End-to-end tests for the Smart Steps AI Professional Persona module."""

import os
import sys
import json
import uuid
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
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


class EndToEndTestRunner:
    """
    Runner for end-to-end tests of the Smart Steps AI module.
    
    This class provides functionality for running end-to-end tests that validate
    the integration of all major components of the Smart Steps AI module.
    """
    
    def __init__(
        self,
        test_dir: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
        log_level: str = "info",
        use_mock: bool = True,
    ):
        """
        Initialize the end-to-end test runner.
        
        Args:
            test_dir (Optional[Union[str, Path]]): Directory for test scenarios (default: None)
                If None, uses ./tests/scenarios
            output_dir (Optional[Union[str, Path]]): Directory for test outputs (default: None)
                If None, uses ./tests/output
            log_level (str): Log level for the test runner (default: "info")
            use_mock (bool): Whether to use mock providers (default: True)
        """
        # Set up directories
        self.test_dir = Path(test_dir) if test_dir else project_root / "tests" / "scenarios"
        self.output_dir = Path(output_dir) if output_dir else project_root / "tests" / "output"
        
        # Create directories if they don't exist
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = StructuredLogger(
            name="e2e_tests",
            level=log_level,
            context={"module": "tests", "use_mock": use_mock}
        )
        
        # Test configuration
        self.use_mock = use_mock
        self.test_scenarios = []
        self.test_results = []
        
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
            
        self.logger.info("End-to-end test runner initialized")
    
    def discover_test_scenarios(self) -> List[Dict[str, Any]]:
        """
        Discover test scenarios in the test directory.
        
        Returns:
            List[Dict[str, Any]]: List of discovered test scenarios
        """
        scenarios = []
        
        for scenario_file in self.test_dir.glob("*.json"):
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    scenario = json.load(f)
                    
                # Validate scenario
                if self._validate_scenario(scenario):
                    scenarios.append({
                        "name": scenario.get("name", scenario_file.stem),
                        "file": scenario_file,
                        "data": scenario
                    })
            except Exception as e:
                self.logger.error(f"Error loading scenario from {scenario_file}", 
                                context={"error": str(e)})
        
        self.test_scenarios = scenarios
        self.logger.info(f"Discovered {len(scenarios)} test scenarios")
        return scenarios
    
    def _validate_scenario(self, scenario: Dict[str, Any]) -> bool:
        """
        Validate a test scenario.
        
        Args:
            scenario (Dict[str, Any]): Scenario to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "persona", "client", "messages"]
        for field in required_fields:
            if field not in scenario:
                self.logger.error(f"Scenario missing required field: {field}")
                return False
                
        # Check messages format
        if not isinstance(scenario["messages"], list):
            self.logger.error("Scenario messages must be a list")
            return False
            
        for message in scenario["messages"]:
            if not isinstance(message, dict) or "role" not in message or "content" not in message:
                self.logger.error("Each message must have 'role' and 'content' fields")
                return False
        
        return True
    
    def create_sample_scenarios(self, count: int = 3) -> None:
        """
        Create sample test scenarios.
        
        Args:
            count (int): Number of sample scenarios to create (default: 3)
        """
        scenarios = [
            {
                "name": "Basic Conversation",
                "description": "Tests a basic conversation with a client.",
                "persona": "dr_hayes",
                "client": "John Doe",
                "messages": [
                    {"role": "client", "content": "Hello, I've been feeling anxious lately."},
                    {"role": "persona", "content": "I understand. Can you tell me more about your anxiety?"},
                    {"role": "client", "content": "It's mainly when I have to speak in public."},
                    {"role": "persona", "content": "Public speaking anxiety is common. Have you noticed any physical symptoms?"},
                    {"role": "client", "content": "Yes, my heart races and I get sweaty palms."}
                ],
                "expected": {
                    "insights": ["anxiety", "public speaking", "physical symptoms"],
                    "analysis": True,
                    "memory": True
                }
            },
            {
                "name": "Trauma Discussion",
                "description": "Tests handling of trauma-related content.",
                "persona": "dr_rivera",
                "client": "Jane Smith",
                "messages": [
                    {"role": "client", "content": "I've been having flashbacks to my accident."},
                    {"role": "persona", "content": "I'm sorry to hear that. How often are these flashbacks occurring?"},
                    {"role": "client", "content": "Almost daily, especially when I hear loud noises."},
                    {"role": "persona", "content": "That sounds difficult. How are these flashbacks affecting your daily life?"},
                    {"role": "client", "content": "I've been avoiding driving and loud places."}
                ],
                "expected": {
                    "insights": ["trauma", "flashbacks", "avoidance"],
                    "analysis": True,
                    "memory": True
                }
            },
            {
                "name": "Goal Setting",
                "description": "Tests goal-setting conversation flow.",
                "persona": "dr_hayes",
                "client": "Robert Johnson",
                "messages": [
                    {"role": "client", "content": "I want to improve my work-life balance."},
                    {"role": "persona", "content": "That's a good goal. What specific challenges are you facing with your work-life balance?"},
                    {"role": "client", "content": "I work too many hours and don't have time for myself."},
                    {"role": "persona", "content": "I understand. What would a better balance look like to you?"},
                    {"role": "client", "content": "I'd like to finish work by 6pm and have weekends free."}
                ],
                "expected": {
                    "insights": ["work-life balance", "goal setting", "boundaries"],
                    "analysis": True,
                    "memory": True
                }
            }
        ]
        
        # Only create the requested number of scenarios
        scenarios = scenarios[:count]
        
        # Save scenarios to files
        for i, scenario in enumerate(scenarios):
            filename = self.test_dir / f"sample_scenario_{i+1}.json"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(scenario, f, indent=2)
                self.logger.info(f"Created sample scenario: {filename}")
            except Exception as e:
                self.logger.error(f"Error creating sample scenario: {str(e)}")
                
        self.logger.info(f"Created {len(scenarios)} sample test scenarios")
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a test scenario.
        
        Args:
            scenario (Dict[str, Any]): Scenario to run
            
        Returns:
            Dict[str, Any]: Test results
        """
        scenario_data = scenario["data"]
        scenario_name = scenario["name"]
        
        self.logger.info(f"Running scenario: {scenario_name}")
        
        # Start timing
        self.logger.start_timer(f"scenario_{scenario_name}")
        
        # Create a session
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            client_name=scenario_data["client"],
            persona_name=scenario_data["persona"],
            tags=scenario_data.get("tags", [])
        )
        
        # Add any system message
        system_content = scenario_data.get("system", "You are a professional therapist helping a client.")
        session.add_message(Message(
            role=MessageRole.SYSTEM,
            content=system_content
        ))
        
        # Process messages
        for message_data in scenario_data["messages"]:
            role_str = message_data["role"].upper()
            role = getattr(MessageRole, role_str) if hasattr(MessageRole, role_str) else MessageRole.CLIENT
            
            message = Message(
                role=role,
                content=message_data["content"]
            )
            
            # Add message to session
            session.add_message(message)
            
            # If this is a client message and we're using a provider, generate a response
            if role == MessageRole.CLIENT and not message_data.get("skip_response", False) and self.use_mock:
                # Get provider
                provider = self.provider_manager.get_provider("mock")
                
                # Generate response
                provider_response = provider.generate_response(session.messages)
                
                # Add response to session
                session.add_message(Message(
                    role=MessageRole.PERSONA,
                    content=provider_response.content
                ))
        
        # Save session
        self.session_manager.save_session(session)
        
        # Analyze session
        analyzer = SessionAnalyzer(
            session_manager=self.session_manager,
            memory_manager=self.memory_manager,
            persona_manager=self.persona_manager
        )
        
        analysis_result = analyzer.analyze_session(session_id)
        
        # Stop timing
        elapsed = self.logger.stop_timer(f"scenario_{scenario_name}", level="info")
        
        # Check expected outcomes
        success = True
        failures = []
        
        if "expected" in scenario_data:
            expected = scenario_data["expected"]
            
            # Check for expected insights
            if "insights" in expected and analysis_result:
                found_insights = 0
                expected_insights = expected["insights"]
                
                for insight in analysis_result.insights:
                    for expected_insight in expected_insights:
                        if expected_insight.lower() in insight.text.lower():
                            found_insights += 1
                            break
                
                if found_insights < len(expected_insights):
                    success = False
                    failures.append(f"Missing expected insights. Found {found_insights}/{len(expected_insights)}")
            
            # Check for expected analysis
            if "analysis" in expected and expected["analysis"] and not analysis_result:
                success = False
                failures.append("Analysis failed to generate")
            
            # Check for expected memory storage
            if "memory" in expected and expected["memory"] and self.memory_manager.enabled:
                # Check if session was stored in memory
                memories = self.memory_manager.search_memories(session.client_name, limit=5)
                if not memories:
                    success = False
                    failures.append("Session not stored in memory")
        
        # Prepare result
        result = {
            "scenario": scenario_name,
            "session_id": session_id,
            "success": success,
            "failures": failures,
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat(),
            "messages_count": session.messages_count,
            "insights_count": len(analysis_result.insights) if analysis_result else 0,
        }
        
        # Log result
        log_level = "info" if success else "warning"
        getattr(self.logger, log_level)(
            f"Scenario {scenario_name} completed: {'SUCCESS' if success else 'FAILURE'}",
            context={
                "scenario": scenario_name,
                "success": success,
                "elapsed": elapsed,
                "failures": failures
            }
        )
        
        # Save result
        self.test_results.append(result)
        
        return result
    
    def run_all_scenarios(self) -> List[Dict[str, Any]]:
        """
        Run all discovered test scenarios.
        
        Returns:
            List[Dict[str, Any]]: Test results
        """
        if not self.test_scenarios:
            self.discover_test_scenarios()
            
        if not self.test_scenarios:
            self.logger.warning("No test scenarios found")
            return []
        
        self.logger.info(f"Running {len(self.test_scenarios)} test scenarios")
        
        # Start timing
        self.logger.start_timer("all_scenarios")
        
        # Run each scenario
        results = []
        for scenario in self.test_scenarios:
            try:
                result = self.run_scenario(scenario)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error running scenario {scenario['name']}", context={"error": str(e)})
                results.append({
                    "scenario": scenario["name"],
                    "success": False,
                    "failures": [f"Exception: {str(e)}"],
                    "elapsed_seconds": 0,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                })
        
        # Stop timing
        total_elapsed = self.logger.stop_timer("all_scenarios", level="info")
        
        # Calculate success rate
        success_count = sum(1 for r in results if r["success"])
        success_rate = success_count / len(results) if results else 0
        
        # Log summary
        self.logger.info(
            f"Test run completed: {success_count}/{len(results)} scenarios passed ({success_rate:.1%})",
            context={
                "total_scenarios": len(results),
                "success_count": success_count,
                "success_rate": success_rate,
                "total_elapsed": total_elapsed
            }
        )
        
        # Save results to file
        output_file = self.output_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_scenarios": len(results),
                    "success_count": success_count,
                    "success_rate": success_rate,
                    "total_elapsed": total_elapsed,
                    "results": results
                }, f, indent=2)
            self.logger.info(f"Test results saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving test results: {str(e)}")
        
        return results
    
    def generate_report(self, results: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Generate a report of test results.
        
        Args:
            results (Optional[List[Dict[str, Any]]]): Test results to report (default: None)
                If None, uses the last run results
                
        Returns:
            str: Test report in Markdown format
        """
        if results is None:
            results = self.test_results
            
        if not results:
            return "# Test Report\n\nNo test results available."
        
        # Calculate summary statistics
        total_scenarios = len(results)
        success_count = sum(1 for r in results if r["success"])
        success_rate = success_count / total_scenarios if total_scenarios else 0
        total_elapsed = sum(r.get("elapsed_seconds", 0) for r in results)
        avg_elapsed = total_elapsed / total_scenarios if total_scenarios else 0
        
        # Generate report
        report = [
            "# End-to-End Test Report",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Scenarios:** {total_scenarios}",
            f"**Success Rate:** {success_count}/{total_scenarios} ({success_rate:.1%})",
            f"**Total Duration:** {total_elapsed:.2f} seconds",
            f"**Average Duration:** {avg_elapsed:.2f} seconds per scenario",
            "",
            "## Scenario Results",
            "",
        ]
        
        # Add results for each scenario
        for i, result in enumerate(results, 1):
            scenario_name = result["scenario"]
            success = result["success"]
            elapsed = result.get("elapsed_seconds", 0)
            failures = result.get("failures", [])
            
            report.append(f"### {i}. {scenario_name}")
            report.append(f"- **Result:** {'✅ PASSED' if success else '❌ FAILED'}")
            report.append(f"- **Duration:** {elapsed:.2f} seconds")
            report.append(f"- **Session ID:** {result.get('session_id', 'N/A')}")
            report.append(f"- **Messages:** {result.get('messages_count', 0)}")
            report.append(f"- **Insights:** {result.get('insights_count', 0)}")
            
            if failures:
                report.append("- **Failures:**")
                for failure in failures:
                    report.append(f"  - {failure}")
            
            report.append("")
        
        # Add summary
        report.append("## Summary")
        report.append("")
        report.append(f"- {'All scenarios passed!' if success_rate == 1 else f'{success_count}/{total_scenarios} scenarios passed'}")
        report.append(f"- Average response time: {avg_elapsed:.2f} seconds")
        report.append("")
        
        return "\n".join(report)
    
    def save_report(self, report: str, filename: Optional[str] = None) -> Optional[Path]:
        """
        Save a test report to a file.
        
        Args:
            report (str): Test report to save
            filename (Optional[str]): Filename to use (default: None)
                If None, generates a filename based on the current date and time
                
        Returns:
            Optional[Path]: Path to the saved report, or None if save failed
        """
        if filename is None:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
        output_file = self.output_dir / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            self.logger.info(f"Test report saved to {output_file}")
            return output_file
        except Exception as e:
            self.logger.error(f"Error saving test report: {str(e)}")
            return None


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Run end-to-end tests for Smart Steps AI")
    parser.add_argument("--create-samples", action="store_true", help="Create sample test scenarios")
    parser.add_argument("--test-dir", type=str, help="Directory for test scenarios")
    parser.add_argument("--output-dir", type=str, help="Directory for test outputs")
    parser.add_argument("--log-level", type=str, default="info", help="Log level (debug, info, warning, error)")
    parser.add_argument("--use-real-provider", action="store_true", help="Use real providers instead of mock")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create test runner
    runner = EndToEndTestRunner(
        test_dir=args.test_dir,
        output_dir=args.output_dir,
        log_level=args.log_level,
        use_mock=not args.use_real_provider
    )
    
    # Create sample scenarios if requested
    if args.create_samples:
        runner.create_sample_scenarios()
    
    # Discover and run test scenarios
    runner.discover_test_scenarios()
    results = runner.run_all_scenarios()
    
    # Generate and save report
    report = runner.generate_report(results)
    runner.save_report(report)
