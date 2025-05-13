"""Test the SessionAnalyzer class."""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.smart_steps_ai.analysis import SessionAnalyzer
from src.smart_steps_ai.analysis.models import ReportFormat
from src.smart_steps_ai.memory import MemoryManager
from src.smart_steps_ai.persistence import PersistenceManager
from src.smart_steps_ai.persona import PersonaManager
from src.smart_steps_ai.session import SessionManager
from src.smart_steps_ai.session.models import MessageRole


class TestSessionAnalyzer(unittest.TestCase):
    """Test the SessionAnalyzer class."""

    def setUp(self):
        """Set up the test environment."""
        # Create a test directory for persistence
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        
        # Initialize persistence manager with test directory
        self.persistence_manager = PersistenceManager(base_dir=self.test_dir)
        
        # Initialize managers
        self.persona_manager = PersonaManager()
        self.session_manager = SessionManager(
            persistence_manager=self.persistence_manager,
            persona_manager=self.persona_manager,
        )
        self.memory_manager = MemoryManager()
        
        # Initialize session analyzer
        self.analyzer = SessionAnalyzer(
            session_manager=self.session_manager,
            memory_manager=self.memory_manager,
            persona_manager=self.persona_manager,
        )
        
        # Test client name
        self.client_name = "Test Analyzer Client"
        
        # Create a test session
        self.session = self.session_manager.create_session(client_name=self.client_name)
        
        # Add some messages to the session
        self.session_manager.add_message(
            session_id=self.session.id,
            role=MessageRole.SYSTEM,
            content="Session started.",
        )
        
        self.session_manager.add_message(
            session_id=self.session.id,
            role=MessageRole.ASSISTANT,
            content="Hello! How are you feeling today?",
        )
        
        self.session_manager.add_message(
            session_id=self.session.id,
            role=MessageRole.CLIENT,
            content="I'm feeling a bit stressed about work, but otherwise okay.",
        )
        
        self.session_manager.add_message(
            session_id=self.session.id,
            role=MessageRole.ASSISTANT,
            content="I understand work can be stressful. Could you tell me more about what's causing you stress?",
        )
        
        self.session_manager.add_message(
            session_id=self.session.id,
            role=MessageRole.CLIENT,
            content="I have a big project due next week and I'm worried I won't finish it in time.",
        )

    def tearDown(self):
        """Clean up the test environment."""
        # Clean up test data
        sessions_dir = self.test_dir / "sessions"
        if sessions_dir.exists():
            for file in sessions_dir.glob("*.json"):
                file.unlink()
        
        metadata_dir = self.test_dir / "session_metadata"
        if metadata_dir.exists():
            for file in metadata_dir.glob("*.json"):
                file.unlink()
        
        analysis_dir = self.test_dir / "analysis"
        if analysis_dir.exists():
            for file in analysis_dir.glob("*.json"):
                file.unlink()

    def test_analyze_session(self):
        """Test analyzing a session."""
        # Analyze the session
        result = self.analyzer.analyze_session(self.session.id)
        
        # Verify analysis result
        self.assertIsNotNone(result, "Analysis result is None")
        self.assertEqual(result.session_id, self.session.id)
        self.assertEqual(result.client_name, self.client_name)
        
        # Check summary
        self.assertIsNotNone(result.summary, "Summary is None")
        self.assertTrue(len(result.summary) > 0, "Summary is empty")
        
        # Check insights
        self.assertTrue(len(result.insights) > 0, "No insights generated")
        
        # Check metrics
        self.assertTrue(len(result.metrics) > 0, "No metrics calculated")
        
        print(f"Successfully analyzed session {self.session.id}")
        print(f"Summary: {result.summary[:100]}...")
        print(f"Generated {len(result.insights)} insights and {len(result.metrics)} metrics")

    def test_generate_reports(self):
        """Test generating reports in different formats."""
        # Analyze the session
        result = self.analyzer.analyze_session(self.session.id)
        
        # Generate reports in different formats
        formats = [
            ReportFormat.TEXT,
            ReportFormat.MARKDOWN,
            ReportFormat.HTML,
            ReportFormat.JSON,
            ReportFormat.CSV,
        ]
        
        for format in formats:
            # Generate the report
            report = self.analyzer.generate_report(result, format)
            
            # Verify report
            self.assertIsNotNone(report, f"Report is None for format {format}")
            self.assertTrue(len(report) > 0, f"Report is empty for format {format}")
            
            print(f"Generated {format.value} report ({len(report)} characters)")
            
            # Write the report to a file for inspection
            report_file = self.test_dir / f"test_report.{format.value}"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            
            print(f"Saved report to {report_file}")


if __name__ == "__main__":
    unittest.main()
