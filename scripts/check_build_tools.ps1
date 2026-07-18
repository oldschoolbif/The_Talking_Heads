# Check Build Tools for 3D Reconstruction
# Checks for Visual Studio Build Tools and CUDA

Write-Host "=== Checking Build Tools for 3D Reconstruction ===" -ForegroundColor Cyan
Write-Host ""

# Check Visual Studio Build Tools
Write-Host "1. Checking Visual Studio Build Tools..." -ForegroundColor Yellow
$vsPath = $null
try {
    $vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
    if ($vsPath) {
        Write-Host "   [OK] Visual Studio found: $vsPath" -ForegroundColor Green
        
        # Check for C++ compiler
        $clPath = Join-Path $vsPath "VC\Tools\MSVC"
        if (Test-Path $clPath) {
            $msvcVersions = Get-ChildItem $clPath -Directory | Sort-Object Name -Descending | Select-Object -First 1
            if ($msvcVersions) {
                $clExe = Join-Path $msvcVersions.FullName "bin\Hostx64\x64\cl.exe"
                if (Test-Path $clExe) {
                    Write-Host "   [OK] C++ compiler found: $clExe" -ForegroundColor Green
                } else {
                    Write-Host "   [WARN] C++ compiler not found at expected location" -ForegroundColor Yellow
                }
            }
        }
    } else {
        Write-Host "   [FAIL] Visual Studio Build Tools not found" -ForegroundColor Red
        Write-Host ""
        Write-Host "   To install:" -ForegroundColor Yellow
        Write-Host "   1. Download: https://visualstudio.microsoft.com/downloads/" -ForegroundColor White
        Write-Host "   2. Select 'Build Tools for Visual Studio 2022'" -ForegroundColor White
        Write-Host "   3. Install 'C++ build tools' workload" -ForegroundColor White
    }
} catch {
    Write-Host "   [FAIL] Could not check for Visual Studio" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check C++ compiler in PATH
Write-Host ""
Write-Host "2. Checking C++ compiler in PATH..." -ForegroundColor Yellow
$clInPath = Get-Command cl -ErrorAction SilentlyContinue
if ($clInPath) {
    Write-Host "   [OK] C++ compiler (cl.exe) found in PATH" -ForegroundColor Green
    Write-Host "   Location: $($clInPath.Source)" -ForegroundColor Gray
} else {
    Write-Host "   [WARN] C++ compiler not in PATH" -ForegroundColor Yellow
    Write-Host "   [INFO] You may need to open 'Developer Command Prompt' or restart PowerShell" -ForegroundColor Gray
}

# Check CUDA
Write-Host ""
Write-Host "3. Checking CUDA Toolkit..." -ForegroundColor Yellow
try {
    $cudaVersion = nvcc --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] CUDA Toolkit found" -ForegroundColor Green
        $cudaVersion | Select-Object -First 3 | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    } else {
        Write-Host "   [FAIL] CUDA Toolkit not found" -ForegroundColor Red
        Write-Host ""
        Write-Host "   To install:" -ForegroundColor Yellow
        Write-Host "   1. Check PyTorch CUDA version:" -ForegroundColor White
        Write-Host "      python -c `"import torch; print('PyTorch CUDA:', torch.version.cuda)`"" -ForegroundColor Gray
        Write-Host "   2. Download matching CUDA Toolkit:" -ForegroundColor White
        Write-Host "      https://developer.nvidia.com/cuda-downloads" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   [FAIL] Could not check CUDA" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Check PyTorch CUDA version
Write-Host ""
Write-Host "4. Checking PyTorch CUDA version..." -ForegroundColor Yellow
try {
    $pytorchCuda = python -c "import torch; print(torch.version.cuda)" 2>&1
    if ($pytorchCuda -and $pytorchCuda -ne "None") {
        Write-Host "   [OK] PyTorch CUDA version: $pytorchCuda" -ForegroundColor Green
        Write-Host "   [INFO] Install CUDA Toolkit version $($pytorchCuda.Split('.')[0]).x to match" -ForegroundColor Gray
    } else {
        Write-Host "   [WARN] PyTorch built without CUDA support" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [FAIL] Could not check PyTorch CUDA" -ForegroundColor Red
}

# Check Cython
Write-Host ""
Write-Host "5. Checking Cython..." -ForegroundColor Yellow
try {
    $cythonVersion = python -c "import Cython; print(Cython.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Cython installed: $cythonVersion" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] Cython not installed" -ForegroundColor Yellow
        Write-Host "   [INFO] Install with: pip install cython" -ForegroundColor Gray
    }
} catch {
    Write-Host "   [WARN] Cython not installed" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host ""

$allGood = $true
if (-not $vsPath) {
    Write-Host "[ACTION REQUIRED] Install Visual Studio Build Tools" -ForegroundColor Red
    $allGood = $false
}
if (-not (Get-Command cl -ErrorAction SilentlyContinue)) {
    Write-Host "[ACTION REQUIRED] C++ compiler not in PATH (restart PowerShell after install)" -ForegroundColor Red
    $allGood = $false
}
if (-not (Get-Command nvcc -ErrorAction SilentlyContinue)) {
    Write-Host "[ACTION REQUIRED] Install CUDA Toolkit" -ForegroundColor Red
    $allGood = $false
}

if ($allGood) {
    Write-Host "[OK] All build tools are ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Build 3DDFA extensions" -ForegroundColor White
    Write-Host "2. Build DECA extensions" -ForegroundColor White
    Write-Host "3. Test 3D reconstruction" -ForegroundColor White
} else {
    Write-Host "[INFO] Install missing tools, then run this script again" -ForegroundColor Yellow
}

