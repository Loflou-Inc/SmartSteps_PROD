
import requests
import json
import sys

def main():
    base_url = 'http://127.0.0.1:9500'

    # Test 1: Health check
    try:
        health = requests.get(f'{base_url}/health')
        print(f'Health check: {health.status_code} - {health.text}')
    except Exception as e:
        print(f'Health check error: {str(e)}')

    # Test 2: List personas
    try:
        personas = requests.get(f'{base_url}/api/v1/personas')
        print(f'Personas: {personas.status_code} - {personas.text[:100]}...')
    except Exception as e:
        print(f'Personas error: {str(e)}')

    # Test 3: Create a session
    try:
        session_data = {
            'client_id': 'test_client',
            'persona_id': 'professional_therapist',
            'title': 'Test Session'
        }
        session = requests.post(f'{base_url}/api/v1/sessions', json=session_data)
        print(f'Create session: {session.status_code} - {session.text[:100]}...')
        
        if session.status_code == 201:
            session_id = session.json()['id']
            
            # Test 4: Send a message
            try:
                message_data = {
                    'message': 'Hello, this is a test message'
                }
                message = requests.post(f'{base_url}/api/v1/conversations/{session_id}', json=message_data)
                print(f'Send message: {message.status_code} - {message.text[:100]}...')
            except Exception as e:
                print(f'Send message error: {str(e)}')
    except Exception as e:
        print(f'Create session error: {str(e)}')

if __name__ == "__main__":
    main()
