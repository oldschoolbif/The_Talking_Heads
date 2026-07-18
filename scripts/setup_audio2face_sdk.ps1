# Audio2Face-3D-SDK Setup Script
# Helps set up and build the Audio2Face SDK from GitHub

Write-Host "=== Audio2Face-3D-SDK Setup ===" -ForegroundColor Cyan
Write-Host ""

$sdkPath = "d:\dev\Audio2Face-3D-SDK"

# Check if SDK is cloned
if (-not (Test-Path $sdkPath)) {
    Write-Host "[FAIL] SDK not found at: $sdkPath" -ForegroundColor Red
    Write-Host "[INFO] Cloning SDK..." -ForegroundColor Yellow
    cd d:\dev
    git clone https://github.com/NVIDIA/Audio2Face-3D-SDK.git
    cd Audio2Face-3D-SDK
    git lfs pull
}

cd $sdkPath

Write-Host "[OK] SDK found at: $sdkPath" -ForegroundColor Green
Write-Host ""

# Check prerequisites
Write-Host "=== Checking Prerequisites ===" -ForegroundColor Cyan
Write-Host ""

# Check CUDA
Write-Host "1. Checking CUDA..." -ForegroundColor Yellow
$cudaPath = $env:CUDA_PATH
if ($cudaPath) {
    Write-Host "   [OK] CUDA_PATH: $cudaPath" -ForegroundColor Green
} else {
    Write-Host "   [WARN] CUDA_PATH not set" -ForegroundColor Yellow
    Write-Host "   [INFO] CUDA 12.8+ required" -ForegroundColor Gray
}

# Check TensorRT
Write-Host ""
Write-Host "2. Checking TensorRT..." -ForegroundColor Yellow
$tensorrtPath = $env:TENSORRT_ROOT_DIR
if ($tensorrtPath) {
    Write-Host "   [OK] TENSORRT_ROOT_DIR: $tensorrtPath" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] TENSORRT_ROOT_DIR not set" -ForegroundColor Red
    Write-Host "   [INFO] TensorRT 10.13+ required" -ForegroundColor Gray
    Write-Host "   [INFO] Download from: https://developer.nvidia.com/tensorrt" -ForegroundColor Cyan
}

# Check Visual Studio
Write-Host ""
Write-Host "3. Checking Visual Studio..." -ForegroundColor Yellow
$vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
if ($vsPath) {
    Write-Host "   [OK] Visual Studio found: $vsPath" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Visual Studio 2022+ not found" -ForegroundColor Red
    Write-Host "   [INFO] Install Visual Studio 2022+ with C++ tools" -ForegroundColor Gray
}

# Check Python
Write-Host ""
Write-Host "4. Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(8|9|10)") {
    Write-Host "   [OK] $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   [WARN] Python 3.8-3.10 required" -ForegroundColor Yellow
    Write-Host "   [INFO] Current: $pythonVersion" -ForegroundColor Gray
}

# Check Git LFS
Write-Host ""
Write-Host "5. Checking Git LFS..." -ForegroundColor Yellow
$gitLfs = git lfs version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Git LFS installed" -ForegroundColor Green
} else {
    Write-Host "   [FAIL] Git LFS not installed" -ForegroundColor Red
    Write-Host "   [INFO] Install from: https://git-lfs.github.com" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== Setup Steps ===" -ForegroundColor Cyan
Write-Host ""

if (-not $tensorrtPath) {
    Write-Host "[ACTION REQUIRED] Set TensorRT path:" -ForegroundColor Yellow
    Write-Host '   $env:TENSORRT_ROOT_DIR = "C:\path\to\tensorrt"' -ForegroundColor Gray
    Write-Host ""
}

Write-Host "To build the SDK, run these commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Fetch dependencies:" -ForegroundColor White
Write-Host "   cd $sdkPath" -ForegroundColor Gray
Write-Host "   .\fetch_deps.bat release" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Set environment variables:" -ForegroundColor White
Write-Host '   $env:TENSORRT_ROOT_DIR = "C:\path\to\tensorrt"' -ForegroundColor Gray
Write-Host '   $env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9"' -ForegroundColor Gray
Write-Host ""
Write-Host "3. Build SDK:" -ForegroundColor White
Write-Host "   .\build.bat all release" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Download models:" -ForegroundColor White
Write-Host "   python -m venv venv" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\activate" -ForegroundColor Gray
Write-Host "   pip install -r deps\requirements.txt" -ForegroundColor Gray
Write-Host "   hf auth login  # Hugging Face authentication" -ForegroundColor Gray
Write-Host "   .\download_models.bat" -ForegroundColor Gray
Write-Host "   .\gen_testdata.bat" -ForegroundColor Gray
Write-Host ""

# Check if we can proceed
$canProceed = $true
if (-not $tensorrtPath) {
    Write-Host "[BLOCKER] TensorRT not configured" -ForegroundColor Red
    $canProceed = $false
}
if (-not $vsPath) {
    Write-Host "[BLOCKER] Visual Studio not found" -ForegroundColor Red
    $canProceed = $false
}

if ($canProceed) {
    Write-Host "[OK] Prerequisites met! Ready to build." -ForegroundColor Green
    Write-Host ""
    Write-Host "Would you like to:" -ForegroundColor Yellow
    Write-Host "1. Fetch dependencies now" -ForegroundColor White
    Write-Host "2. Build SDK now" -ForegroundColor White
    Write-Host "3. Skip for now" -ForegroundColor White
} else {
    Write-Host "[FAIL] Missing prerequisites. Please install them first." -ForegroundColor Red
}

