# The Talking Heads UI - Docker Startup Script
# Similar to exponis-local's start-stack.ps1 pattern

param(
    [switch]$Build = $false,
    [switch]$Logs = $false,
    [switch]$Detached = $false
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$UIRoot = Join-Path $ProjectRoot "ui"
Set-Location $UIRoot

Write-Host "The Talking Heads - Video Generation UI" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "  OK: Docker available" -ForegroundColor Green
    }
} catch {
    Write-Host "  ERROR: Docker not available" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and try again" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Build if requested
$ComposeArgs = @()
if ($Build) {
    Write-Host "Building Docker images..." -ForegroundColor Cyan
    docker-compose build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

# Start services
Write-Host "Starting services..." -ForegroundColor Cyan
$Command = "docker-compose up"
if ($Detached) {
    $Command += " -d"
    Write-Host "  Starting in detached mode..." -ForegroundColor Yellow
}

Invoke-Expression $Command

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 40 -ForegroundColor Cyan
    Write-Host "Services started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access your UI:" -ForegroundColor Yellow
    Write-Host "  Frontend:  http://localhost:3001" -ForegroundColor White
    Write-Host "  API:       http://localhost:8001/api" -ForegroundColor White
    Write-Host "=" * 40 -ForegroundColor Cyan
    Write-Host ""
    
    if ($Logs) {
        Write-Host "Showing logs (Ctrl+C to exit)..." -ForegroundColor Yellow
        docker-compose logs -f
    } elseif ($Detached) {
        Write-Host "View logs with: docker-compose logs -f" -ForegroundColor Gray
        Write-Host "Stop services with: docker-compose down" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "Failed to start services" -ForegroundColor Red
    exit 1
}

