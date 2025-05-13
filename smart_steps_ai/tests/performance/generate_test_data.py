"""
Smart Steps AI Module - Test Data Generator

This script generates test data for performance testing.
It creates a configurable number of sessions with messages to test performance
with large datasets.

Run with: python -m tests.performance.generate_test_data
"""

import argparse
import datetime
import json
import os
import random
import sys
import time
import uuid
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Try to import from the module
try:
    from smart_steps_ai.config.config_manager import ConfigManager
    from smart_steps_ai.conversation.conversation_handler import ConversationHandler
    from smart_steps_ai.memory.memory_manager import MemoryManager
    from smart_steps_ai.persona.persona_manager import PersonaManager
    from smart_steps_ai.providers.mock_provider import MockProvider
    from smart_steps_ai.providers.provider_manager import ProviderManager
    from smart_steps_ai.session.session_manager import SessionManager
    MODULE_IMPORT_SUCCESS = True
except ImportError:
    MODULE_IMPORT_SUCCESS = False
    print("Warning: Could not import Smart Steps AI module. Using direct file manipulation instead.")

# Initialize console
console = Console()

# Sample phrases for test data generation
CLIENT_PHRASES = [
    "I've been feeling really anxious lately.",
    "My work stress is affecting my sleep.",
    "I had a conflict with my partner yesterday.",
    "I don't know how to handle this situation with my boss.",
    "My anxiety gets worse when I have to speak in public.",
    "I feel overwhelmed by my responsibilities.",
    "I've been having trouble focusing at work.",
    "My family doesn't understand my career choices.",
    "I feel like I'm not making progress in my life.",
    "Sometimes I feel like giving up on my goals.",
    "I had a panic attack in the supermarket.",
    "I'm having trouble with my relationship.",
    "My childhood experiences are affecting my current behavior.",
    "I feel judged by others all the time.",
    "I'm worried about my health.",
    "I can't stop thinking about mistakes I've made.",
    "I feel disconnected from people around me.",
    "I've been using unhealthy coping mechanisms.",
    "I have difficulty trusting people.",
    "I feel like I'm not good enough.",
    "I've been trying the techniques you suggested.",
    "I had a breakthrough moment yesterday.",
    "I'm starting to understand my patterns better.",
    "I noticed I was able to calm myself during a stressful situation.",
    "I've been practicing mindfulness like you suggested.",
]

THERAPIST_PHRASES = [
    "Could you tell me more about how that makes you feel?",
    "I'm hearing that you're experiencing a lot of stress right now.",
    "Have you noticed any patterns in when these feelings arise?",
    "Let's explore some strategies that might help in these situations.",
    "It sounds like this has been challenging for you.",
    "What thoughts come up for you when that happens?",
    "How have you been coping with these feelings?",
    "That's a really important insight about yourself.",
    "I'm noticing a theme in what you're describing.",
    "How does that reaction serve you in your life?",
    "What would it look like if you responded differently?",
    "It's completely normal to feel that way given your experiences.",
    "I appreciate your willingness to share that with me.",
    "Let's try to understand this from a different perspective.",
    "What would be a small step you could take this week?",
    "I wonder if there's a connection between these experiences.",
    "Your awareness of this pattern is an important first step.",
    "How might your past experiences be influencing this situation?",
    "What would be helpful for you right now?",
    "I'm hearing that you feel stuck. Let's explore some options.",
    "The progress you're making is significant.",
    "That demonstrates real growth in how you're approaching these situations.",
    "I'd like to acknowledge the effort you're putting into this work.",
    "How would you feel about trying a different approach this week?",
    "What you're describing is a common challenge many people face.",
]

