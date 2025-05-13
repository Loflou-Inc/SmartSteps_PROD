"""
Insights and analysis utilities for the Smart Steps AI module.

Provides functions for generating insights, extracting themes,
analyzing sentiment, and creating progress reports from session data.
"""

from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import re

def generate_session_insights(session, detailed=False) -> Dict[str, List[str]]:
    """
    Generate insights from a therapy session.
    
    Args:
        session: The session object to analyze
        detailed: Whether to generate detailed insights
        
    Returns:
        Dictionary with categories and insights
    """
    # This would normally use AI to analyze the session
    # For now, implement a simple pattern-based approach for demonstration
    
    insights = {
        "Key Observations": [],
        "Potential Areas of Focus": [],
        "Communication Patterns": []
    }
    
    if not hasattr(session, 'messages') or not session.messages:
        return insights
    
    # Extract all message content
    all_content = " ".join([msg.content for msg in session.messages])
    
    # Look for emotion words
    emotion_words = ["happy", "sad", "angry", "frustrated", "anxious", 
                    "worried", "stressed", "calm", "relaxed", "excited"]
    
    for emotion in emotion_words:
        if re.search(r'\b' + emotion + r'\b', all_content, re.IGNORECASE):
            insights["Key Observations"].append(
                f"Client expressed {emotion} feelings during the session."
            )
    
    # Look for potential areas of focus
    focus_areas = ["work", "family", "relationship", "health", "sleep", 
                   "stress", "anxiety", "depression", "trauma", "goal"]
    
    for area in focus_areas:
        if re.search(r'\b' + area + r'\b', all_content, re.IGNORECASE):
            insights["Potential Areas of Focus"].append(
                f"{area.capitalize()} appears to be a significant area in the client's life."
            )
    
    # Analyze communication patterns
    question_count = len(re.findall(r'\?', all_content))
    if question_count > 5:
        insights["Communication Patterns"].append(
            f"Client asked many questions ({question_count}), suggesting an information-seeking approach."
        )
    
    "I"_count = len(re.findall(r'\bI\b', all_content))
    if "I"_count > 10:
        insights["Communication Patterns"].append(
            f"Client used 'I' frequently ({question_count} times), suggesting self-focused perspective."
        )
    
    # If detailed insights requested, add more categories
    if detailed:
        insights["Potential Intervention Strategies"] = [
            "Consider exploring underlying emotions when discussing challenges",
            "Techniques for managing anxiety might be beneficial",
            "Encourage reframing of negative thought patterns when identified"
        ]
        
        insights["Progress Indicators"] = [
            "Client showed awareness of emotional patterns",
            "Willingness to engage in reflective discussion",
            "Identified specific situations that trigger stress responses"
        ]
    
    return insights

def generate_session_summary(session) -> str:
    """
    Generate a summary of a therapy session.
    
    Args:
        session: The session object to summarize
        
    Returns:
        A string summary of the session
    """
    # This would normally use AI to summarize the session
    # For now, create a simple summary for demonstration
    
    if not hasattr(session, 'messages') or not session.messages:
        return "No messages were exchanged in this session."
    
    client_messages = [msg for msg in session.messages if msg.is_user]
    professional_messages = [msg for msg in session.messages if not msg.is_user]
    
    summary = f"Session with {session.client_name} included {len(session.messages)} messages "
    summary += f"({len(client_messages)} from client, {len(professional_messages)} from professional). "
    
    # Extract the first and last messages for context
    if client_messages:
        first_msg = client_messages[0].content[:50] + "..." if len(client_messages[0].content) > 50 else client_messages[0].content
        summary += f"The session began with the client stating: \"{first_msg}\". "
        
    if professional_messages and len(professional_messages) > 1:
        last_msg = professional_messages[-1].content[:50] + "..." if len(professional_messages[-1].content) > 50 else professional_messages[-1].content
        summary += f"The professional concluded with: \"{last_msg}\". "
    
    # Add timing information
    if len(session.messages) >= 2:
        first_time = session.messages[0].timestamp
        last_time = session.messages[-1].timestamp
        duration = last_time - first_time
        minutes = duration.seconds // 60
        
        summary += f"The session lasted approximately {minutes} minutes. "
    
    # Add simple analysis
    all_content = " ".join([msg.content for msg in session.messages])
    
    if "goal" in all_content.lower() or "plan" in all_content.lower():
        summary += "Goals and plans were discussed during the session. "
        
    if "feel" in all_content.lower() or "emotion" in all_content.lower():
        summary += "Emotional content was explored. "
    
    summary += "Overall, the session was focused and productive."
    
    return summary

