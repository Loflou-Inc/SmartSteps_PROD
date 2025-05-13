#!/usr/bin/env python
"""
Analysis Workflow Example

This script demonstrates how to use the analysis capabilities of the Smart Steps AI module
to generate insights, reports, and visualizations from session data.
"""

import os
import time
import json
import uuid
import random
from pathlib import Path
from datetime import datetime, timedelta

from smart_steps_ai.core.config_manager import ConfigManager
from smart_steps_ai.core.persona_manager import PersonaManager
from smart_steps_ai.core.session_manager import SessionManager
from smart_steps_ai.core.layered_memory import LayeredMemoryManager


def setup_example_environment():
    """Set up an example environment for the demonstration."""
    # Create temporary directories
    base_dir = Path("./example_data")
    base_dir.mkdir(exist_ok=True)
    
    config_dir = base_dir / "config"
    data_dir = base_dir / "data"
    personas_dir = base_dir / "personas"
    sessions_dir = base_dir / "sessions"
    reports_dir = base_dir / "reports"
    
    config_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)
    personas_dir.mkdir(exist_ok=True)
    sessions_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)
    
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
        "sessions_dir": sessions_dir,
        "reports_dir": reports_dir
    }


def create_sample_sessions(session_manager, memory_manager, num_sessions=5):
    """Create sample therapy sessions for analysis."""
    print("\n=== Creating Sample Sessions ===\n")
    
    # Client information
    client_name = "Alex Johnson"
    issues = ["anxiety", "work stress", "sleep disturbance", "negative thoughts", "avoidance behaviors"]
    progress_levels = [1, 2, 3, 4, 5]  # 1 = minimal, 5 = significant
    
    # Create multiple sessions over time
    session_ids = []
    
    for i in range(num_sessions):
        # Create session with appropriate date
        date = datetime.now() - timedelta(days=(num_sessions - i) * 7)
        
        session = session_manager.create_session(
            persona_id="therapist",
            client_name=client_name,
            session_type="follow_up" if i > 0 else "initial_consultation",
            metadata={
                "session_number": i + 1,
                "date": date.isoformat()
            }
        )
        
        session_id = session["id"]
        session_ids.append(session_id)
        
        # Generate session content based on session number
        progress = min(i + 1, 5)  # Progress increases with each session
        
        # Create conversation
        conversation = []
        
        # Add greeting
        conversation.append({
            "speaker": "persona",
            "content": f"Hello {client_name}, welcome {'back ' if i > 0 else ''}to your {'follow-up' if i > 0 else 'initial'} session. How have you been since {'our last meeting' if i > 0 else 'we spoke on the phone'}?"
        })
        
        # Client response about current state
        if i == 0:
            # Initial session - client describes problems
            conversation.append({
                "speaker": "client",
                "content": "I've been struggling with anxiety, especially at work. I'm having trouble sleeping and I can't stop worrying about everything."
            })
        else:
            # Follow-up session - client describes progress
            if progress <= 2:
                conversation.append({
                    "speaker": "client",
                    "content": "I'm still having a lot of anxiety, but I've been trying the breathing exercises you suggested. They help sometimes, but I'm still struggling at work."
                })
            elif progress <= 4:
                conversation.append({
                    "speaker": "client",
                    "content": "I'm doing a bit better. The thought record is helping me identify when I'm catastrophizing. My sleep is improving a little too."
                })
            else:
                conversation.append({
                    "speaker": "client",
                    "content": "I'm feeling much better actually. I'm still getting anxious sometimes at work, but I'm using the techniques we discussed and they're really helping."
                })
        
        # Add 4-6 more exchanges
        num_exchanges = random.randint(4, 6)
        
        for j in range(num_exchanges):
            # Therapist question or reflection
            therapist_responses = [
                "Can you tell me more about that?",
                "How does that make you feel?",
                "What thoughts come up when that happens?",
                "Have you noticed any patterns?",
                "How have you been coping with that?",
                "Let's explore that a bit more."
            ]
            
            if progress >= 3:
                therapist_responses.extend([
                    "How did the exercises we discussed last time work for you?",
                    "Have you noticed any changes in your thought patterns?",
                    "What strategies have been most helpful for you?",
                    "Let's build on the progress you've made."
                ])
            
            therapist_response = random.choice(therapist_responses)
            conversation.append({
                "speaker": "persona",
                "content": therapist_response
            })
            
            # Client response
            client_responses = [
                "I'm not sure, I just feel overwhelmed a lot of the time.",
                "When that happens, I start worrying that I'm going to fail at work.",
                "I notice it's worse when I have deadlines coming up.",
                "I've been trying to distract myself, but it doesn't always work.",
                "I just want to feel normal again."
            ]
            
            if progress >= 3:
                client_responses = [
                    "I've been practicing the mindfulness exercises daily.",
                    "I'm getting better at recognizing when my thoughts are spiraling.",
                    "I still get anxious, but I can calm down faster now.",
                    "The sleep routine we discussed has been helping a lot.",
                    "I actually stood up for myself at work this week."
                ]
            
            client_response = random.choice(client_responses)
            conversation.append({
                "speaker": "client",
                "content": client_response
            })
        
        # Add closing exchange
        if i < num_sessions - 1:
            conversation.append({
                "speaker": "persona",
                "content": f"We're making {'some' if progress <= 3 else 'good'} progress. For next week, I'd like you to continue {'with' if progress > 1 else 'working on'} {random.choice(['the thought record', 'mindfulness exercises', 'breathing techniques', 'gradual exposure to stressors', 'implementing better sleep hygiene'])}. How does that sound?"
            })
            
            conversation.append({
                "speaker": "client",
                "content": f"{'I'll try my best' if progress <= 3 else 'Sounds good, I think that will help'}."
            })
        else:
            conversation.append({
                "speaker": "persona",
                "content": "Looking back at where you started and where you are now, you've made significant progress. You have the tools to manage your anxiety now, and you know you can always come back if you need additional support."
            })
            
            conversation.append({
                "speaker": "client",
                "content": "Thank you for all your help. I feel much better equipped to handle my anxiety now."
            })
        
        # Add conversation to session
        for message in conversation:
            session_manager.add_message(
                session_id=session_id,
                speaker=message["speaker"],
                content=message["content"]
            )
            
            # Record client-persona interactions in memory
            if message["speaker"] == "client":
                client_message = message["content"]
                client_idx = conversation.index(message)
                
                # If there's a response from the persona after this client message
                if client_idx + 1 < len(conversation) and conversation[client_idx + 1]["speaker"] == "persona":
                    persona_response = conversation[client_idx + 1]["content"]
                    
                    memory_manager.record_interaction(
                        session_id=session_id,
                        client_message=client_message,
                        persona_response=persona_response
                    )
        
        # Generate insights based on session
        insights = []
        
        if i == 0:
            # Initial assessment insights
            insights = [
                {
                    "content": "Client is experiencing significant anxiety that impacts work performance and sleep.",
                    "domain": "assessment",
                    "confidence": 0.9
                },
                {
                    "content": "Client appears to have limited coping strategies for managing anxiety.",
                    "domain": "coping_skills",
                    "confidence": 0.85
                },
                {
                    "content": "Primary issues appear to be work-related stressors, catastrophic thinking, and sleep disturbance.",
                    "domain": "clinical_focus",
                    "confidence": 0.8
                }
            ]
        elif progress <= 3:
            # Early progress insights
            insights = [
                {
                    "content": "Client is showing initial engagement with therapeutic techniques but still experiencing significant anxiety.",
                    "domain": "progress",
                    "confidence": 0.85
                },
                {
                    "content": f"Client is beginning to use {random.choice(['breathing exercises', 'thought records', 'mindfulness'])} but needs more practice and reinforcement.",
                    "domain": "skill_development",
                    "confidence": 0.8
                },
                {
                    "content": "Some improvement in awareness of anxiety triggers but limited change in emotional response.",
                    "domain": "clinical_progress",
                    "confidence": 0.75
                }
            ]
        else:
            # Significant progress insights
            insights = [
                {
                    "content": "Client is demonstrating significant progress in anxiety management using CBT techniques.",
                    "domain": "progress",
                    "confidence": 0.9
                },
                {
                    "content": "Client now regularly identifies and challenges negative thought patterns with positive results.",
                    "domain": "cognitive_restructuring",
                    "confidence": 0.85
                },
                {
                    "content": "Sleep quality has improved as anxiety management skills have developed.",
                    "domain": "symptom_reduction",
                    "confidence": 0.8
                },
                {
                    "content": "Client is successfully transferring therapy skills to workplace situations.",
                    "domain": "skill_application",
                    "confidence": 0.85
                }
            ]
        
        # Add insights to memory
        for insight in insights:
            memory_manager.generate_insight(
                content=insight["content"],
                domain=insight["domain"],
                sources={
                    "experience": [session_id]
                },
                confidence=insight["confidence"]
            )
        
        # Add session summary
        session_manager.end_session(
            session_id=session_id,
            summary=f"{'Initial assessment' if i == 0 else 'Session ' + str(i+1)} with {client_name}. {'Assessment of anxiety and work-related stress. Introduced CBT framework.' if i == 0 else 'Continued CBT work for anxiety. ' + ('Some' if progress <= 3 else 'Significant') + ' progress noted in ' + random.choice(['thought restructuring', 'anxiety management', 'sleep quality', 'workplace functioning']) + '.'}"
        )
        
        print(f"Created session {i+1} with {len(conversation)} messages and {len(insights)} insights")
    
    return session_ids


