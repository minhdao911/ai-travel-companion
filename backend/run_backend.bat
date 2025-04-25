@echo off
echo Starting AI Travel Companion Backend...

:: Ensure Poetry is installed and in PATH

:: Install dependencies using Poetry
echo Installing dependencies via Poetry...
call poetry install --no-root

:: Run the FastAPI server using Poetry
echo Starting FastAPI server via Poetry...
call poetry run uvicorn main:app --reload

:: This line will only run if the server stops
echo Server stopped. Press any key to exit.
pause > nul