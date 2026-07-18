# Build Audio2Face-3D-SDK Script
# This script builds the Audio2Face SDK step by step

param(
    [string]$TensorRTPath = "D:\dev\TensorRT-10.14.1.48",
    [string]$CUDAPath = $env:CUDA_PATH,
    [switch]$SkipDeps = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Building Audio2Face-3D-SDK ===" -ForegroundColor Cyan
Write-Host ""

# Change to SDK directory
$sdkPath = "d:\dev\Audio2Face-3D-SDK"
if (-not (Test-Path $sdkPath)) {
    Write-Host "[ERROR] SDK directory not found: $sdkPath" -ForegroundColor Red
    exit 1
}

Set-Location $sdkPath
Write-Host "[OK] Changed to SDK directory: $sdkPath" -ForegroundColor Green

# Step 1: Pull Git LFS files
Write-Host "`n[1/5] Pulling Git LFS files..." -ForegroundColor Yellow
try {
    git lfs pull 2>&1 | Out-Null
    Write-Host "[OK] Git LFS files pulled" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Git LFS pull failed or not needed: $_" -ForegroundColor Yellow
}

# Step 2: Fetch dependencies
if (-not $SkipDeps) {
    Write-Host "`n[2/5] Fetching dependencies (this may take a while)..." -ForegroundColor Yellow
    try {
        & .\fetch_deps.bat release
        if ($LASTEXITCODE -ne 0) {
            throw "fetch_deps.bat failed with exit code $LASTEXITCODE"
        }
        Write-Host "[OK] Dependencies fetched" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to fetch dependencies: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n[2/5] Skipping dependency fetch (--SkipDeps specified)" -ForegroundColor Yellow
}

# Step 3: Set environment variables
Write-Host "`n[3/5] Setting environment variables..." -ForegroundColor Yellow

if ($TensorRTPath) {
    $env:TENSORRT_ROOT_DIR = $TensorRTPath
    Write-Host "[OK] TENSORRT_ROOT_DIR set to: $TensorRTPath" -ForegroundColor Green
} else {
    Write-Host "[WARN] TENSORRT_ROOT_DIR not set. You may need to set it manually:" -ForegroundColor Yellow
    Write-Host "  `$env:TENSORRT_ROOT_DIR = 'C:\path\to\tensorrt'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Do you want to continue anyway? (y/n)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Build cancelled." -ForegroundColor Yellow
        exit 0
    }
}

if ($CUDAPath) {
    $env:CUDA_PATH = $CUDAPath
    Write-Host "[OK] CUDA_PATH set to: $CUDAPath" -ForegroundColor Green
} else {
    Write-Host "[WARN] CUDA_PATH not set. Build may fail." -ForegroundColor Yellow
}

# Step 4: Clean build (optional but recommended)
Write-Host "`n[4/5] Cleaning previous build..." -ForegroundColor Yellow
try {
    & .\build.bat clean release 2>&1 | Out-Null
    Write-Host "[OK] Clean completed" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Clean failed (may not be needed): $_" -ForegroundColor Yellow
}

# Step 5: Build SDK
Write-Host "`n[5/5] Building SDK (this will take a while)..." -ForegroundColor Yellow
Write-Host "Environment variables:" -ForegroundColor Cyan
Write-Host "  TENSORRT_ROOT_DIR: $env:TENSORRT_ROOT_DIR" -ForegroundColor Cyan
Write-Host "  CUDA_PATH: $env:CUDA_PATH" -ForegroundColor Cyan
Write-Host ""

try {
    & .\build.bat all release
    if ($LASTEXITCODE -ne 0) {
        throw "build.bat failed with exit code $LASTEXITCODE"
    }
    Write-Host "`n[OK] Build completed successfully!" -ForegroundColor Green
    Write-Host "`nBuild output location: $sdkPath\_build\release" -ForegroundColor Cyan
} catch {
    Write-Host "`n[ERROR] Build failed: $_" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Ensure TensorRT is installed and TENSORRT_ROOT_DIR is set correctly" -ForegroundColor Yellow
    Write-Host "  2. Ensure CUDA 12.8-12.9 is installed (you have 13.0, which may work)" -ForegroundColor Yellow
    Write-Host "  3. Ensure Visual Studio 2022 with C++ tools is installed" -ForegroundColor Yellow
    Write-Host "  4. Check build logs in: $sdkPath\_build" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n=== Build Complete ===" -ForegroundColor Green

