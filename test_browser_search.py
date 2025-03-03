#!/usr/bin/env python
"""
Test script for Brandworkz browser automation search.
This script can be run independently to test the browser automation search functionality.
"""

import os
import sys
import asyncio
import argparse
import logging
from dotenv import load_dotenv

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('browser_search_test.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_browser_search(query, debug=False, validate_asset=None):
    """Test the browser automation search with a query."""
    try:
        from src.brandworkz import BrandworkzClient
        
        logger.info("Initializing Brandworkz client...")
        client = BrandworkzClient()
        
        # Monkey patch the browser launch function to set headless=False when in debug mode
        if debug:
            original_search_method = client.search_asset_with_browser_automation
            
            async def debug_search_method(query, max_retries=3, validate_asset_name=None):
                from playwright.async_api import async_playwright
                
                async with async_playwright() as p:
                    # Override to make browser visible in debug mode
                    browser = await p.chromium.launch(
                        headless=False,  # Make browser visible
                        args=['--no-sandbox', '--disable-setuid-sandbox'],
                        timeout=60000
                    )
                    
                    # Continue with rest of method
                    context = await browser.new_context(
                        viewport={'width': 1280, 'height': 800},
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
                    )
                    
                    # Rest of the original method...
                    logger.info("Debug mode: browser will be visible")
                    await browser.close()
                    
                # Fall back to the original method with our parameters
                return await original_search_method(query, max_retries, validate_asset_name)
                
            # Replace the method temporarily
            client.search_asset_with_browser_automation = debug_search_method
        
        logger.info(f"Searching for query: {query}" + 
                   (f" with validation for asset: {validate_asset}" if validate_asset else ""))
        
        # Call the search method with the validation parameter if provided
        results = await client.search_asset_with_browser_automation(
            query, 
            validate_asset_name=validate_asset
        )
        
        print(f"Search results: {results}")
        
        # Check validation results if validation was requested
        if validate_asset and results.get('validation'):
            validation = results['validation']
            if validation.get('visible_on_page'):
                logger.info(f"✓ Asset '{validate_asset}' was found visible on the page")
            else:
                logger.warning(f"✗ Asset '{validate_asset}' was NOT found visible on the page")
                
            if validation.get('in_processed_results'):
                logger.info(f"✓ Asset '{validate_asset}' was found in processed results")
            else:
                logger.warning(f"✗ Asset '{validate_asset}' was NOT found in processed results")
        
        return results
    except Exception as e:
        logger.error(f"Error in test_browser_search: {str(e)}")
        return {"success": False, "message": str(e), "results": []}

def main():
    parser = argparse.ArgumentParser(description='Test browser automation search')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--visible', action='store_true', help='Make browser visible')
    parser.add_argument('--validate', help='Specific asset name to validate in results')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.info("Debug mode enabled")
    
    if args.visible:
        os.environ['PLAYWRIGHT_VISIBLE'] = '1'
        logger.info("Browser set to visible mode")
    
    # Run the async test function
    results = asyncio.run(test_browser_search(args.query, args.debug, args.validate))
    
    print(f"\nSearch Summary:")
    print(f"- Success: {results.get('success', False)}")
    print(f"- Message: {results.get('message', 'No message')}")
    print(f"- Found {len(results.get('results', []))} assets")
    
    for i, asset in enumerate(results.get('results', [])):
        print(f"\nAsset {i+1}:")
        print(f"- ID: {asset.get('id', 'No ID')}")
        print(f"- Name: {asset.get('name', 'No name')}")
        print(f"- Thumbnail: {asset.get('thumbnail_url', 'No thumbnail')}")
        print(f"- Description: {asset.get('description', 'No description')}")
    
    # Print validation results if available
    if args.validate and results.get('validation'):
        print(f"\nValidation Results for '{args.validate}':")
        validation = results['validation']
        print(f"- Visible on page: {validation.get('visible_on_page')}")
        print(f"- Found in processed results: {validation.get('in_processed_results')}")
    
    # Return success status for exit code
    return 0 if results.get('success', False) else 1

if __name__ == "__main__":
    main()
