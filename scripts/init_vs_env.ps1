# Initialize Visual Studio Build Environment
# This script sets up the C++ compiler environment in PowerShell

$ErrorActionPreference = "Stop"

# Find Visual Studio installation
$vsPath = $null
if (Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe") {
    $vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
}

if (-not $vsPath -or -not (Test-Path $vsPath)) {
    # Try common installation paths
    $commonPaths = @(
        "C:\Program Files\Microsoft Visual Studio\2022\Community",
        "C:\Program Files\Microsoft Visual Studio\2022\BuildTools",
        "C:\Program Files\Microsoft Visual Studio\18\Community",
        "C:\Program Files (x86)\Microsoft Visual Studio\2022\Community",
        "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $vsPath = $path
            break
        }
    }
}

if (-not $vsPath -or -not (Test-Path $vsPath)) {
    Write-Host "[ERROR] Visual Studio not found. Please install Visual Studio Build Tools." -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Found Visual Studio at: $vsPath" -ForegroundColor Green

# Find vcvars64.bat or vcvarsall.bat
$vcvarsPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
if (-not (Test-Path $vcvarsPath)) {
    $vcvarsPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvarsall.bat"
}

if (-not (Test-Path $vcvarsPath)) {
    Write-Host "[ERROR] vcvars64.bat not found at: $vcvarsPath" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Using: $vcvarsPath" -ForegroundColor Green

# Call vcvars64.bat and capture environment variables
# We need to use cmd.exe to run the batch file and capture its output
$tempFile = [System.IO.Path]::GetTempFileName()
$cmdOutput = cmd /c "`"$vcvarsPath`" > `"$tempFile`" 2>&1 && set"

if ($LASTEXITCODE -ne 0) {
    $errorOutput = Get-Content $tempFile -ErrorAction SilentlyContinue
    Write-Host "[ERROR] Failed to initialize Visual Studio environment" -ForegroundColor Red
    Write-Host $errorOutput -ForegroundColor Red
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    exit 1
}

# Parse environment variables from cmd output
$envVars = cmd /c "`"$vcvarsPath`" >nul 2>&1 && set" | Where-Object { $_ -match '^[^=]+=.*' }

foreach ($line in $envVars) {
    if ($line -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        
        # Set environment variable in current session
        [System.Environment]::SetEnvironmentVariable($name, $value, [System.EnvironmentVariableTarget]::Process)
        $env:$name = $value
    }
}

Remove-Item $tempFile -ErrorAction SilentlyContinue

# Verify compiler is now available
$clPath = Get-Command cl -ErrorAction SilentlyContinue
if ($clPath) {
    Write-Host "[OK] C++ compiler initialized: $($clPath.Source)" -ForegroundColor Green
    Write-Host "[OK] Visual Studio environment ready!" -ForegroundColor Green
    return $true
} else {
    Write-Host "[WARN] C++ compiler not found after initialization" -ForegroundColor Yellow
    Write-Host "[INFO] Try running this script in a new PowerShell session" -ForegroundColor Yellow
    return $false
}

