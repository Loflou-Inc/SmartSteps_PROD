#!/usr/bin/env python
"""
Persona Customization Example

This script demonstrates how to create, customize, and validate professional personas
in the Smart Steps AI module.
"""

import os
import json
import shutil
from pathlib import Path

from smart_steps_ai.core.persona_manager import PersonaManager
from smart_steps_ai.core.layered_memory import LayeredMemoryManager
from smart_steps_ai.core.knowledge_store import KnowledgeStore


def setup_example_environment():
    """Set up an example environment for the demonstration."""
    # Create temporary directories
    base_dir = Path("./example_data")
    base_dir.mkdir(exist_ok=True)
    
    data_dir = base_dir / "data"
    personas_dir = base_dir / "personas"
    
    data_dir.mkdir(exist_ok=True)
    personas_dir.mkdir(exist_ok=True)
    
    return {
        "base_dir": base_dir,
        "data_dir": data_dir,
        "personas_dir": personas_dir
    }


def create_base_persona(persona_manager, personas_dir):
    """Create a basic professional persona."""
    print("\n=== Creating Base Persona ===\n")
    
    # Define persona data
    persona_data = {
        "id": "behavioral_analyst",
        "name": "Dr. Michael Rivera",
        "type": "behavioral_analyst",
        "background": "Dr. Rivera is a behavioral analyst with expertise in cognitive-behavioral interventions for at-risk youth.",
        "education": [
            "Ph.D. in Psychology, University of Michigan",
            "M.S. in Applied Behavior Analysis, Florida State University"
        ],
        "specialties": [
            "Cognitive-Behavioral Interventions",
            "Risk Assessment",
            "Youth Rehabilitation",
            "Trauma-Informed Care"
        ],
        "approach": "Evidence-based behavioral analysis focusing on identifying triggers, modifying behavior patterns, and promoting positive development."
    }
    
    # Create persona directory
    persona_dir = personas_dir / "behavioral_analyst"
    persona_dir.mkdir(exist_ok=True)
    
    # Save persona data
    with open(persona_dir / "persona.json", "w") as f:
        json.dump(persona_data, f, indent=2)
    
    print(f"Created base persona: {persona_data['name']}")
    print(f"Type: {persona_data['type']}")
    print(f"Specialties: {', '.join(persona_data['specialties'])}")
    
    # Load persona to verify
    persona = persona_manager.load_persona("behavioral_analyst")
    print(f"\nPersona loaded successfully: {persona['name']}")
    
    return persona


def enhance_persona_with_attributes(persona_manager, personas_dir):
    """Enhance a persona with additional attributes."""
    print("\n=== Enhancing Persona with Additional Attributes ===\n")
    
    # Load the base persona
    persona = persona_manager.load_persona("behavioral_analyst")
    
    # Add additional attributes
    enhanced_persona = persona.copy()
    
    # Add communication style
    enhanced_persona["communication_style"] = {
        "formality": "moderate",
        "empathy": "high",
        "directness": "high",
        "technical_language": "moderate",
        "pace": "measured"
    }
    
    # Add theoretical orientation
    enhanced_persona["theoretical_orientation"] = [
        "Cognitive-Behavioral",
        "Social Learning Theory",
        "Risk-Need-Responsivity Model",
        "Positive Youth Development"
    ]
    
    # Add intervention techniques
    enhanced_persona["intervention_techniques"] = [
        "Cognitive Restructuring",
        "Behavior Modification",
        "Skills Training",
        "Motivational Interviewing",
        "Contingency Management"
    ]
    
    # Add response patterns
    enhanced_persona["response_patterns"] = {
        "assessment_focus": [
            "Identifying behavioral triggers",
            "Evaluating risk factors",
            "Analyzing reinforcement patterns",
            "Monitoring progress indicators"
        ],
        "intervention_strategies": [
            "Collaborative goal setting",
            "Incremental behavior shaping",
            "Environmental modifications",
            "Skill development prioritization"
        ]
    }
    
    # Save enhanced persona
    persona_dir = personas_dir / "behavioral_analyst"
    with open(persona_dir / "persona.json", "w") as f:
        json.dump(enhanced_persona, f, indent=2)
    
    print("Enhanced persona with additional attributes:")
    print(f"Communication Style: {enhanced_persona['communication_style']['formality']} formality, {enhanced_persona['communication_style']['empathy']} empathy")
    print(f"Theoretical Orientation: {', '.join(enhanced_persona['theoretical_orientation'])}")
    print(f"Intervention Techniques: {', '.join(enhanced_persona['intervention_techniques'][:3])} and others")
    
    # Reload persona to verify changes
    updated_persona = persona_manager.load_persona("behavioral_analyst")
    print(f"\nEnhanced persona loaded successfully: {updated_persona['name']}")
    print(f"Added {len(updated_persona) - len(persona)} new attribute categories")
    
    return updated_persona


