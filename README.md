# Brandworkz AI Agent

A comprehensive AI-powered assistant that helps users find and follow Brandworkz-related processes through an intuitive chat interface. The system provides detailed process documentation, intelligent search capabilities, and an administrative interface for process management.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Manual Process Management](#manual-process-management)
- [API Reference](#api-reference)
- [Process JSON Format](#process-json-format)
- [Vector Search](#vector-search)

## Overview

The Brandworkz AI Agent serves as an intelligent assistant that responds to user queries about Brandworkz processes. It leverages natural language processing to understand queries and matches them with relevant processes stored in a structured format. The system includes both a user-facing chat interface and an admin panel for managing process documentation, though the current workflow focuses on manual JSON file editing.

## Features

### Current Implementation

- **AI-Powered Chat Interface**
  - Natural language interaction using OpenAI's models
  - Intelligent matching of queries to relevant processes
  - Context-aware responses that incorporate process details
  - Support for follow-up questions and clarifications

- **Process Documentation System**
  - Structured JSON format for process information
  - Support for categories, titles, descriptions, and keywords
  - Step-by-step instructions with optional numbering
  - Troubleshooting information for common issues
  - Manual file-based management of process JSON files

- **Vector Search Capabilities**
  - Semantic search using OpenAI embeddings
  - High-relevance query matching
  - Support for both vector store and in-memory embeddings
  - Automatic process reloading when updates are made

- **Administrative Panel** (available but not currently used)
  - Complete CRUD operations for processes (Create, Read, Update, Delete)
  - Category-based organization of processes
  - Intuitive form-based interface for process editing
  - Error handling and validation

## Architecture

The application follows a modern client-server architecture:

- **Backend (Python/FastAPI)**
  - RESTful API endpoints for chat and process management
  - Vector search implementation using OpenAI embeddings
  - JSON file-based storage for processes
  - Process loading and indexing system

- **Frontend (React)**
  - Component-based UI with styled-components
  - React Router for navigation
  - Form handling and validation
  - Responsive design for various device sizes

## Project Structure

```
brandworkz-ai-agent/
├── processes/                   # JSON files containing process information
│   ├── category1/               # Processes organized by category
│   │   ├── process1.json        # Individual process file
│   │   └── process2.json
│   └── category2/
│       └── process3.json
├── src/
│   ├── frontend/                # React frontend application
│   │   ├── public/              # Static public assets
│   │   │   ├── index.html
│   │   │   └── favicon.ico
│   │   ├── src/
│   │   │   ├── components/      # React components
│   │   │   │   ├── AdminPanel.jsx   # Admin interface for process management
│   │   │   │   ├── ChatInterface.jsx # Chat UI component
│   │   │   │   ├── Header.jsx   # Application header with navigation
│   │   │   │   ├── Error.jsx    # Error display component
│   │   │   │   └── ...          # Other components
│   │   │   ├── App.jsx          # Main application component
│   │   │   ├── index.js         # Application entry point
│   │   │   └── styles.js        # Global styles
│   │   ├── package.json         # Frontend dependencies
│   │   └── vite.config.js       # Vite configuration
│   ├── static/                  # Static files served by backend
│   │   └── brandworkz-logo.png  # Logo image
│   ├── templates/               # HTML templates
│   │   └── index.html           # Main HTML template
│   ├── ai_engine.py             # AI processing and embedding logic
│   ├── app.py                   # FastAPI backend application
│   └── vector_store.py          # Vector search implementation
├── config/
│   └── config.py                # Application configuration
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables (not in repository)
```

## Setup and Installation

### Prerequisites

- **Python 3.9+**
- **Node.js 16+** and npm 8+
- **OpenAI API key** for AI capabilities

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd brandworkz-ai-agent
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your configuration:
   ```
   OPENAI_API_KEY=your-openai-api-key
   APP_HOST=0.0.0.0
   APP_PORT=8000
   DEBUG=True
   USE_VECTOR_STORE=True
   VECTOR_DB_PATH=data/vector_db
   ```

5. Ensure the processes directory structure exists:
   ```bash
   mkdir -p processes/general
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd src/frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Create a production build (optional):
   ```bash
   npm run build
   ```

## Configuration

The application can be configured through environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings and chat | Required |
| `APP_HOST` | Host to bind the server to | `0.0.0.0` |
| `APP_PORT` | Port to run the server on | `8000` |
| `DEBUG` | Enable debug mode | `False` |
| `USE_VECTOR_STORE` | Use persistent vector store instead of in-memory | `True` |
| `VECTOR_DB_PATH` | Path to store vector database files | `data/vector_db` |

## Usage

### Running the Application

1. **Start the backend server**:
   ```bash
   python -m src.app
   ```
   This will start the FastAPI server on the configured host and port (default: http://localhost:8000).

2. **Start the frontend development server** (for development):
   ```bash
   cd src/frontend
   npm run dev
   ```
   This will start the Vite development server, typically on http://localhost:5173.

### Chat Interface

1. Access the main application page in your browser
2. Type your query in the chat input field (e.g., "How do I download assets?")
3. The AI assistant will respond with relevant process information
4. You can ask follow-up questions for clarification

## Manual Process Management

The current workflow involves manually creating and editing process JSON files rather than using the Admin Panel interface. Here's how to manage processes manually:

### Creating a New Process

1. Identify the appropriate category directory under the `processes/` folder
   ```
   processes/
   ├── general/
   ├── search/
   └── upload/
   ```

2. Create a new JSON file with a descriptive filename (no spaces, use underscores)
   ```
   touch processes/general/new_process.json
   ```

3. Edit the file with proper JSON structure:
   ```json
   {
     "title": "Process Title",
     "description": "Detailed description of the process",
     "keywords": ["keyword1", "keyword2", "keyword3"],
     "steps": [
       "Step 1: Do this first",
       "Step 2: Then do this",
       "Step 3: Finally do this"
     ],
     "troubleshooting": [
       "Problem 1: If you encounter this issue, try this solution",
       "Problem 2: For this error, check these settings"
     ]
   }
   ```

4. Save the file and restart the application to refresh the vector store
   ```bash
   python main.py
   ```

### Editing an Existing Process

1. Locate the process JSON file in the appropriate category directory
2. Edit the JSON file directly using a text editor
3. Save your changes
4. Restart the application to refresh the vector store

### Creating a New Category

1. Create a new directory under the `processes/` folder
   ```bash
   mkdir processes/new_category
   ```

2. Add process JSON files to this directory as needed
3. Restart the application to recognize the new category

### Notes on Manual Process Management

- **JSON Validation**: Ensure your JSON is valid before saving. Invalid JSON will cause process loading errors.
- **Required Fields**: The `title`, `description`, and `keywords` fields are required.
- **File Naming**: Use descriptive filenames without spaces (use underscores instead).
- **Data Reloading**: After creating or editing process files, the application needs to be restarted to reload the processes and update the vector store.

## API Reference

### Chat Endpoints

#### Send a message to the AI assistant

- **URL**: `/api/chat`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "message": "How do I download assets?",
    "conversation_id": "optional-conversation-id"
  }
  ```
- **Response**:
  ```json
  {
    "response": "To download assets, you need to...",
    "conversation_id": "conversation-id",
    "matched_processes": [
      {
        "process_id": "download_assets",
        "similarity": 0.92,
        "title": "Downloading Assets",
        "description": "Process for downloading assets from Brandworkz"
      }
    ]
  }
  ```

### Process Management Endpoints

#### List all processes

- **URL**: `/api/admin/processes`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "processes": [
      {
        "category": "general",
        "filename": "download_assets",
        "title": "Downloading Assets",
        "description": "Process for downloading assets from Brandworkz"
      }
    ]
  }
  ```

#### Create a new process

- **URL**: `/api/admin/processes`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "category": "general",
    "filename": "new_process",
    "data": {
      "title": "New Process",
      "description": "Description of the new process",
      "keywords": ["keyword1", "keyword2"],
      "steps": ["Step 1", "Step 2", "Step 3"],
      "troubleshooting": ["Issue 1: Solution 1", "Issue 2: Solution 2"]
    }
  }
  ```
- **Response**:
  ```json
  {
    "message": "Process 'new_process' created successfully"
  }
  ```

#### Update an existing process

- **URL**: `/api/admin/processes/{category}/{filename}`
- **Method**: `PUT`
- **Request Body**:
  ```json
  {
    "title": "Updated Process",
    "description": "Updated description",
    "keywords": ["keyword1", "keyword2"],
    "steps": ["Updated Step 1", "Updated Step 2"],
    "troubleshooting": ["Updated troubleshooting"]
  }
  ```
- **Response**:
  ```json
  {
    "message": "Process 'filename' updated successfully"
  }
  ```

#### Delete a process

- **URL**: `/api/admin/processes/{category}/{filename}`
- **Method**: `DELETE`
- **Response**:
  ```json
  {
    "message": "Process 'filename' deleted successfully"
  }
  ```

#### List available categories

- **URL**: `/api/admin/categories`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "categories": ["general", "search", "upload"]
  }
  ```

## Process JSON Format

Processes are stored as JSON files in the `processes/{category}/` directories. Each process follows this format:

```json
{
  "title": "Process Title",
  "description": "Detailed description of the process",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "steps": [
    "Step 1: Do this first",
    "Step 2: Then do this",
    "Step 3: Finally do this"
  ],
  "troubleshooting": [
    "Problem 1: If you encounter this issue, try this solution",
    "Problem 2: For this error, check these settings"
  ]
}
```

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `title` | string | Display name of the process | Yes |
| `description` | string | Detailed description | Yes |
| `keywords` | array | List of keywords for matching | Yes |
| `steps` | array | Ordered list of process steps | No |
| `troubleshooting` | array | Common issues and solutions | No |

## Vector Search

The application uses OpenAI embeddings to create vector representations of processes, enabling semantic search capabilities:

- **Embedding Generation**: Combines title, description, and keywords to create dense vector representations
- **Vector Storage**: Supports both persistent storage (using ChromaDB) and in-memory storage
- **Query Matching**: Converts user queries to embeddings and finds the most similar process vectors
- **Automatic Reloading**: Updates the vector store when processes are added, modified, or deleted
- **Fallback Mechanism**: Falls back to in-memory embeddings if vector store is not available
