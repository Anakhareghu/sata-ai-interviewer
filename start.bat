@echo off
echo =============================================
echo   AI Voice Interview System - Starting...
echo =============================================
echo.

REM Start Backend
echo [1/2] Starting Backend Server (port 8000)...
start "AI Interview - Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [2/2] Starting Frontend Dev Server (port 5173)...
start "AI Interview - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo =============================================
echo   Both servers are starting!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo =============================================
echo.
echo Opening browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:5173
