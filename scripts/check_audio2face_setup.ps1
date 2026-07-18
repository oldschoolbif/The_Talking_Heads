# Audio2Face Setup Check Script
# Checks if Audio2Face is installed and configured

Write-Host "=== Audio2Face Setup Check ===" -ForegroundColor Cyan
Write-Host ""

# Check 1: Omniverse Installation
Write-Host "1. Checking Omniverse installation..." -ForegroundColor Yellow
$ovPath = "$env:LOCALAPPDATA\ov\pkg"
if (Test-Path $ovPath) {
    Write-Host "   ✅ Omniverse found at: $ovPath" -ForegroundColor Green
    $ovSize = (Get-ChildItem $ovPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "   📦 Size: $([math]::Round($ovSize, 2)) GB" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Omniverse not found at: $ovPath" -ForegroundColor Red
    Write-Host "   💡 Install from: https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html" -ForegroundColor Yellow
}

Write-Host ""

# Check 2: Audio2Face Extension
Write-Host "2. Checking Audio2Face extension..." -ForegroundColor Yellow
$a2fPaths = @(
    "$env:LOCALAPPDATA\ov\pkg\omni.audio2face",
    "$env:LOCALAPPDATA\ov\pkg\exts\omni.audio2face",
    "C:\Program Files\NVIDIA\Audio2Face",
    "C:\Program Files (x86)\NVIDIA\Audio2Face"
)

$a2fFound = $false
foreach ($path in $a2fPaths) {
    if (Test-Path $path) {
        Write-Host "   ✅ Audio2Face found at: $path" -ForegroundColor Green
        $a2fFound = $true
        
        # Check for executable
        $exe = Get-ChildItem $path -Filter "*.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($exe) {
            Write-Host "   📄 Executable: $($exe.FullName)" -ForegroundColor Gray
        }
        break
    }
}

if (-not $a2fFound) {
    Write-Host "   ❌ Audio2Face extension not found" -ForegroundColor Red
    Write-Host "   💡 Download from: https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html" -ForegroundColor Yellow
}

Write-Host ""

# Check 3: Python Package (py_audio2face)
Write-Host "3. Checking py_audio2face Python package..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Python found: $pythonVersion" -ForegroundColor Green
    
    $pyA2f = pip show py-audio2face 2>&1
    if ($pyA2f -match "Name: py-audio2face") {
        Write-Host "   ✅ py_audio2face installed" -ForegroundColor Green
        $version = ($pyA2f | Select-String "Version:").ToString()
        Write-Host "   📦 $version" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  py_audio2face not installed" -ForegroundColor Yellow
        Write-Host "   💡 Install with: pip install py-audio2face" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Python not found or not in PATH" -ForegroundColor Red
}

Write-Host ""

# Check 4: Character USD Files
Write-Host "4. Checking for character USD files..." -ForegroundColor Yellow
$usdPaths = @(
    ".\examples\personas\*.usd",
    ".\assets\characters\*.usd",
    ".\characters\*.usd"
)

$usdFound = $false
foreach ($pattern in $usdPaths) {
    $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "   ✅ Found USD files:" -ForegroundColor Green
        foreach ($file in $files) {
            Write-Host "      📄 $($file.FullName)" -ForegroundColor Gray
        }
        $usdFound = $true
    }
}

if (-not $usdFound) {
    Write-Host "   ⚠️  No character USD files found" -ForegroundColor Yellow
    Write-Host "   💡 You'll need USD character files for Audio2Face" -ForegroundColor Yellow
    Write-Host "   💡 Get from: Omniverse Asset Store or create in Omniverse Create" -ForegroundColor Yellow
}

Write-Host ""

# Summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host ""

if ($a2fFound) {
    Write-Host "✅ Audio2Face appears to be installed" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Launch Audio2Face GUI to verify it works" -ForegroundColor White
    Write-Host "2. Check if headless server is available" -ForegroundColor White
    Write-Host "3. Install py_audio2face: pip install py-audio2face" -ForegroundColor White
    Write-Host "4. Get character USD files if you don't have them" -ForegroundColor White
} else {
    Write-Host "❌ Audio2Face not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Download Audio2Face standalone:" -ForegroundColor White
    Write-Host "   https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html" -ForegroundColor Cyan
    Write-Host "2. Install following their instructions" -ForegroundColor White
    Write-Host "3. Run this script again to verify" -ForegroundColor White
}

Write-Host ""

