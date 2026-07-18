# Build 3DDFA Extensions - Simple Version
# Uses cmd.exe to run builds with VS environment

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

# Build FaceBoxes NMS
Write-Host "1. Building FaceBoxes NMS extension..." -ForegroundColor Yellow
$faceboxesUtilsPath = "d:\dev\3DDFA_V2\FaceBoxes\utils"
if (-not (Test-Path $faceboxesUtilsPath)) {
    Write-Host "[ERROR] 3DDFA_V2 not found" -ForegroundColor Red
    exit 1
}

# Use cmd.exe to run build with VS environment
$buildScript = @"
@echo off
call "$vcvarsPath" >nul 2>&1
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
cd /d "$faceboxesUtilsPath"
python build.py build_ext --inplace
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
exit /b 0
"@

$tempBat = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.bat'
$buildScript | Out-File -FilePath $tempBat -Encoding ASCII -NoNewline

try {
    cmd /c $tempBat
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to build FaceBoxes extension" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] FaceBoxes extension built" -ForegroundColor Green
} finally {
    Remove-Item $tempBat -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "2. Building Sim3DR extension..." -ForegroundColor Yellow
$sim3drPath = "d:\dev\3DDFA_V2\Sim3DR"

$buildScript2 = @"
@echo off
call "$vcvarsPath" >nul 2>&1
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
cd /d "$sim3drPath"
python setup.py build_ext --inplace
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
exit /b 0
"@

$tempBat2 = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.bat'
$buildScript2 | Out-File -FilePath $tempBat2 -Encoding ASCII -NoNewline

try {
    cmd /c $tempBat2
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to build Sim3DR extension" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Sim3DR extension built" -ForegroundColor Green
} finally {
    Remove-Item $tempBat2 -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=== 3DDFA Build Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test 3DDFA: python d:\dev\3DDFA_V2\demo.py -f examples/inputs/emma.jpg" -ForegroundColor White

