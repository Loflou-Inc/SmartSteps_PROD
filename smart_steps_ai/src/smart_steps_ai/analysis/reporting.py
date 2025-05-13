"""Report generation for session analysis."""

import os
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from ..config import get_config_manager
from ..utils import get_logger
from .models import AnalysisResult, ReportFormat
from .visualization import VisualizationManager


class ReportGenerator:
    """
    Generator for creating reports from session analysis results.
    
    This class provides functionality for generating reports in various formats
    and with various levels of detail, including visualizations.
    """

    def __init__(self, visualization_manager: Optional[VisualizationManager] = None):
        """
        Initialize the report generator.

        Args:
            visualization_manager (Optional[VisualizationManager]): Visualization manager
                If None, a new VisualizationManager will be created
        """
        self.logger = get_logger(__name__)
        self.config = get_config_manager().get()
        self.visualization_manager = visualization_manager or VisualizationManager()
        
        self.logger.debug("Initialized report generator")

    def generate_report(
        self, 
        analysis_result: AnalysisResult, 
        format: Union[str, ReportFormat] = ReportFormat.MARKDOWN,
        include_visualizations: bool = True,
        level_of_detail: str = "standard"  # "minimal", "standard", "detailed"
    ) -> str:
        """
        Generate a report from an analysis result.

        Args:
            analysis_result (AnalysisResult): Analysis result
            format (Union[str, ReportFormat]): Report format (default: ReportFormat.MARKDOWN)
            include_visualizations (bool): Whether to include visualizations (default: True)
            level_of_detail (str): Level of detail to include (default: "standard")
                "minimal" - Basic summary and key points
                "standard" - Summary, insights, metrics, themes, and recommendations
                "detailed" - All available information with extended analysis

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
            return self._generate_text_report(analysis_result, include_visualizations, level_of_detail)
        elif format == ReportFormat.MARKDOWN:
            return self._generate_markdown_report(analysis_result, include_visualizations, level_of_detail)
        elif format == ReportFormat.HTML:
            return self._generate_html_report(analysis_result, include_visualizations, level_of_detail)
        elif format == ReportFormat.JSON:
            return self._generate_json_report(analysis_result, level_of_detail)
        elif format == ReportFormat.CSV:
            return self._generate_csv_report(analysis_result, level_of_detail)
        else:
            # Default to markdown
            return self._generate_markdown_report(analysis_result, include_visualizations, level_of_detail)

    def save_report(
        self, 
        analysis_result: AnalysisResult, 
        output_dir: Union[str, Path], 
        filename: Optional[str] = None,
        format: Union[str, ReportFormat] = ReportFormat.MARKDOWN,
        include_visualizations: bool = True,
        level_of_detail: str = "standard"
    ) -> Path:
        """
        Generate a report and save it to a file.

        Args:
            analysis_result (AnalysisResult): Analysis result
            output_dir (Union[str, Path]): Directory to save the report
            filename (Optional[str]): Filename to use (default: None)
                If None, a filename will be generated based on the analysis result
            format (Union[str, ReportFormat]): Report format (default: ReportFormat.MARKDOWN)
            include_visualizations (bool): Whether to include visualizations (default: True)
            level_of_detail (str): Level of detail to include (default: "standard")

        Returns:
            Path: Path to the saved report
        """
        # Convert format to enum if it's a string
        if isinstance(format, str):
            try:
                format = ReportFormat(format)
            except ValueError:
                self.logger.warning(f"Invalid report format: {format}, using MARKDOWN")
                format = ReportFormat.MARKDOWN
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            client_name = "".join(c for c in analysis_result.client_name if c.isalnum())
            filename = f"report_{client_name}_{timestamp}.{format.value}"
        
        # Generate report
        report_content = self.generate_report(
            analysis_result, format, include_visualizations, level_of_detail
        )
        
        # Save report
        report_path = output_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Saved report to {report_path}")
        return report_path

    def generate_reports(
        self, 
        analysis_result: AnalysisResult, 
        formats: List[Union[str, ReportFormat]],
        output_dir: Union[str, Path],
        include_visualizations: bool = True,
        level_of_detail: str = "standard"
    ) -> Dict[str, Path]:
        """
        Generate reports in multiple formats.

        Args:
            analysis_result (AnalysisResult): Analysis result
            formats (List[Union[str, ReportFormat]]): List of formats to generate
            output_dir (Union[str, Path]): Directory to save the reports
            include_visualizations (bool): Whether to include visualizations (default: True)
            level_of_detail (str): Level of detail to include (default: "standard")

        Returns:
            Dict[str, Path]: Dictionary mapping format names to report paths
        """
        report_paths = {}
        
        for format in formats:
            # Convert format to string if it's an enum
            format_str = format.value if hasattr(format, 'value') else format
            
            # Generate and save report
            report_path = self.save_report(
                analysis_result=analysis_result,
                output_dir=output_dir,
                filename=None,  # Auto-generate filename
                format=format,
                include_visualizations=include_visualizations,
                level_of_detail=level_of_detail
            )
            
            report_paths[format_str] = report_path
        
        return report_paths

    def _generate_text_report(
        self, analysis_result: AnalysisResult, include_visualizations: bool, level_of_detail: str
    ) -> str:
        """
        Generate a text report.

        Args:
            analysis_result (AnalysisResult): Analysis result
            include_visualizations (bool): Whether to include visualizations
            level_of_detail (str): Level of detail to include

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
        
        # For minimal reports, we stop here
        if level_of_detail == "minimal":
            return "\n".join(lines)
        
        # Insights
        if analysis_result.insights:
            lines.append(f"Insights")
            lines.append(f"--------")
            for i, insight in enumerate(analysis_result.insights, 1):
                lines.append(f"{i}. {insight.text}")
                
                # Add more detail for detailed reports
                if level_of_detail == "detailed":
                    lines.append(f"   Category: {insight.category.value}")
                    lines.append(f"   Confidence: {insight.confidence:.2f}")
                    
                    if insight.evidence:
                        lines.append(f"   Evidence:")
                        for j, evidence in enumerate(insight.evidence, 1):
                            lines.append(f"     {j}. {evidence}")
            lines.append("")
        
        # Progress metrics
        if analysis_result.metrics:
            lines.append(f"Progress Metrics")
            lines.append(f"---------------")
            for metric in analysis_result.metrics:
                lines.append(f"{metric.name}: {metric.value:.1f}/{metric.max_value:.1f}")
                lines.append(f"  {metric.description}")
                
                # Add more detail for standard and detailed reports
                if level_of_detail in ["standard", "detailed"]:
                    if metric.change is not None:
                        change_str = "+" if metric.change > 0 else ""
                        lines.append(f"  Change from previous: {change_str}{metric.change:.1f}")
                    
                    if metric.target_value is not None:
                        distance_to_target = metric.target_value - metric.value
                        lines.append(f"  Target: {metric.target_value:.1f} ({distance_to_target:.1f} point{'s' if abs(distance_to_target) != 1 else ''} to go)")
                
                # Add even more detail for detailed reports
                if level_of_detail == "detailed" and metric.change_percentage is not None:
                    lines.append(f"  Change percentage: {metric.change_percentage:.1f}%")
                
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
        
        # Note about visualizations
        if include_visualizations:
            lines.append(f"Note: Visualizations are not available in text format. Use HTML or Markdown for visualizations.")
            lines.append("")
        
        # Session metadata for detailed reports
        if level_of_detail == "detailed" and analysis_result.session_metadata:
            lines.append(f"Session Metadata")
            lines.append(f"---------------")
            for key, value in analysis_result.session_metadata.model_dump().items():
                if key != "message_history":  # Skip message history to avoid huge reports
                    lines.append(f"{key}: {value}")
            lines.append("")
        
        # Additional data for detailed reports
        if level_of_detail == "detailed" and analysis_result.additional_data:
            lines.append(f"Additional Data")
            lines.append(f"---------------")
            for key, value in analysis_result.additional_data.items():
                lines.append(f"{key}: {value}")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_markdown_report(
        self, analysis_result: AnalysisResult, include_visualizations: bool, level_of_detail: str
    ) -> str:
        """
        Generate a markdown report.

        Args:
            analysis_result (AnalysisResult): Analysis result
            include_visualizations (bool): Whether to include visualizations
            level_of_detail (str): Level of detail to include

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
        
        # For minimal reports, we stop here
        if level_of_detail == "minimal":
            return "\n".join(lines)
        
        # Charts for standard and detailed reports
        if include_visualizations and analysis_result.metrics and level_of_detail in ["standard", "detailed"]:
            lines.append(f"## Progress Visualization")
            
            # Create progress chart
            metrics_data = [metric.model_dump() for metric in analysis_result.metrics]
            progress_chart = self.visualization_manager.create_progress_chart(
                metrics=metrics_data,
                title="Progress Metrics"
            )
            
            lines.append(f"![Progress Chart](data:image/png;base64,{progress_chart})")
            lines.append("")
            
            # Add radar chart for detailed reports
            if level_of_detail == "detailed":
                radar_chart = self.visualization_manager.create_metrics_radar_chart(
                    metrics=metrics_data,
                    title="Metrics Radar"
                )
                
                lines.append(f"![Metrics Radar](data:image/png;base64,{radar_chart})")
                lines.append("")
        
        # Insights
        if analysis_result.insights:
            lines.append(f"## Insights")
            
            # Add visualization for standard and detailed reports
            if include_visualizations and level_of_detail in ["standard", "detailed"]:
                insights_data = [insight.model_dump() for insight in analysis_result.insights]
                
                # Category chart
                category_chart = self.visualization_manager.create_insight_category_chart(
                    insights=insights_data,
                    title="Insight Categories"
                )
                
                lines.append(f"![Insight Categories](data:image/png;base64,{category_chart})")
                lines.append("")
                
                # Confidence chart for detailed reports
                if level_of_detail == "detailed":
                    confidence_chart = self.visualization_manager.create_confidence_distribution_chart(
                        insights=insights_data,
                        title="Insight Confidence Distribution"
                    )
                    
                    lines.append(f"![Confidence Distribution](data:image/png;base64,{confidence_chart})")
                    lines.append("")
            
            # List insights
            for i, insight in enumerate(analysis_result.insights, 1):
                lines.append(f"{i}. **{insight.category.value.capitalize()}:** {insight.text} *(Confidence: {insight.confidence:.2f})*")
                
                # Add more detail for detailed reports
                if level_of_detail == "detailed" and insight.evidence:
                    lines.append(f"   **Evidence:**")
                    for evidence in insight.evidence:
                        lines.append(f"   - {evidence}")
                    lines.append("")
            
            lines.append("")
        
        # Progress metrics
        if analysis_result.metrics:
            lines.append(f"## Progress Metrics")
            
            for metric in analysis_result.metrics:
                lines.append(f"### {metric.name}: {metric.value:.1f}/{metric.max_value:.1f}")
                lines.append(f"*{metric.description}*")
                
                # Add more detail for standard and detailed reports
                if level_of_detail in ["standard", "detailed"]:
                    if metric.change is not None:
                        change_str = "+" if metric.change > 0 else ""
                        lines.append(f"**Change from previous:** {change_str}{metric.change:.1f}")
                    
                    if metric.target_value is not None:
                        distance_to_target = metric.target_value - metric.value
                        lines.append(f"**Target:** {metric.target_value:.1f} ({distance_to_target:.1f} point{'s' if abs(distance_to_target) != 1 else ''} to go)")
                
                # Add even more detail for detailed reports
                if level_of_detail == "detailed" and metric.change_percentage is not None:
                    lines.append(f"**Change percentage:** {metric.change_percentage:.1f}%")
                
                lines.append("")
        
        # Themes
        if analysis_result.themes:
            lines.append(f"## Key Themes")
            
            # Add visualization for standard and detailed reports
            if include_visualizations and level_of_detail in ["standard", "detailed"]:
                theme_chart = self.visualization_manager.create_theme_pie_chart(
                    themes=analysis_result.themes,
                    title="Session Themes"
                )
                
                lines.append(f"![Session Themes](data:image/png;base64,{theme_chart})")
                lines.append("")
            
            # List themes
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
        
        # Session metadata for detailed reports
        if level_of_detail == "detailed" and analysis_result.session_metadata:
            lines.append(f"## Session Metadata")
            
            for key, value in analysis_result.session_metadata.model_dump().items():
                if key != "message_history":  # Skip message history to avoid huge reports
                    lines.append(f"**{key}:** {value}  ")
            
            lines.append("")
        
        # Additional data for detailed reports
        if level_of_detail == "detailed" and analysis_result.additional_data:
            lines.append(f"## Additional Data")
            
            for key, value in analysis_result.additional_data.items():
                lines.append(f"**{key}:** {value}  ")
            
            lines.append("")
        
        # Report generation info
        lines.append(f"---")
        lines.append(f"*Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(lines)

    def _generate_html_report(
        self, analysis_result: AnalysisResult, include_visualizations: bool, level_of_detail: str
    ) -> str:
        """
        Generate an HTML report.

        Args:
            analysis_result (AnalysisResult): Analysis result
            include_visualizations (bool): Whether to include visualizations
            level_of_detail (str): Level of detail to include

        Returns:
            str: HTML report
        """
        # Start with basic HTML structure
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Session Analysis Report - {analysis_result.client_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .header {{ border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 20px; }}
        .metric {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 15px; }}
        .insight {{ margin-bottom: 15px; }}
        .category {{ font-weight: bold; color: #555; }}
        .confidence {{ font-style: italic; color: #777; }}
        .evidence {{ margin-left: 20px; color: #666; }}
        .evidence-item {{ margin-bottom: 5px; }}
        .change-positive {{ color: green; }}
        .change-negative {{ color: red; }}
        .visualization {{ text-align: center; margin: 20px 0; }}
        .theme {{ display: inline-block; background-color: #f0f0f0; border-radius: 15px; padding: 5px 12px; margin: 5px; }}
        .recommendation {{ margin-bottom: 10px; }}
        .next-step {{ margin-bottom: 10px; }}
        .footer {{ margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px; font-size: 0.8em; color: #777; }}
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
        
        # For minimal reports, we finish here
        if level_of_detail == "minimal":
            html += f"""
    <div class="footer">
        <p>Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
            return html
        
        # Progress visualizations for standard and detailed reports
        if include_visualizations and analysis_result.metrics and level_of_detail in ["standard", "detailed"]:
            metrics_data = [metric.model_dump() for metric in analysis_result.metrics]
            
            html += f"""
    <div class="section">
        <h2>Progress Visualization</h2>
        <div class="visualization">
            <img src="data:image/png;base64,{self.visualization_manager.create_progress_chart(metrics_data, 'Progress Metrics')}" alt="Progress Chart">
        </div>
"""
            
            # Add radar chart for detailed reports
            if level_of_detail == "detailed":
                html += f"""
        <div class="visualization">
            <img src="data:image/png;base64,{self.visualization_manager.create_metrics_radar_chart(metrics_data, 'Metrics Radar')}" alt="Metrics Radar">
        </div>
"""
            
            html += f"""
    </div>
"""
        
        # Insights
        if analysis_result.insights:
            insights_data = [insight.model_dump() for insight in analysis_result.insights]
            
            html += f"""
    <div class="section">
        <h2>Insights</h2>
"""
            
            # Add visualizations for standard and detailed reports
            if include_visualizations and level_of_detail in ["standard", "detailed"]:
                html += f"""
        <div class="visualization">
            <img src="data:image/png;base64,{self.visualization_manager.create_insight_category_chart(insights_data, 'Insight Categories')}" alt="Insight Categories">
        </div>
"""
                
                # Add confidence chart for detailed reports
                if level_of_detail == "detailed":
                    html += f"""
        <div class="visualization">
            <img src="data:image/png;base64,{self.visualization_manager.create_confidence_distribution_chart(insights_data, 'Insight Confidence Distribution')}" alt="Confidence Distribution">
        </div>
"""
            
            # List insights
            html += f"""
        <ol>
"""
            for insight in analysis_result.insights:
                html += f"""
            <li class="insight">
                <span class="category">{insight.category.value.capitalize()}:</span> {insight.text}
                <span class="confidence">(Confidence: {insight.confidence:.2f})</span>
"""
                
                # Add evidence for detailed reports
                if level_of_detail == "detailed" and insight.evidence:
                    html += f"""
                <div class="evidence">
                    <p>Evidence:</p>
                    <ul>
"""
                    for evidence in insight.evidence:
                        html += f"""
                        <li class="evidence-item">{evidence}</li>
"""
                    html += f"""
                    </ul>
                </div>
"""
                
                html += f"""
            </li>
"""
            
            html += f"""
        </ol>
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
                change_html = ""
                
                if level_of_detail in ["standard", "detailed"] and metric.change is not None:
                    change_class = "change-positive" if metric.change > 0 else "change-negative"
                    change_sign = "+" if metric.change > 0 else ""
                    change_html = f"""<p><strong>Change from previous:</strong> <span class="{change_class}">{change_sign}{metric.change:.1f}</span></p>"""
                
                target_html = ""
                if level_of_detail in ["standard", "detailed"] and metric.target_value is not None:
                    distance_to_target = metric.target_value - metric.value
                    target_html = f"""<p><strong>Target:</strong> {metric.target_value:.1f} ({distance_to_target:.1f} point{'s' if abs(distance_to_target) != 1 else ''} to go)</p>"""
                
                change_percentage_html = ""
                if level_of_detail == "detailed" and metric.change_percentage is not None:
                    change_percentage_html = f"""<p><strong>Change percentage:</strong> {metric.change_percentage:.1f}%</p>"""
                
                html += f"""
        <div class="metric">
            <h3>{metric.name}: {metric.value:.1f}/{metric.max_value:.1f}</h3>
            <p>{metric.description}</p>
            {change_html}
            {target_html}
            {change_percentage_html}
        </div>
