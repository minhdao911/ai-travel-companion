#!/bin/bash

# Change to the script directory
cd "$(dirname "$0")"

# Ensure Poetry is installed and in PATH

# Install dependencies using Poetry if needed
# (Poetry handles this implicitly, but running install ensures environment is up-to-date)
echo "Ensuring dependencies are installed via Poetry..."
poetry install --no-root

# Run the debug script using Poetry
echo "Running debug script..."
poetry run python debug.py