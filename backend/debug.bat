@echo off
echo Starting AI Travel Companion Backend Debug Mode...

:: Ensure Poetry is installed and in PATH

:: Install dependencies using Poetry if needed
:: (Poetry handles this implicitly, but running install ensures environment is up-to-date)
echo Ensuring dependencies are installed via Poetry...
call poetry install --no-root

:: Run the debug script using Poetry
echo Running debug script...
call poetry run python debug.py

:: Exit message
echo Debug mode finished. Press any key to exit.
pause > nul 