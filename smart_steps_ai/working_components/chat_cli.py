"""
Simple CLI chat tool for testing the mock providers
"""

import argparse

from provider.interface import ProviderConfig
from provider.mock import MockProvider
from provider.jane_mock import JaneMockProvider
from provider.message import Message, MessageRole

def main():
    parser = argparse.ArgumentParser(description="CLI Chat with Mock Personas")
    parser.add_argument("--persona", choices=["mock", "jane"], default="jane", help="Persona to chat with")
    parser.add_argument("--model", default="mock-therapist", help="Model to use")
    args = parser.parse_args()
    
    # Setup provider
    if args.persona == "jane":
        provider = JaneMockProvider()
    else:
        provider = MockProvider()
    
    # Initialize provider
    config = ProviderConfig(model=args.model)
    provider.initialize(config)
    
    # Welcome message
    persona_name = "Dr. Jane Donovan" if args.persona == "jane" else "Mock Therapist"
    print(f"\nWelcome to the chat with {persona_name}!")
    print("Type 'exit', 'quit', or 'bye' to end the conversation.\n")
    
    # Chat loop
    messages = []
    
    # Add system message if persona is Jane
    if args.persona == "jane":
        system_prompt = """You are Dr. Jane Donovan, a 46-year-old clinical psychologist with expertise in trauma-informed care, cognitive-behavioral therapy, and working with survivors of childhood trauma. You have personal experience with childhood trauma, which informs your compassionate, authentic approach while maintaining professional boundaries."""
        messages.append(Message(MessageRole.SYSTEM, system_prompt))
    
    # Initial greeting
    response = provider.generate_response(messages)
    print(f"{persona_name}: {response.content}\n")
    
    # Add assistant message to history
    messages.append(Message(MessageRole.ASSISTANT, response.content))
    
    # Main chat loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"\n{persona_name}: Goodbye! Take care.")
            break
        
        # Add user message to history
        messages.append(Message(MessageRole.CLIENT, user_input))
        
        # Generate response
        response = provider.generate_response(messages)
        
        # Display response
        print(f"\n{persona_name}: {response.content}\n")
        
        # Add assistant message to history
        messages.append(Message(MessageRole.ASSISTANT, response.content))

if __name__ == "__main__":
    main()
