#!/usr/bin/env python
"""
Script to import Jane's persona documents and create the Jane persona.

This script automates the creation of the Jane persona and imports
all her background documents into the layered memory system.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

from smart_steps_ai.core.enhanced_persona import EnhancedPersonaManager
from smart_steps_ai.core.layered_memory import LayeredMemoryManager
from smart_steps_ai.utils.document_processor import DocumentProcessor, PdfProcessor

def main():
    """Import Jane's persona documents and create the Jane persona."""
    print("=== Smart Steps AI: Jane Persona Import ===")
    
    # Initialize managers
    enhanced_persona_manager = EnhancedPersonaManager()
    document_processor = DocumentProcessor()
    
    # Define Jane's persona
    jane_persona = {
        "id": "jane_stevens",
        "name": "Dr. Jane Stevens",
        "type": "clinical_psychologist",
        "core_attributes": {
            "education": [
                "University of Chicago (B.A. Psychology)",
                "Northwestern University (M.A. Clinical Psychology)",
                "Northwestern Feinberg School of Medicine (Ph.D. Clinical Psychology)",
                "APA-Accredited CMHC Psychology Internship in NW Ohio"
            ],
            "specializations": [
                "Trauma and PTSD",
                "Personality Disorders",
                "Therapeutic Approaches for Childhood Trauma",
                "Narcissistic Vulnerability"
            ],
            "professional_experience": [
                "Northwest Ohio Psychiatric Hospital",
                "Private Practice Therapist",
                "Clinical Researcher, Trauma Studies"
            ],
            "personality_traits": {
                "empathy": 0.9,
                "analytical": 0.8,
                "resilience": 0.85,
                "introspection": 0.9,
                "openness": 0.7,
                "warmth": 0.8
            }
        },
        "memory_configuration": {
            "reflection_frequency": 5,
            "learning_rate": 0.4,
            "confidence_threshold": 0.7
        },
        "growth_boundaries": {
            "allowed_domains": [
                "trauma-therapy",
                "clinical-psychology",
                "therapeutic-techniques",
                "personality-disorders",
                "childhood-development"
            ],
            "personality_variance": 0.2
        }
    }
    
    # Check if Jane persona already exists
    existing_persona = enhanced_persona_manager.get_persona(jane_persona["id"])
    if existing_persona:
        print(f"Jane persona already exists with ID: {jane_persona['id']}")
        print("Updating existing persona...")
        
        # Update the persona
        enhanced_persona_manager.update_persona(jane_persona["id"], jane_persona)
        print("Persona updated successfully.")
    else:
        # Create the Jane persona
        print("Creating Jane persona...")
        
        # Import the persona definition
        try:
            persona_id = enhanced_persona_manager.import_from_file("jane_persona.json")
            if not persona_id:
                # If import fails, create from the dictionary
                enhanced_persona_manager.update_persona(jane_persona["id"], jane_persona)
                persona_id = jane_persona["id"]
        except:
            # If import fails, create from the dictionary
            persona_id = jane_persona["id"]
            for key, value in jane_persona.items():
                if key != "id":
                    enhanced_persona_manager.update_persona(persona_id, {key: value})
        
        print(f"Persona created successfully with ID: {persona_id}")
    
    # Create memory manager for Jane
    memory_manager = LayeredMemoryManager(jane_persona["id"])
    
    # Define document mappings
    documents = [
        {
            "file": "Jane-Early Trauma and Giftedness in Context.pdf",
            "id": "jane-early-trauma",
            "type": "biography",
            "period": "early-childhood",
            "relevance": ["trauma", "childhood", "development", "giftedness"]
        },
        {
            "file": "Jane's Middle Childhood (Ages 7–12)_ Trauma and Coping.pdf",
            "id": "jane-middle-childhood",
            "type": "biography",
            "period": "middle-childhood",
            "relevance": ["trauma", "childhood", "coping-mechanisms", "abuse"]
        },
        {
            "file": "Jane's Adolescent Trauma and Identity Formation-RESEARCH.pdf",
            "id": "jane-adolescent-trauma",
            "type": "biography",
            "period": "adolescence",
            "relevance": ["trauma", "identity", "adolescent-development"]
        },
        {
            "file": "Jane's Journal_ Clinical Psychologist (Ages 43–46).pdf",
            "id": "jane-journal",
            "type": "journal",
            "period": "adult-professional",
            "relevance": ["clinical-practice", "burnout", "professional-identity"]
        },
        {
            "file": "University of Chicago Undergraduate Psychology Curriculum.pdf",
            "id": "uchicago-psychology",
            "type": "education",
            "period": "undergraduate",
            "relevance": ["psychology", "education", "academic-foundation"]
        },
        {
            "file": "Northwestern University (Feinberg) M.A. in Clinical Psychology (2-Year Program).pdf",
            "id": "northwestern-ma",
            "type": "education",
            "period": "graduate",
            "relevance": ["clinical-psychology", "education", "professional-training"]
        },
        {
            "file": "Northwestern Feinberg School of Medicine – Clinical Psychology PhD Curriculum (Years 1–4).pdf",
            "id": "northwestern-phd",
            "type": "education",
            "period": "graduate",
            "relevance": ["clinical-psychology", "education", "research-training"]
        },
        {
            "file": "Simulating an APA-Accredited CMHC Psychology Internship in NW Ohio.pdf",
            "id": "psychology-internship",
            "type": "education",
            "period": "professional-training",
            "relevance": ["clinical-practice", "professional-development", "supervised-experience"]
        },
        {
            "file": "Wounded Gods_ Narcissistic Vulnerability and PTSD Symptomatology Following Ego-Threatening Trauma.pdf",
            "id": "narcissistic-vulnerability-research",
            "type": "research",
            "period": "professional-research",
            "relevance": ["narcissism", "ptsd", "trauma", "ego-threat", "clinical-research"]
        }
    ]
    
    # Find Jane's documents directory
    jane_dir = os.path.join(project_root, "personas", "Jane")
    if not os.path.exists(jane_dir):
        print(f"Jane's document directory not found: {jane_dir}")
        # Try to find it elsewhere
        possible_paths = [
            os.path.join(project_root, "smart_steps_ai", "personas", "Jane"),
            os.path.join(project_root, "data", "personas", "Jane"),
            os.path.join(project_root, "resources", "personas", "Jane")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                jane_dir = path
                print(f"Found Jane's documents at: {jane_dir}")
                break
        else:
            print("Could not find Jane's document directory. Please specify the path:")
            user_path = input("Path to Jane's documents: ")
            if os.path.exists(user_path):
                jane_dir = user_path
            else:
                print(f"Error: Path not found: {user_path}")
                return
    
    # Import documents
    print("\nImporting Jane's documents...")
    
    # First, check if the PDF processor is available
    try:
        pdf_processor = PdfProcessor()
        pdf_available = True
    except ImportError:
        pdf_available = False
        print("Warning: PDF processing libraries not found.")
        print("Only text files can be processed. Install PyPDF2 or pdfplumber for PDF support.")
    
    # Process documents
    for doc in documents:
        # Check if file exists
        file_path = os.path.join(jane_dir, doc["file"])
        txt_file = os.path.splitext(file_path)[0] + ".txt"
        
        # Find the best available file
        if os.path.exists(file_path):
            # Use the original file
            source_path = file_path
            print(f"Found original document: {doc['file']}")
        elif os.path.exists(txt_file):
            # Use the text version
            source_path = txt_file
            print(f"Found text version: {os.path.basename(txt_file)}")
        else:
            print(f"Warning: Document not found: {doc['file']}")
            continue
        
        # Process the document
        try:
            # Check if it's a PDF and we need to convert
            if source_path.lower().endswith('.pdf') and not pdf_available:
                print(f"Skipping PDF document (no PDF support): {doc['file']}")
                continue
            
            print(f"Processing: {os.path.basename(source_path)}")
            
            # Process the document
            content, metadata = document_processor.process_document(source_path)
            
            # Add document to persona's foundation layer
            memory_manager.foundation.add_document(
                document_id=doc["id"],
                content=content,
                metadata={
                    "title": metadata.get("title", os.path.basename(source_path)),
                    "type": doc["type"],
                    "period": doc["period"],
                    "relevance": doc["relevance"],
                    "source_file": os.path.basename(source_path)
                }
            )
            
            # Add knowledge source to persona definition
            enhanced_persona_manager.add_knowledge_source(
                persona_id=jane_persona["id"],
                source_id=doc["id"],
                source_type=doc["type"],
                source_path=source_path,
                metadata={
                    "period": doc["period"],
                    "relevance": doc["relevance"]
                }
            )
            
            print(f"  [✓] Imported successfully")
        
        except Exception as e:
            print(f"  [✗] Error processing document: {str(e)}")
    
    # Generate some initial insights
    print("\nGenerating initial insights...")
    
    insights = [
        {
            "content": "My personal experience with early childhood trauma gives me a unique perspective on how trauma manifests in adult clients. I can recognize the subtle signs of hypervigilance and dissociation because I've experienced them myself.",
            "domain": "trauma-response",
            "sources": {
                "foundation": ["jane-early-trauma", "jane-middle-childhood"],
                "experience": []
            },
            "confidence": 0.9
        },
        {
            "content": "I've noticed how my academic training in both psychodynamic and cognitive-behavioral approaches allows me to integrate multiple perspectives when treating complex trauma. My own healing journey informs my therapeutic approach in ways textbooks couldn't teach.",
            "domain": "therapeutic-approach",
            "sources": {
                "foundation": ["northwestern-ma", "northwestern-phd", "psychology-internship"],
                "experience": []
            },
            "confidence": 0.85
        },
        {
            "content": "Working at Northwest Ohio Psychiatric Hospital has taught me about the systemic challenges in mental healthcare. The understaffing and limited resources create a constant tension between providing ideal care and managing realistic constraints.",
            "domain": "healthcare-systems",
            "sources": {
                "foundation": ["jane-journal"],
                "experience": []
            },
            "confidence": 0.8
        }
    ]
    
    for insight in insights:
        memory_manager.generate_insight(
            content=insight["content"],
            domain=insight["domain"],
            sources=insight["sources"],
            confidence=insight["confidence"]
        )
        print(f"  [✓] Generated insight on {insight['domain']}")
    
    # Update meta-cognitive layer
    print("\nInitializing meta-cognitive awareness...")
    
    memory_manager.meta_cognitive.update_domain_knowledge(
        domain="trauma-therapy",
        confidence=0.9,
        notes="Strong foundation from both personal experience and professional training"
    )
    
    memory_manager.meta_cognitive.update_domain_knowledge(
        domain="childhood-development",
        confidence=0.85,
        notes="Comprehensive understanding from academic training and research"
    )
    
    memory_manager.meta_cognitive.update_domain_knowledge(
        domain="personality-disorders",
        confidence=0.8,
        notes="Specialized focus in research and clinical practice"
    )
    
    memory_manager.meta_cognitive.update_domain_knowledge(
        domain="medication-management",
        confidence=0.6,
        notes="Basic knowledge from clinical practice, not a primary focus area"
    )
    
    print("  [✓] Updated knowledge self-awareness")
    
    print("\n=== Jane Persona Import Complete ===")
    print(f"Persona ID: {jane_persona['id']}")
    print("Test the persona with:")
    print(f"  smart-steps-ai persona test {jane_persona['id']}")
    print("Or run an interactive test:")
    print(f"  smart-steps-ai persona test {jane_persona['id']} --interactive")

if __name__ == "__main__":
    main()
