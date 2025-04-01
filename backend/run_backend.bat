@echo off
echo Starting AI Travel Companion Backend...

:: Check if virtual environment exists, if not create it
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Run the FastAPI server
echo Starting FastAPI server...
uvicorn main:app --reload

:: This line will only run if the server stops
echo Server stopped