"""
            
            html += f"""
    </div>
"""
        
        # Themes
        if analysis_result.themes:
            html += f"""
    <div class="section">
        <h2>Key Themes</h2>
"""
            
            # Add visualization for standard and detailed reports
            if include_visualizations and level_of_detail in ["standard", "detailed"]:
                html += f"""
        <div class="visualization">
            <img src="data:image/png;base64,{self.visualization_manager.create_theme_pie_chart(analysis_result.themes, 'Session Themes')}" alt="Session Themes">
        </div>
"""
            
            # List themes
            html += f"""
        <div>
"""
            for theme in analysis_result.themes:
                html += f"""
            <div class="theme">{theme}</div>
"""
            
            html += f"""
        </div>
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
                html += f"""
            <li class="recommendation">{recommendation}</li>
"""
            
            html += f"""
        </ol>
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
                html += f"""
            <li class="next-step">{step}</li>
"""
            
            html += f"""
        </ol>
    </div>
"""
        
        # Session metadata for detailed reports
        if level_of_detail == "detailed" and analysis_result.session_metadata:
            html += f"""
    <div class="section">
        <h2>Session Metadata</h2>
        <table>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
"""
            for key, value in analysis_result.session_metadata.model_dump().items():
                if key != "message_history":  # Skip message history to avoid huge reports
                    html += f"""
            <tr>
                <td><strong>{key}</strong></td>
                <td>{value}</td>
            </tr>
