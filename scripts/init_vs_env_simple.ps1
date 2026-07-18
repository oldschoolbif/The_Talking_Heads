# Simple Visual Studio Environment Initializer
# Alternative method using cmd.exe to run vcvars64.bat

param(
    [switch]$Quiet
)

$vsPath = "C:\Program Files\Microsoft Visual Studio\18\Community"

if (-not (Test-Path $vsPath)) {
    # Try to find VS using vswhere
    if (Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe") {
        $vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
    }
}

if (-not $vsPath -or -not (Test-Path $vsPath)) {
    if (-not $Quiet) {
        Write-Host "[ERROR] Visual Studio not found" -ForegroundColor Red
    }
    exit 1
}

$vcvarsPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"

if (-not (Test-Path $vcvarsPath)) {
    if (-not $Quiet) {
        Write-Host "[ERROR] vcvars64.bat not found" -ForegroundColor Red
    }
    exit 1
}

# Use cmd.exe to run vcvars64.bat and set environment
# This method spawns cmd.exe which inherits the environment
$cmdScript = @"
@echo off
call "$vcvarsPath" >nul 2>&1
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
powershell.exe -NoProfile -Command "& { `$env:PATH = '%PATH%'; `$env:INCLUDE = '%INCLUDE%'; `$env:LIB = '%LIB%'; `$env:LIBPATH = '%LIBPATH%'; `$env:VCINSTALLDIR = '%VCINSTALLDIR%'; `$env:VCToolsInstallDir = '%VCToolsInstallDir%'; Get-Command cl -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source }"
"@

$tempBat = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.bat'
$cmdScript | Out-File -FilePath $tempBat -Encoding ASCII

try {
    $clPath = cmd /c $tempBat 2>&1 | Select-Object -Last 1
    
    if ($clPath -and (Test-Path $clPath)) {
        if (-not $Quiet) {
            Write-Host "[OK] Visual Studio environment initialized" -ForegroundColor Green
            Write-Host "[OK] C++ compiler: $clPath" -ForegroundColor Green
        }
        
        # Set environment variables in current PowerShell session
        # We need to parse them from cmd.exe
        $envScript = @"
@echo off
call "$vcvarsPath" >nul 2>&1
echo PATH=%PATH%
echo INCLUDE=%INCLUDE%
echo LIB=%LIB%
echo VCINSTALLDIR=%VCINSTALLDIR%
"@
        
        $envBat = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.bat'
        $envScript | Out-File -FilePath $envBat -Encoding ASCII
        
        $envOutput = cmd /c $envBat 2>&1
        Remove-Item $envBat -ErrorAction SilentlyContinue
        
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
        
        return $true
    } else {
        if (-not $Quiet) {
            Write-Host "[ERROR] Failed to initialize Visual Studio environment" -ForegroundColor Red
        }
        return $false
    }
} finally {
    Remove-Item $tempBat -ErrorAction SilentlyContinue
}

