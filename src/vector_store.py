import os
import json
import logging
import traceback
import numpy as np
from typing import List, Dict, Any, Optional, Union

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector database for semantic search of processes"""
    
    def __init__(self, persist_directory: str = None):
        """
        Initialize the vector store
        
        Args:
            persist_directory: Directory to persist the database (optional)
        """
        self.is_initialized = False
        
        if persist_directory is None:
            # Use default path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            persist_directory = os.path.join(base_dir, 'data', 'vector_db')
            
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
            
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Set up embedding function
            openai_api_key = os.getenv("OPENAI_API_KEY")
            self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-ada-002"
            )
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="brandworkz_processes",
                embedding_function=self.embedding_function
            )
            
            self.is_initialized = True
            logger.info(f"Vector store initialized with collection 'brandworkz_processes' at {persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
    
    def _prepare_metadata(self, data: Dict[str, Any]) -> Dict[str, Union[str, int, float, bool]]:
        """Prepare metadata for storage by converting complex types to JSON strings"""
        prepared_data = {}
        for key, value in data.items():
            # Convert lists and dictionaries to JSON strings
            if isinstance(value, (list, dict)):
                prepared_data[key] = json.dumps(value)
            # Keep primitive types as they are
            elif isinstance(value, (str, int, float, bool)) or value is None:
                prepared_data[key] = value
            else:
                # Convert other types to strings
                prepared_data[key] = str(value)
        
        return prepared_data
    
    def _parse_metadata(self, metadata):
        """Parse metadata into a format suitable for ChromaDB"""
        if not metadata:
            return {}  # Return empty dict if metadata is None
            
        parsed = {}
        for key, value in metadata.items():
            # Convert all values to strings for ChromaDB
            if isinstance(value, (list, dict)):
                parsed[key] = json.dumps(value)
            else:
                parsed[key] = str(value)
        return parsed
    
    def add_process(self, process_id: str, process_data: Dict[str, Any]) -> bool:
        """
        Add a process to the vector store
        
        Args:
            process_id: Unique ID for the process
            process_data: Dictionary with process data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_initialized:
            logger.error("Cannot add process - vector store not initialized")
            return False
            
        try:
            # Prepare document for embedding
            document_text = f"{process_data.get('title', '')} {process_data.get('description', '')}"
            
            # Prepare metadata (convert lists/dicts to strings)
            metadata = self._prepare_metadata(process_data)
            
            # Check if process already exists and delete it
            try:
                self.collection.get(ids=[process_id])
                self.collection.delete(ids=[process_id])
                logger.info(f"Replacing existing process {process_id} in vector store")
            except:
                pass
                
            # Add to collection
            self.collection.add(
                ids=[process_id],
                documents=[document_text],
                metadatas=[metadata]
            )
            
            logger.info(f"Added process {process_id} to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding process {process_id} to vector store: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the vector store for similar processes
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            
        Returns:
            List of process IDs and scores
        """
        if not self.is_initialized:
            logger.error("Cannot query - vector store not initialized")
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            if results and len(results['metadatas']) > 0:
                # Parse metadata back into original format
                parsed_results = []
                for metadata, document, id, distance in zip(
                    results['metadatas'][0],
                    results['documents'][0],
                    results['ids'][0],
                    results['distances'][0]
                ):
                    parsed_metadata = self._parse_metadata(metadata)
                    parsed_metadata['id'] = id
                    parsed_metadata['distance'] = distance
                    parsed_results.append(parsed_metadata)
                
                return parsed_results
            return []
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def clear(self) -> bool:
        """Clear the vector store"""
        if not self.is_initialized:
            logger.error("Vector store not initialized")
            return False
            
        try:
            # Get all IDs in the collection
            all_items = self.collection.get()
            if all_items and 'ids' in all_items and all_items['ids']:
                # Delete items by IDs
                self.collection.delete(ids=all_items['ids'])
                logger.info(f"Cleared vector store - removed {len(all_items['ids'])} items")
            else:
                logger.info("Vector store is already empty")
            return True
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def count(self) -> int:
        """
        Get the number of processes in the vector store
        
        Returns:
            Number of processes in the store, or 0 if error
        """
        if not self.is_initialized:
            logger.error("Cannot count - vector store not initialized")
            return 0
            
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error counting entries in vector store: {e}")
            return 0
            
    def get_process(self, process_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific process from the vector store by ID
        
        Args:
            process_id: The ID of the process to retrieve
            
        Returns:
            Process metadata if found, None otherwise
        """
        if not self.is_initialized:
            logger.error("Cannot get process - vector store not initialized")
            return None
            
        try:
            result = self.collection.get(ids=[process_id])
            
            if result and len(result['metadatas']) > 0:
                # Parse metadata back into original format
                metadata = self._parse_metadata(result['metadatas'][0])
                return metadata
            return None
        except Exception as e:
            logger.error(f"Error getting process {process_id} from vector store: {e}")
            return None
