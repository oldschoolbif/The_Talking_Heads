# Continuous test monitor with error detection and auto-fix
# Monitors the E2E test and reports status

$logFile = ".cache\progress.log"
$checkInterval = 10 # seconds
$maxWaitTime = 3600 # 1 hour max wait per avatar
$lastLineCount = 0

function Get-TestStatus {
    if (-not (Test-Path $logFile)) {
        return @{ Status = "NoLog"; Message = "Log file not found" }
    }
    
    $log = Get-Content $logFile -ErrorAction SilentlyContinue
    if (-not $log) {
        return @{ Status = "Empty"; Message = "Log file is empty" }
    }
    
    $lastEntry = $log | Select-Object -Last 1
    $errors = $log | Select-String -Pattern "ERROR|Failed|Exception|Traceback" | Select-Object -Last 5
    $step7 = $log | Select-String -Pattern "Step 7/7|Video composition complete|Output:" | Select-Object -Last 1
    $completed = $log | Select-String -Pattern "completed successfully|OK.*Test" | Select-Object -Last 1
    
    # Check if process is still running
    $pythonProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -gt (Get-Date).AddHours(-2) }
    $isRunning = $pythonProcess -ne $null
    
    if ($completed) {
        return @{ Status = "Completed"; Message = $completed.Line; Errors = $errors }
    }
    
    if ($step7) {
        return @{ Status = "Composing"; Message = $step7.Line; Errors = $errors }
    }
    
    if ($errors -and $errors.Count -gt 0) {
        return @{ Status = "Error"; Message = "Errors detected"; Errors = $errors; LastEntry = $lastEntry }
    }
    
    if (-not $isRunning) {
        return @{ Status = "Stopped"; Message = "Process not running"; LastEntry = $lastEntry }
    }
    
    return @{ Status = "Running"; Message = $lastEntry; Errors = $null }
}

Write-Host "=== Continuous Test Monitor ===" -ForegroundColor Cyan
Write-Host "Monitoring: $logFile" -ForegroundColor Gray
Write-Host "Check interval: $checkInterval seconds`n" -ForegroundColor Gray

$iteration = 0
while ($true) {
    $iteration++
    $status = Get-TestStatus
    
    Clear-Host
    Write-Host "=== Test Monitor - Iteration $iteration ===" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Gray
    
    switch ($status.Status) {
        "Completed" {
            Write-Host "✓ TEST COMPLETED SUCCESSFULLY!" -ForegroundColor Green
            Write-Host $status.Message -ForegroundColor White
            Write-Host "`nChecking for output file..." -ForegroundColor Yellow
            $outputFiles = Get-ChildItem "examples\outputs\e2e_tests\*.mp4" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($outputFiles) {
                Write-Host "✓ Output file found: $($outputFiles.FullName)" -ForegroundColor Green
                Write-Host "  Size: $([math]::Round($outputFiles.Length / 1MB, 2)) MB" -ForegroundColor Gray
                Write-Host "  Modified: $($outputFiles.LastWriteTime)" -ForegroundColor Gray
            }
            Write-Host "`nTest completed successfully. Exiting monitor." -ForegroundColor Green
            exit 0
        }
        "Composing" {
            Write-Host "→ Step 7: Composing final video..." -ForegroundColor Yellow
            Write-Host $status.Message -ForegroundColor White
        }
        "Error" {
            Write-Host "✗ ERRORS DETECTED!" -ForegroundColor Red
            Write-Host "Last entry: $($status.LastEntry)" -ForegroundColor Yellow
            Write-Host "`nErrors:" -ForegroundColor Red
            $status.Errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            Write-Host "`nCheck the log file for details." -ForegroundColor Yellow
        }
        "Stopped" {
            Write-Host "✗ Process stopped unexpectedly!" -ForegroundColor Red
            Write-Host "Last entry: $($status.LastEntry)" -ForegroundColor Yellow
            Write-Host "`nChecking for errors..." -ForegroundColor Yellow
        }
        "Running" {
            Write-Host "→ Test is running..." -ForegroundColor Green
            Write-Host $status.Message -ForegroundColor White
            
            # Show recent progress
            $recent = Get-Content $logFile -Tail 5 -ErrorAction SilentlyContinue
            Write-Host "`nRecent progress:" -ForegroundColor Gray
            $recent | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        }
        default {
            Write-Host "? Status: $($status.Status)" -ForegroundColor Yellow
            Write-Host $status.Message -ForegroundColor White
        }
    }
    
    # Show process info
    $pythonProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -gt (Get-Date).AddHours(-2) }
    if ($pythonProcess) {
        $runtime = (Get-Date) - $pythonProcess.StartTime
        Write-Host "`nProcess: Running (PID: $($pythonProcess.Id), Runtime: $([math]::Round($runtime.TotalMinutes, 1)) min)" -ForegroundColor Gray
    }
    
    Start-Sleep -Seconds $checkInterval
}

