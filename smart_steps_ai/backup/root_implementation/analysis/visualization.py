"""
Visualization utilities for the Smart Steps AI module.

Provides functions for creating charts and visualizations for
sentiment analysis, progress tracking, and other metrics.
"""

def create_sentiment_chart(sentiment_data, output_path):
    """
    Create a chart visualizing sentiment trends.
    
    Args:
        sentiment_data: Dictionary with sentiment analysis data
        output_path: Path to save the chart image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Extract data
        progression = sentiment_data['progression']
        positions = [entry['position'] for entry in progression]
        scores = [entry['score'] for entry in progression]
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Plot sentiment scores
        plt.plot(positions, scores, 'o-', color='#3498db', linewidth=2)
        
        # Add trendline
        z = np.polyfit(positions, scores, 1)
        p = np.poly1d(z)
        plt.plot(positions, p(positions), "r--", alpha=0.7)
        
        # Add horizontal line at neutral sentiment
        plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        
        # Fill areas
        plt.fill_between(positions, scores, 0, where=[s > 0 for s in scores], 
                         color='#a8e6cf', alpha=0.3, interpolate=True)
        plt.fill_between(positions, scores, 0, where=[s <= 0 for s in scores], 
                         color='#ffaaa5', alpha=0.3, interpolate=True)
        
        # Add labels and title
        plt.xlabel('Message Position in Conversation')
        plt.ylabel('Sentiment Score (-1 to 1)')
        plt.title('Sentiment Progression Throughout Session')
        
        # Add annotations for sentiment levels
        plt.text(positions[-1] + 0.3, 0.8, 'Positive', color='#2ecc71', ha='left')
        plt.text(positions[-1] + 0.3, 0, 'Neutral', color='gray', ha='left')
        plt.text(positions[-1] + 0.3, -0.8, 'Negative', color='#e74c3c', ha='left')
        
        # Customize
        plt.grid(True, alpha=0.3)
        plt.ylim(-1.1, 1.1)
        
        # Add overall trend info
        plt.figtext(0.5, 0.01, sentiment_data['overall']['trend'], 
                   ha='center', fontsize=10, bbox={'facecolor':'#f9f9f9', 'alpha':0.8, 'pad':5})
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    except ImportError:
        print("Matplotlib is required for chart generation.")
        return False
    
    except Exception as e:
        print(f"Error creating sentiment chart: {str(e)}")
        return False

def create_progress_charts(sessions, output_path):
    """
    Create charts visualizing progress across multiple sessions.
    
    Args:
        sessions: List of session objects to analyze
        output_path: Path to save the chart image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
        import numpy as np
        from datetime import datetime, timedelta
        
        # Sort sessions by date
        sessions = sorted(sessions, key=lambda s: s.created_at)
        
        # Extract session dates and message counts
        dates = [s.created_at for s in sessions]
        message_counts = []
        client_ratios = []
        sentiments = []
        
        for session in sessions:
            if hasattr(session, 'messages') and session.messages:
                total = len(session.messages)
                client = sum(1 for msg in session.messages if msg.is_user)
                message_counts.append(total)
                client_ratios.append(client / total if total > 0 else 0)
                
                # Calculate simple sentiment
                from smart_steps_ai.analysis.insights import analyze_sentiment_trends
                sentiment_data = analyze_sentiment_trends(session)
                if sentiment_data and 'overall' in sentiment_data:
                    sentiments.append(sentiment_data['overall']['average'])
                else:
                    sentiments.append(0)
            else:
                message_counts.append(0)
                client_ratios.append(0)
                sentiments.append(0)
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(12, 12))
        gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])
        
        # Convert dates to numbers for plotting
        date_nums = [date.toordinal() for date in dates]
        x_labels = [date.strftime('%Y-%m-%d') for date in dates]
        
        # 1. Engagement chart (message count)
        ax1 = plt.subplot(gs[0])
        ax1.bar(date_nums, message_counts, color='#3498db', alpha=0.7)
        ax1.set_title('Engagement Level by Session')
        ax1.set_ylabel('Message Count')
        ax1.set_xticks(date_nums)
        ax1.set_xticklabels(x_labels, rotation=45, ha='right')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add trendline
        z = np.polyfit(range(len(message_counts)), message_counts, 1)
        p = np.poly1d(z)
        ax1.plot(date_nums, p(range(len(message_counts))), "r--", alpha=0.7)
        
        # 2. Client participation ratio
        ax2 = plt.subplot(gs[1])
        ax2.bar(date_nums, [r * 100 for r in client_ratios], color='#2ecc71', alpha=0.7)
        ax2.set_title('Client Participation Ratio')
        ax2.set_ylabel('Client Messages (%)')
        ax2.set_xticks(date_nums)
        ax2.set_xticklabels(x_labels, rotation=45, ha='right')
        ax2.set_ylim(0, 100)
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Sentiment progression
        ax3 = plt.subplot(gs[2])
        ax3.plot(date_nums, sentiments, 'o-', color='#9b59b6', linewidth=2)
        ax3.set_title('Sentiment Progression Across Sessions')
        ax3.set_ylabel('Average Sentiment (-1 to 1)')
        ax3.set_xticks(date_nums)
        ax3.set_xticklabels(x_labels, rotation=45, ha='right')
        ax3.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        ax3.set_ylim(-1, 1)
        ax3.grid(True, alpha=0.3)
        
        # Fill sentiment areas
        ax3.fill_between(date_nums, sentiments, 0, where=[s > 0 for s in sentiments], 
                        color='#a8e6cf', alpha=0.3, interpolate=True)
        ax3.fill_between(date_nums, sentiments, 0, where=[s <= 0 for s in sentiments], 
                        color='#ffaaa5', alpha=0.3, interpolate=True)
        
        # Add overall summary
        avg_messages = sum(message_counts) / len(message_counts) if message_counts else 0
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        sentiment_trend = "Improving" if sentiments[-1] > sentiments[0] else "Declining" if sentiments[-1] < sentiments[0] else "Stable"
        
        summary = (f"Sessions: {len(sessions)}  |  "
                f"Avg. Messages: {avg_messages:.1f}  |  "
                f"Avg. Sentiment: {avg_sentiment:.2f}  |  "
                f"Sentiment Trend: {sentiment_trend}")
        
        plt.figtext(0.5, 0.01, summary, ha='center', fontsize=10, 
                   bbox={'facecolor':'#f9f9f9', 'alpha':0.8, 'pad':5})
        
        # Save figure
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.4, bottom=0.1)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    except ImportError:
        print("Matplotlib is required for chart generation.")
        return False
    
    except Exception as e:
        print(f"Error creating progress charts: {str(e)}")
        return False

def create_theme_visualization(themes, output_path):
    """
    Create a visualization of key themes.
    
    Args:
        themes: List of (theme, score) tuples
        output_path: Path to save the visualization
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import matplotlib.pyplot as plt
        
        # Extract data
        theme_names = [t for t, _ in themes]
        theme_scores = [s for _, s in themes]
        
        # Create horizontal bar chart
        plt.figure(figsize=(10, 6))
        
        # Sort by score
        sorted_indices = sorted(range(len(theme_scores)), key=lambda i: theme_scores[i])
        theme_names = [theme_names[i] for i in sorted_indices]
        theme_scores = [theme_scores[i] for i in sorted_indices]
        
        # Create bars with gradient colors
        colors = plt.cm.viridis(np.linspace(0.3, 1, len(theme_names)))
        plt.barh(theme_names, theme_scores, color=colors, alpha=0.8)
        
        # Add labels and title
        plt.xlabel('Relevance Score')
        plt.title('Key Themes Identified')
        
        # Customize
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        # Save figure
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return True
    
    except ImportError:
        print("Matplotlib is required for visualization generation.")
        return False
    
    except Exception as e:
        print(f"Error creating theme visualization: {str(e)}")
        return False
