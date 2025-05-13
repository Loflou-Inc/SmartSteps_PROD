"""
Export utilities for the Smart Steps AI module.

Provides functions for exporting sessions, conversations, insights, and
other data to different formats (text, markdown, HTML, etc.).
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional

def export_to_text(session):
    """Export a session to a formatted text file."""
    content = []
    content.append(f"=== Session {session.id} ===")
    content.append(f"Client: {session.client_name}")
    content.append(f"Created: {session.created_at}")
    content.append(f"Status: {'Active' if not session.ended_at else 'Ended'}")
    
    if session.tags:
        content.append(f"Tags: {', '.join(session.tags)}")
    
    if session.notes:
        content.append("\nNotes:")
        content.append(session.notes)
    
    if hasattr(session, 'messages') and session.messages:
        content.append("\nConversation:")
        for msg in session.messages:
            sender = "Client" if msg.is_user else "Professional"
            content.append(f"\n[{msg.timestamp}] {sender}:")
            content.append(msg.content)
    
    return "\n".join(content)

def export_to_markdown(session):
    """Export a session to a markdown file."""
    content = []
    content.append(f"# Session {session.id}")
    content.append(f"**Client:** {session.client_name}")
    content.append(f"**Created:** {session.created_at}")
    content.append(f"**Status:** {'Active' if not session.ended_at else 'Ended'}")
    
    if session.tags:
        content.append(f"**Tags:** {', '.join(session.tags)}")
    
    if session.notes:
        content.append("\n## Notes")
        content.append(session.notes)
    
    if hasattr(session, 'messages') and session.messages:
        content.append("\n## Conversation")
        for msg in session.messages:
            sender = "Client" if msg.is_user else "Professional"
            content.append(f"\n### {sender} ({msg.timestamp})")
            content.append(msg.content)
    
    return "\n\n".join(content)

def export_to_html(session):
    """Export a session to an HTML file."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append(f"  <title>Session {session.id}</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }")
    html.append("    h1, h2, h3 { color: #2c3e50; }")
    html.append("    .meta { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }")
    html.append("    .client { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }")
    html.append("    .professional { background-color: #f0f7ee; padding: 15px; border-radius: 5px; margin: 10px 0; }")
    html.append("    .timestamp { color: #7f8c8d; font-size: 0.8em; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    
    html.append(f"  <h1>Session {session.id}</h1>")
    html.append("  <div class='meta'>")
    html.append(f"    <p><strong>Client:</strong> {session.client_name}</p>")
    html.append(f"    <p><strong>Created:</strong> {session.created_at}</p>")
    html.append(f"    <p><strong>Status:</strong> {'Active' if not session.ended_at else 'Ended'}</p>")
    
    if session.tags:
        html.append(f"    <p><strong>Tags:</strong> {', '.join(session.tags)}</p>")
    
    html.append("  </div>")
    
    if session.notes:
        html.append("  <h2>Notes</h2>")
        html.append(f"  <p>{session.notes.replace('\n', '<br>')}</p>")
    
    if hasattr(session, 'messages') and session.messages:
        html.append("  <h2>Conversation</h2>")
        for msg in session.messages:
            sender = "Client" if msg.is_user else "Professional"
            css_class = "client" if msg.is_user else "professional"
            html.append(f"  <div class='{css_class}'>")
            html.append(f"    <div class='timestamp'>{sender} - {msg.timestamp}</div>")
            html.append(f"    <p>{msg.content.replace('\n', '<br>')}</p>")
            html.append("  </div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)

def export_to_csv(session):
    """Export a session to a CSV file format."""
    content = []
    # Header
    content.append("timestamp,sender,content")
    
    if hasattr(session, 'messages') and session.messages:
        for msg in session.messages:
            sender = "Client" if msg.is_user else "Professional"
            # Escape quotes and newlines for CSV
            safe_content = msg.content.replace('"', '""').replace('\n', ' ')
            content.append(f"{msg.timestamp},\"{sender}\",\"{safe_content}\"")
    
    return "\n".join(content)

def export_conversation_to_text(session, messages, include_metadata=False):
    """Export conversation to a text file."""
    content = []
    
    # Include metadata if requested
    if include_metadata:
        content.append(f"=== Conversation with Session {session.id} ===")
        content.append(f"Client: {session.client_name}")
        content.append(f"Created: {session.created_at}")
        content.append(f"Status: {'Active' if not session.ended_at else 'Ended'}")
        content.append("")
    else:
        content.append(f"=== Conversation ===")
    
    # Add messages
    for msg in messages:
        sender = "Client" if msg.is_user else "Professional"
        content.append(f"[{msg.timestamp}] {sender}:")
        content.append(msg.content)
        content.append("")
    
    return "\n".join(content)

def export_conversation_to_markdown(session, messages, include_metadata=False):
    """Export conversation to a markdown file."""
    content = []
    
    # Include metadata if requested
    if include_metadata:
        content.append(f"# Conversation - Session {session.id}")
        content.append(f"**Client:** {session.client_name}")
        content.append(f"**Created:** {session.created_at}")
        content.append(f"**Status:** {'Active' if not session.ended_at else 'Ended'}")
        content.append("")
    else:
        content.append("# Conversation")
    
    # Add messages
    for msg in messages:
        sender = "Client" if msg.is_user else "Professional"
        content.append(f"## {sender} ({msg.timestamp})")
        content.append(msg.content)
        content.append("")
    
    return "\n".join(content)

def export_conversation_to_json(session, messages, include_metadata=False):
    """Export conversation to a JSON file."""
    data = {
        "messages": [
            {
                "timestamp": msg.timestamp.isoformat(),
                "sender": "client" if msg.is_user else "professional",
                "content": msg.content
            }
            for msg in messages
        ]
    }
    
    # Include metadata if requested
    if include_metadata:
        data["session_id"] = str(session.id)
        data["client"] = session.client_name
        data["created_at"] = session.created_at.isoformat()
        data["status"] = "active" if not session.ended_at else "ended"
    
    return json.dumps(data, indent=2)

def export_conversation_to_html(session, messages, include_metadata=False):
    """Export conversation to an HTML file."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("  <title>Conversation</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }")
    html.append("    h1, h2 { color: #2c3e50; }")
    html.append("    .meta { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }")
    html.append("    .client { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }")
    html.append("    .professional { background-color: #f0f7ee; padding: 15px; border-radius: 5px; margin: 10px 0; }")
    html.append("    .timestamp { color: #7f8c8d; font-size: 0.8em; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    
    # Include metadata if requested
    if include_metadata:
        html.append(f"  <h1>Conversation - Session {session.id}</h1>")
        html.append("  <div class='meta'>")
        html.append(f"    <p><strong>Client:</strong> {session.client_name}</p>")
        html.append(f"    <p><strong>Created:</strong> {session.created_at}</p>")
        html.append(f"    <p><strong>Status:</strong> {'Active' if not session.ended_at else 'Ended'}</p>")
        html.append("  </div>")
    else:
        html.append("  <h1>Conversation</h1>")
    
    # Add messages
    for msg in messages:
        sender = "Client" if msg.is_user else "Professional"
        css_class = "client" if msg.is_user else "professional"
        html.append(f"  <div class='{css_class}'>")
        html.append(f"    <div class='timestamp'>{sender} - {msg.timestamp}</div>")
        html.append(f"    <p>{msg.content.replace('\n', '<br>')}</p>")
        html.append("  </div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)

def export_insights_to_html(session, insights):
    """Export insights to an HTML file."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append(f"  <title>Insights - Session {session.id}</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }")
    html.append("    h1, h2, h3 { color: #2c3e50; }")
    html.append("    .meta { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }")
    html.append("    .insights-section { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 15px 0; }")
    html.append("    ul { padding-left: 20px; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    
    html.append(f"  <h1>Session Insights</h1>")
    html.append("  <div class='meta'>")
    html.append(f"    <p><strong>Session ID:</strong> {session.id}</p>")
    html.append(f"    <p><strong>Client:</strong> {session.client_name}</p>")
    html.append(f"    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>")
    html.append("  </div>")
    
    for category, items in insights.items():
        html.append(f"  <div class='insights-section'>")
        html.append(f"    <h2>{category}</h2>")
        html.append("    <ul>")
        for item in items:
            html.append(f"      <li>{item}</li>")
        html.append("    </ul>")
        html.append("  </div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)

def export_progress_to_html(client_name, period, progress_report):
    """Export progress report to an HTML file."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append(f"  <title>Progress Report - {client_name}</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }")
    html.append("    h1, h2, h3 { color: #2c3e50; }")
    html.append("    .meta { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }")
    html.append("    .summary { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; }")
    html.append("    .section { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 15px 0; }")
    html.append("    ul { padding-left: 20px; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    
    html.append(f"  <h1>Progress Report</h1>")
    html.append("  <div class='meta'>")
    html.append(f"    <p><strong>Client:</strong> {client_name}</p>")
    html.append(f"    <p><strong>Period:</strong> {period.capitalize()}</p>")
    html.append(f"    <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>")
    html.append("  </div>")
    
    html.append("  <div class='summary'>")
    html.append("    <h2>Summary</h2>")
    html.append(f"    <p>{progress_report['summary']}</p>")
    html.append("  </div>")
    
    html.append("  <div class='section'>")
    html.append("    <h2>Key Areas of Progress</h2>")
    html.append("    <ul>")
    for area in progress_report['areas_of_progress']:
        html.append(f"      <li>{area}</li>")
    html.append("    </ul>")
    html.append("  </div>")
    
    html.append("  <div class='section'>")
    html.append("    <h2>Challenges</h2>")
    html.append("    <ul>")
    for challenge in progress_report['challenges']:
        html.append(f"      <li>{challenge}</li>")
    html.append("    </ul>")
    html.append("  </div>")
    
    html.append("  <div class='section'>")
    html.append("    <h2>Recommendations</h2>")
    html.append("    <ul>")
    for rec in progress_report['recommendations']:
        html.append(f"      <li>{rec}</li>")
    html.append("    </ul>")
    html.append("  </div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)

def export_report_to_text(report_data):
    """Export comprehensive report to a text file."""
    content = []
    
    content.append(f"=== Therapy Report ===")
    content.append(f"Client: {report_data['client_name']}")
    content.append(f"Period: {report_data['period'].capitalize()}")
    content.append(f"Date: {report_data['date']}")
    content.append(f"Sessions Analyzed: {report_data['session_count']}")
    content.append("")
    
    content.append("EXECUTIVE SUMMARY")
    content.append(report_data['executive_summary'])
    content.append("")
    
    if 'progress' in report_data:
        content.append("PROGRESS")
        content.append(report_data['progress']['summary'])
        content.append("")
        
        content.append("Key Areas of Progress:")
        for area in report_data['progress']['areas_of_progress']:
            content.append(f"- {area}")
        content.append("")
    
    if 'challenges' in report_data:
        content.append("CHALLENGES")
        for challenge in report_data['challenges']:
            content.append(f"- {challenge}")
        content.append("")
    
    if 'themes' in report_data:
        content.append("KEY THEMES")
        for theme in report_data['themes']:
            content.append(f"- {theme}")
        content.append("")
    
    if 'recommendations' in report_data:
        content.append("RECOMMENDATIONS")
        for rec in report_data['recommendations']:
            content.append(f"- {rec}")
        content.append("")
    
    if 'next_steps' in report_data:
        content.append("NEXT STEPS")
        for step in report_data['next_steps']:
            content.append(f"- {step}")
    
    return "\n".join(content)

def export_report_to_markdown(report_data):
    """Export comprehensive report to a markdown file."""
    content = []
    
    content.append(f"# Therapy Report - {report_data['client_name']}")
    content.append("")
    content.append(f"**Period:** {report_data['period'].capitalize()}")
    content.append(f"**Date:** {report_data['date']}")
    content.append(f"**Sessions Analyzed:** {report_data['session_count']}")
    content.append("")
    
    content.append("## Executive Summary")
    content.append(report_data['executive_summary'])
    content.append("")
    
    if 'progress' in report_data:
        content.append("## Progress")
        content.append(report_data['progress']['summary'])
        content.append("")
        
        content.append("### Key Areas of Progress")
        for area in report_data['progress']['areas_of_progress']:
            content.append(f"* {area}")
        content.append("")
    
    if 'challenges' in report_data:
        content.append("## Challenges")
        for challenge in report_data['challenges']:
            content.append(f"* {challenge}")
        content.append("")
    
    if 'themes' in report_data:
        content.append("## Key Themes")
        for theme in report_data['themes']:
            content.append(f"* {theme}")
        content.append("")
    
    if 'recommendations' in report_data:
        content.append("## Recommendations")
        for rec in report_data['recommendations']:
            content.append(f"* {rec}")
        content.append("")
    
    if 'next_steps' in report_data:
        content.append("## Next Steps")
        for step in report_data['next_steps']:
            content.append(f"* {step}")
    
    return "\n".join(content)

def export_report_to_html(report_data):
    """Export comprehensive report to an HTML file."""
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("  <meta charset='UTF-8'>")
    html.append("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append(f"  <title>Therapy Report - {report_data['client_name']}</title>")
    html.append("  <style>")
    html.append("    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }")
    html.append("    h1, h2, h3 { color: #2c3e50; }")
    html.append("    .meta { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }")
    html.append("    .section { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 15px 0; }")
    html.append("    .summary { background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; }")
    html.append("    ul { padding-left: 20px; }")
    html.append("  </style>")
    html.append("</head>")
    html.append("<body>")
    
    html.append(f"  <h1>Therapy Report</h1>")
    html.append("  <div class='meta'>")
    html.append(f"    <p><strong>Client:</strong> {report_data['client_name']}</p>")
    html.append(f"    <p><strong>Period:</strong> {report_data['period'].capitalize()}</p>")
    html.append(f"    <p><strong>Date:</strong> {report_data['date']}</p>")
    html.append(f"    <p><strong>Sessions Analyzed:</strong> {report_data['session_count']}</p>")
    html.append("  </div>")
    
    html.append("  <div class='summary'>")
    html.append("    <h2>Executive Summary</h2>")
    html.append(f"    <p>{report_data['executive_summary']}</p>")
    html.append("  </div>")
    
    if 'progress' in report_data:
        html.append("  <div class='section'>")
        html.append("    <h2>Progress</h2>")
        html.append(f"    <p>{report_data['progress']['summary']}</p>")
        html.append("    <h3>Key Areas of Progress</h3>")
        html.append("    <ul>")
        for area in report_data['progress']['areas_of_progress']:
            html.append(f"      <li>{area}</li>")
        html.append("    </ul>")
        html.append("  </div>")
    
    if 'challenges' in report_data:
        html.append("  <div class='section'>")
        html.append("    <h2>Challenges</h2>")
        html.append("    <ul>")
        for challenge in report_data['challenges']:
            html.append(f"      <li>{challenge}</li>")
        html.append("    </ul>")
        html.append("  </div>")
    
    if 'themes' in report_data:
        html.append("  <div class='section'>")
        html.append("    <h2>Key Themes</h2>")
        html.append("    <ul>")
        for theme in report_data['themes']:
            html.append(f"      <li>{theme}</li>")
        html.append("    </ul>")
        html.append("  </div>")
    
    if 'recommendations' in report_data:
        html.append("  <div class='section'>")
        html.append("    <h2>Recommendations</h2>")
        html.append("    <ul>")
        for rec in report_data['recommendations']:
            html.append(f"      <li>{rec}</li>")
        html.append("    </ul>")
        html.append("  </div>")
    
    if 'next_steps' in report_data:
        html.append("  <div class='section'>")
        html.append("    <h2>Next Steps</h2>")
        html.append("    <ul>")
        for step in report_data['next_steps']:
            html.append(f"      <li>{step}</li>")
        html.append("    </ul>")
        html.append("  </div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)

# This function would be implemented if weasyprint is available
def export_report_to_pdf(report_data, output_path):
    """Export comprehensive report to a PDF file."""
    try:
        from weasyprint import HTML
        
        # Generate HTML content
        html_content = export_report_to_html(report_data)
        
        # Convert to PDF
        HTML(string=html_content).write_pdf(output_path)
        
        return True
    except ImportError:
        raise ImportError("PDF export requires weasyprint to be installed.")
