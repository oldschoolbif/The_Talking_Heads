# Setup TensorRT Environment Variables
# Run this script before building Audio2Face SDK

param(
    [string]$TensorRTPath = "D:\dev\TensorRT-10.14.1.48"
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Setting up TensorRT Environment ===" -ForegroundColor Cyan
Write-Host ""

# Verify TensorRT path exists
if (-not (Test-Path $TensorRTPath)) {
    Write-Host "[ERROR] TensorRT path not found: $TensorRTPath" -ForegroundColor Red
    Write-Host "Please verify the path and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] TensorRT found at: $TensorRTPath" -ForegroundColor Green

# Set TENSORRT_ROOT_DIR
$env:TENSORRT_ROOT_DIR = $TensorRTPath
Write-Host "[OK] TENSORRT_ROOT_DIR = $env:TENSORRT_ROOT_DIR" -ForegroundColor Green

# Check TensorRT structure
Write-Host "`nChecking TensorRT structure..." -ForegroundColor Yellow
$libPath = Join-Path $TensorRTPath "lib"
$includePath = Join-Path $TensorRTPath "include"
$binPath = Join-Path $TensorRTPath "bin"

$pathsToAdd = @()

if (Test-Path $libPath) {
    Write-Host "[OK] lib directory found" -ForegroundColor Green
    $pathsToAdd += $libPath
} else {
    Write-Host "[WARN] lib directory not found" -ForegroundColor Yellow
}

if (Test-Path $includePath) {
    Write-Host "[OK] include directory found" -ForegroundColor Green
} else {
    Write-Host "[WARN] include directory not found" -ForegroundColor Yellow
}

if (Test-Path $binPath) {
    Write-Host "[OK] bin directory found" -ForegroundColor Green
    $pathsToAdd += $binPath
} else {
    Write-Host "[WARN] bin directory not found" -ForegroundColor Yellow
}

# Add TensorRT paths to PATH if not already present
Write-Host "`nUpdating PATH..." -ForegroundColor Yellow
foreach ($path in $pathsToAdd) {
    if ($env:PATH -notlike "*$path*") {
        $env:PATH = "$path;$env:PATH"
        Write-Host "[OK] Added to PATH: $path" -ForegroundColor Green
    } else {
        Write-Host "[OK] Already in PATH: $path" -ForegroundColor Green
    }
}

# Display current environment
Write-Host "`n=== Environment Variables ===" -ForegroundColor Cyan
Write-Host "TENSORRT_ROOT_DIR: $env:TENSORRT_ROOT_DIR"
Write-Host "CUDA_PATH: $env:CUDA_PATH"
Write-Host ""

# Verify CUDA is set
if (-not $env:CUDA_PATH) {
    Write-Host "[WARN] CUDA_PATH not set. Build may fail." -ForegroundColor Yellow
    Write-Host "Set it with: `$env:CUDA_PATH = 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0'" -ForegroundColor Yellow
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "`nTo use these settings, run this script before building:" -ForegroundColor Yellow
Write-Host "  .\scripts\setup_tensorrt_env.ps1" -ForegroundColor White
Write-Host "`nOr set manually:" -ForegroundColor Yellow
Write-Host "  `$env:TENSORRT_ROOT_DIR = '$TensorRTPath'" -ForegroundColor White
Write-Host ""

