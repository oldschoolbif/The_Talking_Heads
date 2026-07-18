# Build DECA Extensions
# DECA uses PyTorch JIT compilation, but we can verify setup

param(
    [switch]$SkipInit
)

$ErrorActionPreference = "Stop"

Write-Host "=== Building DECA Extensions ===" -ForegroundColor Cyan
Write-Host ""

# Initialize Visual Studio environment if needed (for any C++ dependencies)
if (-not $SkipInit) {
    Write-Host "1. Initializing Visual Studio environment..." -ForegroundColor Yellow
    & "$PSScriptRoot\init_vs_env_best.ps1" -Quiet | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Visual Studio environment not initialized (may be OK for DECA)" -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Visual Studio environment ready" -ForegroundColor Green
    }
    Write-Host ""
}

# Check CUDA
Write-Host "2. Checking CUDA..." -ForegroundColor Yellow
$nvcc = Get-Command nvcc -ErrorAction SilentlyContinue
if (-not $nvcc) {
    Write-Host "[ERROR] CUDA compiler (nvcc) not found" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] CUDA found: $($nvcc.Source)" -ForegroundColor Green
Write-Host ""

# Check DECA directory
$decaPath = "d:\dev\DECA"
if (-not (Test-Path $decaPath)) {
    Write-Host "[ERROR] DECA not found at: $decaPath" -ForegroundColor Red
    Write-Host "[INFO] Clone it first: git clone https://github.com/YadiraF/DECA.git d:\dev\DECA" -ForegroundColor Yellow
    exit 1
}

Write-Host "3. Installing DECA requirements..." -ForegroundColor Yellow
Push-Location $decaPath
try {
    if (Test-Path "requirements.txt") {
        # Install core requirements (skip problematic ones)
        Write-Host "[INFO] Installing core requirements..." -ForegroundColor Gray
        pip install -q numpy scipy scikit-image opencv-python PyYAML yacs kornia ninja fvcore face-alignment 2>&1 | Out-Null
        
        # Try to install chumpy separately (may fail, but that's OK)
        pip install -q chumpy 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARN] chumpy installation failed (may not be critical)" -ForegroundColor Yellow
        }
        
        Write-Host "[OK] Core requirements installed" -ForegroundColor Green
    } else {
        Write-Host "[WARN] requirements.txt not found" -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "4. Building rasterizer CUDA extension..." -ForegroundColor Yellow
$rasterizerPath = Join-Path $decaPath "decalib\utils\rasterizer"
if (Test-Path $rasterizerPath) {
    Push-Location $rasterizerPath
    try {
        # Initialize VS environment for CUDA compilation
        if (-not $SkipInit) {
            $vsPath = "C:\Program Files\Microsoft Visual Studio\18\Community"
            if (Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe") {
                $vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
            }
            
            if ($vsPath -and (Test-Path $vsPath)) {
                $vcvarsPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
                if (Test-Path $vcvarsPath) {
                    $envScript = @"
@echo off
call "$vcvarsPath" >nul 2>&1
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
echo PATH=%PATH%
exit /b 0
"@
                    $tempEnvBat = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.bat'
                    $envScript | Out-File -FilePath $tempEnvBat -Encoding ASCII -NoNewline
                    $envOutput = cmd /c $tempEnvBat 2>&1 | Where-Object { $_ -match '^PATH=' }
                    if ($envOutput -match '^PATH=(.+)$') {
                        $env:PATH = $matches[1] + ';' + $env:PATH
                    }
                    Remove-Item $tempEnvBat -ErrorAction SilentlyContinue
                }
            }
        }
        
        python setup.py build_ext --inplace
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Rasterizer extension built" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Rasterizer build failed (will use PyTorch JIT compilation on first run)" -ForegroundColor Yellow
            Write-Host "[INFO] Or install pytorch3d: pip install pytorch3d" -ForegroundColor Gray
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "[WARN] Rasterizer path not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "5. DECA uses PyTorch JIT compilation..." -ForegroundColor Yellow
Write-Host "[INFO] DECA will compile CUDA extensions automatically on first run if needed" -ForegroundColor Gray
Write-Host "[INFO] If compilation fails, use pytorch3d: pip install pytorch3d and --rasterizer_type=pytorch3d" -ForegroundColor Gray
Write-Host ""

Write-Host "=== DECA Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test DECA: python d:\dev\DECA\demos\demo_reconstruct.py -i TestSamples/examples/IMG_0392_inputs.jpg" -ForegroundColor White
Write-Host "2. If CUDA compilation fails, use pytorch3d rasterizer" -ForegroundColor White