def add_knowledge_to_persona(memory_manager):
    """Add knowledge to a persona using the layered memory system."""
    print("\n=== Adding Knowledge to Persona ===\n")
    
    # Add foundation knowledge
    print("Adding foundation knowledge...")
    
    # Example 1: Core theoretical knowledge
    theoretical_knowledge = """
    The Risk-Need-Responsivity (RNR) model is a key framework in behavioral analysis for at-risk populations. 
    It consists of three principles:
    
    1. Risk Principle: Match the intensity of interventions to the individual's risk level.
    2. Need Principle: Target criminogenic needs that are directly linked to criminal behavior.
    3. Responsivity Principle: Tailor the intervention to the individual's learning style and abilities.
    
    Research indicates that adherence to these principles significantly improves intervention outcomes, 
    with meta-analyses showing 17-35% reduction in recidivism when all three principles are followed.
    """
    
    memory_manager.foundation.add_document(
        document_id="rnr_model",
        content=theoretical_knowledge,
        metadata={
            "type": "theoretical_knowledge",
            "relevance": "high",
            "domain": "behavioral_analysis"
        }
    )
    
    # Example 2: Intervention techniques
    intervention_techniques = """
    Cognitive Restructuring is a technique used to identify and modify maladaptive thought patterns.
    The process involves:
    
    1. Identifying automatic negative thoughts
    2. Evaluating the evidence for and against these thoughts
    3. Developing more balanced alternative thoughts
    4. Practicing the implementation of these alternatives in daily situations
    
    This technique is particularly effective for addressing distortions such as catastrophizing, 
    all-or-nothing thinking, and overgeneralizing, which are common in at-risk youth populations.
    
    Implementation typically follows a structured approach, beginning with education about the 
    thought-feeling-behavior connection, followed by guided practice in identifying thoughts, 
    and culminating in independent application of restructuring techniques.
    """
    
    memory_manager.foundation.add_document(
        document_id="cognitive_restructuring",
        content=intervention_techniques,
        metadata={
            "type": "intervention_technique",
            "relevance": "high",
            "domain": "cognitive_behavioral"
        }
    )
    
    # Example 3: Case conceptualization approach
    case_conceptualization = """
    Behavioral analysis case conceptualization for at-risk youth follows a structured format:
    
    1. Presenting Issues: Identify specific behavioral concerns, their frequency, intensity, and context.
    
    2. Developmental History: Examine developmental milestones, early experiences, and attachment patterns 
       that may contribute to current behavioral patterns.
    
    3. Functional Analysis:
       - Antecedents: Events or situations that precede problematic behaviors
       - Behaviors: Detailed description of concerning behaviors
       - Consequences: Outcomes that may maintain the behaviors
    
    4. Risk and Protective Factors:
       - Individual factors (e.g., impulsivity, skill deficits)
       - Family factors (e.g., parenting style, family conflict)
       - Peer factors (e.g., deviant peer associations)
       - School/Community factors (e.g., academic performance, neighborhood resources)
    
    5. Theoretical Understanding: Application of relevant theories (e.g., social learning, attachment)
       to explain behavioral patterns.
    
    6. Intervention Planning: Targeted interventions based on the conceptualization, prioritizing
       factors with the strongest influence on behavior.
    
    Regular reassessment of the conceptualization ensures that interventions remain responsive
    to changes in the youth's circumstances and development.
    """
    
    memory_manager.foundation.add_document(
        document_id="case_conceptualization",
        content=case_conceptualization,
        metadata={
            "type": "clinical_approach",
            "relevance": "high",
            "domain": "assessment"
        }
    )
    
    # Generate insights
    print("\nGenerating insights from knowledge...")
    
    memory_manager.generate_insight(
        content="The effectiveness of behavioral interventions is significantly enhanced when properly matched to the individual's risk level, criminogenic needs, and learning style.",
        domain="intervention_planning",
        sources={
            "foundation": ["rnr_model"]
        },
        confidence=0.9
    )
    
    memory_manager.generate_insight(
        content="Cognitive restructuring techniques should be adapted based on the youth's developmental stage and cognitive abilities, with more concrete approaches for younger or cognitively limited individuals.",
        domain="cognitive_behavioral",
        sources={
            "foundation": ["cognitive_restructuring"]
        },
        confidence=0.85
    )
    
    memory_manager.generate_insight(
        content="Comprehensive case conceptualization that integrates multiple ecological levels (individual, family, peer, community) provides the most effective foundation for intervention planning with at-risk youth.",
        domain="assessment",
        sources={
            "foundation": ["case_conceptualization"]
        },
        confidence=0.88
    )
    
    # Retrieve context to verify knowledge integration
    test_query = "How should I apply the Risk-Need-Responsivity model in my work with at-risk youth?"
    context = memory_manager.retrieve_context(query=test_query)
    formatted_context = memory_manager.format_context(context)
    
    print(f"\nRetrieved {len(formatted_context.split())} words of context for query: '{test_query}'")
    print("Knowledge successfully integrated into persona memory system.")
    
    return formatted_context


