import os
import json
import glob
import logging
from dotenv import load_dotenv
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Brandworkz credentials
BRANDWORKZ_URL = os.getenv("BRANDWORKZ_URL", "")
BRANDWORKZ_USERNAME = os.getenv("BRANDWORKZ_USERNAME", "")
BRANDWORKZ_PASSWORD = os.getenv("BRANDWORKZ_PASSWORD", "")

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Vector store enabled flag
USE_VECTOR_STORE = os.getenv("USE_VECTOR_STORE", "True").lower() == "true"
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    'data', 
    'vector_db'
))

# App settings
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Define process instructions for common tasks
# This dictionary will be populated from JSON files
PROCESS_INSTRUCTIONS = {}
PROCESS_KEYWORDS = {}
PROCESS_EMBEDDINGS = {}  # New dictionary to store embeddings

# Path to the processes directory
PROCESSES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'processes')
logger.info(f"Loading processes from: {PROCESSES_DIR}")

# Initialize vector store if enabled
vector_store = None
if USE_VECTOR_STORE:
    try:
        from src.vector_store import VectorStore
        vector_store = VectorStore(persist_directory=VECTOR_DB_PATH)
        if not vector_store.is_initialized:
            logger.warning("Vector store initialization failed, falling back to in-memory embeddings")
            USE_VECTOR_STORE = False
        else:
            logger.info(f"Vector store initialized with {vector_store.count()} processes")
    except ImportError as e:
        logger.error(f"ChromaDB not installed or other import error: {e}")
        logger.error("Falling back to in-memory embeddings")
        USE_VECTOR_STORE = False
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        logger.error("Falling back to in-memory embeddings")
        USE_VECTOR_STORE = False

def generate_embedding(text):
    """Generate embedding for text using OpenAI's embedding model"""
    try:
        # For OpenAI 1.0.0+
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None

def load_processes_from_files():
    """
    Load process instructions from JSON files in the processes directory
    """
    global PROCESS_INSTRUCTIONS, PROCESS_KEYWORDS, PROCESS_EMBEDDINGS
    
    # Clear existing process instructions and keywords
    PROCESS_INSTRUCTIONS = {}
    PROCESS_KEYWORDS = {}
    PROCESS_EMBEDDINGS = {}
    
    # Clear vector store if enabled
    if USE_VECTOR_STORE and vector_store:
        try:
            vector_store.clear()
            logger.info("Cleared vector store")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
    
    # Find all JSON files in the processes directory and its subdirectories
    process_files = glob.glob(os.path.join(PROCESSES_DIR, '**', '*.json'), recursive=True)
    
    for file_path in process_files:
        try:
            with open(file_path, 'r') as f:
                process_data = json.load(f)
                
            # Get process name from filename (without extension)
            process_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Store the process data
            if 'steps' in process_data:
                # Simple process with just steps
                PROCESS_INSTRUCTIONS[process_name] = process_data['steps']
            else:
                # Complex process with structured data
                PROCESS_INSTRUCTIONS[process_name] = process_data
                
            # Store the keywords for matching
            if 'keywords' in process_data:
                PROCESS_KEYWORDS[process_name] = process_data['keywords']
            
            # Add to vector store if enabled
            if USE_VECTOR_STORE and vector_store and vector_store.is_initialized:
                success = vector_store.add_process(process_name, process_data)
                if not success:
                    logger.warning(f"Failed to add process {process_name} to vector store, generating in-memory embedding instead")
                    # Fall back to in-memory embedding
                    embedding_text = process_data.get('title', '') + ' ' + process_data.get('description', '')
                    if 'keywords' in process_data:
                        embedding_text += ' ' + ' '.join(process_data['keywords'])
                    
                    if embedding_text:
                        embedding = generate_embedding(embedding_text)
                        if embedding:
                            PROCESS_EMBEDDINGS[process_name] = embedding
            else:
                # Generate and store embedding for in-memory approach
                embedding_text = process_data.get('title', '') + ' ' + process_data.get('description', '')
                if 'keywords' in process_data:
                    embedding_text += ' ' + ' '.join(process_data['keywords'])
                
                if embedding_text:
                    embedding = generate_embedding(embedding_text)
                    if embedding:
                        PROCESS_EMBEDDINGS[process_name] = embedding
                
            logger.info(f"Loaded process: {process_name}")
                
        except Exception as e:
            logger.error(f"Error loading process file {file_path}: {e}")
    
    logger.info(f"Loaded {len(PROCESS_INSTRUCTIONS)} processes from files")
    
    if USE_VECTOR_STORE and vector_store and vector_store.is_initialized:
        logger.info(f"Added {vector_store.count()} processes to vector store")
    else:
        logger.info(f"Generated embeddings for {len(PROCESS_EMBEDDINGS)} processes")

