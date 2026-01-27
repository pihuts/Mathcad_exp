@echo off
title Mathcad Automator Launcher
echo ===================================================
echo   Mathcad Automator - Dev Environment Launcher
echo ===================================================
echo.

REM 1. Check/Install Frontend
if not exist "frontend\node_modules" (
    echo [Launcher] Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM 2. Check/Create Backend Venv
if not exist ".venv" (
    echo [Launcher] Creating Python virtual environment...
    python -m venv .venv
)

REM 3. Activate Venv
call .venv\Scripts\activate.bat

REM 4. Install Requirements (Check roughly)
pip install -r requirements.txt

echo.
echo [Launcher] Starting services...
echo.

REM Start Frontend in new window
start "Mathcad Auto Frontend" cmd /k "cd frontend && npm run dev"

REM Start Backend in new window
start "Mathcad Auto Backend" cmd /k ".venv\Scripts\activate && python -m src.server.main"

echo [Launcher] Services started! 
echo.
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:5173
echo.
echo Press any key to close this launcher (Services will stay open)...
pause >nul
