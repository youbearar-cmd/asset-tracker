@echo off
echo Starting Real-time Asset Tracker...

echo Starting Backend (FastAPI)...
start cmd /k "cd backend && python main_api.py"

echo Starting Frontend (Vite)...
start cmd /k "cd frontend && npm.cmd run dev"

echo.
echo Application is starting!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
pause
