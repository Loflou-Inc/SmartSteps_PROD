
import requests
import sys
from requests.exceptions import RequestException

# Make sure we see output immediately
sys.stdout.reconfigure(line_buffering=True)

print("Starting API OpenAPI test...")
base_url = 'http://127.0.0.1:9500'

# Test OpenAPI docs
try:
    print("Testing OpenAPI docs...")
    openapi = requests.get(f'{base_url}/api/openapi.json', timeout=5)
    print(f'OpenAPI status: {openapi.status_code}')
    if openapi.status_code == 200:
        api_spec = openapi.json()
        endpoint_count = len(api_spec.get('paths', {}))
        print(f'Found {endpoint_count} API endpoints defined')
        print(f'API Title: {api_spec.get("info", {}).get("title", "Unknown")}')
    else:
        print(f'OpenAPI response: {openapi.text[:200]}...')
except RequestException as e:
    print(f'OpenAPI error: {str(e)}')

print("Test completed.")
