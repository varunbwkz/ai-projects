#!/usr/bin/env python
"""
Test script for the Brandworkz API endpoints.
This script is used to test the search_assets API endpoint.
"""

import os
import sys
import json
import requests
import argparse

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_search_assets(query, base_url="http://localhost:8000"):
    """Test the search_assets API endpoint."""
    try:
        print(f"Testing search_assets API endpoint with query: '{query}'")
        
        # Define the API endpoint URL
        url = f"{base_url}/api/search_assets"
        
        # Define the request payload
        payload = {
            "query": query,
            "max_results": 20
        }
        
        # Make the POST request to the API
        response = requests.post(url, json=payload)
        
        # Print the response status code
        print(f"Response status code: {response.status_code}")
        
        # Parse the JSON response
        data = response.json()
        
        # Print a formatted version of the response
        print("\nAPI Response:")
        print(json.dumps(data, indent=2))
        
        # Print a summary of the results
        if data.get("success", False):
            print(f"\nSearch successful!")
            print(f"Message: {data.get('message', 'No message')}")
            print(f"Found {len(data.get('results', []))} assets")
            print(f"Search source: {data.get('source', 'Unknown')}")
            
            # Print details of each asset
            for i, asset in enumerate(data.get("results", []), 1):
                print(f"\nAsset {i}:")
                print(f"- ID: {asset.get('id', 'No ID')}")
                print(f"- Name: {asset.get('name', 'No name')}")
                print(f"- Type: {asset.get('type', 'Unknown type')}")
                print(f"- Size: {asset.get('file_size', 'Unknown size')}")
                print(f"- Description: {asset.get('description', 'No description')}")
                print(f"- Thumbnail: {asset.get('thumbnail_url', 'No thumbnail')}")
        else:
            print(f"\nSearch failed!")
            print(f"Message: {data.get('message', 'No error message')}")
            
        return data
        
    except Exception as e:
        print(f"Error testing API: {str(e)}")
        return {"success": False, "message": str(e)}

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Test the Brandworkz API endpoints.')
    parser.add_argument('query', help='Search query to test')
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL of the API')
    
    args = parser.parse_args()
    
    test_search_assets(args.query, args.url)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
