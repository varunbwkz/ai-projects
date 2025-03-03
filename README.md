# Brandworkz AI Agent

This repository contains the code for the Brandworkz AI Agent, which provides an AI-powered interface to interact with the Brandworkz Digital Asset Management system.

## Features

- **Browser Automation for Asset Search**: Robust Playwright-based browser automation for searching Brandworkz assets
- **Rich Asset Information Extraction**: Extracts detailed asset information including type, size, and thumbnail URLs
- **Playwright Validation**: Ability to validate specific assets in search results for testing
- **API Integration**: FastAPI-based API endpoints for integration with other systems
- **Fallback Mechanism**: Automatic fallback from API to browser automation when needed

## Getting Started

### Prerequisites

- Python 3.9+
- Playwright for browser automation
- FastAPI for API endpoints

### Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd brandworkz-ai-agent
    ```

2. Set up the environment:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

3. Configure your Brandworkz credentials:
    Create a `.env` file with the following contents:
    ```
    BRANDWORKZ_URL=https://your-brandworkz-instance.com
    BRANDWORKZ_USERNAME=your-username
    BRANDWORKZ_PASSWORD=your-password
    ```

### Running the Service

Start the server:
```bash
./run.sh
```

## Testing

### Testing Browser Automation

To test the browser automation for asset search:

```bash
python test_browser_search.py "search query" [options]
```

Options:
- `--debug`: Enable debug mode with additional logging
- `--visible`: Make the browser visible during automation
- `--validate "asset name"`: Validate a specific asset in the search results

### Testing the API

To test the API endpoints:

```bash
python test_api.py "search query" [--url "http://api-url"]
```

## Advanced Asset Validation

The system includes advanced asset validation capabilities for both automated testing and user verification:

1. **DOM-Based Validation**: Validates assets directly in the DOM using Playwright's expect functionality
2. **Content Validation**: Checks if an asset with a specific name is present in the search results
3. **Detailed Asset Information**: Extracts complete asset details including:
   - Asset ID
   - Asset name
   - Asset type (JPG, PNG, etc.)
   - File size
   - Thumbnail URL

## API Endpoints

### Search Assets

**Endpoint**: `/api/search_assets`  
**Method**: POST  
**Payload**:
```json
{
  "query": "search term",
  "max_results": 20
}
```

**Response**:
```json
{
  "success": true,
  "message": "Found X assets matching 'search term'",
  "results": [
    {
      "id": "asset-id",
      "name": "Asset Name",
      "thumbnail_url": "thumbnail-url",
      "description": "Type: JPG, Size: 22KB",
      "type": "Image",
      "file_size": "22KB",
      "source": "browser_automation"
    }
  ],
  "source": "browser_automation"
}
```

## License

[License Information]
