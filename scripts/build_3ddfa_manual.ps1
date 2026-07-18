# Build 3DDFA Extensions - Manual VS Environment Setup
# This avoids the distutils VS detection issue

$ErrorActionPreference = "Stop"

Write-Host "=== Building 3DDFA Extensions ===" -ForegroundColor Cyan
Write-Host ""

# Find Visual Studio
$vsPath = "C:\Program Files\Microsoft Visual Studio\18\Community"
if (-not (Test-Path $vsPath)) {
    if (Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe") {
        $vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
    }
}

if (-not $vsPath -or -not (Test-Path $vsPath)) {
    Write-Host "[ERROR] Visual Studio not found" -ForegroundColor Red
    exit 1
}

$vcvarsPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
if (-not (Test-Path $vcvarsPath)) {
    Write-Host "[ERROR] vcvars64.bat not found" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Using Visual Studio at: $vsPath" -ForegroundColor Green
Write-Host ""

# Initialize VS environment by calling vcvars64.bat and capturing key variables
Write-Host "1. Initializing Visual Studio environment..." -ForegroundColor Yellow
$envScript = @"
@echo off
call "$vcvarsPath" >nul 2>&1
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
echo PATH=%PATH%
echo INCLUDE=%INCLUDE%
echo LIB=%LIB%
echo VCINSTALLDIR=%VCINSTALLDIR%
exit /b 0
"@

$tempEnvBat = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.bat'
$envScript | Out-File -FilePath $tempEnvBat -Encoding ASCII -NoNewline

try {
    $envOutput = cmd /c $tempEnvBat 2>&1 | Where-Object { $_ -match '^[A-Z_]+=' }
    
    foreach ($line in $envOutput) {
        if ($line -match '^PATH=(.+)$') {
            $env:PATH = $matches[1] + ';' + $env:PATH
        } elseif ($line -match '^INCLUDE=(.+)$') {
            $env:INCLUDE = $matches[1]
        } elseif ($line -match '^LIB=(.+)$') {
            $env:LIB = $matches[1]
        } elseif ($line -match '^VCINSTALLDIR=(.+)$') {
            $env:VCINSTALLDIR = $matches[1]
        }
    }
    
    # Verify compiler
    $clPath = Get-Command cl -ErrorAction SilentlyContinue
    if (-not $clPath) {
        Write-Host "[ERROR] Failed to initialize VS environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] VS environment initialized" -ForegroundColor Green
} finally {
    Remove-Item $tempEnvBat -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "2. Building FaceBoxes NMS extension..." -ForegroundColor Yellow
$faceboxesUtilsPath = "d:\dev\3DDFA_V2\FaceBoxes\utils"
if (-not (Test-Path $faceboxesUtilsPath)) {
    Write-Host "[ERROR] 3DDFA_V2 not found" -ForegroundColor Red
    exit 1
}

Push-Location $faceboxesUtilsPath
try {
    # Set distutils to use our compiler directly
    $env:DISTUTILS_USE_SDK = "1"
    
    python build.py build_ext --inplace
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to build FaceBoxes extension" -ForegroundColor Red
        Write-Host "[INFO] Check error messages above" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "[OK] FaceBoxes extension built" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "3. Building Sim3DR extension..." -ForegroundColor Yellow
$sim3drPath = "d:\dev\3DDFA_V2\Sim3DR"
Push-Location $sim3drPath
try {
    python setup.py build_ext --inplace
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to build Sim3DR extension" -ForegroundColor Red
        Write-Host "[INFO] Check error messages above" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "[OK] Sim3DR extension built" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== 3DDFA Build Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test 3DDFA: python d:\dev\3DDFA_V2\demo.py -f examples/inputs/emma.jpg" -ForegroundColor White

