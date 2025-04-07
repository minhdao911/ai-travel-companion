#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Make the debug.py file executable
chmod +x debug.py

# Run the test functions in debug mode
python debug.py debug