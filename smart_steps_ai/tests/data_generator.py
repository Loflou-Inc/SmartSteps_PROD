"""Test data generation tools for the Smart Steps AI Professional Persona module."""

import os
import sys
import json
import random
import uuid
import argparse
from faker import Faker
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import the Smart Steps AI module components
from src.smart_steps_ai.utils import get_logger, StructuredLogger
from src.smart_steps_ai.session.models import MessageRole


class TestDataGenerator:
    """
    Generator for test data for the Smart Steps AI module.
    
    This class provides functionality for generating test data for various
    components of the Smart Steps AI module, including sessions, clients,
    messages, and test scenarios.
    """
    
    def __init__(
        self, 
        output_dir: Optional[Union[str, Path]] = None,
        log_level: str = "info",
        seed: Optional[int] = None,
    ):
        """
        Initialize the test data generator.
        
        Args:
            output_dir (Optional[Union[str, Path]]): Directory for test data outputs (default: None)
                If None, uses ./tests/data
            log_level (str): Log level for the generator (default: "info")
            seed (Optional[int]): Random seed for reproducibility (default: None)
        """
        # Set up directories
        self.output_dir = Path(output_dir) if output_dir else project_root / "tests" / "data"
        
        # Create directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = StructuredLogger(
            name="test_data_generator",
            level=log_level,
            context={"module": "test_data_generator"}
        )
        
        # Set up Faker with seed if provided
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)
        
        self.logger.info("Test data generator initialized")
        
        # Define template data
        self.personas = ["dr_hayes", "dr_rivera", "dr_jane"]
        self.session_tags = ["anxiety", "depression", "trauma", "stress", "relationships", 
                             "work", "family", "social", "school", "health", "self-esteem"]
        
        # Define message templates for different topics
        self.message_templates = {
            "anxiety": [
                "I've been feeling really anxious lately about $context.",
                "My anxiety has been getting worse, especially when I $context.",
                "I can't stop worrying about $context and it's affecting my sleep.",
                "Whenever I think about $context, I get this overwhelming sense of dread.",
                "My heart races and I feel panicky when I have to $context."
            ],
            "depression": [
                "I've been feeling really down lately about $context.",
                "I don't enjoy $context like I used to, nothing seems fun anymore.",
                "I've been sleeping a lot more than usual and just don't have energy for $context.",
                "I feel hopeless about $context, like things will never get better.",
                "It's hard to even get out of bed to $context."
            ],
            "relationships": [
                "My relationship with $context has been really challenging lately.",
                "I don't know how to communicate effectively with $context.",
                "I keep getting into the same arguments with $context.",
                "I'm not sure if my relationship with $context is healthy.",
                "I feel like $context doesn't understand me at all."
            ],
            "work": [
                "I'm really stressed about my work situation with $context.",
                "I'm worried I might lose my job because of $context.",
                "My boss is always criticizing my work on $context.",
                "I feel overwhelmed by my workload, especially $context.",
                "I don't know if I'm in the right career because I struggle with $context."
            ],
            "trauma": [
                "I keep having flashbacks about $context.",
                "I can't stop thinking about what happened with $context.",
                "Ever since $context, I've been jumpy and on edge.",
                "I avoid anything that reminds me of $context.",
                "I haven't told anyone about $context before."
            ]
        }
        
        # Define response templates for different client issues
        self.response_templates = {
            "anxiety": [
                "I understand that anxiety about $context can be overwhelming. Can you tell me more about when you first noticed these feelings?",
                "Anxiety related to $context is something many people experience. What physical symptoms do you notice when you're feeling anxious?",
                "It sounds like $context is triggering significant anxiety for you. Have you found anything that helps reduce these feelings, even temporarily?",
                "I hear that $context is causing you a lot of worry. How has this been affecting your daily life?",
                "When you feel anxious about $context, what thoughts tend to go through your mind?"
            ],
            "depression": [
                "I'm sorry to hear you've been feeling down about $context. How long have you been experiencing these feelings?",
                "Loss of interest in $context can be a sign of depression. Have you noticed any other changes in your daily habits or routines?",
                "That feeling of hopelessness around $context sounds really difficult. Have you ever experienced similar feelings in the past?",
                "When you're struggling to get out of bed for $context, what thoughts or feelings are you experiencing?",
                "I hear that $context isn't bringing you joy anymore. What are some things that used to make you feel good?"
            ],
            "relationships": [
                "Relationships with $context can be complex. Can you tell me more about the specific challenges you're facing?",
                "Communication with $context seems to be a concern for you. What happens when you try to express your needs?",
                "Those repeated arguments with $context sound frustrating. What are they typically about?",
                "You're questioning whether your relationship with $context is healthy, which is important to reflect on. What aspects concern you?",
                "Feeling misunderstood by $context can be isolating. Can you share an example of a time when you felt this way?"
            ],
            "work": [
                "Work stress related to $context can be overwhelming. How has this been affecting you outside of work?",
                "The uncertainty about your job due to $context sounds challenging. What would it mean for you if you did lose your job?",
                "Constant criticism about $context from your boss must be difficult. How do you typically respond to this feedback?",
                "Feeling overwhelmed by $context at work is common. How do you currently manage your workload?",
                "Career uncertainty around $context is something many people grapple with. What aspects of your current job do you find fulfilling?"
            ],
            "trauma": [
                "Experiencing flashbacks about $context can be very distressing. How often do these flashbacks occur?",
                "It takes courage to talk about $context. How are you feeling about sharing this with me today?",
                "Being jumpy and on edge since $context is a common response to trauma. How has this been affecting your daily life?",
                "Avoiding reminders of $context is a natural coping mechanism. What kinds of things do you find yourself avoiding?",
                "Thank you for trusting me with your experience of $context. Is there anything specific you're hoping to address regarding this?"
            ],
            "general": [
                "Thank you for sharing that. Can you tell me more about how $context has been affecting you?",
                "I'm curious about your experience with $context. Could you elaborate a bit more?",
                "It sounds like $context has been significant for you. How have you been coping with this?",
                "What aspects of $context do you find most challenging?",
                "How long has $context been an issue for you?"
            ]
        }
        
        # Context templates for different topics
        self.context_templates = {
            "anxiety": [
                "public speaking", "social situations", "work deadlines", "health concerns", 
                "driving", "flying", "financial issues", "the future", "making decisions",
                "being judged by others", "failing an important test", "letting others down"
            ],
            "depression": [
                "my relationship ending", "losing my job", "the state of the world", 
                "feeling like a failure", "being alone", "the future", "my health issues",
                "not achieving my goals", "comparing myself to others", "past mistakes"
            ],
            "relationships": [
                "my partner", "my parents", "my children", "my in-laws", "my boss",
                "my coworkers", "my friends", "my siblings", "my ex", "my roommate"
            ],
            "work": [
                "meeting deadlines", "presentations", "my performance review", 
                "office politics", "my new role", "the company reorganization",
                "working overtime", "the project I'm leading", "remote work", 
                "balancing work and personal life"
            ],
            "trauma": [
                "the accident", "my childhood experiences", "the assault", 
                "losing someone close to me", "the natural disaster", "the medical emergency",
                "witnessing violence", "military service", "an abusive relationship"
            ]
        }
    
    def generate_client_data(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate sample client data.
        
        Args:
            count (int): Number of clients to generate (default: 10)
            
        Returns:
            List[Dict[str, Any]]: Generated client data
        """
        self.logger.info(f"Generating {count} sample clients")
        
        clients = []
        
        for _ in range(count):
            # Generate profile
            profile = self.faker.profile()
            age = random.randint(18, 75)
            
            # Generate personal information
            client = {
                "id": str(uuid.uuid4()),
                "first_name": profile["name"].split()[0],
                "last_name": profile["name"].split()[-1],
                "email": profile["mail"],
                "age": age,
                "gender": profile["sex"],
                "occupation": profile["job"],
                "primary_concern": random.choice(list(self.message_templates.keys())),
                "tags": random.sample(self.session_tags, k=random.randint(1, 3)),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
            }
            
            clients.append(client)
            
        self.logger.info(f"Generated {len(clients)} sample clients")
        return clients
    
    def generate_conversation(
        self,
        client: Dict[str, Any],
        topic: Optional[str] = None,
        message_count: int = 10,
        include_system: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Generate a sample conversation between a client and a persona.
        
        Args:
            client (Dict[str, Any]): Client data
            topic (Optional[str]): Conversation topic (default: None)
                If None, uses the client's primary concern
            message_count (int): Number of messages to generate (default: 10)
            include_system (bool): Whether to include a system message (default: True)
            
        Returns:
            List[Dict[str, Any]]: Generated conversation messages
        """
        # Determine topic
        if topic is None:
            topic = client.get("primary_concern", random.choice(list(self.message_templates.keys())))
        
        # Choose context for the conversation
        context = random.choice(self.context_templates.get(topic, self.context_templates["anxiety"]))
        
        # Choose persona
        persona = random.choice(self.personas)
        
        # Initialize messages
        messages = []
        
        # Add system message if requested
        if include_system:
            messages.append({
                "role": "SYSTEM",
                "content": f"You are a professional therapist using a {topic}-focused approach. Help the client with their {topic} concerns."
            })
        
        # Add initial client message
        initial_template = random.choice(self.message_templates.get(topic, self.message_templates["anxiety"]))
        initial_message = initial_template.replace("$context", context)
        
        messages.append({
            "role": "CLIENT",
            "content": initial_message
        })
        
        # Generate conversation
        for i in range(1, message_count):
            if i % 2 == 0:
                # Client message
                message_templates = self.message_templates.get(topic, self.message_templates["anxiety"])
                template = random.choice(message_templates)
                message = template.replace("$context", context)
                
                messages.append({
                    "role": "CLIENT",
                    "content": message
                })
            else:
                # Persona response
                response_templates = self.response_templates.get(topic, self.response_templates["general"])
                template = random.choice(response_templates)
                message = template.replace("$context", context)
                
                messages.append({
                    "role": "PERSONA",
                    "content": message
                })
        
        return messages
    
    def generate_session_data(
        self,
        client: Optional[Dict[str, Any]] = None,
        topics: Optional[List[str]] = None,
        session_count: int = 1,
        messages_per_session: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generate sample session data for a client.
        
        Args:
            client (Optional[Dict[str, Any]]): Client data (default: None)
                If None, generates a new client
            topics (Optional[List[str]]): Topics for sessions (default: None)
                If None, uses the client's primary concern or random topics
            session_count (int): Number of sessions to generate (default: 1)
            messages_per_session (int): Messages per session (default: 10)
            
        Returns:
            List[Dict[str, Any]]: Generated session data
        """
        # Generate client if not provided
        if client is None:
            client = self.generate_client_data(1)[0]
            
        # Get topics
        if topics is None:
            primary_concern = client.get("primary_concern")
            if primary_concern:
                topics = [primary_concern]
            else:
                topics = list(self.message_templates.keys())
        
        self.logger.info(f"Generating {session_count} sample sessions for client {client['first_name']} {client['last_name']}")
        
        sessions = []
        
        for i in range(session_count):
            # Choose topic for this session
            topic = random.choice(topics)
            
            # Choose persona
            persona = random.choice(self.personas)
            
            # Generate conversation
            messages = self.generate_conversation(
                client=client,
                topic=topic,
                message_count=messages_per_session,
                include_system=True
            )
            
            # Generate session data
            session = {
                "id": str(uuid.uuid4()),
                "client_id": client["id"],
                "client_name": f"{client['first_name']} {client['last_name']}",
                "persona": persona,
                "created_at": (datetime.now() - timedelta(days=session_count - i)).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=session_count - i, hours=random.randint(0, 12))).isoformat(),
                "tags": client.get("tags", []) + [topic],
                "state": "completed" if i < session_count - 1 else random.choice(["active", "completed"]),
                "messages": messages
            }
            
            sessions.append(session)
            
        self.logger.info(f"Generated {len(sessions)} sample sessions")
        return sessions
    
    def generate_test_scenario(
        self,
        client: Optional[Dict[str, Any]] = None,
        topic: Optional[str] = None,
        message_count: int = 10,
        include_expected: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a test scenario for end-to-end testing.
        
        Args:
            client (Optional[Dict[str, Any]]): Client data (default: None)
                If None, generates a new client
            topic (Optional[str]): Scenario topic (default: None)
                If None, uses the client's primary concern or a random topic
            message_count (int): Number of messages to generate (default: 10)
            include_expected (bool): Whether to include expected outcomes (default: True)
            
        Returns:
            Dict[str, Any]: Generated test scenario
        """
        # Generate client if not provided
        if client is None:
            client = self.generate_client_data(1)[0]
            
        # Get topic
        if topic is None:
            topic = client.get("primary_concern", random.choice(list(self.message_templates.keys())))
            
        # Choose context
        context = random.choice(self.context_templates.get(topic, self.context_templates["anxiety"]))
        
        # Choose persona
        persona = random.choice(self.personas)
        
        # Generate conversation
        messages = self.generate_conversation(
            client=client,
            topic=topic,
            message_count=message_count,
            include_system=False
        )
        
        # Generate scenario
        scenario = {
            "name": f"{topic.capitalize()} Scenario for {client['first_name']}",
            "description": f"Test scenario for {topic} concerns related to {context}.",
            "persona": persona,
            "client": f"{client['first_name']} {client['last_name']}",
            "system": f"You are a professional therapist using a {topic}-focused approach. Help the client with their {topic} concerns related to {context}.",
            "tags": client.get("tags", []) + [topic],
            "messages": messages
        }
        
        # Add expected outcomes if requested
        if include_expected:
            # Generate expected insights based on topic
            insights = []
            
            if topic == "anxiety":
                insights = ["anxiety", "worry", context, "physical symptoms", "coping strategies"]
            elif topic == "depression":
                insights = ["depression", "low mood", context, "loss of interest", "sleep changes"]
            elif topic == "relationships":
                insights = ["relationship difficulties", context, "communication", "boundaries", "patterns"]
            elif topic == "work":
                insights = ["work stress", context, "burnout", "career development", "work-life balance"]
            elif topic == "trauma":
                insights = ["trauma", context, "flashbacks", "avoidance", "coping mechanisms"]
            else:
                insights = [topic, context, "emotional response", "behavioral patterns", "coping strategies"]
            
            # Add expected outcome
            scenario["expected"] = {
                "insights": random.sample(insights, k=min(3, len(insights))),
                "analysis": True,
                "memory": True
            }
        
        return scenario
    
    def generate_bulk_data(
        self,
        client_count: int = 5,
        sessions_per_client: int = 3,
        messages_per_session: int = 10,
        scenario_count: int = 5,
        save_to_disk: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a bulk set of test data.
        
        Args:
            client_count (int): Number of clients to generate (default: 5)
            sessions_per_client (int): Sessions per client (default: 3)
            messages_per_session (int): Messages per session (default: 10)
            scenario_count (int): Number of test scenarios to generate (default: 5)
            save_to_disk (bool): Whether to save data to disk (default: True)
            
        Returns:
            Dict[str, Any]: Generated test data
        """
        self.logger.info(f"Generating bulk test data: {client_count} clients, {sessions_per_client} sessions per client, {scenario_count} scenarios")
        
        # Generate clients
        clients = self.generate_client_data(client_count)
        
        # Generate sessions for each client
        all_sessions = []
        for client in clients:
            sessions = self.generate_session_data(
                client=client,
                session_count=sessions_per_client,
                messages_per_session=messages_per_session
            )
            all_sessions.extend(sessions)
            
        # Generate test scenarios
        scenarios = []
        for i in range(scenario_count):
            # Choose a random client
            client = random.choice(clients)
            
            # Generate scenario
            scenario = self.generate_test_scenario(
                client=client,
                message_count=messages_per_session
            )
            
            scenarios.append(scenario)
            
        # Prepare bulk data
        bulk_data = {
            "generated_at": datetime.now().isoformat(),
            "clients": clients,
            "sessions": all_sessions,
            "scenarios": scenarios,
            "metadata": {
                "client_count": len(clients),
                "session_count": len(all_sessions),
                "scenario_count": len(scenarios),
                "messages_per_session": messages_per_session
            }
        }
        
        # Save data to disk if requested
        if save_to_disk:
            self._save_bulk_data(bulk_data)
            
        self.logger.info(f"Generated bulk test data: {len(clients)} clients, {len(all_sessions)} sessions, {len(scenarios)} scenarios")
        return bulk_data
    
    def _save_bulk_data(self, data: Dict[str, Any]) -> None:
        """
        Save bulk test data to disk.
        
        Args:
            data (Dict[str, Any]): Bulk test data
        """
        # Create timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create directory for this dataset
        dataset_dir = self.output_dir / f"testdata_{timestamp}"
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Save clients
        clients_file = dataset_dir / "clients.json"
        with open(clients_file, 'w', encoding='utf-8') as f:
            json.dump(data["clients"], f, indent=2)
            
        # Save sessions
        sessions_file = dataset_dir / "sessions.json"
        with open(sessions_file, 'w', encoding='utf-8') as f:
            json.dump(data["sessions"], f, indent=2)
            
        # Save scenarios
        scenarios_dir = dataset_dir / "scenarios"
        scenarios_dir.mkdir(parents=True, exist_ok=True)
        
        for i, scenario in enumerate(data["scenarios"]):
            scenario_file = scenarios_dir / f"scenario_{i+1}.json"
            with open(scenario_file, 'w', encoding='utf-8') as f:
                json.dump(scenario, f, indent=2)
                
        # Save metadata
        metadata_file = dataset_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": data["generated_at"],
                "metadata": data["metadata"],
                "files": {
                    "clients": str(clients_file.relative_to(self.output_dir)),
                    "sessions": str(sessions_file.relative_to(self.output_dir)),
                    "scenarios": str(scenarios_dir.relative_to(self.output_dir))
                }
            }, f, indent=2)
            
        self.logger.info(f"Saved bulk test data to {dataset_dir}")


if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Generate test data for Smart Steps AI")
    parser.add_argument("--output-dir", type=str, help="Directory for test data outputs")
    parser.add_argument("--log-level", type=str, default="info", help="Log level (debug, info, warning, error)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--clients", type=int, default=5, help="Number of clients to generate")
    parser.add_argument("--sessions", type=int, default=3, help="Sessions per client")
    parser.add_argument("--messages", type=int, default=10, help="Messages per session")
    parser.add_argument("--scenarios", type=int, default=5, help="Number of test scenarios to generate")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create test data generator
    generator = TestDataGenerator(
        output_dir=args.output_dir,
        log_level=args.log_level,
        seed=args.seed
    )
    
    # Generate bulk data
    generator.generate_bulk_data(
        client_count=args.clients,
        sessions_per_client=args.sessions,
        messages_per_session=args.messages,
        scenario_count=args.scenarios
    )
