#!/bin/bash

echo "🤖 Starting AI Conversation Platform..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Run the application
echo ""
echo "Starting server..."
echo "Open your browser to: http://localhost:5000"
echo ""
python app.py