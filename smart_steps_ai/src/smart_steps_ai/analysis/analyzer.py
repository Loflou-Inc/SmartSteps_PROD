"""Session analysis for the Smart Steps AI module."""

import datetime
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from ..config import get_config_manager
from ..utils import get_logger
from .models import AnalysisResult, Insight, InsightCategory, ProgressMetric, ReportFormat


class SessionAnalyzer:
    """
    Analyzer for session data.
    
    This class provides functionality for analyzing session data, generating
    insights, tracking progress, and creating reports.
    """

    def __init__(
        self,
        session_manager: Optional[Any] = None,
        memory_manager: Optional[Any] = None,
        persona_manager: Optional[Any] = None,
        provider_manager: Optional[Any] = None,
    ):
        """
        Initialize the session analyzer.

        Args:
            session_manager (Optional[SessionManager]): Session manager (default: None)
                If None, a new SessionManager will be created
            memory_manager (Optional[MemoryManager]): Memory manager (default: None)
                If None, a new MemoryManager will be created
            persona_manager (Optional[PersonaManager]): Persona manager (default: None)
                If None, a new PersonaManager will be created
            provider_manager (Optional[Any]): Provider manager (default: None)
                If None, a new ProviderManager will be created
        """
        self.logger = get_logger(__name__)
        self.config = get_config_manager().get()
        
        # Check if we're in testing mode from environment variable
        if os.environ.get("SMART_STEPS_APP_ENVIRONMENT") == "testing":
            # Set config environment to testing if not already set
            if not hasattr(self.config.app, 'environment') or self.config.app.environment != "testing":
                import types
                if not hasattr(self.config, 'app'):
                    self.config.app = types.SimpleNamespace()
                self.config.app.environment = "testing"
                self.logger.info("Set environment to testing mode from environment variable")
        
        # Import managers here to avoid circular imports
        from ..session import SessionManager
        from ..memory import MemoryManager
        from ..persona import PersonaManager
        
        # Set up required managers
        self.session_manager = session_manager or SessionManager()
        self.memory_manager = memory_manager or MemoryManager()
        self.persona_manager = persona_manager or PersonaManager()
        
        # Import here to avoid circular imports
        from ..provider import ProviderManager
        self.provider_manager = provider_manager or ProviderManager()
        
        # Create insight generator
        from .insight_generator import InsightGenerator
        self.insight_generator = InsightGenerator(provider_manager=self.provider_manager)
        
        self.logger.debug("Initialized session analyzer")

    def analyze_session(self, session_id: str) -> Optional[AnalysisResult]:
        """
        Analyze a session.

        Args:
            session_id (str): ID of the session

        Returns:
            Optional[AnalysisResult]: Analysis result or None if the session is not found
        """
        # Import Session here to avoid circular imports
        from ..session import Session
        
        # Get the session
        session = self.session_manager.get_session(session_id)
        if session is None:
            self.logger.warning(f"Session not found for analysis: {session_id}")
            return None
        
        self.logger.info(f"Starting analysis for session {session_id}")
        
        try:
            # Create the analysis result with required fields
            result = AnalysisResult(
                session_id=session_id,
                client_name=session.client_name,
                persona_name=session.persona_name,
                session_metadata=session.to_metadata(),
                summary="Initial summary placeholder",  # Will be replaced below
            )
            
            # Generate actual content for all required fields
            result.summary = self.generate_summary(session)
            result.insights = self.extract_insights(session)
            result.metrics = self.calculate_progress_metrics(session)
            result.themes = self.identify_themes(session)
            result.recommendations = self.generate_recommendations(session)
            result.next_steps = self.suggest_next_steps(session)
            
            # Store analysis results in memory if enabled
            if self.memory_manager.enabled:
                self._store_analysis_results(result)
            
            self.logger.info(f"Successfully analyzed session {session_id}: {len(result.insights)} insights, {len(result.metrics)} metrics")
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing session {session_id}: {str(e)}")
            return None

    def generate_summary(self, session: Any) -> str:
        """
        Generate a summary of the session.

        Args:
            session (Session): Session to summarize

        Returns:
            str: Session summary
        """
        # Get the conversation text
        conversation = session.get_conversation_text(include_role=True, include_timestamps=False)
        
        # For now, generate a basic summary
        summary = f"Session with {session.client_name} using the {session.persona_metadata.display_name} persona. "
        summary += f"The session contained {session.messages_count} messages "
        summary += f"and lasted for {session.duration_seconds // 60} minutes. "
        
        if session.state.value == "completed":
            summary += "The session was completed."
        elif session.state.value == "active":
            summary += "The session is still active."
        else:
            summary += f"The session is currently {session.state.value}."
        
        # Store the summary in memory
        if self.memory_manager.enabled:
            self.memory_manager.store_session_summary(session, summary)
        
        return summary

    def extract_insights(self, session: Any, provider_name: Optional[str] = None) -> List[Insight]:
        """
        Extract insights from a session using AI.

        Args:
            session (Session): Session to analyze
            provider_name (Optional[str]): Name of the provider to use (default: None)
                If None, uses the default provider or mock provider in testing

        Returns:
            List[Insight]: Extracted insights
        """
        try:
            # Check if we should use a real provider or mock
            provider = provider_name
            
            # If no provider specified, and we're in testing mode, use mock
            if not provider and self.config.app.environment == "testing":
                provider = "mock"
            
            # Generate insights using AI
            insight_types = ["general", "emotional", "cognitive", "behavioral", "progress", "challenges"]
            
            # Add a timeout for testing mode to prevent hanging
            if self.config.app.environment == "testing":
                max_wait_time = 0.5  # half second timeout for testing
                import time
                start_time = time.time()
                
                insights = self.insight_generator.generate_insights(
                    session=session,
                    insight_types=insight_types,
                    provider_name=provider
                )
                
                # Check if we've hit the timeout
                elapsed_time = time.time() - start_time
                if elapsed_time > max_wait_time:
                    self.logger.warning(f"Insight generation exceeded timeout ({max_wait_time}s), returning mock insights instead")
                    return self._generate_fallback_insights(session)
            else:
                # Normal mode without timeout
                insights = self.insight_generator.generate_insights(
                    session=session,
                    insight_types=insight_types,
                    provider_name=provider
                )
            
            # Store insights in memory
            if self.memory_manager.enabled:
                for insight in insights:
                    self.memory_manager.store_session_insight(
                        session=session,
                        insight=insight.text,
                        importance=5 + int(insight.confidence * 2),  # Scale importance based on confidence
                    )
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to extract insights using AI: {str(e)}")
            
            # Fall back to basic insights if AI extraction fails
            return self._generate_fallback_insights(session)
    
    def _generate_fallback_insights(self, session: Any) -> List[Insight]:
        """
        Generate basic fallback insights when AI extraction fails.

        Args:
            session (Session): Session to analyze

        Returns:
            List[Insight]: Basic insights
        """
        # Simple placeholder implementation
        insights = []
        
        # Example insights
        if session.messages_count > 0:
            insights.append(
                Insight(
                    text=f"Session with {session.client_name} included {session.messages_count} messages.",
                    category=InsightCategory.GENERAL,
                    confidence=0.9,
                )
            )
        
        if session.duration_seconds > 300:  # 5 minutes
            insights.append(
                Insight(
                    text=f"Session lasted for {session.duration_seconds // 60} minutes, indicating substantial engagement.",
                    category=InsightCategory.PATTERN,
                    confidence=0.8,
                )
            )
        
        return insights

    def calculate_progress_metrics(self, session: Any) -> List[ProgressMetric]:
        """
        Calculate progress metrics for a session.

        Args:
            session (Session): Session to analyze

        Returns:
            List[ProgressMetric]: Progress metrics
        """
        metrics = []
        
        # Example metrics (in a real implementation, these would be calculated dynamically)
        engagement_metric = ProgressMetric(
            name="Engagement",
            description="Level of client engagement in the session",
            value=min(session.messages_count / 10, 10.0),  # Simple calculation based on message count
            previous_value=5.0,  # In a real implementation, this would be loaded from history
            target_value=8.0,
        )
        engagement_metric.calculate_changes()
        metrics.append(engagement_metric)
        
        session_progress = ProgressMetric(
            name="Session Progress",
            description="Progress toward session goals",
            value=7.5,  # In a real implementation, this would be calculated based on content
            previous_value=6.8,
            target_value=9.0,
        )
        session_progress.calculate_changes()
        metrics.append(session_progress)
        
        return metrics

    def identify_themes(self, session: Any) -> List[str]:
        """
        Identify themes in a session.

        Args:
            session (Session): Session to analyze

        Returns:
            List[str]: Identified themes
        """
        # Simple placeholder implementation
        themes = []
        
        # In a real implementation, these would be extracted using NLP
        themes.append("Session Structure")
        
        # Example: add themes based on tags if available
        for tag in session.tags:
            if tag not in themes:
                themes.append(tag)
        
        return themes

    def generate_recommendations(self, session: Any) -> List[str]:
        """
        Generate recommendations based on the session.

        Args:
            session (Session): Session to analyze

        Returns:
            List[str]: Recommendations
        """
        # Simple placeholder implementation
        recommendations = []
        
        # Example recommendations (in a real implementation, these would be generated dynamically)
        recommendations.append(
            f"Continue with regular sessions to maintain progress."
        )
        
        recommendations.append(
            f"Consider reviewing key points from this session at the start of the next one."
        )
        
        return recommendations

    def suggest_next_steps(self, session: Any) -> List[str]:
        """
        Suggest next steps based on the session.

        Args:
            session (Session): Session to analyze

        Returns:
            List[str]: Suggested next steps
        """
        # Simple placeholder implementation
        next_steps = []
        
        # Example next steps (in a real implementation, these would be generated dynamically)
        next_steps.append(
            f"Schedule follow-up session within the next week."
        )
        
        next_steps.append(
            f"Prepare specific topics to explore in the next session."
        )
        
        return next_steps

    def generate_report(
        self, analysis_result: AnalysisResult, format: Union[str, ReportFormat] = ReportFormat.MARKDOWN
    ) -> str:
        """
        Generate a report from an analysis result.

        Args:
            analysis_result (AnalysisResult): Analysis result
            format (Union[str, ReportFormat]): Report format (default: ReportFormat.MARKDOWN)

        Returns:
            str: Generated report
        """
        # Convert format to enum if it's a string
        if isinstance(format, str):
            try:
                format = ReportFormat(format)
            except ValueError:
                self.logger.warning(f"Invalid report format: {format}, using MARKDOWN")
                format = ReportFormat.MARKDOWN
        
        # Generate the report based on the format
        if format == ReportFormat.TEXT:
            return self._generate_text_report(analysis_result)
        elif format == ReportFormat.MARKDOWN:
            return self._generate_markdown_report(analysis_result)
        elif format == ReportFormat.HTML:
            return self._generate_html_report(analysis_result)
        elif format == ReportFormat.JSON:
            return self._generate_json_report(analysis_result)
        elif format == ReportFormat.CSV:
            return self._generate_csv_report(analysis_result)
        else:
            # Default to markdown
            return self._generate_markdown_report(analysis_result)

    def _generate_text_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate a text report.

        Args:
            analysis_result (AnalysisResult): Analysis result

        Returns:
            str: Text report
        """
        lines = []
        
        # Header
        lines.append(f"Session Analysis Report")
        lines.append(f"======================")
        lines.append("")
        
        # Basic information
        lines.append(f"Client: {analysis_result.client_name}")
        lines.append(f"Persona: {analysis_result.persona_name}")
        lines.append(f"Date: {analysis_result.timestamp.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Session ID: {analysis_result.session_id}")
        lines.append("")
        
        # Summary
        lines.append(f"Summary")
        lines.append(f"-------")
        lines.append(analysis_result.summary)
        lines.append("")
        
        # Insights
        if analysis_result.insights:
            lines.append(f"Insights")
            lines.append(f"--------")
            for i, insight in enumerate(analysis_result.insights, 1):
                lines.append(f"{i}. {insight.text} (Category: {insight.category.value}, Confidence: {insight.confidence:.2f})")
            lines.append("")
        
        # Progress metrics
        if analysis_result.metrics:
            lines.append(f"Progress Metrics")
            lines.append(f"---------------")
            for metric in analysis_result.metrics:
                lines.append(f"{metric.name}: {metric.value:.1f}/{metric.max_value:.1f} - {metric.description}")
                if metric.change is not None:
                    change_str = "+" if metric.change > 0 else ""
                    lines.append(f"  Change from previous: {change_str}{metric.change:.1f}")
            lines.append("")
        
        # Themes
        if analysis_result.themes:
            lines.append(f"Key Themes")
            lines.append(f"----------")
            for theme in analysis_result.themes:
                lines.append(f"- {theme}")
            lines.append("")
        
        # Recommendations
        if analysis_result.recommendations:
            lines.append(f"Recommendations")
            lines.append(f"--------------")
            for i, recommendation in enumerate(analysis_result.recommendations, 1):
                lines.append(f"{i}. {recommendation}")
            lines.append("")
        
        # Next steps
        if analysis_result.next_steps:
            lines.append(f"Next Steps")
            lines.append(f"----------")
            for i, step in enumerate(analysis_result.next_steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_markdown_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate a markdown report.

        Args:
            analysis_result (AnalysisResult): Analysis result

        Returns:
            str: Markdown report
        """
        lines = []
        
        # Header
        lines.append(f"# Session Analysis Report")
        lines.append("")
        
        # Basic information
        lines.append(f"**Client:** {analysis_result.client_name}  ")
        lines.append(f"**Persona:** {analysis_result.persona_name}  ")
        lines.append(f"**Date:** {analysis_result.timestamp.strftime('%Y-%m-%d %H:%M')}  ")
        lines.append(f"**Session ID:** {analysis_result.session_id}  ")
        lines.append("")
        
        # Summary
        lines.append(f"## Summary")
        lines.append(analysis_result.summary)
        lines.append("")
        
        # Insights
        if analysis_result.insights:
            lines.append(f"## Insights")
            for i, insight in enumerate(analysis_result.insights, 1):
                lines.append(f"{i}. **{insight.category.value.capitalize()}:** {insight.text} *(Confidence: {insight.confidence:.2f})*")
            lines.append("")
        
        # Progress metrics
        if analysis_result.metrics:
            lines.append(f"## Progress Metrics")
            for metric in analysis_result.metrics:
                lines.append(f"### {metric.name}: {metric.value:.1f}/{metric.max_value:.1f}")
                lines.append(f"*{metric.description}*")
                if metric.change is not None:
                    change_str = "+" if metric.change > 0 else ""
                    lines.append(f"**Change from previous:** {change_str}{metric.change:.1f}")
                lines.append("")
        
        # Themes
        if analysis_result.themes:
            lines.append(f"## Key Themes")
            for theme in analysis_result.themes:
                lines.append(f"- {theme}")
            lines.append("")
        
        # Recommendations
        if analysis_result.recommendations:
            lines.append(f"## Recommendations")
            for i, recommendation in enumerate(analysis_result.recommendations, 1):
                lines.append(f"{i}. {recommendation}")
            lines.append("")
        
        # Next steps
        if analysis_result.next_steps:
            lines.append(f"## Next Steps")
            for i, step in enumerate(analysis_result.next_steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_html_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate an HTML report.

        Args:
            analysis_result (AnalysisResult): Analysis result

        Returns:
            str: HTML report
        """
        # Convert markdown to HTML
        markdown = self._generate_markdown_report(analysis_result)
        
        # Simple HTML wrapper
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Session Analysis Report - {analysis_result.client_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .header {{ border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 20px; }}
        .metric {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 10px; }}
        .insight {{ margin-bottom: 10px; }}
        .category {{ font-weight: bold; color: #555; }}
        .confidence {{ font-style: italic; color: #777; }}
        .change-positive {{ color: green; }}
        .change-negative {{ color: red; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Session Analysis Report</h1>
        <p><strong>Client:</strong> {analysis_result.client_name}</p>
        <p><strong>Persona:</strong> {analysis_result.persona_name}</p>
        <p><strong>Date:</strong> {analysis_result.timestamp.strftime('%Y-%m-%d %H:%M')}</p>
        <p><strong>Session ID:</strong> {analysis_result.session_id}</p>
    </div>
    
    <div class="section">
        <h2>Summary</h2>
        <p>{analysis_result.summary}</p>
    </div>
"""
        
        # Insights
        if analysis_result.insights:
            html += f"""
    <div class="section">
        <h2>Insights</h2>
        <ol>
"""
            for insight in analysis_result.insights:
                html += f"""            <li class="insight">
                <span class="category">{insight.category.value.capitalize()}:</span> {insight.text}
                <span class="confidence">(Confidence: {insight.confidence:.2f})</span>
            </li>
"""
            html += f"""        </ol>
    </div>
"""
        
        # Progress metrics
        if analysis_result.metrics:
            html += f"""
    <div class="section">
        <h2>Progress Metrics</h2>
"""
            for metric in analysis_result.metrics:
                change_class = ""
                change_str = ""
                if metric.change is not None:
                    change_class = "change-positive" if metric.change > 0 else "change-negative"
                    change_str = "+" if metric.change > 0 else ""
                    change_str += f"{metric.change:.1f}"
                
                html += f"""        <div class="metric">
            <h3>{metric.name}: {metric.value:.1f}/{metric.max_value:.1f}</h3>
            <p>{metric.description}</p>
"""
                if metric.change is not None:
                    html += f"""            <p><strong>Change from previous:</strong> <span class="{change_class}">{change_str}</span></p>
"""
                html += f"""        </div>
"""
            html += f"""    </div>
"""
        
        # Themes
        if analysis_result.themes:
            html += f"""
    <div class="section">
        <h2>Key Themes</h2>
        <ul>
"""
            for theme in analysis_result.themes:
                html += f"""            <li>{theme}</li>
"""
            html += f"""        </ul>
    </div>
"""
        
        # Recommendations
        if analysis_result.recommendations:
            html += f"""
    <div class="section">
        <h2>Recommendations</h2>
        <ol>
"""
            for recommendation in analysis_result.recommendations:
                html += f"""            <li>{recommendation}</li>
"""
            html += f"""        </ol>
    </div>
"""
        
        # Next steps
        if analysis_result.next_steps:
            html += f"""
    <div class="section">
        <h2>Next Steps</h2>
        <ol>
"""
            for step in analysis_result.next_steps:
                html += f"""            <li>{step}</li>
"""
            html += f"""        </ol>
    </div>
"""
        
        html += f"""
</body>
</html>
"""
        
        return html

    def _generate_json_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate a JSON report.

        Args:
            analysis_result (AnalysisResult): Analysis result

        Returns:
            str: JSON report
        """
        # Convert to JSON
        return analysis_result.model_dump_json(indent=2)

    def _generate_csv_report(self, analysis_result: AnalysisResult) -> str:
        """
        Generate a CSV report.

        Args:
            analysis_result (AnalysisResult): Analysis result

        Returns:
            str: CSV report
        """
        # Simple CSV format (limited to basic fields)
        lines = []
        
        # Header
        lines.append("Field,Value")
        
        # Basic information
        lines.append(f"Client,{analysis_result.client_name}")
        lines.append(f"Persona,{analysis_result.persona_name}")
        lines.append(f"Date,{analysis_result.timestamp.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Session ID,{analysis_result.session_id}")
        
        # Summary (escape commas and quotes)
        summary = analysis_result.summary.replace('"', '""')
        lines.append(f"Summary,\"{summary}\"")
        
        # Insights
        for i, insight in enumerate(analysis_result.insights, 1):
            text = insight.text.replace('"', '""')
            lines.append(f"Insight {i},\"{text}\"")
            lines.append(f"Insight {i} Category,{insight.category.value}")
            lines.append(f"Insight {i} Confidence,{insight.confidence:.2f}")
        
        # Progress metrics
        for metric in analysis_result.metrics:
            lines.append(f"Metric {metric.name},\"{metric.value:.1f}/{metric.max_value:.1f}\"")
            lines.append(f"Metric {metric.name} Description,\"{metric.description}\"")
            if metric.change is not None:
                lines.append(f"Metric {metric.name} Change,{metric.change:.1f}")
        
        # Themes
        for i, theme in enumerate(analysis_result.themes, 1):
            lines.append(f"Theme {i},\"{theme}\"")
        
        # Recommendations
        for i, recommendation in enumerate(analysis_result.recommendations, 1):
            text = recommendation.replace('"', '""')
            lines.append(f"Recommendation {i},\"{text}\"")
        
        # Next steps
        for i, step in enumerate(analysis_result.next_steps, 1):
            text = step.replace('"', '""')
            lines.append(f"Next Step {i},\"{text}\"")
        
        return "\n".join(lines)

    def _store_analysis_results(self, result: AnalysisResult) -> None:
        """
        Store analysis results in memory.

        Args:
            result (AnalysisResult): Analysis result
        """
        if not self.memory_manager.enabled:
            return
        
        # Import MemoryType here
        from ..memory.models import MemoryType
        
        # Store summary
        self.memory_manager.store_memory(
            text=result.summary,
            client_name=result.client_name,
            memory_type=MemoryType.SESSION_SUMMARY,
            source_type="analysis",
            source_id=f"analysis_{result.session_id}",
            importance=7,
            tags=["analysis_summary"],
        )
        
        # Store insights
        for insight in result.insights:
            self.memory_manager.store_memory(
                text=insight.text,
                client_name=result.client_name,
                memory_type=MemoryType.INSIGHT,
                source_type="analysis",
                source_id=f"analysis_{result.session_id}",
                importance=int(5 + insight.confidence * 3),  # Scale importance based on confidence
                tags=["analysis_insight", f"category_{insight.category.value}"],
            )
        
        # Store recommendations
        for recommendation in result.recommendations:
            self.memory_manager.store_memory(
                text=recommendation,
                client_name=result.client_name,
                memory_type=MemoryType.STRATEGY,
                source_type="analysis",
                source_id=f"analysis_{result.session_id}",
                importance=6,
                tags=["analysis_recommendation"],
            )
