#!/usr/bin/env python
"""
Test script for the enhanced persona system.

This script demonstrates the use of the enhanced persona system
by creating a test persona and showing how to use the layered memory.
"""

import os
import sys
from pathlib import Path

# Add the project root to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

from smart_steps_ai.core.enhanced_persona import EnhancedPersonaManager
from smart_steps_ai.core.layered_memory import LayeredMemoryManager

def main():
    """Test the enhanced persona system."""
    print("=== Smart Steps AI: Enhanced Persona Test ===")
    
    # Initialize managers
    enhanced_persona_manager = EnhancedPersonaManager()
    
    # Create a test persona
    persona_id = "test_persona"
    
    # Check if test persona already exists
    existing_persona = enhanced_persona_manager.get_persona(persona_id)
    if existing_persona:
        print(f"Test persona already exists with ID: {persona_id}")
    else:
        # Create the test persona
        print("Creating test persona...")
        
        persona_id = enhanced_persona_manager.create_persona(
            name="Test Therapist",
            persona_type="therapist",
            core_attributes={
                "education": ["University Example", "College Sample"],
                "specializations": ["Cognitive Behavioral Therapy", "Anxiety Disorders"],
                "professional_experience": ["Private Practice", "Community Clinic"],
                "personality_traits": {
                    "empathy": 0.8,
                    "analytical": 0.7,
                    "openness": 0.6
                }
            }
        )
        
        print(f"Persona created successfully with ID: {persona_id}")
    
    # Create memory manager for the test persona
    memory_manager = LayeredMemoryManager(persona_id)
    
    # Add a sample document to the foundation layer
    sample_content = """
    # Cognitive Behavioral Therapy Overview
    
    Cognitive Behavioral Therapy (CBT) is a form of psychological treatment that has been demonstrated
    to be effective for a range of problems including depression, anxiety disorders, alcohol and drug use
    problems, marital problems, eating disorders, and severe mental illness.
    
    ## Key Principles
    
    - CBT is based on the cognitive model: the way we perceive situations influences our emotional, behavioral,
      and physiological reactions.
    - CBT treatment focuses on changing thinking patterns and behaviors.
    - CBT uses a variety of techniques to change thinking patterns, including identifying distortions,
      using cognitive restructuring, and understanding the behavior and motivation of others.
    
    ## Effectiveness
    
    Numerous research studies suggest that CBT leads to significant improvement in functioning and quality
    of life. In many studies, CBT has been demonstrated to be as effective as, or more effective than,
    other forms of psychological therapy or psychiatric medications.
    """
    
    # Add document to foundation layer
    print("\nAdding sample document to foundation layer...")
    memory_manager.foundation.add_document(
        document_id="cbt-overview",
        content=sample_content,
        metadata={
            "title": "Cognitive Behavioral Therapy Overview",
            "type": "knowledge",
            "relevance": ["cbt", "therapy-techniques", "treatment-approaches"]
        }
    )
    print("Document added successfully.")
    
    # Record a sample interaction
    print("\nRecording sample interaction...")
    interaction_id = memory_manager.record_interaction(
        session_id="session-001",
        client_message="I've been feeling really anxious lately, especially in social situations.",
        persona_response="I understand that anxiety can be really challenging, especially when it affects your social interactions. Can you tell me more about the specific situations that trigger your anxiety?"
    )
    print(f"Interaction recorded with ID: {interaction_id}")
    
    # Generate a sample insight
    print("\nGenerating sample insight...")
    insight_id = memory_manager.generate_insight(
        content="I've noticed that clients with social anxiety often respond well to a combination of CBT techniques and gradual exposure therapy, especially when the approach is personalized to their specific triggers.",
        domain="anxiety-treatment",
        sources={
            "foundation": ["cbt-overview"],
            "experience": ["session-001"]
        },
        confidence=0.8
    )
    print(f"Insight generated with ID: {insight_id}")
    
    # Test context retrieval
    print("\nRetrieving context for a query...")
    query = "What are effective approaches for treating anxiety?"
    context = memory_manager.retrieve_context(query, session_id="session-001")
    
    print("\n--- Retrieved Context ---")
    print(memory_manager.format_context(context))
    print("-------------------------")
    
    # List all personas
    print("\nListing all personas:")
    personas = enhanced_persona_manager.list_personas()
    for p in personas:
        print(f"  - {p['name']} ({p['id']}): {p['type']}")
    
    print("\n=== Enhanced Persona Test Complete ===")
    print("Try using the CLI commands to interact with personas:")
    print("  smart-steps-ai persona list")
    print(f"  smart-steps-ai persona info {persona_id}")
    print(f"  smart-steps-ai persona test {persona_id} --interactive")

if __name__ == "__main__":
    main()
