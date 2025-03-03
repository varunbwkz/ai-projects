import os
import logging
import json
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import glob
import shutil

from src.brandworkz import BrandworkzClient
from src.ai_engine import AIEngine
from config.config import APP_HOST, APP_PORT, DEBUG

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Brandworkz AI Agent", description="An AI assistant for the Brandworkz platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directory for templates and static files
os.makedirs("src/templates", exist_ok=True)
os.makedirs("src/static", exist_ok=True)
os.makedirs("src/static/react", exist_ok=True)

# Set up templates
templates = Jinja2Templates(directory="src/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")
app.mount("/assets", StaticFiles(directory="src/static/react/assets"), name="assets")

# Initialize clients
brandworkz_client = BrandworkzClient()
ai_engine = AIEngine()

# Models for API
class ChatRequest(BaseModel):
    message: str

# class SearchRequest(BaseModel):
#     query: str
#     document_type: Optional[str] = None
#     max_results: int = 20

class ProcessRequest(BaseModel):
    process_name: str

# Models for Process Admin API
class ProcessData(BaseModel):
    title: str
    description: str
    keywords: List[str]
    steps: Optional[List[str]] = None
    troubleshooting: Optional[List[str]] = None
    sections: Optional[List[Dict[str, Any]]] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class ProcessCreateRequest(BaseModel):
    category: str  # e.g., "asset_management", "metadata_management", etc.
    filename: str  # without extension
    data: ProcessData

    class Config:
        orm_mode = True