class TestDataGenerator:
    """Generator for test data used in performance testing."""
    
    def __init__(self):
        """Initialize the generator."""
        self.config_path = Path("G:/My Drive/Deftech/SmartSteps/smart_steps_ai/config")
        self.data_path = Path("G:/My Drive/Deftech/SmartSteps/smart_steps_ai/data")
        
        if MODULE_IMPORT_SUCCESS:
            # Initialize components if module import succeeded
            self.config_manager = ConfigManager()
            self.persona_manager = PersonaManager(self.config_manager)
            self.session_manager = SessionManager(self.config_manager)
            self.memory_manager = MemoryManager(self.config_manager)
            self.provider_manager = ProviderManager(self.config_manager)
            
            # Register mock provider for testing
            mock_provider = MockProvider(self.config_manager)
            self.provider_manager.register_provider("mock", mock_provider)
            self.provider_manager.set_default_provider("mock")
            
            self.conversation_handler = ConversationHandler(
                session_manager=self.session_manager,
                provider_manager=self.provider_manager,
                memory_manager=self.memory_manager,
                persona_manager=self.persona_manager
            )
        else:
            # Ensure data paths exist
            os.makedirs(self.data_path / "sessions", exist_ok=True)
            os.makedirs(self.data_path / "conversations", exist_ok=True)
            os.makedirs(self.data_path / "memory", exist_ok=True)
    
    def generate_test_sessions(self, num_sessions, messages_per_session, persona_id="therapist_cbt"):
        """Generate test sessions with messages."""
        console.print(f"[bold green]Generating {num_sessions} test sessions with {messages_per_session} messages each[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn()
        ) as progress:
            task = progress.add_task(f"Generating test data...", total=num_sessions)
            
            for i in range(num_sessions):
                session_id = self._create_session(i, persona_id)
                if session_id:
                    self._add_messages(session_id, messages_per_session)
                progress.update(task, advance=1)
        
        console.print(f"[bold green]Test data generation complete![/bold green]")
    
    def _create_session(self, index, persona_id):
        """Create a test session."""
        client_name = f"TestClient_{index:04d}"
        
        if MODULE_IMPORT_SUCCESS:
            # Create session using the module
            try:
                persona = self.persona_manager.get_persona(persona_id)
                session = self.session_manager.create_session(
                    client_name=client_name,
                    persona_id=persona.id,
                    metadata={"test_data": True, "generated_at": time.time()}
                )
                return session.id
            except Exception as e:
                console.print(f"[bold red]Error creating session: {str(e)}[/bold red]")
                return None
        else:
            # Create session JSON directly
            try:
                session_id = str(uuid.uuid4())
                session_data = {
                    "id": session_id,
                    "client_name": client_name,
                    "persona_id": persona_id,
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat(),
                    "status": "active",
                    "metadata": {
                        "test_data": True,
                        "generated_at": time.time()
                    }
                }
                
                # Save session JSON
                session_file = self.data_path / "sessions" / f"{session_id}.json"
                with open(session_file, "w") as f:
                    json.dump(session_data, f, indent=2)
                
                return session_id
            except Exception as e:
                console.print(f"[bold red]Error creating session file: {str(e)}[/bold red]")
                return None
    
    def _add_messages(self, session_id, count):
        """Add test messages to a session."""
        if MODULE_IMPORT_SUCCESS:
            # Add messages using the module
            try:
                for i in range(count):
                    user_message = random.choice(CLIENT_PHRASES)
                    self.conversation_handler.add_message(
                        session_id=session_id,
                        user_message=user_message,
                        client=True
                    )
                    
                    # Add small delay to avoid overwhelming the system
                    if i % 10 == 0:
                        time.sleep(0.1)
            except Exception as e:
                console.print(f"[bold red]Error adding messages: {str(e)}[/bold red]")
        else:
            # Create message files directly
            try:
                # Create conversation directory
                conv_dir = self.data_path / "conversations" / session_id
                os.makedirs(conv_dir, exist_ok=True)
                
                # Add messages
                for i in range(count):
                    # Create client message
                    message_id = str(uuid.uuid4())
                    timestamp = time.time() + (i * 60)  # Space messages by 1 minute
                    
                    client_message = {
                        "id": message_id,
                        "session_id": session_id,
                        "content": random.choice(CLIENT_PHRASES),
                        "timestamp": timestamp,
                        "created_at": datetime.datetime.fromtimestamp(timestamp).isoformat(),
                        "client": True,
                        "metadata": {
                            "test_data": True,
                            "index": i
                        }
                    }
                    
                    # Save client message
                    msg_file = conv_dir / f"{message_id}.json"
                    with open(msg_file, "w") as f:
                        json.dump(client_message, f, indent=2)
                    
                    # Create therapist response
                    response_id = str(uuid.uuid4())
                    response_timestamp = timestamp + 10  # 10 seconds later
                    
                    therapist_message = {
                        "id": response_id,
                        "session_id": session_id,
                        "content": random.choice(THERAPIST_PHRASES),
                        "timestamp": response_timestamp,
                        "created_at": datetime.datetime.fromtimestamp(response_timestamp).isoformat(),
                        "client": False,
                        "metadata": {
                            "test_data": True,
                            "index": i,
                            "response_to": message_id
                        }
                    }
                    
                    # Save therapist message
                    resp_file = conv_dir / f"{response_id}.json"
                    with open(resp_file, "w") as f:
                        json.dump(therapist_message, f, indent=2)
            except Exception as e:
                console.print(f"[bold red]Error creating message files: {str(e)}[/bold red]")
    
    def generate_large_dataset(self, num_sessions=100, messages_per_session=50):
        """Generate a large dataset for performance testing."""
        console.print(f"[bold blue]Generating Large Dataset for Performance Testing[/bold blue]")
        console.print(f"Sessions: {num_sessions}, Messages per session: {messages_per_session}")
        console.print("This may take several minutes...")
        
        # Generate sessions with different personas
        personas = ["therapist_cbt", "therapist_psychodynamic", "counselor_behavioral"]
        sessions_per_persona = num_sessions // len(personas)
        
        for persona in personas:
            console.print(f"Generating sessions for persona: [cyan]{persona}[/cyan]")
            self.generate_test_sessions(
                num_sessions=sessions_per_persona, 
                messages_per_session=messages_per_session,
                persona_id=persona
            )
        
        # Generate any remaining sessions
        remaining = num_sessions - (sessions_per_persona * len(personas))
        if remaining > 0:
            console.print(f"Generating {remaining} remaining sessions with default persona")
            self.generate_test_sessions(
                num_sessions=remaining,
                messages_per_session=messages_per_session
            )
        
        console.print("[bold green]Large dataset generation complete![/bold green]")
        console.print(f"Total sessions: {num_sessions}")
        console.print(f"Total messages: ~{num_sessions * messages_per_session * 2} (including responses)")
        
        # Create data summary file
        self._create_data_summary(num_sessions, messages_per_session)
    
    def _create_data_summary(self, num_sessions, messages_per_session):
        """Create a summary file of the generated data."""
        summary = {
            "generated_at": datetime.datetime.now().isoformat(),
            "num_sessions": num_sessions,
            "messages_per_session": messages_per_session,
            "total_messages": num_sessions * messages_per_session * 2,  # Including responses
            "generator_version": "1.0.0",
            "personas_used": ["therapist_cbt", "therapist_psychodynamic", "counselor_behavioral"],
            "module_import_success": MODULE_IMPORT_SUCCESS
        }
        
        summary_file = self.data_path / "test_data_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        console.print(f"Data summary written to: [bold]{summary_file}[/bold]")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate test data for performance testing")
    parser.add_argument(
        "--sessions", type=int, default=50,
        help="Number of sessions to generate (default: 50)"
    )
    parser.add_argument(
        "--messages", type=int, default=20,
        help="Messages per session (default: 20)"
    )
    parser.add_argument(
        "--persona", type=str, default="therapist_cbt",
        help="Persona ID to use (default: therapist_cbt)"
    )
    parser.add_argument(
        "--large", action="store_true",
        help="Generate a large dataset with multiple personas"
    )
    
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    generator = TestDataGenerator()
    
    try:
        if args.large:
            generator.generate_large_dataset(args.sessions, args.messages)
        else:
            generator.generate_test_sessions(args.sessions, args.messages, args.persona)
    except KeyboardInterrupt:
        console.print("\n[bold red]Data generation interrupted by user[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error during data generation: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
