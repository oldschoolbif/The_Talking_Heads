# Quick status check for running tests
# Run: .\scripts\check_status.ps1

$logFile = ".cache\progress.log"

Write-Host "`n=== Test Status Check ===" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Gray

# Check if processes are running
$processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -gt (Get-Date).AddHours(-2) }
if ($processes) {
    Write-Host "✓ Python process(es) running:" -ForegroundColor Green
    foreach ($proc in $processes) {
        $runtime = (Get-Date) - $proc.StartTime
        Write-Host "  PID: $($proc.Id) | Started: $($proc.StartTime.ToString('HH:mm:ss')) | Runtime: $([math]::Round($runtime.TotalMinutes, 1)) min" -ForegroundColor White
    }
} else {
    Write-Host "✗ No Python processes running" -ForegroundColor Red
}

Write-Host "`n--- Latest Progress ---" -ForegroundColor Yellow
if (Test-Path $logFile) {
    $latest = Get-Content $logFile -ErrorAction SilentlyContinue | Select-Object -Last 5
    if ($latest) {
        foreach ($line in $latest) {
            Write-Host "  $line" -ForegroundColor White
        }
    } else {
        Write-Host "  (No log entries)" -ForegroundColor Gray
    }
} else {
    Write-Host "  (No log file found)" -ForegroundColor Gray
}

Write-Host "`n--- Summary ---" -ForegroundColor Yellow
if (Test-Path $logFile) {
    $log = Get-Content $logFile -ErrorAction SilentlyContinue
    $heygenPolling = ($log | Select-String -Pattern "HeyGen:.*polling" | Measure-Object).Count
    $didPolling = ($log | Select-String -Pattern "D-ID:.*polling" | Measure-Object).Count
    $heygenCreated = ($log | Select-String -Pattern "HeyGen:.*Video creation request submitted" | Measure-Object).Count
    $didCreated = ($log | Select-String -Pattern "D-ID:.*Video creation request submitted" | Measure-Object).Count
    $errorCount = ($log | Select-String -Pattern "^\[ERROR\]|\[X\] Error" | Measure-Object).Count
    $successCount = ($log | Select-String -Pattern "(HeyGen|D-ID):.*Video ready" | Measure-Object).Count
    
    Write-Host "  HeyGen videos: $heygenCreated created, $heygenPolling polling entries" -ForegroundColor White
    Write-Host "  D-ID videos: $didCreated created, $didPolling polling entries" -ForegroundColor White
    if ($errorCount -gt 0) {
        Write-Host "  Errors: $errorCount" -ForegroundColor Red
    }
    if ($successCount -gt 0) {
        Write-Host "  Videos completed: $successCount" -ForegroundColor Green
    }
}

Write-Host "`n"

