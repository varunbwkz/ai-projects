"""
Process Recommender for Brandworkz AI Agent

This module provides functionality to recommend related processes
based on semantic similarity and common usage patterns.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from config.config import generate_embedding, PROCESS_INSTRUCTIONS, PROCESS_EMBEDDINGS
from src.analytics import analytics

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcessRecommender:
    """Provides recommendations for related processes."""
    
    def __init__(self):
        """Initialize the process recommender."""
        self.process_cache = {}
        self._load_processes()
    
    def _load_processes(self) -> None:
        """Load all processes for recommendation."""
        self.process_cache = {}
        
        # Find all process files
        processes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'processes')
        
        for root, _, files in os.walk(processes_dir):
            for filename in files:
                if filename.endswith(".json") and filename != "navigate_to.json":
                    try:
                        file_path = os.path.join(root, filename)
                        process_id = os.path.splitext(filename)[0]
                        
                        with open(file_path, 'r') as f:
                            process_data = json.load(f)
                            
                        # Add to cache
                        self.process_cache[process_id] = {
                            "title": process_data.get("title", ""),
                            "description": process_data.get("description", ""),
                            "keywords": process_data.get("keywords", []),
                            "category": os.path.basename(root) if os.path.basename(root) != "processes" else "other"
                        }
                    except Exception as e:
                        logger.error(f"Error loading process {filename}: {e}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
            
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)
    
    def _get_process_embedding(self, process_id: str) -> Optional[List[float]]:
        """Get embedding for a process."""
        # Check if embedding already exists
        if process_id in PROCESS_EMBEDDINGS:
            return PROCESS_EMBEDDINGS[process_id]
        
        # Generate new embedding
        if process_id in self.process_cache:
            process = self.process_cache[process_id]
            text = process["title"] + " " + process["description"]
            if process["keywords"]:
                text += " " + " ".join(process["keywords"])
            
            embedding = generate_embedding(text)
            if embedding:
                PROCESS_EMBEDDINGS[process_id] = embedding
                return embedding
        
        return None
    
    def get_related_processes(self, process_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get related processes based on semantic similarity and usage patterns.
        
        Args:
            process_id: Process ID to find related processes for
            limit: Maximum number of recommendations to return
            
        Returns:
            List of related process dictionaries with score and reason
        """
        if process_id not in self.process_cache:
            return []
        
        target_process = self.process_cache[process_id]
        target_category = target_process["category"]
        
        results = []
        
        # Get embedding for target process
        target_embedding = self._get_process_embedding(process_id)
        
        # Calculate similarity scores for all processes
        similarity_scores = {}
        category_matches = {}
        keyword_overlap = {}
        
        for pid, process in self.process_cache.items():
            if pid == process_id:
                continue
            
            # Calculate semantic similarity if embeddings are available
            score = 0.0
            if target_embedding:
                process_embedding = self._get_process_embedding(pid)
                if process_embedding:
                    score = self._cosine_similarity(target_embedding, process_embedding)
            
            similarity_scores[pid] = score
            
            # Check if in same category
            if process["category"] == target_category:
                category_matches[pid] = True
            
            # Calculate keyword overlap
            if "keywords" in target_process and "keywords" in process:
                target_keywords = set(target_process["keywords"])
                process_keywords = set(process["keywords"])
                overlap = len(target_keywords.intersection(process_keywords))
                if overlap > 0:
                    keyword_overlap[pid] = overlap
        
        # Get popular processes from analytics
        popular_processes = {
            item["process"]: item["count"] 
            for item in analytics.get_popular_processes(limit=10)
        }
        
        # Scoring
        process_scores = []
        for pid, process in self.process_cache.items():
            if pid == process_id:
                continue
            
            # Base score is semantic similarity (0-1)
            score = similarity_scores.get(pid, 0.0)
            
            # Add bonus for same category (0.2)
            if pid in category_matches:
                score += 0.2
            
            # Add bonus for keyword overlap (0.1 per keyword, max 0.3)
            overlap = keyword_overlap.get(pid, 0)
            score += min(overlap * 0.1, 0.3)
            
            # Add bonus for popularity (0.1 for being in top 10)
            if pid in popular_processes:
                score += 0.1
            
            # Determine reason for recommendation
            reason = "Related process"
            if pid in category_matches:
                reason = "Same category"
            elif overlap > 0:
                reason = f"Similar keywords ({overlap} common)"
            
            process_scores.append({
                "process_id": pid,
                "title": process["title"],
                "description": process["description"][:100] + "..." if len(process["description"]) > 100 else process["description"],
                "category": process["category"],
                "score": score,
                "reason": reason
            })
        
        # Sort by score descending
        process_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top N recommendations
        return process_scores[:limit]

# Singleton instance
recommender = ProcessRecommender()
