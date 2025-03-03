#!/usr/bin/env python
"""
Vector Database Diagnostic Tool

This script helps diagnose and fix issues with the vector database setup.
"""

import os
import sys
import logging
import argparse
import json
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vectordb-diagnostics")

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        "chromadb",
        "openai",
        "numpy"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            logger.error(f"❌ {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_api_key():
    """Check if the OpenAI API key is set"""
    logger.info("Checking OpenAI API key...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("❌ OPENAI_API_KEY is not set in environment or .env file")
        return False
    
    logger.info("✅ OPENAI_API_KEY is set")
    return True

def test_embedding_generation():
    """Test if embedding generation works"""
    logger.info("Testing embedding generation...")
    
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input="Hello world"
        )
        
        embedding = response['data'][0]['embedding']
        
        if embedding and len(embedding) > 0:
            logger.info(f"✅ Embedding generation works (vector dimension: {len(embedding)})")
            return True
        else:
            logger.error("❌ Embedding generation failed - empty embedding")
            return False
    except Exception as e:
        logger.error(f"❌ Embedding generation failed: {e}")
        return False

def test_vector_store():
    """Test if the vector store works"""
    logger.info("Testing vector store functionality...")
    
    try:
        from src.vector_store import VectorStore
        
        # Create test directory
        test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_vector_db')
        os.makedirs(test_dir, exist_ok=True)
        
        # Initialize vector store
        vector_store = VectorStore(persist_directory=test_dir)
        
        if not vector_store.is_initialized:
            logger.error("❌ Vector store initialization failed")
            return False
        
        # Test adding a process
        test_process = {
            'title': 'Test Process',
            'description': 'This is a test process',
            'keywords': ['test', 'vector', 'database'],
            'steps': ['Step 1: Do this first', 'Step 2: Then do this', 'Step 3: Finally do this']
        }
        
        # Add process to vector store
        result = vector_store.add_process('test_process', test_process)
        if not result:
            logger.error("❌ Failed to add test process to vector store")
            return False
        
        logger.info("✅ Successfully added test process to vector store")
        
        # Test retrieving process
        retrieved_process = vector_store.get_process('test_process')
        if not retrieved_process:
            logger.error("❌ Failed to retrieve test process from vector store")
            return False
            
        # Verify keywords and steps were properly preserved
        if isinstance(retrieved_process.get('keywords'), list) and len(retrieved_process.get('keywords', [])) == 3:
            logger.info("✅ Successfully retrieved keywords as a list from vector store")
        else:
            logger.warning(f"⚠️ Keywords were not properly preserved: {retrieved_process.get('keywords')}")
            
        if isinstance(retrieved_process.get('steps'), list) and len(retrieved_process.get('steps', [])) == 3:
            logger.info("✅ Successfully retrieved steps as a list from vector store")
        else:
            logger.warning(f"⚠️ Steps were not properly preserved: {retrieved_process.get('steps')}")
        
        # Test querying
        query_results = vector_store.query("test vector", n_results=1)
        
        if not query_results or len(query_results) == 0:
            logger.error("❌ Vector store query returned no results")
            return False
        
        logger.info(f"✅ Vector store query successful: {json.dumps(query_results[0], indent=2)}")
        
        # Clean up
        vector_store.clear()
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
        
        return True
    except Exception as e:
        logger.error(f"❌ Vector store test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def repair_database():
    """Attempt to repair the vector database"""
    logger.info("Attempting to repair vector database...")
    
    try:
        # Get the vector store path from config
        from config.config import VECTOR_DB_PATH
        
        if os.path.exists(VECTOR_DB_PATH):
            logger.info(f"Found vector database at {VECTOR_DB_PATH}")
            
            # Backup the existing database
            backup_path = VECTOR_DB_PATH + "_backup"
            import shutil
            
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path, ignore_errors=True)
                
            shutil.copytree(VECTOR_DB_PATH, backup_path)
            logger.info(f"✅ Created backup at {backup_path}")
            
            # Clear the existing database
            shutil.rmtree(VECTOR_DB_PATH, ignore_errors=True)
            logger.info(f"✅ Cleared existing database at {VECTOR_DB_PATH}")
            
            # Recreate directory
            os.makedirs(VECTOR_DB_PATH, exist_ok=True)
            
            # Reload the processes
            from config.config import load_processes_from_files
            load_processes_from_files()
            
            logger.info("✅ Repaired and reloaded the vector database")
            return True
        else:
            logger.info(f"Vector database directory doesn't exist at {VECTOR_DB_PATH}")
            
            # Create the directory
            os.makedirs(VECTOR_DB_PATH, exist_ok=True)
            
            # Load the processes
            from config.config import load_processes_from_files
            load_processes_from_files()
            
            logger.info("✅ Created and loaded a new vector database")
            return True
    except Exception as e:
        logger.error(f"❌ Database repair failed: {e}")
        return False

def test_search():
    """Test searching for processes"""
    logger.info("Testing process search...")
    
    try:
        # Import config
        from config.config import search_processes_vector
        
        # Test queries
        test_queries = [
            "How do I upload a file?",
            "What is the process for metadata management?",
            "I need to search for assets"
        ]
        
        for query in test_queries:
            results = search_processes_vector(query, top_k=1)
            
            if results and len(results) > 0:
                process_id = results[0]['process_id']
                similarity = results[0]['similarity']
                logger.info(f"✅ Query: '{query}' => Process: '{process_id}' (similarity: {similarity:.2f})")
            else:
                logger.warning(f"⚠️ Query: '{query}' => No matching process found")
        
        return True
    except Exception as e:
        logger.error(f"❌ Search test failed: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Vector Database Diagnostic Tool')
    parser.add_argument('--repair', action='store_true', help='Attempt to repair the vector database')
    parser.add_argument('--test-search', action='store_true', help='Test searching for processes')
    
    args = parser.parse_args()
    
    logger.info("Running vector database diagnostics...")
    
    # Always run dependency check
    dependencies_ok = check_dependencies()
    
    # Always check API key
    api_key_ok = check_api_key()
    
    if not dependencies_ok or not api_key_ok:
        logger.error("❌ Basic requirements check failed. Please fix the issues before continuing.")
        return 1
    
    # Test embedding generation
    embedding_ok = test_embedding_generation()
    
    if not embedding_ok:
        logger.error("❌ Embedding generation failed. Please check your API key and network connection.")
        return 1
    
    # Test vector store
    vectorstore_ok = test_vector_store()
    
    if args.repair:
        repair_result = repair_database()
        if repair_result:
            logger.info("✅ Database repair completed successfully")
        else:
            logger.error("❌ Database repair failed")
            return 1
    
    if args.test_search:
        search_ok = test_search()
        if search_ok:
            logger.info("✅ Search functionality working properly")
        else:
            logger.error("❌ Search functionality test failed")
            return 1
    
    if vectorstore_ok:
        logger.info("✅ All vector database diagnostics passed!")
    else:
        logger.warning("⚠️ Some vector database tests failed. Consider running with --repair option.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
