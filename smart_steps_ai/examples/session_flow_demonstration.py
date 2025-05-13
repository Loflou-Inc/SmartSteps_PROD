#!/usr/bin/env python
"""
Session Flow Demonstration

This script demonstrates a complete session flow in the Smart Steps AI module,
from creation to analysis.
"""

import os
import time
import json
import uuid
from pathlib import Path
from datetime import datetime

from smart_steps_ai.core.config_manager import ConfigManager
from smart_steps_ai.core.persona_manager import PersonaManager
from smart_steps_ai.core.session_manager import SessionManager
from smart_steps_ai.core.layered_memory import LayeredMemoryManager
from smart_steps_ai.core.cache_manager import performance_monitor
from smart_steps_ai.core.memory_optimizer import memory_monitor


def setup_example_environment():
    """Set up an example environment for the demonstration."""
    # Create temporary directories
    base_dir = Path("./example_data")
    base_dir.mkdir(exist_ok=True)
    
    config_dir = base_dir / "config"
    data_dir = base_dir / "data"
    personas_dir = base_dir / "personas"
    sessions_dir = base_dir / "sessions"
    
    config_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)
    personas_dir.mkdir(exist_ok=True)
    sessions_dir.mkdir(exist_ok=True)
    
    # Create example persona
    persona_dir = personas_dir / "therapist"
    persona_dir.mkdir(exist_ok=True)
    
    persona_data = {
        "id": "therapist",
        "name": "Dr. Sarah Thompson",
        "type": "therapist",
        "background": "Dr. Thompson is a licensed clinical psychologist with over 15 years of experience in cognitive behavioral therapy.",
        "education": ["Ph.D. in Clinical Psychology, Stanford University", 
                      "M.A. in Psychology, University of California, Berkeley"],
        "specialties": ["Cognitive Behavioral Therapy", "Anxiety Disorders", "Depression", "Trauma"],
        "approach": "Dr. Thompson uses evidence-based cognitive behavioral therapy techniques to help clients identify and change negative thought patterns."
    }
    
    with open(persona_dir / "persona.json", "w") as f:
        json.dump(persona_data, f, indent=2)
    
    return {
        "base_dir": base_dir,
        "config_dir": config_dir,
        "data_dir": data_dir,
        "personas_dir": personas_dir,
        "sessions_dir": sessions_dir
    }


def create_session(persona_manager, session_manager):
    """Create a new therapy session."""
    print("\n=== Creating a New Session ===\n")
    
    # Load the therapist persona
    persona = persona_manager.load_persona("therapist")
    print(f"Loaded persona: {persona['name']}")
    print(f"Specialties: {', '.join(persona['specialties'])}")
    
    # Create a new session
    client_name = "Alex Johnson"
    session_type = "initial_consultation"
    
    session = session_manager.create_session(
        persona_id="therapist",
        client_name=client_name,
        session_type=session_type
    )
    
    print(f"Created new session for {client_name}")
    print(f"Session ID: {session['id']}")
    print(f"Session type: {session['session_type']}")
    print(f"Created at: {session['created_at']}")
    
    return session


