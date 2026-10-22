@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo   Sakshi -- Audited Agentic Support Platform
echo   Installing Dependencies (Backend + Frontend)
echo =======================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ and re-run this script.
    pause
    exit /b 1
)
echo [OK] Python detected.

:: 2. Check Node.js and npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm / Node.js is not installed or not in your PATH.
    echo Please install Node.js 18+ and re-run this script.
    pause
    exit /b 1
)
echo [OK] npm detected.
echo.

:: 3. Install Python Backend Dependencies
echo -------------------------------------------------------
echo [1/3] Installing Python Backend dependencies...
echo -------------------------------------------------------
python -m pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)
echo [OK] Python dependencies installed successfully.
echo.

:: 4. Install Frontend NPM Dependencies
echo -------------------------------------------------------
echo [2/3] Installing Frontend NPM dependencies...
echo -------------------------------------------------------
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install npm dependencies.
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Frontend dependencies installed successfully.
echo.

:: 5. Initialize and Seed SQLite Database
echo -------------------------------------------------------
echo [3/3] Initializing and Seeding SQLite Database...
echo -------------------------------------------------------
python -m backend.db.seed
if %errorlevel% neq 0 (
    echo [ERROR] Failed to seed database.
    pause
    exit /b 1
)
echo [OK] Database seeded with genesis block, mock orders, customers, and settlements.
echo.

echo =======================================================
echo   Installation Completed Successfully!
echo   Run 'run.bat' to launch the entire project.
echo =======================================================
echo.
pause
