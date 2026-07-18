# Best Method: Initialize Visual Studio Environment in PowerShell
# This uses cmd.exe to run vcvars64.bat and captures all environment variables

param(
    [switch]$Quiet
)

function Initialize-VSEnvironment {
    # Find Visual Studio
    $vsPath = $null
    
    if (Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe") {
        $vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
    }
    
    if (-not $vsPath -or -not (Test-Path $vsPath)) {
        # Try common paths
        $commonPaths = @(
            "C:\Program Files\Microsoft Visual Studio\18\Community",
            "C:\Program Files\Microsoft Visual Studio\2022\Community",
            "C:\Program Files\Microsoft Visual Studio\2022\BuildTools"
        )
        
        foreach ($path in $commonPaths) {
            if (Test-Path $path) {
                $vsPath = $path
                break
            }
        }
    }
    
    if (-not $vsPath -or -not (Test-Path $vsPath)) {
        if (-not $Quiet) {
            Write-Host "[ERROR] Visual Studio not found" -ForegroundColor Red
        }
        return $false
    }
    
    # Find vcvars64.bat
    $vcvarsPath = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"
    if (-not (Test-Path $vcvarsPath)) {
        if (-not $Quiet) {
            Write-Host "[ERROR] vcvars64.bat not found at: $vcvarsPath" -ForegroundColor Red
        }
        return $false
    }
    
    # Create a temporary batch file that runs vcvars64.bat and outputs all env vars
    $tempBat = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.bat'
    
    $batContent = @"
@echo off
call "$vcvarsPath" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to initialize Visual Studio environment
    exit /b %ERRORLEVEL%
)
set
"@
    
    $batContent | Out-File -FilePath $tempBat -Encoding ASCII -NoNewline
    
    try {
        # Run the batch file and capture all environment variables
        $envOutput = cmd /c $tempBat 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            if (-not $Quiet) {
                Write-Host "[ERROR] Failed to initialize Visual Studio environment" -ForegroundColor Red
                Write-Host ($envOutput -join "`n") -ForegroundColor Red
            }
            return $false
        }
        
        # Parse and set environment variables
        $varsSet = 0
        foreach ($line in $envOutput) {
            if ($line -match '^([^=]+)=(.*)$') {
                $varName = $matches[1]
                $varValue = $matches[2]
                
                # Set in current PowerShell session
                Set-Item -Path "env:$varName" -Value $varValue -ErrorAction SilentlyContinue
                $varsSet++
            }
        }
        
        # Verify compiler is available
        $clPath = Get-Command cl -ErrorAction SilentlyContinue
        if ($clPath) {
            if (-not $Quiet) {
                Write-Host "[OK] Visual Studio environment initialized" -ForegroundColor Green
                Write-Host "[OK] C++ compiler: $($clPath.Source)" -ForegroundColor Green
                Write-Host "[OK] Set $varsSet environment variables" -ForegroundColor Gray
            }
            return $true
        } else {
            if (-not $Quiet) {
                Write-Host "[WARN] Environment initialized but compiler not found in PATH" -ForegroundColor Yellow
            }
            return $false
        }
    } finally {
        Remove-Item $tempBat -ErrorAction SilentlyContinue
    }
}

# Initialize
Initialize-VSEnvironment

