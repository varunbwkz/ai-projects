#!/bin/bash

echo "Starting Brandworkz AI Agent..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
python main.py 