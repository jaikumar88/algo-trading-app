@echo off
title RAG Trading System Startup
color 0A

echo.
echo ========================================
echo    RAG Trading System Startup
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
echo [1/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Kill any existing processes
echo [2/5] Cleaning up existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Flask in a new window
echo [3/5] Starting Flask application...
start "RAG Trading Flask App" /min cmd /c ".venv\Scripts\python.exe app.py"

REM Wait for Flask to start
echo [4/5] Waiting for Flask to start...
timeout /t 8 /nobreak >nul

REM Start ngrok in a new window
echo [5/5] Starting ngrok tunnel...
start "RAG Trading ngrok" cmd /k "ngrok http 5000"

REM Wait for ngrok to initialize
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo    Services Started Successfully!
echo ========================================
echo.
echo Local URLs:
echo   Dashboard: http://localhost:5000/dashboard
echo   Signals:   http://localhost:5000/signals
echo   Health:    http://localhost:5000/api/health
echo.
echo ngrok Web Interface: http://localhost:4040
echo.
echo Instructions:
echo 1. Check ngrok window for your public URL
echo 2. Use: https://your-ngrok-url.app/webhook for TradingView
echo 3. Test webhook with: curl -X POST https://your-url/webhook -H "Content-Type: application/json" -d "{\"test\": \"data\"}"
echo.
echo TradingView Alert Template:
echo {"action": "buy", "symbol": "{{ticker}}", "price": {{close}}, "volume": 0.1}
echo.
echo Press any key to STOP all services...
pause >nul

echo.
echo Stopping all services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
echo Services stopped.
echo.
pause