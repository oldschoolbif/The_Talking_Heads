# The Talking Heads UI - Startup Script
# Similar to exponis-local's quick-start pattern

param(
    [switch]$SkipBackend = $false
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$UIRoot = Join-Path $ProjectRoot "ui"

Set-Location $UIRoot

Write-Host "🎬 The Talking Heads - Video Generation UI" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "  ✅ Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "  ✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Node.js not found. Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Python not found. Backend API won't work." -ForegroundColor Yellow
}

Write-Host ""

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing UI dependencies..." -ForegroundColor Cyan
    npm install
    Write-Host ""
}

# Install Python dependencies if needed
if (-not $SkipBackend) {
    Write-Host "📦 Checking Python dependencies..." -ForegroundColor Cyan
    try {
        python -c "import flask, flask_cors" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  Installing Flask dependencies..." -ForegroundColor Yellow
            pip install flask flask-cors
        } else {
            Write-Host "  ✅ Python dependencies ready" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠️  Could not check Python dependencies" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Start backend server
if (-not $SkipBackend) {
    Write-Host "🚀 Starting backend API server (port 8001)..." -ForegroundColor Cyan
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:UIRoot
        python server.py
    }
    Start-Sleep -Seconds 2
    Write-Host "  ✅ Backend started" -ForegroundColor Green
    Write-Host ""
}

# Set environment variables for React
$env:PORT = "3001"
$env:REACT_APP_API_URL = "http://localhost:8001/api"

# Start frontend dev server
Write-Host "🚀 Starting React dev server (port 3001)..." -ForegroundColor Cyan
Write-Host ""
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🌐 Access your UI:" -ForegroundColor Yellow
Write-Host "  Frontend:  http://localhost:3001" -ForegroundColor White
Write-Host "  API:       http://localhost:8001/api" -ForegroundColor White
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Gray
Write-Host ""

# Start React dev server (this blocks)
npm start

# Cleanup
if (-not $SkipBackend) {
    Write-Host "`n🛑 Stopping backend server..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
}

