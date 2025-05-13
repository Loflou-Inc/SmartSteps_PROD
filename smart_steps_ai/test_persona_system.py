"""Test script for the persona management system."""

import sys
import os
from pathlib import Path

# Add project root to path
project_dir = Path(r"G:\My Drive\Deftech\SmartSteps\smart_steps_ai")
sys.path.insert(0, str(project_dir))

from src.smart_steps_ai.persona.jane_builder import build_jane
from src.smart_steps_ai.persona.enhanced_manager import EnhancedPersonaManager

def test_build_jane():
    """Test building the Jane persona from documents."""
    print("\n===== Testing Jane Persona Builder =====")
    
    # Build Jane
    jane_path = build_jane()
    
    print(f"Built Jane persona and saved to {jane_path}")
    print("Jane persona created successfully!")
    
    return jane_path

def test_enhanced_persona_manager(jane_path):
    """Test the enhanced persona manager."""
    print("\n===== Testing Enhanced Persona Manager =====")
    
    # Create the personas directory
    personas_dir = project_dir / "personas"
    personas_dir.mkdir(exist_ok=True)
    
    # Copy Jane to the personas directory
    jane_name = jane_path.name
    target_path = personas_dir / jane_name
    
    # Copy the file
    import shutil
    shutil.copy2(jane_path, target_path)
    
    print(f"Copied Jane persona to {target_path}")
    
    # Create manager
    manager = EnhancedPersonaManager(personas_dir)
    
    # Get Jane
    jane = manager.get_enhanced_persona("jane-clinical-psychologist")
    
    if jane:
        print("Successfully loaded enhanced Jane persona")
        print(f"Name: {jane.full_name}")
        print(f"Age: {jane.current_age}")
        print(f"Life events: {len(jane.life_events)}")
        print(f"Therapeutic approaches: {len(jane.therapeutic_approaches)}")
        print(f"Values and beliefs: {len(jane.values_and_beliefs)}")
        print(f"Canonical details: {len(jane.canonical_details)}")
        
        # Add a canonical detail
        print("\nAdding a canonical detail...")
        success, detail, error = manager.add_canonical_detail(
            persona_name="jane-clinical-psychologist",
            detail="The last incident with my stepfather happened on my 16th birthday. He threw me against a wall when I asked to go out with friends.",
            context="Client asked about the final incident of abuse",
            categories=["abuse", "stepfather", "trauma", "childhood"],
            related_event_id=jane.life_events[0].id  # First life event is childhood abuse
        )
        
        if success and detail:
            print(f"Successfully added canonical detail: {detail.id}")
            print(f"Detail: {detail.detail}")
            
            # Test retrieving the detail
            print("\nRetrieving canonical details about abuse...")
            abuse_details = manager.get_canonical_details(
                persona_name="jane-clinical-psychologist",
                category="abuse"
            )
            
            if abuse_details:
                print(f"Found {len(abuse_details)} details about abuse:")
                for d in abuse_details:
                    print(f"- {d.detail}")
            else:
                print("No abuse details found")
            
            # Test recording usage
            print("\nRecording usage of the canonical detail...")
            success = manager.record_detail_usage(
                persona_name="jane-clinical-psychologist",
                detail_id=detail.id
            )
            
            if success:
                print("Successfully recorded usage")
                
                # Get the updated detail
                updated_jane = manager.get_enhanced_persona("jane-clinical-psychologist")
                if updated_jane:
                    for d in updated_jane.canonical_details:
                        if d.id == detail.id:
                            print(f"Updated usage count: {d.usage_count}")
                            print(f"Reference history: {len(d.reference_history)} entries")
            else:
                print("Failed to record usage")
            
            # Test getting relevant details
            print("\nGetting details relevant to 'final abuse incident'...")
            relevant_details = manager.get_relevant_canonical_details(
                persona_name="jane-clinical-psychologist",
                query="final abuse incident"
            )
            
            if relevant_details:
                print(f"Found {len(relevant_details)} relevant details:")
                for d in relevant_details:
                    print(f"- {d.detail}")
            else:
                print("No relevant details found")
        else:
            print(f"Failed to add canonical detail: {error}")
    else:
        print("Failed to load enhanced Jane persona")
    
    print("\nEnhanced Persona Manager test completed!")

if __name__ == "__main__":
    jane_path = test_build_jane()
    test_enhanced_persona_manager(jane_path)
