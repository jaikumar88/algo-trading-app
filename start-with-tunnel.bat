@echo off
title RAG Trading System with LocalTunnel
color 0A

echo.
echo ========================================
echo  RAG Trading System with LocalTunnel
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then install requirements: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Kill any existing processes
echo [2/4] Cleaning up existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Check if localtunnel is installed
where lt >nul 2>&1
if errorlevel 1 (
    echo.
    echo LocalTunnel not found. Installing...
    call npm install -g localtunnel
    if errorlevel 1 (
        echo ERROR: Failed to install localtunnel
        echo Please install Node.js first: https://nodejs.org/
        pause
        exit /b 1
    )
)

REM Start Flask app in background
echo [3/4] Starting Flask application on port 5000...
start /B "" python app.py > flask_stdout.log 2> flask_stderr.log

REM Wait for Flask to start
echo Waiting for Flask to initialize...
timeout /t 8 /nobreak >nul

REM Start LocalTunnel
echo [4/4] Starting LocalTunnel with subdomain 'trading-backend'...
echo.
echo ========================================
echo   Services Starting...
echo ========================================
echo   Flask App:    http://localhost:5000
echo   LocalTunnel:  https://trading-backend.loca.lt
echo ========================================
echo.
echo Press Ctrl+C to stop both services
echo.

REM Run LocalTunnel (this will keep the window open)
lt --port 5000 --subdomain trading-backend

REM If LocalTunnel exits, cleanup
echo.
echo Stopping services...
taskkill /f /im python.exe >nul 2>&1
echo Services stopped.
pause
