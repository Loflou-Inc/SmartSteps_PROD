"""Quick end-to-end test script for Smart Steps AI."""

import os
import sys
from pathlib import Path

# Set environment variables for testing
os.environ["SMART_STEPS_APP_ENVIRONMENT"] = "testing"
os.environ["SMART_STEPS_PROVIDERS_USE_MOCK"] = "true"
os.environ["SMART_STEPS_PROVIDERS_MOCK_ENABLED"] = "true"

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import the test runner
from test_end_to_end import EndToEndTest

def run_tests():
    """Run the end-to-end tests and print results."""
    print("\nRunning end-to-end tests...\n")
    
    # Create the test runner
    test_runner = EndToEndTest(use_mock=True)
    
    # Run the tests
    results = test_runner.run_all_tests()
    
    # Generate a report
    report_path = Path("./output/test_reports") / f"end_to_end_test_report_quick.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = test_runner.generate_report(report_path)
    
    # Summarize results
    print("\nTest Summary:")
    print(f"Total tests: {results['total_tests']}")
    print(f"Passed: {results['passed_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Skipped: {results['skipped_tests']}")
    print(f"Total duration: {results['total_duration']:.2f} seconds")
    
    # Print individual test results
    print("\nResults by test:")
    for test_name, result in test_runner.stats["test_results"].items():
        status = "PASS" if result["result"] == "PASSED" else "FAIL"
        print(f"[{status}] {test_name} ({result['duration']:.2f}s)")
        if result["result"] == "FAILED" and "error" in result["details"]:
            print(f"   Error: {result['details']['error']}")
    
    return results["failed_tests"] == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
