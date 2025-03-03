#!/usr/bin/env python3
"""
Test Query for Brandworkz AI Agent Vector Store

This script allows testing of vector store queries
to check semantic search functionality.
"""

import os
import logging
from dotenv import load_dotenv
from src.vector_store import VectorStore

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('vector-query-test')

def test_query(query_text, n_results=3):
    """
    Test a query against the vector store
    
    Args:
        query_text: The text to query for
        n_results: Number of results to return
    """
    try:
        vector_store = VectorStore()
        
        if not vector_store.is_initialized:
            logger.error("Vector store initialization failed")
            return
        
        logger.info(f"Querying vector store for: '{query_text}'")
        results = vector_store.query(query_text, n_results=n_results)
        
        if not results:
            logger.warning("No results found")
            return
        
        logger.info(f"Found {len(results)} matching processes:")
        
        for i, result in enumerate(results):
            # Calculate similarity score (1.0 - distance)
            similarity = 1.0 - result.get('distance', 0.0)
            similarity_percent = similarity * 100
            
            print(f"\n--- Match #{i+1}: {result.get('id')} (Similarity: {similarity_percent:.1f}%) ---")
            print(f"Title: {result.get('title', 'N/A')}")
            print(f"Description: {result.get('description', 'N/A')}")
            
            # Print keywords if available
            if 'keywords' in result:
                print(f"Keywords: {', '.join(result['keywords'])}")
            
            # Print the first few steps if available
            if 'steps' in result and isinstance(result['steps'], list):
                print("\nFirst steps:")
                for j, step in enumerate(result['steps'][:3]):
                    print(f"  {j+1}. {step}")
                if len(result['steps']) > 3:
                    print(f"  ... and {len(result['steps']) - 3} more steps")
            
            print(f"Distance: {result.get('distance', 'N/A')}")
            print("-" * 80)
    
    except Exception as e:
        logger.error(f"Error querying vector store: {e}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Test queries
    print("\n=== TEST QUERY RESULTS ===\n")
    
    # Try a few different queries
    test_query("How do I share assets with other users?")
    test_query("I need to add metadata to my assets")
    test_query("searching for images in the system")