"""
            
            html += f"""
        </table>
    </div>
"""
        
        # Additional data for detailed reports
        if level_of_detail == "detailed" and analysis_result.additional_data:
            html += f"""
    <div class="section">
        <h2>Additional Data</h2>
        <table>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
"""
            for key, value in analysis_result.additional_data.items():
                html += f"""
            <tr>
                <td><strong>{key}</strong></td>
                <td>{value}</td>
            </tr>
"""
            
            html += f"""
        </table>
    </div>
"""
        
        # Footer
        html += f"""
    <div class="footer">
        <p>Report generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        return html

    def _generate_json_report(self, analysis_result: AnalysisResult, level_of_detail: str) -> str:
        """
        Generate a JSON report.

        Args:
            analysis_result (AnalysisResult): Analysis result
            level_of_detail (str): Level of detail to include

        Returns:
            str: JSON report
        """
        # For minimal reports, include only basic information
        if level_of_detail == "minimal":
            report_data = {
                "client_name": analysis_result.client_name,
                "persona_name": analysis_result.persona_name,
                "session_id": analysis_result.session_id,
                "timestamp": analysis_result.timestamp.isoformat(),
                "summary": analysis_result.summary
            }
        else:
            # For standard and detailed reports, include all data
            report_data = analysis_result.model_dump()
            
            # For standard reports, exclude session metadata and additional data
            if level_of_detail == "standard":
                report_data.pop("session_metadata", None)
                report_data.pop("additional_data", None)
        
        return json.dumps(report_data, indent=2)

    def _generate_csv_report(self, analysis_result: AnalysisResult, level_of_detail: str) -> str:
        """
        Generate a CSV report.

        Args:
            analysis_result (AnalysisResult): Analysis result
            level_of_detail (str): Level of detail to include

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
        
        # For minimal reports, we stop here
        if level_of_detail == "minimal":
            return "\n".join(lines)
        
        # Insights
        for i, insight in enumerate(analysis_result.insights, 1):
            text = insight.text.replace('"', '""')
            lines.append(f"Insight {i},\"{text}\"")
            lines.append(f"Insight {i} Category,{insight.category.value}")
            lines.append(f"Insight {i} Confidence,{insight.confidence:.2f}")
            
            # Add evidence for detailed reports
            if level_of_detail == "detailed" and insight.evidence:
                for j, evidence in enumerate(insight.evidence, 1):
                    evidence_text = evidence.replace('"', '""')
                    lines.append(f"Insight {i} Evidence {j},\"{evidence_text}\"")
        
        # Progress metrics
        for metric in analysis_result.metrics:
            lines.append(f"Metric {metric.name},\"{metric.value:.1f}/{metric.max_value:.1f}\"")
            lines.append(f"Metric {metric.name} Description,\"{metric.description}\"")
            
            # Add more detail for standard and detailed reports
            if level_of_detail in ["standard", "detailed"]:
                if metric.change is not None:
                    lines.append(f"Metric {metric.name} Change,{metric.change:.1f}")
                
                if metric.target_value is not None:
                    lines.append(f"Metric {metric.name} Target,{metric.target_value:.1f}")
            
            # Add even more detail for detailed reports
            if level_of_detail == "detailed" and metric.change_percentage is not None:
                lines.append(f"Metric {metric.name} Change Percentage,{metric.change_percentage:.1f}")
        
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
        
        # Session metadata and additional data for detailed reports
        if level_of_detail == "detailed":
            if analysis_result.session_metadata:
                for key, value in analysis_result.session_metadata.model_dump().items():
                    if key != "message_history":  # Skip message history to avoid huge reports
                        if isinstance(value, str):
                            value = value.replace('"', '""')
                            lines.append(f"Session Metadata {key},\"{value}\"")
                        else:
                            lines.append(f"Session Metadata {key},{value}")
            
            if analysis_result.additional_data:
                for key, value in analysis_result.additional_data.items():
                    if isinstance(value, str):
                        value = value.replace('"', '""')
                        lines.append(f"Additional Data {key},\"{value}\"")
                    else:
                        lines.append(f"Additional Data {key},{value}")
        
        return "\n".join(lines)