# Load processes when this module is imported
load_processes_from_files()

# New helper function to support enhanced process guides
def get_formatted_process_guide(process_name):
    """
    Get a formatted process guide with rich structure for complex processes.
    
    Args:
        process_name: Name of the process
        
    Returns:
        Formatted string with the process guide or None if not found
    """
    process = PROCESS_INSTRUCTIONS.get(process_name)
    
    if not process:
        return None
        
    # Handle simple list-based process instructions
    if isinstance(process, list):
        formatted_steps = []
        for i, step in enumerate(process):
            # Format with the number followed by the step in a way that makes it clear these are exact instructions
            formatted_steps.append(f"Step {i+1}: {step}")
        
        # Join with double newlines for better spacing between steps
        return "\n\n".join(formatted_steps)
        
    # Handle complex structured process instructions
    if isinstance(process, dict):
        result = []
        
        # Add description if available
        if 'description' in process:
            result.append(f"{process['description']}")
            result.append("")  # Add an empty line after description
            
        # Add prerequisites if any
        if 'prerequisites' in process:
            result.append("### Prerequisites")
            result.append("")  # Add an empty line after header
            for prereq in process['prerequisites']:
                result.append(f"- {prereq}")
            result.append("")  # Add an empty line for spacing
                
        # Add sections
        if 'sections' in process:
            for i, section in enumerate(process['sections']):
                section_name = section.get('name', f'Section {i+1}')
                result.append(f"### {section_name}")
                result.append("")  # Add empty line after section header
                
                # Add steps as a properly formatted numbered list
                if 'steps' in section:
                    for j, step in enumerate(section['steps']):
                        # Use standard markdown numbered list format
                        result.append(f"{j+1}. {step}")
                    result.append("")  # Add spacing between steps and notes
                
                # Add notes if any
                if 'notes' in section:
                    result.append(f"**Note:** {section['notes']}")
                    result.append("")  # Add spacing after notes
                    
                # Add tips if any
                if 'tips' in section:
                    result.append(f"**Tip:** {section['tips']}")
                    result.append("")  # Add spacing after tips
                    
                # Add troubleshooting if any
                if 'troubleshooting' in section:
                    result.append("**Troubleshooting:**")
                    result.append("")  # Add empty line after troubleshooting header
                    for issue in section['troubleshooting']:
                        result.append(f"- {issue}")
                    result.append("")  # Add spacing after troubleshooting
                
                result.append("")  # Add extra spacing between sections
        
        # Join with single newline since we've already added empty lines
        return "\n".join(result)
        
    return None

def get_process_keywords():
    """
    Get the process keywords mapping for use in matching queries.
    
    Returns:
        Dictionary mapping process names to keyword lists
    """
    return PROCESS_KEYWORDS

def get_process(process_name):
    """Get a process by name"""
    return PROCESS_INSTRUCTIONS.get(process_name)

def search_processes_vector(query, top_k=3):
    """
    Search for processes using vector similarity
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        List of process names and scores
    """
    try:
        if USE_VECTOR_STORE and vector_store and vector_store.is_initialized:
            # Use vector store for search
            results = vector_store.query(query, n_results=top_k)
            
            # Transform the results to match the expected format
            transformed_results = []
            for result in results:
                # Convert distance to similarity (1.0 - distance)
                similarity = 1.0 - result.get('distance', 0.0)
                
                transformed_results.append({
                    'process_id': result.get('id'),
                    'similarity': similarity,
                    'metadata': result  # Include the original metadata for potential use
                })
                
            return transformed_results
        else:
            # Use in-memory embeddings
            query_embedding = generate_embedding(query)
            if not query_embedding:
                return []
            
            results = []
            for process_name, embedding in PROCESS_EMBEDDINGS.items():
                from src.ai_engine import AIEngine
                # Reuse the cosine similarity function from AIEngine
                similarity = AIEngine._cosine_similarity(AIEngine, query_embedding, embedding)
                results.append({
                    'process_id': process_name,
                    'similarity': similarity
                })
            
            # Sort by similarity and get top_k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
    except Exception as e:
        logger.error(f"Error in search_processes_vector: {e}")
        return []
