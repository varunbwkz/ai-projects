#!/usr/bin/env python3
"""
Validation script for process guide JSON files
This script validates all process JSON files in the processes directory 
to ensure they follow the required format.
"""

import os
import json
import glob
import sys
from typing import Dict, List, Any, Optional

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSES_DIR = SCRIPT_DIR

# Define required fields
REQUIRED_FIELDS = {
    "simple": ["title", "description", "keywords", "steps"],
    "complex": ["title", "description", "keywords", "sections"]
}

def validate_process_file(file_path: str) -> List[str]:
    """Validate a single process file and return any errors."""
    errors = []
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON in {file_path}: {str(e)}"]
    except Exception as e:
        return [f"Error reading {file_path}: {str(e)}"]
    
    # Determine if this is a simple or complex process
    process_type = "simple" if "steps" in data else "complex"
    
    # Check required fields
    for field in REQUIRED_FIELDS[process_type]:
        if field not in data:
            errors.append(f"Missing required field '{field}' in {file_path}")
    
    # Validate title and description
    if "title" in data and not isinstance(data["title"], str):
        errors.append(f"Title must be a string in {file_path}")
    
    if "description" in data and not isinstance(data["description"], str):
        errors.append(f"Description must be a string in {file_path}")
    
    # Validate keywords
    if "keywords" in data:
        if not isinstance(data["keywords"], list):
            errors.append(f"Keywords must be a list in {file_path}")
        elif not all(isinstance(k, str) for k in data["keywords"]):
            errors.append(f"All keywords must be strings in {file_path}")
        elif len(data["keywords"]) < 3:
            errors.append(f"At least 3 keywords are recommended in {file_path}")
    
    # Validate steps for simple process
    if process_type == "simple" and "steps" in data:
        if not isinstance(data["steps"], list):
            errors.append(f"Steps must be a list in {file_path}")
        elif not all(isinstance(s, str) for s in data["steps"]):
            errors.append(f"All steps must be strings in {file_path}")
        elif len(data["steps"]) < 2:
            errors.append(f"At least 2 steps are recommended in {file_path}")
    
    # Validate sections for complex process
    if process_type == "complex" and "sections" in data:
        if not isinstance(data["sections"], list):
            errors.append(f"Sections must be a list in {file_path}")
        else:
            for i, section in enumerate(data["sections"]):
                if not isinstance(section, dict):
                    errors.append(f"Section {i+1} must be an object in {file_path}")
                    continue
                
                if "name" not in section:
                    errors.append(f"Missing 'name' in section {i+1} in {file_path}")
                
                if "steps" not in section:
                    errors.append(f"Missing 'steps' in section {i+1} in {file_path}")
                elif not isinstance(section["steps"], list):
                    errors.append(f"Steps must be a list in section {i+1} in {file_path}")
                elif not all(isinstance(s, str) for s in section["steps"]):
                    errors.append(f"All steps must be strings in section {i+1} in {file_path}")
    
    # Validate prerequisites if present
    if "prerequisites" in data:
        if not isinstance(data["prerequisites"], list):
            errors.append(f"Prerequisites must be a list in {file_path}")
        elif not all(isinstance(p, str) for p in data["prerequisites"]):
            errors.append(f"All prerequisites must be strings in {file_path}")
    
    return errors

def validate_all_processes() -> Dict[str, List[str]]:
    """Validate all process files and return errors by file."""
    all_errors = {}
    
    # Find all JSON files
    process_files = glob.glob(os.path.join(PROCESSES_DIR, '**', '*.json'), recursive=True)
    
    for file_path in process_files:
        errors = validate_process_file(file_path)
        if errors:
            rel_path = os.path.relpath(file_path, PROCESSES_DIR)
            all_errors[rel_path] = errors
    
    return all_errors

def main():
    """Main validation function."""
    print(f"Validating process files in {PROCESSES_DIR}...")
    
    all_errors = validate_all_processes()
    
    if not all_errors:
        print("✅ All process files are valid!")
        return 0
    
    print("\n❌ Validation errors found:")
    for file_path, errors in all_errors.items():
        print(f"\n{file_path}:")
        for error in errors:
            print(f"  - {error}")
    
    print(f"\nFound errors in {len(all_errors)} file(s). Please fix these issues.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
