"""Clean test with proper error handling for the Smart Steps AI module."""

import os
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set environment variables for testing - use testing mode but don't bypass real logic
os.environ["SMART_STEPS_APP_ENVIRONMENT"] = "testing"
os.environ["SMART_STEPS_PROVIDERS_USE_MOCK"] = "true"
os.environ["SMART_STEPS_PROVIDERS_MOCK_ENABLED"] = "true"

# Import the test module
from test_end_to_end import EndToEndTest

def run_test():
    """Run the end-to-end tests with proper error handling."""
    print("\nRunning end-to-end tests with real logic...\n")
    
    try:
        # Create the test runner
        test_runner = EndToEndTest(use_mock=True)
        
        # Run the tests
        results = test_runner.run_all_tests()
        
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
                if "validation_errors" in result["details"]:
                    print("   Validation errors:")
                    for error in result["details"]["validation_errors"]:
                        print(f"   - {error}")
        
        print("\nTest report saved to output/test_reports directory")
        
        return results["failed_tests"] == 0
        
    except Exception as e:
        print(f"\nError running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
