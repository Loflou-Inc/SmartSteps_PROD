
import requests
import time
import sys
from requests.exceptions import RequestException

# Make sure we see output immediately
sys.stdout.reconfigure(line_buffering=True)

print("Starting API test...")
base_url = 'http://127.0.0.1:9500'

# Test 1: Health check with timeout
try:
    print("Testing health endpoint...")
    health = requests.get(f'{base_url}/health', timeout=5)
    print(f'Health check response status: {health.status_code}')
    print(f'Health check response body: {health.text}')
except RequestException as e:
    print(f'Health check error: {str(e)}')

print("Test completed.")
