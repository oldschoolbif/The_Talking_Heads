# Test FLAME 2023 with DECA
# This script helps test if DECA works with FLAME 2023 model

param(
    [string]$Flame2023ModelPath = ""
)

$ErrorActionPreference = "Stop"

Write-Host "=== Testing FLAME 2023 with DECA ===" -ForegroundColor Cyan
Write-Host ""

$decaDataPath = "d:\dev\DECA\data"
$backupPath = "$decaDataPath\generic_model.pkl.backup"
$currentModelPath = "$decaDataPath\generic_model.pkl"

# Check if DECA data directory exists
if (-not (Test-Path $decaDataPath)) {
    Write-Host "[ERROR] DECA data directory not found: $decaDataPath" -ForegroundColor Red
    Write-Host "[INFO] Make sure DECA is installed at d:\dev\DECA" -ForegroundColor Yellow
    exit 1
}

# Check if current model exists
if (-not (Test-Path $currentModelPath)) {
    Write-Host "[WARN] Current FLAME model not found: $currentModelPath" -ForegroundColor Yellow
    Write-Host "[INFO] You may need to download FLAME 2020 first" -ForegroundColor Gray
    Write-Host "[INFO] Or proceed with FLAME 2023 if you have it" -ForegroundColor Gray
    Write-Host ""
    $proceed = Read-Host "Continue anyway? (Y/N)"
    if ($proceed -ne "Y" -and $proceed -ne "y") {
        exit 0
    }
} else {
    Write-Host "[OK] Found current FLAME model: $currentModelPath" -ForegroundColor Green
    $currentSize = (Get-Item $currentModelPath).Length / 1MB
    Write-Host "[INFO] Current model size: $([math]::Round($currentSize, 2)) MB" -ForegroundColor Gray
    Write-Host ""
}

# Get FLAME 2023 model path
if ([string]::IsNullOrEmpty($Flame2023ModelPath)) {
    Write-Host "Please provide the path to FLAME 2023 generic_model.pkl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "If you haven't downloaded it yet:" -ForegroundColor White
    Write-Host "1. Go to: https://flame.is.tue.mpg.de/download.php" -ForegroundColor Cyan
    Write-Host "2. Select: 'FLAME 2023 Open' or 'FLAME 2023'" -ForegroundColor Yellow
    Write-Host "3. Download and extract generic_model.pkl" -ForegroundColor Cyan
    Write-Host ""
    $Flame2023ModelPath = Read-Host "Enter path to FLAME 2023 generic_model.pkl (or press Enter to skip)"
    
    if ([string]::IsNullOrEmpty($Flame2023ModelPath)) {
        Write-Host "Skipping test. Download FLAME 2023 and run this script again." -ForegroundColor Yellow
        exit 0
    }
}

# Verify FLAME 2023 model exists
if (-not (Test-Path $Flame2023ModelPath)) {
    Write-Host "[ERROR] FLAME 2023 model not found: $Flame2023ModelPath" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Found FLAME 2023 model: $Flame2023ModelPath" -ForegroundColor Green
$flame2023Size = (Get-Item $Flame2023ModelPath).Length / 1MB
Write-Host "[INFO] FLAME 2023 model size: $([math]::Round($flame2023Size, 2)) MB" -ForegroundColor Gray
Write-Host ""

# Backup current model if it exists
if (Test-Path $currentModelPath) {
    Write-Host "1. Backing up current FLAME model..." -ForegroundColor Yellow
    if (Test-Path $backupPath) {
        $overwrite = Read-Host "Backup already exists. Overwrite? (Y/N)"
        if ($overwrite -eq "Y" -or $overwrite -eq "y") {
            Copy-Item $currentModelPath -Destination $backupPath -Force
            Write-Host "[OK] Backup created: $backupPath" -ForegroundColor Green
        }
    } else {
        Copy-Item $currentModelPath -Destination $backupPath -Force
        Write-Host "[OK] Backup created: $backupPath" -ForegroundColor Green
    }
    Write-Host ""
}

# Replace with FLAME 2023 model
Write-Host "2. Replacing with FLAME 2023 model..." -ForegroundColor Yellow
Copy-Item $Flame2023ModelPath -Destination $currentModelPath -Force
Write-Host "[OK] FLAME 2023 model installed" -ForegroundColor Green
Write-Host ""

# Test DECA
Write-Host "3. Testing DECA with FLAME 2023..." -ForegroundColor Yellow
Write-Host "[INFO] Running DECA reconstruction test..." -ForegroundColor Gray
Write-Host ""

$testImage = "d:\dev\DECA\TestSamples\examples\IMG_0392_inputs.jpg"
if (-not (Test-Path $testImage)) {
    Write-Host "[WARN] Test image not found: $testImage" -ForegroundColor Yellow
    Write-Host "[INFO] You can test manually with:" -ForegroundColor Gray
    Write-Host "  python d:\dev\DECA\demos\demo_reconstruct.py -i <your_image.jpg>" -ForegroundColor White
    Write-Host ""
    Write-Host "[OK] FLAME 2023 model installed. Test manually to verify it works." -ForegroundColor Green
    Write-Host ""
    Write-Host "To restore FLAME 2020:" -ForegroundColor Yellow
    Write-Host "  Copy-Item '$backupPath' -Destination '$currentModelPath' -Force" -ForegroundColor White
    exit 0
}

Push-Location "d:\dev\DECA"
try {
    Write-Host "Running: python demos/demo_reconstruct.py -i $testImage" -ForegroundColor Gray
    Write-Host ""
    
    python demos/demo_reconstruct.py -i $testImage 2>&1 | ForEach-Object {
        if ($_ -match "error|Error|ERROR|failed|Failed|FAILED|Traceback|FileNotFoundError|AttributeError|KeyError") {
            Write-Host $_ -ForegroundColor Red
        } elseif ($_ -match "warning|Warning|WARNING") {
            Write-Host $_ -ForegroundColor Yellow
        } else {
            Write-Host $_
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] DECA test completed successfully with FLAME 2023!" -ForegroundColor Green
        Write-Host "[INFO] FLAME 2023 appears to be compatible with DECA" -ForegroundColor Green
        Write-Host ""
        Write-Host "To restore FLAME 2020 (if needed):" -ForegroundColor Yellow
        Write-Host "  Copy-Item '$backupPath' -Destination '$currentModelPath' -Force" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "[WARN] DECA test had errors. FLAME 2023 may not be compatible." -ForegroundColor Yellow
        Write-Host "[INFO] Check error messages above for details" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Restoring FLAME 2020..." -ForegroundColor Yellow
        if (Test-Path $backupPath) {
            Copy-Item $backupPath -Destination $currentModelPath -Force
            Write-Host "[OK] FLAME 2020 restored" -ForegroundColor Green
        } else {
            Write-Host "[WARN] No backup found. You may need to re-download FLAME 2020" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "[ERROR] Test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Restoring FLAME 2020..." -ForegroundColor Yellow
    if (Test-Path $backupPath) {
        Copy-Item $backupPath -Destination $currentModelPath -Force
        Write-Host "[OK] FLAME 2020 restored" -ForegroundColor Green
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan

