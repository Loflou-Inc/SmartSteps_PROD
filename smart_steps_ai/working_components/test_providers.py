"""
A minimal test script to use the mock providers without any API
"""

from provider.mock import MockProvider
from provider.jane_mock import JaneMockProvider
from provider.interface import ProviderConfig
from provider.message import Message, MessageRole

# Create messages
messages = [
    Message(MessageRole.CLIENT, "Hello, I've been feeling anxious lately about my job.")
]

# Test basic mock provider
print("Testing basic mock provider...")
mock_provider = MockProvider()
config = ProviderConfig(model="mock-therapist")
mock_provider.initialize(config)
response = mock_provider.generate_response(messages)
print(f"Mock response: {response.content}\n")

# Test Jane mock provider with trauma question
print("Testing Jane mock provider with trauma question...")
jane_provider = JaneMockProvider()
config = ProviderConfig(model="mock-jane")
jane_provider.initialize(config)
trauma_message = Message(MessageRole.CLIENT, "Can you tell me about your own trauma experience?")
response = jane_provider.generate_response([trauma_message])
print(f"Jane trauma response: {response.content}\n")

# Test Jane mock provider with education question
print("Testing Jane mock provider with education question...")
education_message = Message(MessageRole.CLIENT, "Where did you go to school?")
response = jane_provider.generate_response([education_message])
print(f"Jane education response: {response.content}\n")

print("All tests completed.")
