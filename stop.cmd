@echo off
echo Stopping RAG Trading System...

REM Kill Flask processes
taskkill /f /im python.exe 2>nul

REM Kill ngrok processes  
taskkill /f /im ngrok.exe 2>nul

echo All services stopped.
pause