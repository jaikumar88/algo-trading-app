# Build and copy React client to Flask static directory
# Run this after building the client to serve it from Flask

Write-Host "Building React client..." -ForegroundColor Cyan
Set-Location client
npm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful! Copying to Flask static..." -ForegroundColor Green
    Set-Location ..
    
    # Remove old client static files
    if (Test-Path "static\client") {
        Remove-Item -Recurse -Force "static\client"
    }
    
    # Copy new build
    Copy-Item -Recurse "client\dist" "static\client"
    
    Write-Host "✓ Client copied to static\client\" -ForegroundColor Green
    Write-Host ""
    Write-Host "To serve from Flask, add this route to app.py:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "@app.route('/')" -ForegroundColor White
    Write-Host "@app.route('/client')" -ForegroundColor White
    Write-Host "@app.route('/client/<path:path>')" -ForegroundColor White
    Write-Host "def serve_client(path='index.html'):" -ForegroundColor White
    Write-Host "    from flask import send_from_directory" -ForegroundColor White
    Write-Host "    return send_from_directory('static/client', path)" -ForegroundColor White
    Write-Host ""
    Write-Host "Then access at: http://localhost:5000/client" -ForegroundColor Cyan
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    Set-Location ..
    exit 1
}
