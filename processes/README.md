# Brandworkz AI Agent - Process Guide Directory

This directory contains the process guides used by the Brandworkz AI Agent. Each process is defined as a JSON file within an appropriate category subdirectory.

## Directory Structure

- **asset_management/** - Processes related to uploading, searching, and managing assets
- **collection_management/** - Processes related to creating and managing collections
- **sharing_collaboration/** - Processes related to sharing assets and collaborating with team members
- **workflow_management/** - Processes related to workflows and approval processes

## Adding a New Process

To add a new process guide, follow these steps:

1. Determine the appropriate category directory for your process
2. Create a new JSON file with a descriptive name (use snake_case)
3. Use one of the following formats:

### Simple Process Format

For straightforward processes with just a list of steps:

```json
{
  "title": "Process Title",
  "description": "Brief description of what this process accomplishes",
  "keywords": ["keyword1", "keyword2", "related term", "action phrase"],
  "steps": [
    "Step 1 description",
    "Step 2 description",
    "Step 3 description",
    "..."
  ]
}
```

### Complex Process Format

For more detailed processes with sections, prerequisites, and additional notes:

```json
{
  "title": "Process Title",
  "description": "Comprehensive description of the process",
  "keywords": ["keyword1", "keyword2", "related term", "action phrase"],
  "prerequisites": [
    "Prerequisite 1",
    "Prerequisite 2",
    "..."
  ],
  "sections": [
    {
      "name": "First Section Name",
      "steps": [
        "Step 1 description",
        "Step 2 description",
        "..."
      ],
      "notes": "Optional notes about this section",
      "tips": "Optional tips for this section"
    },
    {
      "name": "Second Section Name",
      "steps": [
        "Step 1 description",
        "Step 2 description",
        "..."
      ],
      "troubleshooting": [
        "Troubleshooting tip 1",
        "Troubleshooting tip 2",
        "..."
      ]
    }
  ]
}
```

## Important Fields

- **title**: A descriptive title for the process
- **description**: A brief explanation of what the process accomplishes
- **keywords**: An array of terms and phrases that users might use when asking about this process (critical for matching user queries)
- **steps**: For simple processes, an array of step-by-step instructions
- **prerequisites**: (Optional) Requirements before starting this process
- **sections**: For complex processes, an array of sections each with its own steps and optional notes

## Recommendations

1. **Keywords**: Include variations of terms (e.g., "upload", "uploading", "add file") to improve matching
2. **Steps**: Keep steps concise and focused on a single action
3. **Organization**: Create new category directories if needed for logical grouping
4. **Validation**: Verify your JSON is valid before adding it to the system
