@echo off
cls
echo Starting RAG Trading System...

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Clean up any existing processes
taskkill /f /im python.exe /fi "WINDOWTITLE eq *app.py*" 2>nul
taskkill /f /im ngrok.exe 2>nul
timeout 2 >nul

REM Start Flask app
echo Starting Flask...
start "Flask" cmd /k "python app.py"

REM Wait a bit
timeout 5 >nul

REM Start ngrok
echo Starting ngrok...
start "ngrok" cmd /k "ngrok http 5000"

echo.
echo Both services are starting...
echo Check the Flask window for any errors
echo Check the ngrok window for your public URL
echo.
echo Use the ngrok URL + /webhook for TradingView alerts
echo Example: https://abc123.ngrok.app/webhook
echo.
pause