def perform_basic_analysis(session_manager, session_ids):
    """Perform basic analysis on the sessions."""
    print("\n=== Basic Session Analysis ===\n")
    
    print("Session Summaries:")
    print("-----------------")
    
    for session_id in session_ids:
        session = session_manager.get_session(session_id)
        print(f"Session #{session['metadata'].get('session_number', '?')} - {session['created_at']}")
        print(f"Summary: {session['summary']}")
        print()
    
    # Message count analysis
    total_messages = 0
    client_messages = 0
    persona_messages = 0
    
    for session_id in session_ids:
        messages = session_manager.get_messages(session_id)
        total_messages += len(messages)
        
        for message in messages:
            if message["speaker"] == "client":
                client_messages += 1
            elif message["speaker"] == "persona":
                persona_messages += 1
    
    print("Message Statistics:")
    print("------------------")
    print(f"Total messages: {total_messages}")
    print(f"Client messages: {client_messages}")
    print(f"Persona messages: {persona_messages}")
    print(f"Average messages per session: {total_messages / len(session_ids):.1f}")
    
    # Basic content analysis
    all_content = ""
    
    for session_id in session_ids:
        messages = session_manager.get_messages(session_id)
        for message in messages:
            all_content += message["content"] + " "
    
    # Simple word frequency analysis
    words = all_content.lower().split()
    word_counts = {}
    
    for word in words:
        word = word.strip(".,?!\"'()[]{}:;")
        if len(word) > 3:  # Skip short words
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Get top 10 words
    top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("\nTop 10 Words:")
    print("------------")
    for word, count in top_words:
        print(f"{word}: {count}")


