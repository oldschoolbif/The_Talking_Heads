# Test 3D Reconstruction Tools (3DDFA and DECA)
# Tests both tools with sample images

param(
    [string]$ImagePath = "",
    [switch]$Test3DDFA = $true,
    [switch]$TestDECA = $true
)

$ErrorActionPreference = "Continue"

Write-Host "=== Testing 3D Reconstruction Tools ===" -ForegroundColor Cyan
Write-Host ""

# Test 3DDFA
if ($Test3DDFA) {
    Write-Host "1. Testing 3DDFA..." -ForegroundColor Yellow
    $tddfaPath = "d:\dev\3DDFA_V2"
    
    if (-not (Test-Path $tddfaPath)) {
        Write-Host "[ERROR] 3DDFA_V2 not found at: $tddfaPath" -ForegroundColor Red
    } else {
        Push-Location $tddfaPath
        
        # Use default test image if none provided
        if ([string]::IsNullOrEmpty($ImagePath)) {
            $testImage = "examples/inputs/emma.jpg"
        } else {
            $testImage = $ImagePath
        }
        
        if (-not (Test-Path $testImage)) {
            Write-Host "[WARN] Test image not found: $testImage" -ForegroundColor Yellow
            Write-Host "[INFO] Available test images:" -ForegroundColor Gray
            Get-ChildItem "examples/inputs" -Filter "*.jpg" -ErrorAction SilentlyContinue | ForEach-Object {
                Write-Host "  - $($_.FullName)" -ForegroundColor Gray
            }
        } else {
            Write-Host "[INFO] Testing with image: $testImage" -ForegroundColor Gray
            Write-Host "[INFO] Running: python demo.py -f $testImage" -ForegroundColor Gray
            Write-Host ""
            
            python demo.py -f $testImage 2>&1 | ForEach-Object {
                if ($_ -match "error|Error|ERROR|failed|Failed|FAILED") {
                    Write-Host $_ -ForegroundColor Red
                } elseif ($_ -match "warning|Warning|WARNING") {
                    Write-Host $_ -ForegroundColor Yellow
                } else {
                    Write-Host $_
                }
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "[OK] 3DDFA test completed successfully" -ForegroundColor Green
                Write-Host "[INFO] Check examples/results/ for output images" -ForegroundColor Gray
            } else {
                Write-Host ""
                Write-Host "[ERROR] 3DDFA test failed" -ForegroundColor Red
            }
        }
        
        Pop-Location
    }
    
    Write-Host ""
}

# Test DECA
if ($TestDECA) {
    Write-Host "2. Testing DECA..." -ForegroundColor Yellow
    $decaPath = "d:\dev\DECA"
    
    if (-not (Test-Path $decaPath)) {
        Write-Host "[ERROR] DECA not found at: $decaPath" -ForegroundColor Red
    } else {
        Push-Location $decaPath
        
        # Use default test image if none provided
        if ([string]::IsNullOrEmpty($ImagePath)) {
            $testImage = "TestSamples/examples/IMG_0392_inputs.jpg"
        } else {
            $testImage = $ImagePath
        }
        
        if (-not (Test-Path $testImage)) {
            Write-Host "[WARN] Test image not found: $testImage" -ForegroundColor Yellow
            Write-Host "[INFO] Available test images:" -ForegroundColor Gray
            Get-ChildItem "TestSamples/examples" -Filter "*.jpg" -ErrorAction SilentlyContinue | ForEach-Object {
                Write-Host "  - $($_.FullName)" -ForegroundColor Gray
            }
        } else {
            Write-Host "[INFO] Testing with image: $testImage" -ForegroundColor Gray
            Write-Host "[INFO] Running: python demos/demo_reconstruct.py -i $testImage" -ForegroundColor Gray
            Write-Host "[INFO] Note: DECA will compile CUDA extensions on first run (may take a few minutes)" -ForegroundColor Gray
            Write-Host ""
            
            python demos/demo_reconstruct.py -i $testImage 2>&1 | ForEach-Object {
                if ($_ -match "error|Error|ERROR|failed|Failed|FAILED") {
                    Write-Host $_ -ForegroundColor Red
                } elseif ($_ -match "warning|Warning|WARNING|compiling|Compiling") {
                    Write-Host $_ -ForegroundColor Yellow
                } else {
                    Write-Host $_
                }
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "[OK] DECA test completed successfully" -ForegroundColor Green
                Write-Host "[INFO] Check TestSamples/examples/results/ for output files" -ForegroundColor Gray
            } else {
                Write-Host ""
                Write-Host "[WARN] DECA test had issues (check output above)" -ForegroundColor Yellow
                Write-Host "[INFO] Try with pytorch3d: pip install pytorch3d" -ForegroundColor Gray
                Write-Host "[INFO] Then run: python demos/demo_reconstruct.py -i $testImage --rasterizer_type=pytorch3d" -ForegroundColor Gray
            }
        }
        
        Pop-Location
    }
    
    Write-Host ""
}

Write-Host "=== Testing Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "- 3DDFA: Fast 3D face reconstruction" -ForegroundColor White
Write-Host "- DECA: High-quality detailed 3D face reconstruction with expressions" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test with your own headshot images" -ForegroundColor White
Write-Host "2. Convert 3D models to USD format for Audio2Face" -ForegroundColor White
Write-Host "3. Or use 2D animation tools (SadTalker) for simpler workflow" -ForegroundColor White
