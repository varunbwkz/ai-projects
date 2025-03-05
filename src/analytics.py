"""
Process Analytics for Brandworkz AI Agent

This module provides functionality to track and analyze user interactions
with the AI agent, particularly which processes users are searching for.
"""

import os
import json
import logging
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcessAnalytics:
    """Class for tracking and analyzing process usage metrics."""
    
    def __init__(self, analytics_file: str = None):
        """
        Initialize the analytics tracker.
        
        Args:
            analytics_file: Path to the JSON file for storing analytics data
        """
        self.analytics_file = analytics_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'process_analytics.json'
        )
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.analytics_file), exist_ok=True)
        
        # Load existing analytics data or initialize new data
        self.analytics_data = self._load_analytics()
    
    def _load_analytics(self) -> Dict[str, Any]:
        """
        Load analytics data from the JSON file.
        
        Returns:
            Dictionary containing analytics data
        """
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading analytics data: {e}")
        
        # Return default structure if file doesn't exist or loading fails
        return {
            "process_requests": {},
            "daily_stats": {},
            "unmatched_queries": []
        }
    
    def _save_analytics(self) -> bool:
        """
        Save analytics data to the JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.analytics_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
            return False
    
    def track_process_request(self, query: str, matched_process: Optional[str] = None) -> None:
        """
        Track a process request from a user.
        
        Args:
            query: The user's original query
            matched_process: The process that was matched, or None if no match
        """
        # Get today's date as string
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Initialize daily stats if needed
        if today not in self.analytics_data["daily_stats"]:
            self.analytics_data["daily_stats"][today] = {
                "total_requests": 0,
                "matched_requests": 0,
                "unmatched_requests": 0,
                "processes": {}
            }
        
        # Update daily stats
        self.analytics_data["daily_stats"][today]["total_requests"] += 1
        
        if matched_process:
            # Update matched process stats
            if matched_process not in self.analytics_data["process_requests"]:
                self.analytics_data["process_requests"][matched_process] = {
                    "count": 0,
                    "queries": []
                }
            
            # Update overall process count
            self.analytics_data["process_requests"][matched_process]["count"] += 1
            
            # Add query to list (limit to 100 most recent)
            queries = self.analytics_data["process_requests"][matched_process]["queries"]
            queries.append({"query": query, "timestamp": datetime.now().isoformat()})
            self.analytics_data["process_requests"][matched_process]["queries"] = queries[-100:]
            
            # Update daily process stats
            if matched_process not in self.analytics_data["daily_stats"][today]["processes"]:
                self.analytics_data["daily_stats"][today]["processes"][matched_process] = 0
            self.analytics_data["daily_stats"][today]["processes"][matched_process] += 1
            
            # Increment matched count
            self.analytics_data["daily_stats"][today]["matched_requests"] += 1
        else:
            # Track unmatched query
            self.analytics_data["unmatched_queries"].append({
                "query": query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only the 100 most recent unmatched queries
            self.analytics_data["unmatched_queries"] = self.analytics_data["unmatched_queries"][-100:]
            
            # Increment unmatched count
            self.analytics_data["daily_stats"][today]["unmatched_requests"] += 1
        
        # Save updated analytics
        self._save_analytics()
    
    def get_popular_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequently requested processes.
        
        Args:
            limit: Maximum number of processes to return
            
        Returns:
            List of dictionaries with process name and count
        """
        processes = []
        
        for process_name, data in self.analytics_data["process_requests"].items():
            processes.append({
                "process": process_name,
                "count": data["count"]
            })
        
        # Sort by count in descending order
        return sorted(processes, key=lambda x: x["count"], reverse=True)[:limit]
    
    def get_daily_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get daily statistics for the specified number of recent days.
        
        Args:
            days: Number of recent days to include
            
        Returns:
            Dictionary with daily statistics
        """
        # Sort dates in descending order
        sorted_dates = sorted(self.analytics_data["daily_stats"].keys(), reverse=True)
        
        # Get stats for the specified number of days
        recent_stats = {}
        for date in sorted_dates[:days]:
            recent_stats[date] = self.analytics_data["daily_stats"][date]
        
        return recent_stats
    
    def get_unmatched_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent unmatched queries.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of unmatched queries with timestamps
        """
        return self.analytics_data["unmatched_queries"][-limit:]
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive analytics report.
        
        Returns:
            Dictionary with report data
        """
        # Get total request count
        total_requests = sum(
            day_stats["total_requests"] 
            for day_stats in self.analytics_data["daily_stats"].values()
        )
        
        # Get total matched and unmatched counts
        matched_requests = sum(
            day_stats["matched_requests"] 
            for day_stats in self.analytics_data["daily_stats"].values()
        )
        
        unmatched_requests = sum(
            day_stats["unmatched_requests"] 
            for day_stats in self.analytics_data["daily_stats"].values()
        )
        
        # Calculate match rate
        match_rate = (matched_requests / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "matched_requests": matched_requests,
            "unmatched_requests": unmatched_requests,
            "match_rate": round(match_rate, 2),
            "popular_processes": self.get_popular_processes(),
            "recent_daily_stats": self.get_daily_stats(),
            "recent_unmatched": self.get_unmatched_queries()
        }

# Singleton instance for use throughout the application
analytics = ProcessAnalytics()
