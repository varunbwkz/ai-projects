# Brandworkz AI Agent

An advanced AI chatbot for interacting with the Brandworkz platform. This agent provides document search capabilities and step-by-step guidance for Brandworkz processes.

## Features

- **Document Search**: Search for various document types (images, PDFs, etc.) in the Brandworkz system
- **Process Guidance**: Step-by-step instructions for common Brandworkz tasks
- **Conversational Interface**: Natural language interactions using OpenAI's GPT models
- **React Web Interface**: Modern, responsive UI with light/dark mode built with React
- **AI-Powered Responses**: Intelligent responses based on structured process guides
- **Markdown Support**: Rich text formatting for better readability

## Technologies

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: React, Styled Components, React Markdown
- **AI**: OpenAI GPT API
- **Styling**: CSS Variables for theming, with light/dark mode support

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- OpenAI API key
- Brandworkz account credentials

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd brandworkz-ai-agent
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file:
   ```
   cp .env.example .env
   ```

4. Edit the `.env` file with your OpenAI API key and Brandworkz credentials.

5. Build the React frontend:
   ```
   ./deploy_frontend.sh
   ```
   This script will install npm dependencies and build the React application.

## Running the Application

1. Start the FastAPI server:
   ```
   python main.py
   ```

2. Open your browser and navigate to `http://localhost:8000`

## Development

### Backend Development

For backend development, you can run the FastAPI server with auto-reload:
```
python main.py
```

### Frontend Development

For frontend development with hot-reloading:
```
cd src/frontend
npm start
```

This will start the React development server at `http://localhost:5173` with API requests proxied to the FastAPI backend.

## How It Works

The Brandworkz AI Agent consists of three main components:

1. **Brandworkz Client**: Handles authentication and interactions with the Brandworkz platform
2. **AI Engine**: Manages conversations and generates responses using OpenAI's models
3. **Web Interface**: Provides a user-friendly interface using FastAPI and modern frontend technologies

## Customizing Process Instructions

Process instructions are now managed in a scalable directory-based structure rather than directly in `config.py`. This makes adding and maintaining process guides more manageable, especially as the number of guides grows.

### Process Directory Structure

```
processes/
├── README.md                 # Documentation for adding processes
├── validate_processes.py     # Script to validate process JSON files
├── asset_management/         # Process category
│   ├── upload_asset.json
│   ├── search_asset.json
│   └── metadata_management.json
├── collection_management/    # Process category
│   └── create_collection.json
├── sharing_collaboration/    # Process category
│   └── share_assets.json
└── workflow_management/      # Process category
    └── initiate_approval.json
```

### Adding New Processes

1. **Determine the Category**: Place your process in the appropriate category directory or create a new one if needed.

2. **Create a JSON File**: Create a new JSON file with a descriptive name (e.g., `download_assets.json`).

3. **Simple Process Format**:
```json
{
  "title": "Human-Readable Title",
  "description": "A detailed description of what this guide covers",
  "keywords": ["keyword1", "keyword2", "specific phrase"],
  "steps": [
    "Step 1",
    "Step 2",
    "Step 3"
  ]
}
```

4. **Complex Process Format**:
```json
{
  "title": "Human-Readable Title",
  "description": "A detailed description of what this guide covers",
  "keywords": ["keyword1", "keyword2", "specific phrase"],
  "prerequisites": [
    "Prerequisite 1",
    "Prerequisite 2"
  ],
  "sections": [
    {
      "name": "Section Name",
      "steps": [
        "Step 1",
        "Step 2",
        "Step 3"
      ],
      "notes": "Optional notes about this section",
      "tips": "Optional tips for this section",
      "troubleshooting": [
        "Problem 1 and solution",
        "Problem 2 and solution"
      ]
    }
    // Add more sections as needed
  ]
}
```

5. **Validate Your Process**:
```bash
python processes/validate_processes.py
```

### Benefits of the Directory-Based Approach

- **Scalability**: Easily add hundreds of processes without bloating the codebase
- **Maintainability**: Edit individual processes without affecting others
- **Organization**: Group processes by categories for better navigation
- **Collaboration**: Multiple team members can work on different processes
- **Version Control**: Track changes to individual processes more effectively

For more detailed instructions on creating processes, refer to the `processes/README.md` file.

## Security Notes

- The agent stores API keys and credentials in memory only during runtime
- For production deployment we will need to consider using a secure secret management solution
- Review authentication mechanisms and access controls before deployment

## Acknowledgements

- OpenAI for providing the AI capabilities
- The Brandworkz Team who are the true champions here!
