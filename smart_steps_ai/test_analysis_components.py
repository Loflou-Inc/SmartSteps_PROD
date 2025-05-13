"""Test script for the analysis module components."""

import os
import sys
from pathlib import Path
import datetime
import json
import base64
from io import BytesIO

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import the visualization and reporting modules directly
from src.smart_steps_ai.analysis.visualization import VisualizationManager
from src.smart_steps_ai.analysis.reporting import ReportGenerator
from src.smart_steps_ai.analysis.models import AnalysisResult, InsightCategory, ProgressMetric, Insight, ReportFormat

def test_visualization():
    """Test the visualization functionality."""
    print("\n===== Testing Visualization =====")
    
    # Create visualization manager
    visualization_manager = VisualizationManager()
    
    # Create test metrics
    metrics = [
        {
            "name": "Engagement",
            "description": "Level of client engagement in session",
            "value": 7.5,
            "previous_value": 6.0,
            "target_value": 9.0
        },
        {
            "name": "Anxiety",
            "description": "Reported anxiety level",
            "value": 8.0,
            "previous_value": 9.0,
            "target_value": 5.0
        },
        {
            "name": "Focus",
            "description": "Ability to maintain focus",
            "value": 5.5,
            "previous_value": 4.0,
            "target_value": 7.0
        }
    ]
    
    # Create test insights
    insights = [
        {
            "text": "Client shows patterns of perfectionism when discussing work projects",
            "category": "cognitive",
            "confidence": 0.85
        },
        {
            "text": "Client appears to avoid starting tasks that seem overwhelming",
            "category": "behavioral",
            "confidence": 0.9
        },
        {
            "text": "Client expresses anxiety primarily in physical symptoms like freezing up",
            "category": "emotional",
            "confidence": 0.75
        },
        {
            "text": "Client has insight into the connection between procrastination and anxiety",
            "category": "cognitive",
            "confidence": 0.8
        }
    ]
    
    # Create test themes
    themes = [
        "Work Stress",
        "Procrastination",
        "Perfectionism",
        "Anxiety",
        "Cognitive Blocks"
    ]
    
    # Create output directory
    output_dir = Path("./output/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate visualizations
    print(f"Generating visualizations...")
    
    try:
        # Progress chart
        progress_chart = visualization_manager.create_progress_chart(metrics)
        with open(output_dir / "progress_chart.png", "wb") as f:
            f.write(base64.b64decode(progress_chart))
        print(f"- Created progress chart")
        
        # Radar chart
        radar_chart = visualization_manager.create_metrics_radar_chart(metrics)
        with open(output_dir / "radar_chart.png", "wb") as f:
            f.write(base64.b64decode(radar_chart))
        print(f"- Created radar chart")
        
        # Insight category chart
        category_chart = visualization_manager.create_insight_category_chart(insights)
        with open(output_dir / "category_chart.png", "wb") as f:
            f.write(base64.b64decode(category_chart))
        print(f"- Created insight category chart")
        
        # Theme pie chart
        theme_chart = visualization_manager.create_theme_pie_chart(themes)
        with open(output_dir / "theme_chart.png", "wb") as f:
            f.write(base64.b64decode(theme_chart))
        print(f"- Created theme pie chart")
        
        # Confidence distribution chart
        confidence_chart = visualization_manager.create_confidence_distribution_chart(insights)
        with open(output_dir / "confidence_chart.png", "wb") as f:
            f.write(base64.b64decode(confidence_chart))
        print(f"- Created confidence distribution chart")
        
        print(f"Visualizations saved to {output_dir}")
        return True
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        return False

def test_reporting():
    """Test the report generation functionality."""
    print("\n===== Testing Report Generation =====")
    
    # Create sample insights
    insights = [
        Insight(
            text="Client shows patterns of perfectionism when discussing work projects",
            category=InsightCategory.COGNITIVE,
            confidence=0.85
        ),
        Insight(
            text="Client appears to avoid starting tasks that seem overwhelming",
            category=InsightCategory.BEHAVIORAL,
            confidence=0.9
        ),
        Insight(
            text="Client expresses anxiety primarily in physical symptoms",
            category=InsightCategory.EMOTIONAL,
            confidence=0.75
        )
    ]
    
    # Create sample metrics
    metrics = [
        ProgressMetric(
            name="Engagement",
            description="Level of client engagement in session",
            value=7.5,
            previous_value=6.0,
            target_value=9.0
        ),
        ProgressMetric(
            name="Anxiety",
            description="Reported anxiety level",
            value=8.0,
            previous_value=9.0,
            target_value=5.0
        )
    ]
    
    # Calculate changes
    for metric in metrics:
        metric.calculate_changes()
    
    # Create sample themes
    themes = [
        "Work Stress",
        "Procrastination",
        "Perfectionism",
        "Anxiety"
    ]
    
    # Create sample recommendations
    recommendations = [
        "Explore breaking down tasks into smaller steps",
        "Practice mindfulness techniques for anxiety",
        "Develop a structured approach to task initiation"
    ]
    
    # Create sample next steps
    next_steps = [
        "Schedule follow-up session within one week",
        "Client to practice task decomposition daily",
        "Review homework at next session"
    ]
    
    # Create an analysis result
    analysis_result = AnalysisResult(
        session_id="test-session-001",
        client_name="Test Client",
        persona_name="Test Therapist",
        summary="The client discussed anxiety related to work tasks, particularly around starting large projects. They showed insight into their patterns of procrastination followed by panic.",
        insights=insights,
        metrics=metrics,
        themes=themes,
        recommendations=recommendations,
        next_steps=next_steps
    )
    
    # Create report generator
    report_generator = ReportGenerator()
    
    # Create output directory
    output_dir = Path("./output/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Generate reports in different formats
        formats = [
            ReportFormat.TEXT,
            ReportFormat.MARKDOWN,
            ReportFormat.HTML
            # JSON and CSV handling will need custom datetime handling
        ]
        
        print(f"Generating reports in {len(formats)} formats...")
        report_paths = {}
        
        for format in formats:
            # Generate report
            report = report_generator.generate_report(
                analysis_result=analysis_result,
                format=format,
                include_visualizations=(format != ReportFormat.TEXT and format != ReportFormat.CSV),
                level_of_detail="standard"
            )
            
            # Save report
            filename = f"report_{format.value}.{format.value}"
            if format == ReportFormat.HTML:
                filename = f"report_{format.value}.html"
            elif format == ReportFormat.JSON:
                filename = f"report_{format.value}.json"
                
            report_path = output_dir / filename
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
                
            report_paths[format.value] = report_path
            print(f"- Generated {format.value} report")
        
        # Print the report paths
        print(f"\nGenerated Reports:")
        for format_name, report_path in report_paths.items():
            print(f"  {format_name}: {report_path}")
        
        return True
    except Exception as e:
        print(f"Error generating reports: {e}")
        return False

if __name__ == "__main__":
    viz_success = test_visualization()
    report_success = test_reporting()
    
    if viz_success and report_success:
        print("\nAll tests completed successfully!")
    else:
        print("\nSome tests failed. Check the output for details.")
