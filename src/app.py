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

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the React app."""
    return FileResponse("src/static/react/index.html")

@app.get("/{rest_of_path:path}", response_class=HTMLResponse)
async def serve_react_routes(rest_of_path: str):
    """Serve React app for all routes."""
    return FileResponse("src/static/react/index.html")

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

def run_app():
    """Run the FastAPI application."""
    uvicorn.run("src.app:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)

if __name__ == "__main__":
    run_app()
