#!/bin/bash

echo "Building and deploying the React frontend..."

# Navigate to the frontend directory
cd src/frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
  echo "Installing npm dependencies..."
  npm install
fi

# Build the React app
echo "Building React application..."
npm run build

echo "Frontend build complete! The FastAPI server will now serve the React app."
echo "Run the server using: python main.py" 