def create_specialized_persona_variant(persona_manager, personas_dir, base_persona_id):
    """Create a specialized variant of an existing persona."""
    print("\n=== Creating Specialized Persona Variant ===\n")
    
    # Load the base persona
    base_persona = persona_manager.load_persona(base_persona_id)
    
    # Create a specialized variant
    specialized_persona = base_persona.copy()
    specialized_persona["id"] = "juvenile_justice_specialist"
    specialized_persona["name"] = "Dr. Sofia Mendez"
    specialized_persona["type"] = "juvenile_justice_specialist"
    specialized_persona["background"] = "Dr. Mendez is a behavioral analyst specializing in juvenile justice, with extensive experience working in detention facilities and diversion programs."
    
    # Modify education
    specialized_persona["education"] = [
        "Ph.D. in Forensic Psychology, John Jay College of Criminal Justice",
        "M.S. in Criminal Justice, University of California, Irvine",
        "Certificate in Juvenile Justice Intervention, Georgetown University"
    ]
    
    # Refine specialties
    specialized_persona["specialties"] = [
        "Juvenile Justice Intervention",
        "Recidivism Reduction",
        "Risk Assessment",
        "Trauma-Informed Care",
        "Court-Mandated Treatment"
    ]
    
    # Update approach
    specialized_persona["approach"] = "Evidence-based assessment and intervention within juvenile justice contexts, balancing accountability with rehabilitation, and addressing unique developmental needs of justice-involved youth."
    
    # Refine theoretical orientation
    specialized_persona["theoretical_orientation"] = [
        "Risk-Need-Responsivity Model",
        "Cognitive-Behavioral",
        "Desistance Theory",
        "Restorative Justice"
    ]
    
    # Update intervention techniques
    specialized_persona["intervention_techniques"] = [
        "Risk Assessment",
        "Criminogenic Need Targeting",
        "Cognitive Restructuring",
        "Skill Building",
        "Family System Intervention",
        "Community Reintegration Planning"
    ]
    
    # Add specific response patterns
    specialized_persona["response_patterns"]["juvenile_justice_focus"] = [
        "Emphasizing personal accountability while acknowledging developmental factors",
        "Balancing public safety concerns with rehabilitation needs",
        "Addressing criminogenic thinking patterns",
        "Focusing on prosocial skill development",
        "Engaging family and community support systems"
    ]
    
    # Save specialized persona
    specialized_dir = personas_dir / "juvenile_justice_specialist"
    specialized_dir.mkdir(exist_ok=True)
    
    with open(specialized_dir / "persona.json", "w") as f:
        json.dump(specialized_persona, f, indent=2)
    
    print(f"Created specialized persona variant: {specialized_persona['name']}")
    print(f"Type: {specialized_persona['type']}")
    print(f"Specialties: {', '.join(specialized_persona['specialties'][:3])} and others")
    
    # Verify the specialized persona is loaded correctly
    loaded_persona = persona_manager.load_persona("juvenile_justice_specialist")
    print(f"\nSpecialized persona loaded successfully: {loaded_persona['name']}")
    
    return loaded_persona


