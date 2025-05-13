"""Analysis Manager for Smart Steps AI."""

from typing import Dict, List, Optional, Union

from smart_steps_ai.config import ConfigManager
from smart_steps_ai.session import SessionManager  
from smart_steps_ai.provider import ProviderManager
from smart_steps_ai.utils.logging import setup_logger
from .analyzer import SessionAnalyzer
from .models import AnalysisResult, InsightCategory
from .insight_generator import InsightGenerator
from .reporting import ReportGenerator
from .visualization import VisualizationManager

# Configure logging
logger = setup_logger(__name__)

class AnalysisManager:
    """
    Manager for analysis operations.
    
    This class coordinates the components of the analysis system, including
    session analysis, insight generation, and reporting.
    """
    
    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        session_manager: Optional[SessionManager] = None,
        provider_manager: Optional[ProviderManager] = None,
    ):
        """
        Initialize the analysis manager.
        
        Args:
            config_manager (Optional[ConfigManager]): Configuration manager
            session_manager (Optional[SessionManager]): Session manager
            provider_manager (Optional[ProviderManager]): Provider manager
        """
        self.logger = logger
        self.config_manager = config_manager or ConfigManager()
        self.session_manager = session_manager or SessionManager()
        self.provider_manager = provider_manager or ProviderManager()
        
        # Initialize analysis components
        self.session_analyzer = SessionAnalyzer()
        self.insight_generator = InsightGenerator()
        self.report_generator = ReportGenerator()
        self.visualization_manager = VisualizationManager()
        
        self.logger.debug("Initialized analysis manager")
    
    async def analyze_session(
        self, 
        session_id: str,
        categories: Optional[List[Union[str, InsightCategory]]] = None,
        generate_report: bool = False
    ) -> AnalysisResult:
        """
        Analyze a session and generate insights.
        
        Args:
            session_id (str): ID of the session to analyze
            categories (Optional[List[Union[str, InsightCategory]]]): Insight categories to include
            generate_report (bool): Whether to generate a report
            
        Returns:
            AnalysisResult: Results of the analysis
            
        Raises:
            ValueError: If the session is not found
        """
        # Get the session
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        # Analyze the session
        self.logger.info(f"Analyzing session {session_id}")
        analysis = await self.session_analyzer.analyze_session(session)
        
        # Generate insights
        if categories:
            # Convert string categories to enum if needed
            enum_categories = []
            for category in categories:
                if isinstance(category, str):
                    try:
                        enum_categories.append(InsightCategory(category))
                    except ValueError:
                        self.logger.warning(f"Invalid insight category: {category}")
                else:
                    enum_categories.append(category)
            
            # Filter insights by category
            analysis.insights = [
                insight for insight in analysis.insights 
                if insight.category in enum_categories
            ]
        
        # Generate report if requested
        if generate_report:
            report = self.report_generator.generate_report(analysis)
            analysis.report = report
        
        return analysis
    
    def get_analysis(self, session_id: str) -> Optional[AnalysisResult]:
        """
        Get the analysis results for a session.
        
        Args:
            session_id (str): ID of the session
            
        Returns:
            Optional[AnalysisResult]: Analysis results or None if not found
        """
        # This would normally fetch from a persistence layer
        # For now, just analyze again
        try:
            return self.session_analyzer.get_cached_analysis(session_id)
        except KeyError:
            self.logger.warning(f"No cached analysis found for session {session_id}")
            return None
    
    def generate_visualization(
        self, 
        analysis: AnalysisResult,
        visualization_type: str
    ) -> Dict:
        """
        Generate a visualization for analysis results.
        
        Args:
            analysis (AnalysisResult): Analysis results
            visualization_type (str): Type of visualization
            
        Returns:
            Dict: Visualization data
        """
        return self.visualization_manager.generate_visualization(
            analysis, visualization_type
        )
