#!/bin/bash

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python -m venv brandworkz-venv || python3 -m venv brandworkz-venv

# Activate virtual environment
source brandworkz-venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Setup completed
echo "Setup completed! You can now run the application with:"
echo "./run.sh" 