def validate_persona_cohesion(persona_manager, memory_manager, personas_dir):
    """Validate the psychological cohesion of a persona."""
    print("\n=== Validating Persona Psychological Cohesion ===\n")
    
    # Create a validation function that scores different aspects of the persona
    def validate_persona(persona_id):
        persona = persona_manager.load_persona(persona_id)
        
        validation_results = {}
        
        # Check completeness (required fields)
        required_fields = ["id", "name", "type", "background", "education", "specialties", "approach"]
        completeness_score = sum(1 for field in required_fields if field in persona) / len(required_fields)
        validation_results["completeness"] = {
            "score": completeness_score,
            "missing_fields": [field for field in required_fields if field not in persona]
        }
        
        # Check consistency (theoretical orientation aligns with intervention techniques)
        consistency_score = 0.0
        inconsistencies = []
        
        if "theoretical_orientation" in persona and "intervention_techniques" in persona:
            # Simple check: CBT orientation should include cognitive restructuring
            if "Cognitive-Behavioral" in persona["theoretical_orientation"] and not any("Cognitive" in technique for technique in persona["intervention_techniques"]):
                inconsistencies.append("Cognitive-Behavioral orientation without cognitive techniques")
                consistency_score = 0.7
            else:
                consistency_score = 1.0
        
        validation_results["consistency"] = {
            "score": consistency_score,
            "inconsistencies": inconsistencies
        }
        
        # Check richness (amount of detail)
        richness_factors = {
            "background": len(persona.get("background", "").split()) / 50,  # Expect ~50 words
            "specialties": len(persona.get("specialties", [])) / 4,  # Expect at least 4 specialties
            "education": len(persona.get("education", [])) / 2,  # Expect at least 2 education items
            "approach": len(persona.get("approach", "").split()) / 30  # Expect ~30 words
        }
        
        # Cap each factor at 1.0
        richness_factors = {k: min(v, 1.0) for k, v in richness_factors.items()}
        richness_score = sum(richness_factors.values()) / len(richness_factors)
        
        validation_results["richness"] = {
            "score": richness_score,
            "factor_scores": richness_factors
        }
        
        # Check psychological coherence (theoretical orientation, intervention techniques, communication style)
        coherence_score = 0.0
        coherence_issues = []
        
        if all(field in persona for field in ["theoretical_orientation", "intervention_techniques", "communication_style"]):
            # Check if empirical approaches match communication style
            empirical_approaches = ["Cognitive-Behavioral", "Social Learning", "Behavioral Analysis"]
            if any(approach in persona["theoretical_orientation"] for approach in empirical_approaches):
                if persona["communication_style"].get("technical_language") == "low":
                    coherence_issues.append("Empirical orientation with low technical language")
                    coherence_score = 0.8
                else:
                    coherence_score = 1.0
        
        validation_results["psychological_coherence"] = {
            "score": coherence_score,
            "issues": coherence_issues
        }
        
        # Calculate overall score (weighted)
        weights = {
            "completeness": 0.3,
            "consistency": 0.3,
            "richness": 0.2,
            "psychological_coherence": 0.2
        }
        
        overall_score = sum(validation_results[factor]["score"] * weight for factor, weight in weights.items())
        validation_results["overall_score"] = overall_score
        
        return validation_results
    
    # Validate both personas
    base_results = validate_persona("behavioral_analyst")
    specialized_results = validate_persona("juvenile_justice_specialist")
    
    # Print validation results
    print("Validation Results for Base Persona:")
    print(f"Completeness: {base_results['completeness']['score']:.2f}")
    print(f"Consistency: {base_results['consistency']['score']:.2f}")
    print(f"Richness: {base_results['richness']['score']:.2f}")
    print(f"Psychological Coherence: {base_results['psychological_coherence']['score']:.2f}")
    print(f"Overall Score: {base_results['overall_score']:.2f}")
    
    print("\nValidation Results for Specialized Persona:")
    print(f"Completeness: {specialized_results['completeness']['score']:.2f}")
    print(f"Consistency: {specialized_results['consistency']['score']:.2f}")
    print(f"Richness: {specialized_results['richness']['score']:.2f}")
    print(f"Psychological Coherence: {specialized_results['psychological_coherence']['score']:.2f}")
    print(f"Overall Score: {specialized_results['overall_score']:.2f}")
    
    # Provide improvement suggestions based on validation results
    print("\nImprovement Suggestions:")
    
    if base_results["completeness"]["missing_fields"]:
        print(f"- Add missing fields to Base Persona: {', '.join(base_results['completeness']['missing_fields'])}")
    
    if specialized_results["completeness"]["missing_fields"]:
        print(f"- Add missing fields to Specialized Persona: {', '.join(specialized_results['completeness']['missing_fields'])}")
    
    if base_results["richness"]["score"] < 0.8:
        low_richness = [k for k, v in base_results["richness"]["factor_scores"].items() if v < 0.8]
        print(f"- Enhance detail level in Base Persona for: {', '.join(low_richness)}")
    
    if specialized_results["richness"]["score"] < 0.8:
        low_richness = [k for k, v in specialized_results["richness"]["factor_scores"].items() if v < 0.8]
        print(f"- Enhance detail level in Specialized Persona for: {', '.join(low_richness)}")
    
    return {
        "base_persona": base_results,
        "specialized_persona": specialized_results
    }


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
    """Main function to run the persona customization demonstration."""
    print("=== Smart Steps AI Persona Customization Demonstration ===\n")
    
    # Setup example environment
    dirs = setup_example_environment()
    
    try:
        # Initialize components
        persona_manager = PersonaManager(personas_dir=dirs["personas_dir"])
        memory_manager = LayeredMemoryManager(
            persona_id="behavioral_analyst",
            data_dir=dirs["data_dir"] / "memory"
        )
        
        # Run demonstration
        base_persona = create_base_persona(persona_manager, dirs["personas_dir"])
        enhanced_persona = enhance_persona_with_attributes(persona_manager, dirs["personas_dir"])
        knowledge_context = add_knowledge_to_persona(memory_manager)
        specialized_persona = create_specialized_persona_variant(persona_manager, dirs["personas_dir"], "behavioral_analyst")
        validation_results = validate_persona_cohesion(persona_manager, memory_manager, dirs["personas_dir"])
        
        print("\n=== Persona Customization Demonstration Completed ===")
        print("\nThe demonstration showed how to:")
        print("1. Create a base professional persona")
        print("2. Enhance a persona with additional attributes")
        print("3. Add knowledge to a persona using the layered memory system")
        print("4. Create a specialized variant of an existing persona")
        print("5. Validate the psychological cohesion of personas")
    
    finally:
        # Clean up
        cleanup_example_environment(dirs)


if __name__ == "__main__":
    main()
