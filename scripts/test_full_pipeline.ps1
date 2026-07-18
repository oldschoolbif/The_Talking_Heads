# Test Full Pipeline: TTS + Avatar Generation
# Creates a complete podcast with TTS and avatar movements

param(
    [string]$ScriptFile = "",
    [string]$AvatarEngine = "mock",  # Use mock for testing (no API needed)
    [string]$TTSEngine = "bark",     # Use bark (local GPU)
    [switch]$UseRealAvatars = $false  # Set to true to use real APIs (HeyGen/D-ID)
)

$ErrorActionPreference = "Stop"

Write-Host "=== Full Pipeline Test: TTS + Avatar Generation ===" -ForegroundColor Cyan
Write-Host ""

# Find project root
$projectRoot = "d:\dev\The_Talking_Heads"
if (-not (Test-Path $projectRoot)) {
    Write-Host "[ERROR] Project root not found: $projectRoot" -ForegroundColor Red
    exit 1
}

Push-Location $projectRoot

try {
    # Create test script if not provided
    if ([string]::IsNullOrEmpty($ScriptFile)) {
        Write-Host "Creating test script..." -ForegroundColor Yellow
        $testScript = @"
# Test Podcast - TTS and Avatar Generation

ALICE: Hello everyone! Welcome to our test podcast.
BOB: Thanks for joining us today.
ALICE: We're testing the full pipeline with TTS and avatar generation.
BOB: This should create a complete video with animated avatars.
ALICE: Let's see how it works!
"@
        
        $scriptPath = "examples\scripts\test_full_pipeline.txt"
        $testScript | Out-File -FilePath $scriptPath -Encoding UTF8
        Write-Host "[OK] Created test script: $scriptPath" -ForegroundColor Green
        $ScriptFile = $scriptPath
    }
    
    if (-not (Test-Path $ScriptFile)) {
        Write-Host "[ERROR] Script file not found: $ScriptFile" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[INFO] Using script: $ScriptFile" -ForegroundColor Gray
    Write-Host "[INFO] TTS Engine: $TTSEngine" -ForegroundColor Gray
    Write-Host "[INFO] Avatar Engine: $AvatarEngine" -ForegroundColor Gray
    Write-Host ""
    
    # Update config temporarily for this test
    Write-Host "Updating configuration for test..." -ForegroundColor Yellow
    
    # Load config
    $configPath = "config\config.yaml"
    $configContent = Get-Content $configPath -Raw
    $config = [ordered]@{}
    
    # Parse YAML (simple approach)
    # We'll use Python to update config properly
    
    # Create Python test script
    $pythonTest = @"
import sys
import yaml
from pathlib import Path

# Load config
config_path = Path("config/config.yaml")
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Update TTS engine
config['tts']['engine'] = '$TTSEngine'

# Update avatar engine
config['avatar']['engine'] = '$AvatarEngine'

# Save config
with open(config_path, 'w', encoding='utf-8') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print("Config updated successfully")
"@
    
    $tempPy = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.py'
    $pythonTest | Out-File -FilePath $tempPy -Encoding UTF8
    
    try {
        python $tempPy
        Write-Host "[OK] Configuration updated" -ForegroundColor Green
    } finally {
        Remove-Item $tempPy -ErrorAction SilentlyContinue
    }
    
    Write-Host ""
    Write-Host "Running pipeline..." -ForegroundColor Yellow
    Write-Host ""
    
    # Run the pipeline
    python -m src.cli.main create $ScriptFile --scene studio --layout switching
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=== Test Complete ===" -ForegroundColor Green
        Write-Host ""
        Write-Host "Check outputs in: examples/outputs/" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "[ERROR] Pipeline failed" -ForegroundColor Red
        exit 1
    }
    
} finally {
    Pop-Location
}

