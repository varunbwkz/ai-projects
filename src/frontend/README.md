# Brandworkz AI Assistant React Frontend

This is the React-based UI for the Brandworkz AI Assistant. It provides a modern, responsive interface for interacting with the Brandworkz AI.

## Features

- 🎨 Modern UI with light/dark mode support
- 💬 Interactive chat interface
- 📑 Process guides with markdown support
- 🔍 Categorized process selection
- 📤 Export conversations as markdown
- 🔄 Real-time feedback mechanism

## Development

### Prerequisites

- Node.js (v14+)
- npm or yarn

### Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run start
   ```

3. The development server will start on http://localhost:5173 and will proxy API requests to the FastAPI backend on port 8000.

### Building for Production

To build the application for production:

```bash
npm run build
```

This will create optimized production files in the `../static/react` directory, which will be served by the FastAPI backend.

Alternatively, you can use the deploy script from the project root:

```bash
./deploy_frontend.sh
```

## Project Structure

- `src/components` - React components
- `src/context` - Context API for state management
- `src/App.jsx` - Main application component
- `src/index.css` - Global styles

## Styling

The application uses styled-components for styling, with CSS variables for theming. Theme switching is handled through the ThemeContext.
