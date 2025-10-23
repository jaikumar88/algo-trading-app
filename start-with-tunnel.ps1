# RAG Trading System with LocalTunnel Startup Script
# Starts Flask app and LocalTunnel together

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RAG Trading System with LocalTunnel" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
}
else {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Red
    exit 1
}

# Kill existing processes
Write-Host "[2/4] Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*lt*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Check if localtunnel is installed
Write-Host "[3/4] Checking LocalTunnel installation..." -ForegroundColor Yellow
$ltInstalled = Get-Command lt -ErrorAction SilentlyContinue
if (-not $ltInstalled) {
    Write-Host "  Installing LocalTunnel..." -ForegroundColor Yellow
    npm install -g localtunnel
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install localtunnel" -ForegroundColor Red
        Write-Host "Please install Node.js first: https://nodejs.org/" -ForegroundColor Red
        exit 1
    }
}

# Start Flask app in background
Write-Host "[4/4] Starting services..." -ForegroundColor Yellow
Write-Host "  Starting Flask application..." -ForegroundColor Gray

$flaskJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & .venv\Scripts\python.exe app.py
}

# Wait for Flask to start
Write-Host "  Waiting for Flask to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Check if Flask started successfully
if ($flaskJob.State -eq "Failed") {
    Write-Host "ERROR: Flask failed to start" -ForegroundColor Red
    Receive-Job $flaskJob
    exit 1
}

# Start LocalTunnel
Write-Host "  Starting LocalTunnel..." -ForegroundColor Gray
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Services Started Successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Local:       http://localhost:5000" -ForegroundColor White
Write-Host "  Public URL:  https://trading-backend.loca.lt" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Run LocalTunnel (this will keep the window open)
try {
    lt --port 5000 --subdomain trading-backend
}
finally {
    # Cleanup on exit
    Write-Host ""
    Write-Host "Stopping services..." -ForegroundColor Yellow
    Stop-Job $flaskJob -ErrorAction SilentlyContinue
    Remove-Job $flaskJob -Force -ErrorAction SilentlyContinue
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Services stopped." -ForegroundColor Green
}
