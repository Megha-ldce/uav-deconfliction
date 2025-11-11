#!/bin/bash
echo "UAV Deconfliction System Setup"
echo "================================"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
pytest tests/test_deconfliction.py -v

# Run main application
echo "Running main application..."
python src/main.py

echo "================================"
echo "Complete! Check outputs/ directory for visualizations"
