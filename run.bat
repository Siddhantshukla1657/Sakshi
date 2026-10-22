@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo   Sakshi -- Audited Agentic Support Platform
echo   Launching Backend (FastAPI) and Frontend (Vite + React)
echo =======================================================
echo.

:: 1. Verify Database exists or auto-seed
if not exist "backend\sakshi.db" (
    echo [INFO] Database not found. Auto-seeding initial database...
    python -m backend.db.seed
    echo.
)

:: 2. Launch FastAPI Backend on port 8000 in a new window
echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Sakshi Backend API (Port 8000)" cmd /k "title Sakshi Backend API && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

:: 3. Launch Vite Frontend on port 5173 in a new window
echo [2/2] Starting Vite Frontend on http://127.0.0.1:5173 ...
start "Sakshi Frontend (Port 5173)" cmd /k "title Sakshi Frontend && cd frontend && npm run dev -- --host 127.0.0.1 --port 5173"

:: 4. Wait briefly and open browser
echo.
echo Waiting 3 seconds for servers to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser at http://127.0.0.1:5173 ...
start http://127.0.0.1:5173

echo.
echo =======================================================
echo   Sakshi is now running!
echo   - Web Console:   http://127.0.0.1:5173
echo   - API / Swagger: http://127.0.0.1:8000/docs
echo   - API Health:    http://127.0.0.1:8000/api/health
echo.
echo   To stop the servers, close the opened terminal windows.
echo =======================================================
echo.
pause