def conduct_session(session_manager, memory_manager, session):
    """Conduct a therapy session with a client."""
    print("\n=== Conducting Session ===\n")
    
    session_id = session["id"]
    
    # Define the conversation flow
    conversation = [
        {
            "speaker": "persona",
            "content": "Hello Alex, I'm Dr. Thompson. It's nice to meet you. How are you feeling today?"
        },
        {
            "speaker": "client",
            "content": "I've been feeling really anxious lately. I can't seem to stop worrying about everything."
        },
        {
            "speaker": "persona",
            "content": "I'm sorry to hear you've been feeling anxious. Can you tell me more about what kind of worries have been troubling you?"
        },
        {
            "speaker": "client",
            "content": "I'm constantly worried about work, even when I'm not there. I keep thinking I'm going to miss a deadline or make a mistake."
        },
        {
            "speaker": "persona",
            "content": "It sounds like your work worries are following you home. How long has this been happening, and has anything changed recently at work?"
        },
        {
            "speaker": "client",
            "content": "It's been getting worse over the past few months. We have a new manager who has really high expectations, and I'm afraid of letting them down."
        },
        {
            "speaker": "persona",
            "content": "That change in management sounds significant. How do these worries affect your daily life? Are they impacting your sleep or other activities?"
        },
        {
            "speaker": "client",
            "content": "Yes, I'm having trouble sleeping. I lie awake thinking about work, and then I'm tired the next day, which makes me more anxious about my performance."
        },
        {
            "speaker": "persona",
            "content": "I understand. This cycle of anxiety and sleep disruption can be difficult to break. Have you tried any strategies to manage your anxiety so far?"
        },
        {
            "speaker": "client",
            "content": "I've tried some deep breathing, but it's hard to remember to do it when I'm feeling overwhelmed."
        },
        {
            "speaker": "persona",
            "content": "Deep breathing can be helpful. For our next session, I'd like to teach you some additional CBT techniques specifically for managing work-related anxiety and improving sleep. In the meantime, could you keep a simple log of when you notice anxiety spikes and what thoughts accompany them?"
        },
        {
            "speaker": "client",
            "content": "I can try to do that. Will that help us figure out what's causing the anxiety?"
        },
        {
            "speaker": "persona",
            "content": "Exactly. Tracking your anxiety will help us identify patterns and triggers, which is the first step in CBT. We'll use this information to develop strategies tailored to your specific situation. How does that sound?"
        },
        {
            "speaker": "client",
            "content": "That makes sense. I'll try keeping a log before our next session."
        },
        {
            "speaker": "persona",
            "content": "Great. Before we wrap up today, do you have any questions for me about the approach we'll be taking or anything else?"
        },
        {
            "speaker": "client",
            "content": "Not right now. I'm just hoping this will help me feel better soon."
        },
        {
            "speaker": "persona",
            "content": "I understand. CBT has been shown to be effective for anxiety, and we'll work at a pace that feels right for you. I look forward to our next session where we can dive deeper into some techniques that might help."
        }
    ]
    
    # Conduct the session
    for i, message in enumerate(conversation):
        speaker = message["speaker"]
        content = message["content"]
        
        # Add message to session
        session_manager.add_message(
            session_id=session_id,
            speaker=speaker,
            content=content
        )
        
        # If client message, record in memory
        if speaker == "client":
            print(f"Client: {content}")
        else:
            print(f"Persona: {content}")
        
        # Record interaction in layered memory
        if i > 0 and speaker == "persona":
            memory_manager.record_interaction(
                session_id=session_id,
                client_message=conversation[i-1]["content"],
                persona_response=content
            )
    
    # Generate insights
    insights = [
        {
            "content": "Client is experiencing work-related anxiety that is affecting sleep quality.",
            "domain": "anxiety",
            "confidence": 0.9
        },
        {
            "content": "Change in management appears to be a significant trigger for increased anxiety.",
            "domain": "workplace_stress",
            "confidence": 0.85
        },
        {
            "content": "Client is experiencing a negative feedback loop between anxiety and sleep disruption.",
            "domain": "sleep_disorders",
            "confidence": 0.8
        },
        {
            "content": "Client has limited coping strategies for managing anxiety.",
            "domain": "coping_skills",
            "confidence": 0.75
        }
    ]
    
    print("\n=== Generating Insights ===\n")
    
    for insight in insights:
        memory_manager.generate_insight(
            content=insight["content"],
            domain=insight["domain"],
            sources={
                "experience": [session_id]
            },
            confidence=insight["confidence"]
        )
        print(f"Generated insight ({insight['domain']}): {insight['content']}")
    
    # End the session
    session_manager.end_session(
        session_id=session_id,
        summary="Initial session with Alex who is experiencing work-related anxiety and sleep disruption. Plan to introduce CBT techniques in next session. Assigned anxiety tracking homework."
    )
    
    print("\nSession completed and saved.")
    
    return session_id


