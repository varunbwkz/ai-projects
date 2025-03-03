#!/usr/bin/env python3
"""
Bulk Process Loader for Brandworkz AI Agent

This script loads all process files from the processes directory
and adds them to the ChromaDB vector store.
"""

import os
import json
import glob
import logging
import argparse
from typing import Dict, Any, List
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('process-loader')

def load_process_files(processes_dir: str) -> Dict[str, Dict[str, Any]]:
    """
    Load all process files from the specified directory
    
    Args:
        processes_dir: Directory containing process JSON files
        
    Returns:
        Dictionary mapping process IDs to process data
    """
    processes = {}
    
    # Find all JSON files in the processes directory and subdirectories
    process_files = glob.glob(os.path.join(processes_dir, '**', '*.json'), recursive=True)
    
    if not process_files:
        logger.warning(f"No process files found in {processes_dir}")
        return processes
    
    logger.info(f"Found {len(process_files)} process files")
    
    for file_path in process_files:
        try:
            with open(file_path, 'r') as f:
                process_data = json.load(f)
                
            # Get process name from filename (without extension)
            process_id = os.path.splitext(os.path.basename(file_path))[0]
            
            # Store the process data
            processes[process_id] = process_data
            logger.info(f"Loaded process '{process_id}' from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading process file {file_path}: {e}")
    
    return processes

def add_processes_to_vector_store(processes: Dict[str, Dict[str, Any]]) -> int:
    """
    Add processes to the vector store
    
    Args:
        processes: Dictionary mapping process IDs to process data
        
    Returns:
        Number of processes successfully added
    """
    try:
        from src.vector_store import VectorStore
        
        vector_store = VectorStore()
        
        if not vector_store.is_initialized:
            logger.error("Vector store initialization failed")
            return 0
        
        # Clear existing content if requested
        if args.clear:
            logger.info("Clearing vector store before loading processes")
            vector_store.clear()
        
        # Track successful additions
        successful = 0
        
        # Add processes to vector store
        for process_id, process_data in processes.items():
            try:
                if vector_store.add_process(process_id, process_data):
                    successful += 1
                    logger.info(f"Added process '{process_id}' to vector store")
                else:
                    logger.warning(f"Failed to add process '{process_id}' to vector store")
            except Exception as e:
                logger.error(f"Error adding process '{process_id}' to vector store: {e}")
        
        logger.info(f"Successfully added {successful}/{len(processes)} processes to vector store")
        return successful
    
    except ImportError as e:
        logger.error(f"Could not import VectorStore: {e}")
        return 0
    
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        return 0

def load_and_report_processes() -> None:
    """
    Load processes from files and report statistics
    """
    # Get the processes directory path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processes_dir = os.path.join(base_dir, 'processes')
    
    # Check if custom directory was specified
    if args.processes_dir:
        if os.path.isdir(args.processes_dir):
            processes_dir = args.processes_dir
        else:
            logger.error(f"Specified processes directory does not exist: {args.processes_dir}")
            return
    
    logger.info(f"Loading processes from {processes_dir}")
    
    # Load processes from files
    processes = load_process_files(processes_dir)
    
    if not processes:
        logger.warning("No processes were loaded from files")
        return
    
    logger.info(f"Loaded {len(processes)} processes from files")
    
    # Add to vector store if enabled
    if not args.no_vector_store:
        added = add_processes_to_vector_store(processes)
        if added > 0:
            logger.info(f"Added {added} processes to vector store")
        else:
            logger.warning("No processes were added to vector store")
    else:
        logger.info("Skipping vector store integration (--no-vector-store flag used)")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Bulk load processes into vector store')
    parser.add_argument('--processes-dir', help='Directory containing process JSON files')
    parser.add_argument('--clear', action='store_true', help='Clear vector store before loading')
    parser.add_argument('--no-vector-store', action='store_true', help='Skip adding to vector store')
    
    args = parser.parse_args()
    
    # Load and report process data
    load_and_report_processes()