def perform_trend_analysis(session_manager, memory_manager, session_ids):
    """Perform trend analysis across multiple sessions."""
    print("\n=== Trend Analysis ===\n")
    
    # Define topics for analysis
    topics = ["anxiety", "coping skills", "sleep", "work performance", "negative thoughts"]
    
    for topic in topics:
        print(f"\nTrend Analysis for '{topic}':")
        print("-" * (24 + len(topic)))
        
        session_data = []
        
        for session_id in session_ids:
            session = session_manager.get_session(session_id)
            session_number = session["metadata"].get("session_number", "?")
            
            # Get all messages for this session
            messages = session_manager.get_messages(session_id)
            
            # Extract client messages
            client_messages = [msg["content"] for msg in messages if msg["speaker"] == "client"]
            client_text = " ".join(client_messages)
            
            # Simple keyword analysis (in a real system, this would be more sophisticated)
            # Count mentions of topic
            mention_count = client_text.lower().count(topic.lower())
            
            # Get sentiment (-1 to 1) - simplified simulation
            # In early sessions, sentiment for problems is more negative
            # In later sessions, sentiment improves
            base_sentiment = -0.5 + (float(session_number) - 1) * 0.2
            
            # Add some randomness
            sentiment = min(1.0, max(-1.0, base_sentiment + random.uniform(-0.1, 0.1)))
            
            session_data.append({
                "session_number": session_number,
                "mentions": mention_count,
                "sentiment": sentiment
            })
        
        # Print trend analysis
        for data in session_data:
            sentiment_display = "😞" if data["sentiment"] < -0.3 else "😐" if data["sentiment"] < 0.3 else "🙂"
            print(f"Session {data['session_number']}: Mentions: {data['mentions']}, Sentiment: {data['sentiment']:.2f} {sentiment_display}")
        
        # Summarize trend
        if session_data[0]["sentiment"] < session_data[-1]["sentiment"]:
            sentiment_change = f"improved from {session_data[0]['sentiment']:.2f} to {session_data[-1]['sentiment']:.2f}"
        else:
            sentiment_change = f"declined from {session_data[0]['sentiment']:.2f} to {session_data[-1]['sentiment']:.2f}"
        
        mention_change = session_data[0]["mentions"] - session_data[-1]["mentions"]
        if mention_change > 0:
            mention_trend = f"decreased by {mention_change}"
        elif mention_change < 0:
            mention_trend = f"increased by {abs(mention_change)}"
        else:
            mention_trend = "remained stable"
        
        print(f"\nSummary: Mentions of '{topic}' {mention_trend} over {len(session_ids)} sessions.")
        print(f"Client sentiment regarding '{topic}' has {sentiment_change}.")


