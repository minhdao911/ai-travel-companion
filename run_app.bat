@echo off
echo Starting AI Travel Companion (Full Stack)...

:: Start the backend server in a new window
echo Starting backend server...
start "AI Travel Companion Backend" cmd /c "cd backend && echo Installing dependencies via Poetry... && call poetry install --no-root && echo Starting FastAPI server via Poetry... && call poetry run uvicorn main:app --reload"

:: Give the backend a moment to start
timeout /t 3 /nobreak > nul
echo Backend server running at http://localhost:8000

:: Start the frontend server in the current window
echo Starting frontend server...
cd frontend || (echo Error: Cannot find frontend directory && exit /b 1)

:: Install dependencies if needed
echo Installing dependencies...
call npm install

:: Run the frontend development server
echo Starting Vue.js development server...
call npm run dev

:: This line will only run if the frontend server stops
echo Frontend server stopped. The backend server window remains open.