class ProcessUpdateRequest(BaseModel):
    category: str
    filename: str
    data: ProcessData

    class Config:
        orm_mode = True

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat messages."""
    try:
        # Generate response
        response = ai_engine.generate_response(request.message)
        
        return JSONResponse({
            "response": response,
            "success": True
        })
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return JSONResponse({
            "response": f"Sorry, I encountered an error: {str(e)}",
            "success": False
        })

# @app.post("/api/search")
# async def search(request: SearchRequest):
#     """Search for documents."""
#     try:
#         # Ensure authenticated
#         if not brandworkz_client.ensure_authenticated():
#             return JSONResponse({
#                 "response": "Failed to authenticate with Brandworkz.",
#                 "success": False,
#                 "results": []
#             })
#         
#         # Perform search
#         search_results = brandworkz_client.search_documents(
#             query=request.query,
#             document_type=request.document_type,
#             max_results=request.max_results
#         )
#         
#         # Generate answer based on search results
#         answer = ai_engine.search_answer(request.query, search_results)
#         
#         return JSONResponse({
#             "response": answer,
#             "success": True,
#             "results": search_results
#         })
#     except Exception as e:
#         logger.error(f"Error in search endpoint: {str(e)}")
#         return JSONResponse({
#             "response": f"Sorry, I encountered an error while searching: {str(e)}",
#             "success": False,
#             "results": []
#         })

@app.post("/api/process")
async def process(request: ProcessRequest):
    """Get process instructions."""
    try:
        # Generate process instructions
        instructions = ai_engine.guide_process(request.process_name)
        
        # Check if there's a direct match for the requested process
        if not instructions or "I'm sorry, but I don't have specific information" in instructions:
            # Try to find a match using our keyword matching
            matched_process = ai_engine._match_process(request.process_name)
            if matched_process:
                instructions = ai_engine.guide_process(matched_process)
        
        return JSONResponse({
            "response": instructions,
            "success": True
        })
    except Exception as e:
        logger.error(f"Error in process endpoint: {str(e)}")
        return JSONResponse({
            "response": f"Sorry, I encountered an error: {str(e)}",
            "success": False
        })

# @app.post("/api/download/{asset_id}")
# async def download(asset_id: str):
#     """Download a document."""
#     try:
#         # Ensure authenticated
#         if not brandworkz_client.ensure_authenticated():
#             return JSONResponse({
#                 "response": "Failed to authenticate with Brandworkz.",
#                 "success": False
#             })
#         
#         # Get document metadata
#         document = brandworkz_client.get_document(asset_id)
#         
#         if not document:
#             return JSONResponse({
#                 "response": f"Document with ID {asset_id} not found.",
#                 "success": False
#             })
#         
#         # Get download URL for the document
#         download_url = f"{brandworkz_client.base_url}asset/{asset_id}/download"
#         
#         return JSONResponse({
#             "response": f"Document available for download.",
#             "success": True,
#             "document": document,
#             "download_url": download_url
#         })
#     except Exception as e:
#         logger.error(f"Error in download endpoint: {str(e)}")
#         return JSONResponse({
#             "response": f"Sorry, I encountered an error while downloading: {str(e)}",
#             "success": False
#         })

# Process Admin API Routes
@app.get("/api/admin/processes", response_class=JSONResponse)
async def get_all_processes():
    """Get all available processes organized by category"""
    processes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "processes")
    result = {}
    
    # Skip the README and validation script
    skip_files = ["README.md", "validate_processes.py"]
    
    for category in os.listdir(processes_dir):
        category_path = os.path.join(processes_dir, category)
        
        # Skip if not a directory or if it's a special file
        if not os.path.isdir(category_path) or category in skip_files:
            continue
            
        result[category] = []
        
        # Get all JSON files in this category
        for file_name in os.listdir(category_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(category_path, file_name)
                try:
                    with open(file_path, 'r') as f:
                        process_data = json.load(f)
                    
                    # Add filename (without extension) and data
                    result[category].append({
                        "filename": os.path.splitext(file_name)[0],
                        "data": process_data
                    })
                except Exception as e:
                    logger.error(f"Error reading process file {file_path}: {str(e)}")
    
    return result

@app.post("/api/admin/processes", response_class=JSONResponse)
async def create_process(request: ProcessCreateRequest):
    """Create a new process file"""
    logger.info(f"Creating process: {request.filename} in category {request.category}")
    
    processes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "processes")
    category_dir = os.path.join(processes_dir, request.category)
    
    # Ensure category directory exists
    if not os.path.exists(category_dir):
        logger.error(f"Category directory doesn't exist: {category_dir}")
        return JSONResponse(
            status_code=400,
            content={"error": f"Category '{request.category}' does not exist"}
        )
    
    # Check if file already exists
    file_path = os.path.join(category_dir, f"{request.filename}.json")
    if os.path.exists(file_path):
        logger.error(f"Process file already exists: {file_path}")
        return JSONResponse(
            status_code=400,
            content={"error": f"Process '{request.filename}' already exists in category '{request.category}'"}
        )
    
    # Save the process file
    try:
        # Convert to dictionary
        process_data = request.data.dict(exclude_unset=True)
        logger.info(f"Process data: {process_data}")
        
        with open(file_path, 'w') as f:
            json.dump(process_data, f, indent=2)
        
        logger.info(f"Successfully created process file: {file_path}")
        
        # Reload processes to update vector store
        from config.config import load_processes_from_files
        load_processes_from_files()
        logger.info("Reloaded processes and updated vector store")
        
        return {"message": f"Process '{request.filename}' created successfully"}
    except Exception as e:
        logger.error(f"Error creating process file {file_path}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error creating process file: {str(e)}"}
        )

@app.put("/api/admin/processes/{category}/{filename}", response_class=JSONResponse)
async def update_process(category: str, filename: str, process_data: ProcessData):
    """Update an existing process file"""
    logger.info(f"Updating process: {filename} in category {category}")
    
    processes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "processes")
    file_path = os.path.join(processes_dir, category, f"{filename}.json")
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"Process file doesn't exist: {file_path}")
        return JSONResponse(
            status_code=404,
            content={"error": f"Process '{filename}' not found in category '{category}'"}
        )
    
    # Update the process file
    try:
        # Convert to dictionary
        data_dict = process_data.dict(exclude_unset=True)
        logger.info(f"Process data: {data_dict}")
        
        with open(file_path, 'w') as f:
            json.dump(data_dict, f, indent=2)
        
        logger.info(f"Successfully updated process file: {file_path}")
        
        # Reload processes to update vector store
        from config.config import load_processes_from_files
        load_processes_from_files()
        logger.info("Reloaded processes and updated vector store")
        
        return {"message": f"Process '{filename}' updated successfully"}
    except Exception as e:
        logger.error(f"Error updating process file {file_path}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error updating process file: {str(e)}"}
        )

@app.delete("/api/admin/processes/{category}/{filename}", response_class=JSONResponse)
async def delete_process(category: str, filename: str):
    """Delete a process file"""
    processes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "processes")
    file_path = os.path.join(processes_dir, category, f"{filename}.json")
    
    # Check if file exists
    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"error": f"Process '{filename}' not found in category '{category}'"}
        )
    
    # Delete the process file
    try:
        os.remove(file_path)
        return {"message": f"Process '{filename}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting process file {file_path}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error deleting process file: {str(e)}"}
        )

@app.get("/api/admin/categories", response_class=JSONResponse)
async def get_categories():
    """Get all available process categories"""
    processes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "processes")
    categories = []
    
    # Skip the README and validation script
    skip_files = ["README.md", "validate_processes.py"]
    
    for item in os.listdir(processes_dir):
        item_path = os.path.join(processes_dir, item)
        if os.path.isdir(item_path) and item not in skip_files:
            categories.append(item)
    
    return categories

# Only after all API routes, define the index and catch-all routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the React app."""
    return FileResponse("src/static/react/index.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    """Serve the React app for admin panel."""
    return FileResponse("src/static/react/index.html")

# This catch-all route should be the last route defined
@app.get("/{rest_of_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def serve_react_routes(rest_of_path: str):
    """Serve React app for all non-API routes."""
    # This route now excludes API paths since they are handled above
    return FileResponse("src/static/react/index.html")

def run_app():
    """Run the FastAPI application."""
    uvicorn.run("src.app:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)

if __name__ == "__main__":
    run_app()