def extract_key_themes(session, count=5) -> List[Tuple[str, float]]:
    """
    Extract key themes from a therapy session.
    
    Args:
        session: The session object to analyze
        count: Maximum number of themes to extract
        
    Returns:
        List of (theme, relevance_score) tuples
    """
    # This would normally use NLP techniques like topic modeling
    # For now, implement a simple keyword frequency approach
    
    if not hasattr(session, 'messages') or not session.messages:
        return []
    
    # Extract all message content
    all_content = " ".join([msg.content for msg in session.messages if msg.is_user])
    
    # Define common stop words to exclude
    stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
                      'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 
                      'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 
                      'itself', 'they', 'them', 'their', 'theirs', 'themselves', 
                      'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 
                      'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 
                      'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 
                      'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 
                      'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 
                      'into', 'through', 'during', 'before', 'after', 'above', 'below', 
                      'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 
                      'under', 'again', 'further', 'then', 'once', 'here', 'there', 
                      'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 
                      'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 
                      'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 
                      's', 't', 'can', 'will', 'just', 'don', 'should', 'now'])
    
    # Tokenize and clean text
    words = re.findall(r'\b\w+\b', all_content.lower())
    words = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Count word frequencies
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # Get most frequent words
    frequent_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:count*2]
    
    # Group similar words (very simple approach)
    themes = []
    used_words = set()
    
    for word, count in frequent_words:
        if word in used_words:
            continue
            
        related = [w for w, c in frequent_words if w.startswith(word[:3]) and w not in used_words]
        if related:
            # Create a theme from the most frequent word and related words
            theme_score = sum(word_counts.get(w, 0) for w in related) / len(all_content.split())
            if len(related) > 1:
                theme_name = f"{word.capitalize()} (related: {', '.join(r for r in related[:2] if r != word)})"
            else:
                theme_name = word.capitalize()
                
            themes.append((theme_name, theme_score))
            used_words.update(related)
        
        if len(themes) >= count:
            break
    
    return themes

