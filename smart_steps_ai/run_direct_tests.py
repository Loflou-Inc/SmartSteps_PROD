import os

# Set testing environment variables
os.environ["SMART_STEPS_APP_ENVIRONMENT"] = "testing"
os.environ["SMART_STEPS_PROVIDERS_USE_MOCK"] = "true"
os.environ["SMART_STEPS_PROVIDERS_MOCK_ENABLED"] = "true"

# Import test module directly
from test_end_to_end import EndToEndTest

# Run tests
test_runner = EndToEndTest(use_mock=True)
results = test_runner.run_all_tests()

# Print results
print("\nFinal Test Results:")
for test_name, result in test_runner.stats["test_results"].items():
    status = "✅" if result["result"] == "PASSED" else "❌"
    print(f"{status} {test_name}")

# Return exit code
exit(0 if test_runner.stats["failed_tests"] == 0 else 1)
