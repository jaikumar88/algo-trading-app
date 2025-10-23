@echo off
echo ========================================
echo   STARTING TRADING SYSTEM SERVICES
echo ========================================
echo.

echo Starting Flask Backend...
start "Flask Backend" python start_flask.py

echo Waiting 3 seconds for Flask to start...
timeout /t 3 /nobreak >nul

echo Starting ngrok Tunnel...
start "ngrok Tunnel" python start_tunnel.py

echo.
echo ========================================
echo   ALL SERVICES STARTED!
echo ========================================
echo.
echo Local Client:  http://localhost:5173
echo GitHub Pages:  https://jaikumar88.github.io/algo-trading-app/
echo.
echo Both windows will remain open. Close them to stop the services.
echo.
pause