def analyze_sentiment_trends(session) -> Dict[str, Any]:
    """
    Analyze sentiment trends throughout a session.
    
    Args:
        session: The session object to analyze
        
    Returns:
        Dictionary with sentiment analysis data
    """
    # This would normally use a sentiment analysis model
    # For now, implement a simple keyword-based approach
    
    if not hasattr(session, 'messages') or len(session.messages) < 3:
        return {}
    
    # Define simple sentiment dictionaries
    positive_words = set(['good', 'great', 'excellent', 'happy', 'positive', 'better', 
                         'improved', 'helpful', 'hope', 'confident', 'glad', 'pleased', 
                         'thank', 'appreciate', 'excited', 'wonderful', 'enjoy', 'like'])
    
    negative_words = set(['bad', 'terrible', 'awful', 'sad', 'negative', 'worse', 
                         'difficult', 'hard', 'problem', 'issue', 'worried', 'anxious', 
                         'stressed', 'depressed', 'unhappy', 'confused', 'frustrated', 
                         'angry', 'upset', 'hate', 'dislike', 'concern', 'fear'])
    
    # Get client messages only
    client_messages = [msg for msg in session.messages if msg.is_user]
    
    if not client_messages:
        return {}
    
    # Calculate sentiment scores for each message
    sentiment_scores = []
    
    for msg in client_messages:
        words = re.findall(r'\b\w+\b', msg.content.lower())
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        # Score from -1 (negative) to 1 (positive)
        total_words = len(words) if len(words) > 0 else 1
        score = (pos_count - neg_count) / (total_words * 0.5)  # Normalize to -1 to 1
        score = max(min(score, 1.0), -1.0)  # Clamp to -1 to 1
        
        sentiment_scores.append(score)
    
    # Create progression data
    progression = []
    for i, score in enumerate(sentiment_scores):
        label = "Positive" if score > 0.3 else "Negative" if score < -0.3 else "Neutral"
        progression.append({
            "position": i + 1,
            "score": score,
            "label": label
        })
    
    # Calculate overall sentiment
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    # Determine trend
    if len(sentiment_scores) >= 3:
        first_third = sum(sentiment_scores[:len(sentiment_scores)//3]) / (len(sentiment_scores)//3)
        last_third = sum(sentiment_scores[-len(sentiment_scores)//3:]) / (len(sentiment_scores)//3)
        
        if last_third > first_third + 0.3:
            trend = "Significant improvement in sentiment throughout the session"
        elif last_third > first_third + 0.1:
            trend = "Slight improvement in sentiment throughout the session"
        elif first_third > last_third + 0.3:
            trend = "Significant decline in sentiment throughout the session"
        elif first_third > last_third + 0.1:
            trend = "Slight decline in sentiment throughout the session"
        else:
            trend = "Stable sentiment throughout the session"
    else:
        trend = "Not enough data to determine sentiment trend"
    
    return {
        "overall": {
            "average": avg_sentiment,
            "trend": trend
        },
        "progression": progression
    }

def generate_progress_report(sessions) -> Dict[str, Any]:
    """
    Generate a progress report across multiple sessions.
    
    Args:
        sessions: List of session objects to analyze
        
    Returns:
        Dictionary with progress report data
    """
    # This would normally use AI to analyze progress across sessions
    # For now, implement a simple approach for demonstration
    
    if not sessions:
        return {}
    
    # Sort sessions by date
    sessions = sorted(sessions, key=lambda s: s.created_at)
    
    # Extract basic statistics
    session_count = len(sessions)
    first_session_date = sessions[0].created_at
    last_session_date = sessions[-1].created_at
    
    # Calculate time span
    time_span = (last_session_date - first_session_date).days
    time_span_str = f"{time_span} days" if time_span > 0 else "same day"
    
    # Count messages across all sessions
    total_messages = 0
    client_messages = 0
    
    for session in sessions:
        if hasattr(session, 'messages') and session.messages:
            total_messages += len(session.messages)
            client_messages += sum(1 for msg in session.messages if msg.is_user)
    
    # Generate summary
    summary = f"Analysis of {session_count} sessions over {time_span_str} "
    summary += f"({first_session_date.strftime('%Y-%m-%d')} to {last_session_date.strftime('%Y-%m-%d')}). "
    summary += f"A total of {total_messages} messages were exchanged, with {client_messages} from the client. "
    
    if session_count >= 3:
        summary += "Regular engagement indicates commitment to the therapeutic process. "
    
    summary += "The client has shown progress in key areas and continues to work through identified challenges."
    
    # Generate areas of progress (these would normally be AI-identified)
    areas_of_progress = [
        "Improved ability to articulate thoughts and feelings",
        "Increased awareness of emotional patterns",
        "Development of coping strategies for identified stressors",
        "Greater consistency in applying therapeutic techniques"
    ]
    
    # Generate challenges (these would normally be AI-identified)
    challenges = [
        "Managing stress during high-pressure situations",
        "Establishing consistent self-care routines",
        "Addressing persistent negative thought patterns",
        "Navigating difficult interpersonal dynamics"
    ]
    
    # Generate recommendations (these would normally be AI-identified)
    recommendations = [
        "Continue practicing mindfulness techniques daily",
        "Explore deeper emotional responses to identified triggers",
        "Consider journaling between sessions to track patterns",
        "Develop a structured plan for implementing coping strategies",
        "Focus on small, achievable goals to build momentum"
    ]
    
    return {
        "summary": summary,
        "areas_of_progress": areas_of_progress,
        "challenges": challenges,
        "recommendations": recommendations
    }
