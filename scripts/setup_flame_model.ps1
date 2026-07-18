# Setup FLAME Model for DECA
# Helper script to extract and place FLAME model

param(
    [string]$FlameZipPath = ""
)

$ErrorActionPreference = "Stop"

Write-Host "=== FLAME Model Setup for DECA ===" -ForegroundColor Cyan
Write-Host ""

$decaDataPath = "d:\dev\DECA\data"

# Check if model already exists
if (Test-Path "$decaDataPath\generic_model.pkl") {
    Write-Host "[INFO] FLAME model already exists at: $decaDataPath\generic_model.pkl" -ForegroundColor Green
    $overwrite = Read-Host "Overwrite existing model? (Y/N)"
    if ($overwrite -ne "Y" -and $overwrite -ne "y") {
        Write-Host "Skipping setup." -ForegroundColor Yellow
        exit 0
    }
}

# Get ZIP file path
if ([string]::IsNullOrEmpty($FlameZipPath)) {
    Write-Host "Please provide the path to FLAME2020.zip" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "If you haven't downloaded it yet:" -ForegroundColor White
    Write-Host "1. Register at: https://flame.is.tue.mpg.de/" -ForegroundColor Cyan
    Write-Host "2. Go to: https://flame.is.tue.mpg.de/download.php" -ForegroundColor Cyan
    Write-Host "3. Select: 'FLAME 2020 (fixed mouth, improved expressions, more data)'" -ForegroundColor Yellow
    Write-Host "   (NOT FLAME 2023 - DECA needs FLAME 2020)" -ForegroundColor Yellow
    Write-Host "4. Agree to license terms and download" -ForegroundColor Cyan
    Write-Host ""
    $FlameZipPath = Read-Host "Enter path to FLAME2020.zip (or press Enter to skip)"
    
    if ([string]::IsNullOrEmpty($FlameZipPath)) {
        Write-Host "Skipping setup. Download manually and place generic_model.pkl in: $decaDataPath" -ForegroundColor Yellow
        exit 0
    }
}

# Verify ZIP file exists
if (-not (Test-Path $FlameZipPath)) {
    Write-Host "[ERROR] ZIP file not found: $FlameZipPath" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Found ZIP file: $FlameZipPath" -ForegroundColor Green
Write-Host ""

# Create temp directory
$tempDir = Join-Path $env:TEMP "flame_extract_$(Get-Random)"
Write-Host "1. Extracting FLAME2020.zip..." -ForegroundColor Yellow

try {
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    Expand-Archive -Path $FlameZipPath -DestinationPath $tempDir -Force
    
    Write-Host "[OK] Extraction complete" -ForegroundColor Green
    Write-Host ""
    
    # Find generic_model.pkl
    Write-Host "2. Looking for generic_model.pkl..." -ForegroundColor Yellow
    $modelFile = Get-ChildItem -Path $tempDir -Recurse -Filter "generic_model.pkl" | Select-Object -First 1
    
    if (-not $modelFile) {
        Write-Host "[ERROR] generic_model.pkl not found in ZIP file" -ForegroundColor Red
        Write-Host "[INFO] Contents of extracted folder:" -ForegroundColor Yellow
        Get-ChildItem -Path $tempDir -Recurse | Select-Object FullName | Format-Table -AutoSize
        exit 1
    }
    
    Write-Host "[OK] Found: $($modelFile.FullName)" -ForegroundColor Green
    Write-Host ""
    
    # Ensure DECA data directory exists
    if (-not (Test-Path $decaDataPath)) {
        New-Item -ItemType Directory -Path $decaDataPath -Force | Out-Null
        Write-Host "[INFO] Created directory: $decaDataPath" -ForegroundColor Gray
    }
    
    # Copy model file
    Write-Host "3. Copying model to DECA data folder..." -ForegroundColor Yellow
    $targetPath = Join-Path $decaDataPath "generic_model.pkl"
    Copy-Item $modelFile.FullName -Destination $targetPath -Force
    
    Write-Host "[OK] Copied to: $targetPath" -ForegroundColor Green
    Write-Host ""
    
    # Verify
    if (Test-Path $targetPath) {
        $fileSize = (Get-Item $targetPath).Length / 1MB
        Write-Host "[OK] FLAME model setup complete!" -ForegroundColor Green
        Write-Host "[INFO] File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "1. Test DECA: python d:\dev\DECA\demos\demo_reconstruct.py -i TestSamples/examples/IMG_0392_inputs.jpg" -ForegroundColor White
    } else {
        Write-Host "[ERROR] Failed to copy model file" -ForegroundColor Red
        exit 1
    }
    
} finally {
    # Cleanup temp directory
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