def generate_comprehensive_report(session_manager, memory_manager, session_ids, reports_dir):
    """Generate a comprehensive therapeutic report."""
    print("\n=== Generating Comprehensive Report ===\n")
    
    # Get client info from first session
    first_session = session_manager.get_session(session_ids[0])
    client_name = first_session["client_name"]
    
    # Get therapist info
    therapist_name = "Dr. Sarah Thompson"
    
    # Create report structure
    report = {
        "title": f"Therapy Progress Report for {client_name}",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "therapist": therapist_name,
        "client": client_name,
        "session_count": len(session_ids),
        "duration": f"{len(session_ids)} weeks",
        "sections": []
    }
    
    # Add summary section
    report["sections"].append({
        "heading": "Executive Summary",
        "content": (
            f"{client_name} has completed {len(session_ids)} sessions of Cognitive Behavioral Therapy (CBT) "
            f"focused on anxiety management, particularly related to workplace stress. "
            f"The client has demonstrated {'significant' if len(session_ids) >= 5 else 'some'} progress in developing "
            f"coping strategies and reducing anxiety symptoms. Initial presenting concerns included "
            f"work-related anxiety, sleep disturbance, and limited coping mechanisms. "
            f"Through consistent application of CBT techniques, the client has {'shown notable improvement in ' if len(session_ids) >= 4 else 'begun to develop skills in '}"
            f"identifying negative thought patterns, implementing stress reduction techniques, and improving sleep hygiene."
        )
    })
    
    # Add presenting concerns section
    report["sections"].append({
        "heading": "Presenting Concerns",
        "content": (
            "The client initially presented with:\n"
            "- Significant anxiety, particularly related to workplace performance\n"
            "- Sleep disturbance exacerbated by racing thoughts\n"
            "- Tendency toward catastrophic thinking\n"
            "- Limited coping strategies for managing stress and anxiety\n"
            "- Avoidance behaviors that reinforced anxiety patterns"
        )
    })
    
    # Add intervention section
    report["sections"].append({
        "heading": "Therapeutic Interventions",
        "content": (
            "The following CBT interventions were implemented during the course of therapy:\n"
            "- Cognitive restructuring to identify and challenge negative thought patterns\n"
            "- Mindfulness and relaxation techniques for anxiety management\n"
            "- Sleep hygiene education and implementation\n"
            "- Gradual exposure to anxiety-provoking situations\n"
            "- Development of personalized coping strategies\n"
            "- Thought records to track and analyze anxious thinking"
        )
    })
    
    # Add progress section
    first_session = session_manager.get_session(session_ids[0])
    last_session = session_manager.get_session(session_ids[-1])
    
    progress_content = (
        f"Over the course of {len(session_ids)} sessions, {client_name} has demonstrated the following progress:\n\n"
    )
    
    # Progress in key areas
    progress_areas = [
        {
            "area": "Anxiety Management",
            "initial": "Frequent intense anxiety with limited management skills",
            "current": f"{'Significantly reduced anxiety with regular application of coping strategies' if len(session_ids) >= 4 else 'Moderate improvement in anxiety with beginning application of coping strategies'}",
            "improvement": 4 if len(session_ids) >= 4 else 2
        },
        {
            "area": "Sleep Quality",
            "initial": "Disrupted sleep due to racing thoughts and worry",
            "current": f"{'Improved sleep consistency and quality through applied sleep hygiene' if len(session_ids) >= 3 else 'Some improvement in sleep with inconsistent application of techniques'}",
            "improvement": 3 if len(session_ids) >= 3 else 2
        },
        {
            "area": "Cognitive Patterns",
            "initial": "Frequent catastrophizing and negative predictions",
            "current": f"{'Regularly identifies and challenges negative thought patterns' if len(session_ids) >= 4 else 'Increased awareness of negative thought patterns'}",
            "improvement": 4 if len(session_ids) >= 4 else 2
        },
        {
            "area": "Workplace Functioning",
            "initial": "Significant anxiety impacting work performance",
            "current": f"{'Successfully implementing coping strategies in workplace situations' if len(session_ids) >= 4 else 'Beginning to apply anxiety management techniques at work'}",
            "improvement": 3 if len(session_ids) >= 4 else 2
        }
    ]
    
    # Add progress areas to content
    for area in progress_areas:
        progress_content += f"**{area['area']}**\n"
        progress_content += f"- Initial Status: {area['initial']}\n"
        progress_content += f"- Current Status: {area['current']}\n"
        progress_content += f"- Improvement: {'●' * area['improvement']}{'○' * (5 - area['improvement'])}\n\n"
    
    report["sections"].append({
        "heading": "Progress Assessment",
        "content": progress_content
    })
    
    # Add recommendations section
    if len(session_ids) >= 5:
        recommendations = (
            "Based on the significant progress demonstrated, the following recommendations are made:\n\n"
            "1. Transition to biweekly maintenance sessions to support continued progress\n"
            "2. Continue daily practice of mindfulness and cognitive restructuring techniques\n"
            "3. Implement workplace stress management plan developed in therapy\n"
            "4. Maintain sleep hygiene practices that have proven effective\n"
            "5. Schedule a follow-up assessment in 3 months to evaluate maintenance of gains"
        )
    else:
        recommendations = (
            "Based on the progress demonstrated thus far, the following recommendations are made:\n\n"
            "1. Continue weekly therapy sessions focusing on anxiety management techniques\n"
            "2. Increase frequency of thought record completion to daily practice\n"
            "3. Implement structured sleep routine as discussed in session\n"
            "4. Begin gradual exposure to identified workplace stressors\n"
            "5. Review and expand coping strategy toolkit in upcoming sessions"
        )
    
    report["sections"].append({
        "heading": "Recommendations",
        "content": recommendations
    })
    
    # Add insights from memory
    insights_content = "Key insights developed throughout the therapeutic process:\n\n"
    
    # Get insights from memory (simplified simulation)
    key_insights = [
        "Client's anxiety manifests primarily through physical symptoms and catastrophic thinking patterns.",
        "Work-related stressors are significant triggers, particularly interactions with authority figures.",
        "Sleep disruption creates a negative feedback loop that intensifies daytime anxiety.",
        "Client responds well to structured cognitive techniques with clear implementation steps.",
        f"{'Significant improvement occurs when techniques are practiced consistently.' if len(session_ids) >= 4 else 'Initial resistance to practice is giving way to recognition of technique effectiveness.'}"
    ]
    
    for i, insight in enumerate(key_insights, 1):
        insights_content += f"{i}. {insight}\n"
    
    report["sections"].append({
        "heading": "Clinical Insights",
        "content": insights_content
    })
    
    # Generate report file
    report_path = Path(reports_dir) / f"{client_name.replace(' ', '_')}_Progress_Report.md"
    
    with open(report_path, 'w') as f:
        f.write(f"# {report['title']}\n\n")
        f.write(f"Date: {report['date']}\n")
        f.write(f"Therapist: {report['therapist']}\n")
        f.write(f"Client: {report['client']}\n")
        f.write(f"Sessions Completed: {report['session_count']}\n")
        f.write(f"Duration: {report['duration']}\n\n")
        
        for section in report["sections"]:
            f.write(f"## {section['heading']}\n\n")
            f.write(f"{section['content']}\n\n")
    
    print(f"Comprehensive report generated at: {report_path}")
    
    return report_path


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
    """Main function to run the analysis workflow demonstration."""
    print("=== Smart Steps AI Analysis Workflow Demonstration ===\n")
    
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
        
        # Create sample sessions
        session_ids = create_sample_sessions(session_manager, memory_manager, num_sessions=5)
        
        # Run analyses
        perform_basic_analysis(session_manager, session_ids)
        perform_trend_analysis(session_manager, memory_manager, session_ids)
        report_path = generate_comprehensive_report(session_manager, memory_manager, session_ids, dirs["reports_dir"])
        
        print("\n=== Analysis Workflow Demonstration Completed ===")
    
    finally:
        # Clean up
        cleanup_example_environment(dirs)


if __name__ == "__main__":
    main()
