import requests
import logging
from bs4 import BeautifulSoup
import json
import os
from typing import Dict, List, Optional, Any, Union
import base64
from io import BytesIO
from PIL import Image

from config.config import BRANDWORKZ_URL, BRANDWORKZ_USERNAME, BRANDWORKZ_PASSWORD

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrandworkzClient:
    """Client for interacting with the Brandworkz platform."""
    
    def __init__(self, url: str = BRANDWORKZ_URL, username: str = BRANDWORKZ_USERNAME, password: str = BRANDWORKZ_PASSWORD):
        """Initialize the Brandworkz client with credentials."""
        self.base_url = url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.authenticated = False
    
    def login(self) -> bool:
        """
        Authenticate with the Brandworkz system.
        
        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        try:
            login_url = f"{self.base_url}j_spring_security_check"
            payload = {
                'j_username': self.username,
                'j_password': self.password
            }
            
            response = self.session.post(login_url, data=payload)
            
            if response.status_code == 200 and not "login-error" in response.text:
                self.authenticated = True
                logger.info("Successfully authenticated with Brandworkz")
                return True
            else:
                logger.error(f"Failed to authenticate: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def ensure_authenticated(self) -> bool:
        """Ensure the client is authenticated before making requests."""
        if not self.authenticated:
            return self.login()
        return True
    
    def search_documents(self, query: str, document_type: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for documents in the Brandworkz system.
        
        Args:
            query: The search query
            document_type: Filter by document type (e.g., "image", "pdf")
            max_results: Maximum number of results to return
            
        Returns:
            List of document metadata
        """
        if not self.ensure_authenticated():
            return []
            
        try:
            search_url = f"{self.base_url}api/search"
            
            params = {
                'q': query,
                'limit': max_results,
            }
            
            if document_type:
                params['type'] = document_type
                
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                search_results = response.json()
                logger.info(f"Found {len(search_results.get('results', []))} results for query: {query}")
                return search_results.get('results', [])
            else:
                logger.error(f"Search failed: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    def get_document(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific document.
        
        Args:
            asset_id: The ID of the document
            
        Returns:
            Document metadata or None if not found
        """
        if not self.ensure_authenticated():
            return None
            
        try:
            asset_url = f"{self.base_url}api/assets/{asset_id}"
            response = self.session.get(asset_url)
            
            if response.status_code == 200:
                asset_data = response.json()
                logger.info(f"Retrieved document: {asset_id}")
                return asset_data
            else:
                logger.error(f"Failed to get document {asset_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting document {asset_id}: {str(e)}")
            return None
    
    def download_document(self, asset_id: str, save_path: Optional[str] = None) -> Optional[bytes]:
        """
        Download a document from Brandworkz.
        
        Args:
            asset_id: The ID of the document to download
            save_path: Path to save the document (if None, return bytes)
            
        Returns:
            Document bytes if save_path is None, otherwise None
        """
        if not self.ensure_authenticated():
            return None
            
        try:
            download_url = f"{self.base_url}api/assets/{asset_id}/download"
            response = self.session.get(download_url, stream=True)
            
            if response.status_code == 200:
                if save_path:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    logger.info(f"Downloaded document {asset_id} to {save_path}")
                    return None
                else:
                    content = response.content
                    logger.info(f"Downloaded document {asset_id} to memory")
                    return content
            else:
                logger.error(f"Failed to download document {asset_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading document {asset_id}: {str(e)}")
            return None
