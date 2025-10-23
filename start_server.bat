@echo off
echo Starting RAG Trading System...

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Kill any existing processes
taskkill /f /im python.exe /fi "WINDOWTITLE eq app.py*" >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1

REM Wait for cleanup
timeout /t 2 /nobreak >nul

echo Starting Flask application...
start "Flask App" cmd /k "python app.py"

REM Wait for Flask to start
timeout /t 5 /nobreak >nul

echo Starting ngrok tunnel...
start "ngrok" cmd /k "ngrok http 5000"

REM Wait for ngrok to start
timeout /t 3 /nobreak >nul

echo.
echo ====================================
echo RAG Trading System Started!
echo ====================================
echo.
echo Local Dashboard: http://localhost:5000/dashboard
echo ngrok Web UI: http://localhost:4040
echo.
echo Check the ngrok window for your public webhook URL
echo Use that URL + /webhook for TradingView alerts
echo.
echo Press any key to stop all services...
pause >nul

REM Cleanup
echo Stopping services...
taskkill /f /im python.exe /fi "WINDOWTITLE eq app.py*" >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
echo Services stopped.