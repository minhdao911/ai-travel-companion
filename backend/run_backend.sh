#!/bin/bash

# Poetry automatically handles virtual environments
# No need to create or activate manually

# Install dependencies using Poetry
echo "Installing dependencies via Poetry..."
poetry install --no-root

# Run the FastAPI server using Poetry
echo "Starting FastAPI server via Poetry..."
poetry run uvicorn main:app --reload

# This line will only run if the server stops
echo "Server stopped"