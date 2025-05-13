"""Test script for the enhanced session management system."""

import sys
import os
from pathlib import Path

# Add project root to path
project_dir = Path(r"G:\My Drive\Deftech\SmartSteps\smart_steps_ai")
sys.path.insert(0, str(project_dir))

from src.smart_steps_ai.persona.jane_builder import build_jane
from src.smart_steps_ai.persona.enhanced_manager import EnhancedPersonaManager
from src.smart_steps_ai.session.jane_conversation import JaneConversationHandler
from src.smart_steps_ai.provider import ProviderManager

def setup_jane_environment():
    """Set up the environment with Jane persona."""
    print("\n===== Setting Up Jane Environment =====")
    
    # Build Jane
    jane_path = build_jane()
    
    # Create the personas directory
    personas_dir = project_dir / "personas"
    personas_dir.mkdir(exist_ok=True)
    
    # Copy Jane to the personas directory
    jane_name = jane_path.name
    target_path = personas_dir / jane_name
    
    # Copy the file
    import shutil
    shutil.copy2(jane_path, target_path)
    
    print(f"Jane persona set up at {target_path}")
    return target_path

def test_jane_conversation():
    """Test the Jane conversation handler."""
    print("\n===== Testing Jane Conversation Handler =====")
    
    # Create enhanced persona manager that will load Jane
    enhanced_persona_manager = EnhancedPersonaManager(project_dir / "personas")
    
    # Get Jane to confirm it's loaded
    jane = enhanced_persona_manager.get_enhanced_persona("jane-clinical-psychologist")
    if not jane:
        print("Failed to load Jane persona, aborting test")
        return
    
    print(f"Successfully loaded Jane persona: {jane.display_name}")
    
    # Create the provider manager
    provider_manager = ProviderManager()
    
    # List available providers
    providers = provider_manager.list_providers()
    print(f"Available providers: {providers}")
    
    # Create the Jane conversation handler with the enhanced_persona_manager
    conversation_handler = JaneConversationHandler(
        provider_manager=provider_manager,
        enhanced_persona_manager=enhanced_persona_manager
    )
    
    # Also pass the enhanced_persona_manager to the session manager
    # This ensures the session manager can find Jane
    conversation_handler.session_manager.persona_manager = enhanced_persona_manager
    
    # Create a new session with Jane
    session_info = conversation_handler.create_new_session(
        client_name="Test Client",
        persona_name="jane-clinical-psychologist",
        session_type="standard",
        initial_message="Hello, I'm here for my first session. Can you tell me a bit about yourself?",
        provider_name="jane_mock"  # Use the Jane-specific mock provider
    )
    
    if not session_info:
        print("Failed to create session")
        return
    
    print(f"Created session: {session_info['id']}")
    
    # Get the conversation history
    history = conversation_handler.get_conversation_history(session_info['id'])
    
    if history:
        print("\nInitial conversation:")
        for message in history:
            print(f"{message['role'].upper()}: {message['content'][:100]}...")
    
    # Test a biographical question
    print("\nSending biographical question about Jane's trauma...")
    client_msg, assistant_msg = conversation_handler.send_message(
        session_id=session_info['id'],
        message="Can you tell me more about the abuse you suffered as a child? What was the last incident like?",
        provider_name="jane_mock"
    )
    
    if assistant_msg:
        print(f"\nJane's response:")
        print(f"{assistant_msg.content}")
        
        # Check if the response was stored as a canonical detail
        print("\nChecking for new canonical details...")
        enhanced_persona_manager = EnhancedPersonaManager(project_dir / "personas")
        details = enhanced_persona_manager.get_canonical_details(
            persona_name="jane-clinical-psychologist",
            category="abuse"
        )
        
        if details:
            print(f"Found {len(details)} abuse-related canonical details:")
            for detail in details:
                print(f"- {detail.detail}")
                print(f"  Usage count: {detail.usage_count}")
                print(f"  Categories: {detail.categories}")
        else:
            print("No abuse-related canonical details found")
    
    # Test another biographical question that should use the same canonical detail
    print("\nSending follow-up question about the same incident...")
    client_msg, assistant_msg = conversation_handler.send_message(
        session_id=session_info['id'],
        message="That sounds terrible. How old were you when that last incident happened?",
        provider_name="jane_mock"
    )
    
    if assistant_msg:
        print(f"\nJane's response to follow-up:")
        print(f"{assistant_msg.content}")
        
        # Check if the canonical detail was reused
        print("\nChecking if canonical details were reused...")
        enhanced_persona_manager = EnhancedPersonaManager(project_dir / "personas")
        details = enhanced_persona_manager.get_canonical_details(
            persona_name="jane-clinical-psychologist",
            category="abuse"
        )
        
        if details:
            print(f"Canonical details after follow-up:")
            for detail in details:
                print(f"- {detail.detail}")
                print(f"  Usage count: {detail.usage_count}")
                print(f"  Categories: {detail.categories}")
                print(f"  Reference history: {len(detail.reference_history)} entries")
        else:
            print("No canonical details found after follow-up")
    
    # Get the final conversation history
    history = conversation_handler.get_conversation_history(session_info['id'])
    
    if history:
        print("\nFinal conversation history (messages only):")
        for message in history:
            if message['role'] in ['client', 'assistant']:
                print(f"{message['role'].upper()}: {message['content'][:100]}...")
    
    print("\nJane Conversation Handler test completed!")

if __name__ == "__main__":
    setup_jane_environment()
    test_jane_conversation()
