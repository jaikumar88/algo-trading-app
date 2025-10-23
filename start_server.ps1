# RAG Trading System - Combined Startup Script
# This script starts both the Flask app and ngrok tunnel

Write-Host "🚀 Starting RAG Trading System..." -ForegroundColor Green

# Check if ngrok is installed
try {
    $ngrokVersion = & ngrok version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "ngrok not found"
    }
    Write-Host "✅ ngrok is installed: $($ngrokVersion.Split()[2])" -ForegroundColor Green
} catch {
    Write-Host "❌ ngrok is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install ngrok from https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "After installation, run: ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

# Kill any existing processes
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*app.py*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait a moment for cleanup
Start-Sleep -Seconds 2

# Start Flask app in background
Write-Host "🐍 Starting Flask application..." -ForegroundColor Cyan
$flaskJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & .\.venv\Scripts\python.exe app.py
}

# Wait for Flask to start
Write-Host "⏳ Waiting for Flask to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if Flask is running
$flaskRunning = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $flaskRunning = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $flaskRunning) {
    Write-Host "❌ Flask failed to start properly" -ForegroundColor Red
    Write-Host "Check logs in flask_stderr.log for errors" -ForegroundColor Yellow
    Stop-Job $flaskJob -ErrorAction SilentlyContinue
    Remove-Job $flaskJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "✅ Flask application is running on http://localhost:5000" -ForegroundColor Green

# Start ngrok tunnel
Write-Host "🌐 Starting ngrok tunnel..." -ForegroundColor Cyan
$ngrokJob = Start-Job -ScriptBlock {
    & ngrok http 5000 --log=stdout
}

# Wait for ngrok to start
Start-Sleep -Seconds 3

# Get ngrok tunnel URL
Write-Host "🔍 Getting ngrok tunnel URL..." -ForegroundColor Yellow
$maxAttempts = 10
$attempt = 0
$tunnelUrl = $null

while ($attempt -lt $maxAttempts -and -not $tunnelUrl) {
    try {
        $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
        $tunnel = $ngrokApi.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
        if ($tunnel) {
            $tunnelUrl = $tunnel.public_url
        }
    } catch {
        Start-Sleep -Seconds 1
    }
    $attempt++
}

if ($tunnelUrl) {
    Write-Host ""
    Write-Host "🎉 RAG Trading System is now running!" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host ""
    Write-Host "📱 Local URLs:" -ForegroundColor Cyan
    Write-Host "   Dashboard: http://localhost:5000/dashboard" -ForegroundColor White
    Write-Host "   Signals:   http://localhost:5000/signals" -ForegroundColor White
    Write-Host "   API:       http://localhost:5000/api/trading/trades" -ForegroundColor White
    Write-Host ""
    Write-Host "🌍 Public URLs (for TradingView):" -ForegroundColor Cyan
    Write-Host "   Webhook:   $tunnelUrl/webhook" -ForegroundColor Green
    Write-Host "   Dashboard: $tunnelUrl/dashboard" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 TradingView Webhook Configuration:" -ForegroundColor Yellow
    Write-Host "   URL: $tunnelUrl/webhook" -ForegroundColor Green
    Write-Host "   Method: POST" -ForegroundColor White
    Write-Host "   Content-Type: application/json" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 ngrok Web Interface: http://localhost:4040" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "📝 Example TradingView Alert Message:" -ForegroundColor Yellow
    Write-Host '   {"action": "buy", "symbol": "{{ticker}}", "price": {{close}}, "volume": 0.1}' -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  Could not retrieve ngrok tunnel URL" -ForegroundColor Yellow
    Write-Host "Check ngrok status at http://localhost:4040" -ForegroundColor White
}

# Keep script running and monitor processes
Write-Host "🔄 Monitoring services... Press Ctrl+C to stop all services" -ForegroundColor Cyan
Write-Host ""

try {
    while ($true) {
        # Check if Flask job is still running
        if ($flaskJob.State -ne "Running") {
            Write-Host "❌ Flask application stopped unexpectedly" -ForegroundColor Red
            break
        }
        
        # Check if ngrok job is still running
        if ($ngrokJob.State -ne "Running") {
            Write-Host "❌ ngrok tunnel stopped unexpectedly" -ForegroundColor Red
            break
        }
        
        Start-Sleep -Seconds 5
    }
} catch {
    Write-Host "🛑 Shutting down services..." -ForegroundColor Yellow
} finally {
    # Cleanup
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    Stop-Job $flaskJob -ErrorAction SilentlyContinue
    Stop-Job $ngrokJob -ErrorAction SilentlyContinue
    Remove-Job $flaskJob -ErrorAction SilentlyContinue
    Remove-Job $ngrokJob -ErrorAction SilentlyContinue
    
    # Kill processes
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*app.py*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ All services stopped" -ForegroundColor Green
}