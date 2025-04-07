@echo off
setlocal

:: Change to the script directory
cd /d "%~dp0"

:: Check if the virtual environment exists
if not exist venv (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: Run the test functions in debug mode
python debug.py debug

endlocal 