def analyze_session(session_manager, memory_manager, session_id):
    """Analyze the completed therapy session."""
    print("\n=== Analyzing Session ===\n")
    
    # Retrieve session
    session = session_manager.get_session(session_id)
    print(f"Analyzing session for {session['client_name']}")
    
    # Get session messages
    messages = session_manager.get_messages(session_id)
    print(f"Session contains {len(messages)} messages")
    
    # Get session summary
    summary = session["summary"]
    print(f"Session summary: {summary}")
    
    # Retrieve context for specific topics
    topics = ["anxiety", "work stress", "sleep", "coping strategies"]
    
    for topic in topics:
        print(f"\nContext for '{topic}':")
        context = memory_manager.retrieve_context(
            query=topic,
            session_id=session_id
        )
        
        # Format and display context
        formatted_context = memory_manager.format_context(context)
        print(f"Retrieved {len(formatted_context.split())} words of context")
        
        # Just show a brief excerpt of each section
        for section in ["foundation", "experience", "synthesis", "meta_cognitive"]:
            if context[section]:
                excerpt = context[section][:100] + "..." if len(context[section]) > 100 else context[section]
                print(f"- {section.capitalize()}: {excerpt}")
    
    # Generate "report"
    print("\n=== Session Report ===\n")
    
    print("INITIAL CONSULTATION REPORT")
    print("==========================\n")
    print(f"Client: {session['client_name']}")
    print(f"Date: {session['created_at']}")
    print(f"Therapist: Dr. Sarah Thompson")
    print("\nPRESENTING CONCERNS:")
    print("- Work-related anxiety")
    print("- Sleep disruption")
    print("- Limited coping strategies")
    print("- Worry about job performance")
    print("\nOBSERVATIONS:")
    print("- Client is experiencing anxiety related to changes in workplace management")
    print("- Anxiety is creating a negative cycle with sleep disruption")
    print("- Client has attempted deep breathing but needs additional coping strategies")
    print("- Client is receptive to CBT approach and homework assignments")
    print("\nPLAN:")
    print("1. Introduce CBT techniques for managing anxiety")
    print("2. Provide strategies for improving sleep hygiene")
    print("3. Review anxiety tracking log at next session")
    print("4. Develop personalized coping strategies")
    
    print("\nSession analysis completed.")


def cleanup_example_environment(dirs):
    """Clean up the example environment."""
    import shutil
    
    print("\nCleaning up example environment...")
    
    try:
        shutil.rmtree(dirs["base_dir"])
        print("Cleanup completed successfully!")
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


def main():
    """Main function to run the session flow demonstration."""
    print("=== Smart Steps AI Session Flow Demonstration ===\n")
    
    # Start performance monitoring
    performance_monitor.timings.clear()
    performance_monitor.execution_counts.clear()
    
    # Setup example environment
    dirs = setup_example_environment()
    
    try:
        # Initialize components
        persona_manager = PersonaManager(personas_dir=dirs["personas_dir"])
        session_manager = SessionManager(
            sessions_dir=dirs["sessions_dir"],
            persona_manager=persona_manager
        )
        memory_manager = LayeredMemoryManager(
            persona_id="therapist",
            data_dir=dirs["data_dir"] / "memory"
        )
        
        # Run demonstration
        session = create_session(persona_manager, session_manager)
        session_id = conduct_session(session_manager, memory_manager, session)
        analyze_session(session_manager, memory_manager, session_id)
        
        # Generate performance report
        print("\n=== Performance Report ===\n")
        report = performance_monitor.get_performance_report()
        
        print("Operation Performance:")
        print("---------------------")
        for operation, metrics in report.items():
            print(f"Operation: {operation}")
            print(f"  Average time: {metrics['average_time'] * 1000:.2f} ms")
            print(f"  Execution count: {metrics['execution_count']}")
            print()
        
        # Get memory usage
        memory_usage = memory_monitor.get_memory_usage()
        print("Memory Usage:")
        print("-------------")
        print(f"Total objects: {memory_usage['total_objects']}")
        print(f"Total size (MB): {memory_usage['total_size_mb']:.2f}")
        
        print("\n=== Demonstration completed successfully! ===")
    
    finally:
        # Clean up
        cleanup_example_environment(dirs)


if __name__ == "__main__":
    main()
