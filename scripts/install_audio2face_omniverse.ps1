# Install Audio2Face via Omniverse
# This script helps install Audio2Face extension through Omniverse

Write-Host "=== Audio2Face Installation via Omniverse ===" -ForegroundColor Cyan
Write-Host ""

# Check if Omniverse Launcher exists
$launcherPaths = @(
    "$env:LOCALAPPDATA\ov\pkg\launcher\omni.launcher.exe",
    "$env:LOCALAPPDATA\Programs\ov\launcher\omni.launcher.exe",
    "$env:ProgramFiles\NVIDIA\Omniverse\launcher\omni.launcher.exe"
)

$launcherFound = $false
foreach ($path in $launcherPaths) {
    if (Test-Path $path) {
        Write-Host "[OK] Found Omniverse Launcher at: $path" -ForegroundColor Green
        $launcherFound = $true
        break
    }
}

if (-not $launcherFound) {
    Write-Host "[FAIL] Omniverse Launcher not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "1. Install Audio2Face standalone from:" -ForegroundColor White
    Write-Host "   https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Or build Audio2Face-3D-SDK from GitHub:" -ForegroundColor White
    Write-Host "   https://github.com/NVIDIA/Audio2Face-3D-SDK" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "=== Installation Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To install Audio2Face:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Launch Omniverse Launcher:" -ForegroundColor White
Write-Host "   Start-Process '$launcherPath'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. In Omniverse Launcher:" -ForegroundColor White
Write-Host "   - Go to 'Exchange' tab" -ForegroundColor Gray
Write-Host "   - Search for 'Audio2Face'" -ForegroundColor Gray
Write-Host "   - Click 'Install'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Wait for installation to complete" -ForegroundColor White
Write-Host ""
Write-Host "4. Verify installation:" -ForegroundColor White
Write-Host "   python scripts/test_audio2face_integration.py" -ForegroundColor Gray
Write-Host ""

# Offer to launch launcher
$launch = Read-Host "Launch Omniverse Launcher now? (Y/N)"
if ($launch -eq "Y" -or $launch -eq "y") {
    Start-Process $launcherPath
    Write-Host ""
    Write-Host "[INFO] Launcher opened. Follow the steps above to install Audio2Face." -ForegroundColor Yellow
}

