# Start script for The Talking Heads UI (PowerShell)

Write-Host "Starting The Talking Heads UI..." -ForegroundColor Cyan
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start Flask API server in background
Write-Host "Starting Flask API server on port 5001..." -ForegroundColor Green
$apiJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python server.py
}

# Wait a moment for API to start
Start-Sleep -Seconds 3

# Start React dev server
Write-Host "Starting React dev server on port 3000..." -ForegroundColor Green
Write-Host "UI will be available at http://localhost:3000" -ForegroundColor Yellow
Write-Host "API will be available at http://localhost:5001" -ForegroundColor Yellow
Write-Host ""
npm start

# Cleanup on exit
Stop-Job $apiJob
Remove-Job $apiJob

