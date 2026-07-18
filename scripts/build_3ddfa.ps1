# Build 3DDFA Extensions
# This script initializes VS environment and builds 3DDFA Cython extensions

param(
    [switch]$SkipInit
)

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

# Initialize VS environment if needed
if (-not $SkipInit) {
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
}

# Verify compiler is available
$clPath = Get-Command cl -ErrorAction SilentlyContinue
if (-not $clPath) {
    Write-Host "[ERROR] C++ compiler not found. Run init_vs_env_best.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "2. Building FaceBoxes NMS extension..." -ForegroundColor Yellow
$faceboxesPath = "d:\dev\3DDFA_V2\FaceBoxes"
if (-not (Test-Path $faceboxesPath)) {
    Write-Host "[ERROR] 3DDFA_V2 not found at: $faceboxesPath" -ForegroundColor Red
    Write-Host "[INFO] Clone it first: git clone https://github.com/cleardusk/3DDFA_V2.git d:\dev\3DDFA_V2" -ForegroundColor Yellow
    exit 1
}

# FaceBoxes build: cd utils, then python build.py build_ext --inplace
$faceboxesUtilsPath = Join-Path $faceboxesPath "utils"
Push-Location $faceboxesUtilsPath
try {
    $env:DISTUTILS_USE_SDK = "1"
    python build.py build_ext --inplace
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to build FaceBoxes extension" -ForegroundColor Red
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
    $env:DISTUTILS_USE_SDK = "1"
    python setup.py build_ext --inplace
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to build Sim3DR extension" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Sim3DR extension built" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "4. Building render extension (optional)..." -ForegroundColor Yellow
$renderPath = "d:\dev\3DDFA_V2\utils\asset"
if (Test-Path $renderPath) {
    Push-Location $renderPath
    try {
        # On Windows, we can use cl.exe (MSVC) or gcc (MinGW)
        # Try cl.exe first (from VS environment)
        $clPath = Get-Command cl -ErrorAction SilentlyContinue
        if ($clPath) {
            Write-Host "[INFO] Using MSVC compiler (cl.exe)" -ForegroundColor Gray
            # Compile as DLL on Windows
            cl /LD /O2 render.c /Fe:render.dll 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0 -and (Test-Path "render.dll")) {
                Write-Host "[OK] Render extension built (render.dll)" -ForegroundColor Green
            } else {
                Write-Host "[WARN] Render extension build failed (optional, can use Python fallback)" -ForegroundColor Yellow
            }
        } else {
            # Try gcc (MinGW)
            $gccPath = Get-Command gcc -ErrorAction SilentlyContinue
            if ($gccPath) {
                Write-Host "[INFO] Using GCC compiler" -ForegroundColor Gray
                gcc -shared -Wall -O3 render.c -o render.dll -fPIC 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0 -and (Test-Path "render.dll")) {
                    Write-Host "[OK] Render extension built (render.dll)" -ForegroundColor Green
                } else {
                    Write-Host "[WARN] Render extension build failed (optional)" -ForegroundColor Yellow
                }
            } else {
                Write-Host "[WARN] No C compiler found for render extension (optional)" -ForegroundColor Yellow
                Write-Host "[INFO] 3DDFA will use Python fallback for rendering" -ForegroundColor Gray
            }
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "[WARN] Render path not found (optional)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== 3DDFA Build Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test 3DDFA: python d:\dev\3DDFA_V2\demo.py -f examples/inputs/emma.jpg" -ForegroundColor White
Write-Host "2. Build DECA extensions (if needed)" -ForegroundColor White

