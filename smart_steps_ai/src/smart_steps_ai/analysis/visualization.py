"""Data visualization utilities for analysis reports."""

import os
import base64
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class VisualizationManager:
    """
    Manager for creating visualizations from analysis data.
    
    This class provides methods for generating various types of visualizations
    from session analysis results, including progress charts, theme distributions,
    and insight breakdowns.
    """

    def __init__(self, theme_style: str = 'default'):
        """
        Initialize the visualization manager.

        Args:
            theme_style (str): Matplotlib style to use (default: 'default')
        """
        # Use a standard style
        if theme_style != 'default':
            try:
                plt.style.use(theme_style)
            except Exception as e:
                print(f"Warning: Style '{theme_style}' not found, using default")
        
        self.default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        
    def create_progress_chart(
        self, 
        metrics: List[Dict[str, Any]], 
        title: str = "Progress Over Time",
        figsize: Tuple[int, int] = (10, 6)
    ) -> str:
        """
        Create a progress chart from metric data.

        Args:
            metrics (List[Dict[str, Any]]): List of metric dictionaries with 'name', 'value',
                'previous_value', and optionally 'target_value'
            title (str): Chart title (default: "Progress Over Time")
            figsize (Tuple[int, int]): Figure size (width, height) in inches (default: (10, 6))

        Returns:
            str: Base64-encoded PNG image
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)
        
        # Prepare data
        names = []
        current_values = []
        previous_values = []
        target_values = []
        has_targets = False
        
        for metric in metrics:
            names.append(metric.get('name', 'Unknown'))
            current_values.append(metric.get('value', 0))
            previous_values.append(metric.get('previous_value', 0))
            
            # Check if target values are available
            if 'target_value' in metric and metric['target_value'] is not None:
                target_values.append(metric['target_value'])
                has_targets = True
            else:
                target_values.append(0)
        
        # Set up the plot
        x = range(len(names))
        width = 0.35
        
        # Plot bars
        current_bars = ax.bar([i - width/2 for i in x], current_values, width, 
                             label='Current', color=self.default_colors[0])
        previous_bars = ax.bar([i + width/2 for i in x], previous_values, width, 
                              label='Previous', color=self.default_colors[1], alpha=0.7)
        
        # Add target markers if available
        if has_targets:
            for i, target in enumerate(target_values):
                if target > 0:
                    ax.plot([i - width, i + width], [target, target], 
                           color=self.default_colors[2], linestyle='--', linewidth=2)
            
            # Add target to legend
            ax.plot([], [], color=self.default_colors[2], linestyle='--', linewidth=2, 
                   label='Target')
        
        # Add value labels on bars
        self._add_value_labels(current_bars)
        self._add_value_labels(previous_bars)
        
        # Customize the plot
        ax.set_ylabel('Score')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend()
        
        # Set y-axis limits with some padding
        max_value = max(max(current_values), max(previous_values), 
                         max(target_values) if has_targets else 0)
        ax.set_ylim(0, max_value * 1.2)
        
        # Adjust layout
        fig.tight_layout()
        
        # Convert to base64
        return self._figure_to_base64(fig)
    
    def create_metrics_radar_chart(
        self, 
        metrics: List[Dict[str, Any]], 
        title: str = "Progress Metrics",
        figsize: Tuple[int, int] = (8, 8)
    ) -> str:
        """
        Create a radar chart for metrics visualization.

        Args:
            metrics (List[Dict[str, Any]]): List of metric dictionaries with 'name', 'value',
                'previous_value', and optionally 'target_value'
            title (str): Chart title (default: "Progress Metrics")
            figsize (Tuple[int, int]): Figure size (width, height) in inches (default: (8, 8))

        Returns:
            str: Base64-encoded PNG image
        """
        # Create figure and axis
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, polar=True)
        
        # Prepare data
        names = []
        current_values = []
        previous_values = []
        target_values = []
        has_previous = False
        has_targets = False
        
        for metric in metrics:
            names.append(metric.get('name', 'Unknown'))
            current_values.append(metric.get('value', 0))
            
            if 'previous_value' in metric and metric['previous_value'] is not None:
                previous_values.append(metric['previous_value'])
                has_previous = True
            else:
                previous_values.append(0)
                
            if 'target_value' in metric and metric['target_value'] is not None:
                target_values.append(metric['target_value'])
                has_targets = True
            else:
                target_values.append(0)
        
        # Number of metrics
        N = len(names)
        
        # Create angle positions
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Add the values for plotting (close the loop)
        current_values += current_values[:1]
        previous_values += previous_values[:1]
        target_values += target_values[:1]
        
        # Add labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(names)
        
        # Draw current values
        ax.plot(angles, current_values, 'o-', linewidth=2, label='Current', 
               color=self.default_colors[0])
        ax.fill(angles, current_values, alpha=0.25, color=self.default_colors[0])
        
        # Draw previous values if available
        if has_previous:
            ax.plot(angles, previous_values, 'o-', linewidth=1.5, label='Previous', 
                   color=self.default_colors[1], alpha=0.7)
            ax.fill(angles, previous_values, alpha=0.1, color=self.default_colors[1])
        
        # Draw target values if available
        if has_targets:
            ax.plot(angles, target_values, '--', linewidth=1.5, label='Target', 
                   color=self.default_colors[2])
        
        # Add legend
        ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        
        # Set chart limits
        max_value = max(max(current_values), 
                         max(previous_values) if has_previous else 0,
                         max(target_values) if has_targets else 0)
        ax.set_ylim(0, max_value * 1.2)
        
        # Set title
        ax.set_title(title, size=15, y=1.1)
        
        # Adjust layout
        fig.tight_layout()
        
        # Convert to base64
        return self._figure_to_base64(fig)
    
    def create_insight_category_chart(
        self, 
        insights: List[Dict[str, Any]], 
        title: str = "Insight Categories",
        figsize: Tuple[int, int] = (10, 6)
    ) -> str:
        """
        Create a chart showing the distribution of insight categories.

        Args:
            insights (List[Dict[str, Any]]): List of insight dictionaries with 'category'
            title (str): Chart title (default: "Insight Categories")
            figsize (Tuple[int, int]): Figure size (width, height) in inches (default: (10, 6))

        Returns:
            str: Base64-encoded PNG image
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)
        
        # Count categories
        category_counts = {}
        for insight in insights:
            category = insight.get('category', 'unknown')
            if isinstance(category, dict) and 'value' in category:
                category = category['value']
                
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Prepare data
        categories = list(category_counts.keys())
        counts = list(category_counts.values())
        
        # Sort by frequency
        sorted_data = sorted(zip(categories, counts), key=lambda x: x[1], reverse=True)
        categories, counts = zip(*sorted_data) if sorted_data else ([], [])
        
        # Create colors
        colors = self.default_colors[:len(categories)]
        
        # Create chart
        bars = ax.bar(categories, counts, color=colors)
        
        # Add value labels
        self._add_value_labels(bars)
        
        # Customize the plot
        ax.set_ylabel('Count')
        ax.set_title(title)
        plt.xticks(rotation=45, ha='right')
        
        # Adjust layout
        fig.tight_layout()
        
        # Convert to base64
        return self._figure_to_base64(fig)
    
    def create_theme_pie_chart(
        self, 
        themes: List[str], 
        title: str = "Session Themes",
        figsize: Tuple[int, int] = (8, 8)
    ) -> str:
        """
        Create a pie chart showing the distribution of themes.

        Args:
            themes (List[str]): List of themes
            title (str): Chart title (default: "Session Themes")
            figsize (Tuple[int, int]): Figure size (width, height) in inches (default: (8, 8))

        Returns:
            str: Base64-encoded PNG image
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)
        
        # Count theme occurrences
        theme_counts = {}
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
        
        # Prepare data
        labels = list(theme_counts.keys())
        counts = list(theme_counts.values())
        
        # Create pie chart
        explode = [0.1 if i == counts.index(max(counts)) else 0 for i in range(len(counts))]
        ax.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, explode=explode,
              shadow=True, colors=plt.cm.tab10.colors[:len(counts)])
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Set title
        ax.set_title(title)
        
        # Adjust layout
        fig.tight_layout()
        
        # Convert to base64
        return self._figure_to_base64(fig)
    
    def create_confidence_distribution_chart(
        self, 
        insights: List[Dict[str, Any]], 
        title: str = "Insight Confidence Distribution",
        figsize: Tuple[int, int] = (10, 6)
    ) -> str:
        """
        Create a histogram showing the distribution of insight confidence scores.

        Args:
            insights (List[Dict[str, Any]]): List of insight dictionaries with 'confidence'
            title (str): Chart title (default: "Insight Confidence Distribution")
            figsize (Tuple[int, int]): Figure size (width, height) in inches (default: (10, 6))

        Returns:
            str: Base64-encoded PNG image
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)
        
        # Extract confidence scores
        confidence_scores = []
        for insight in insights:
            confidence = insight.get('confidence', None)
            if confidence is not None:
                confidence_scores.append(float(confidence))
        
        # Create histogram
        n, bins, patches = ax.hist(confidence_scores, bins=10, alpha=0.7, 
                                   color=self.default_colors[0])
        
        # Customize the plot
        ax.set_xlabel('Confidence Score')
        ax.set_ylabel('Count')
        ax.set_title(title)
        
        # Adjust layout
        fig.tight_layout()
        
        # Convert to base64
        return self._figure_to_base64(fig)
    
    def _add_value_labels(self, bars):
        """
        Add value labels to bar charts.

        Args:
            bars: Bar container from matplotlib
        """
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.,
                height * 1.01,
                f"{height:.1f}",
                ha='center', va='bottom', fontsize=9
            )
    
    def _figure_to_base64(self, fig):
        """
        Convert a matplotlib figure to a base64-encoded PNG.

        Args:
            fig: Matplotlib figure

        Returns:
            str: Base64-encoded PNG
        """
        # Save figure to a BytesIO object
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)  # Close the figure to free memory
        
        # Encode as base64
        buf.seek(0)
        img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return img_data
    
    def save_figure_to_file(self, fig, filename: str) -> str:
        """
        Save a matplotlib figure to a file.

        Args:
            fig: Matplotlib figure
            filename (str): Filename to save to

        Returns:
            str: Path to saved file
        """
        # Create directory if it doesn't exist
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Save figure
        fig.savefig(filename, dpi=100)
        plt.close(fig)  # Close the figure to free memory
        
        return filename
