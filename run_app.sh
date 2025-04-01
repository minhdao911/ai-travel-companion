#!/bin/bash

echo "Starting AI Travel Companion (Full Stack)..."

# Function to clean up background processes when script exits
cleanup() {
    echo "Shutting down servers..."
    # Find and kill the backend server process
    if [ -f "backend_pid.txt" ]; then
        BACKEND_PID=$(cat backend_pid.txt)
        if ps -p $BACKEND_PID > /dev/null; then
            kill $BACKEND_PID
            echo "Backend server stopped"
        fi
        rm backend_pid.txt
    fi
    exit 0
}

# Set up the cleanup function to run when script receives SIGINT (Ctrl+C)
trap cleanup SIGINT SIGTERM

# Start the backend
echo "Starting backend server..."
(
    # Navigate to the backend directory
    cd backend || { echo "Error: Cannot find backend directory"; exit 1; }

    # Check if virtual environment exists, if not create it
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate

    # Run the FastAPI server
    echo "Starting FastAPI server..."
    uvicorn main:app --reload
) &

# Save the backend process ID
echo $! > backend_pid.txt

# Wait a moment to ensure backend starts up
sleep 2
echo "Backend server running at http://localhost:8000"

# Start the frontend
echo "Starting frontend server..."
(
    # Navigate to the frontend directory
    cd frontend || { echo "Error: Cannot find frontend directory"; exit 1; }

    # Install dependencies if needed
    echo "Installing dependencies..."
    bun install

    # Run the frontend development server
    echo "Starting Vue.js development server..."
    bun dev
)

# If the frontend server exits, clean up the backend
cleanup 