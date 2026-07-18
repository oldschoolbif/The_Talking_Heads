# Monitor progress for multiple videos running in parallel
# Shows progress for each video separately

$logFile = ".cache\progress.log"
$updateInterval = 5  # seconds

Write-Host "`n=== Dual Video Progress Monitor ===" -ForegroundColor Green
Write-Host "Monitoring: $logFile" -ForegroundColor Cyan
Write-Host "Update interval: $updateInterval seconds" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

function Get-LatestProgress {
    param([string]$pattern)
    
    if (Test-Path $logFile) {
        $entries = Get-Content $logFile -ErrorAction SilentlyContinue | Select-String -Pattern $pattern
        if ($entries) {
            return $entries | Select-Object -Last 1
        }
    }
    return $null
}

function Show-Progress {
    Clear-Host
    Write-Host "`n=== Progress Update - $(Get-Date -Format 'HH:mm:ss') ===" -ForegroundColor Cyan
    
    # Get all HeyGen polling entries
    $allLog = Get-Content $logFile -ErrorAction SilentlyContinue
    if (-not $allLog) {
        Write-Host "No log file found" -ForegroundColor Yellow
        return
    }
    
    # Extract HeyGen polling entries with elapsed time
    $heygenEntries = $allLog | Select-String -Pattern "HeyGen.*polling.*elapsed" | Select-Object -Last 10
    
    # Group by elapsed time to identify different videos
    $videos = @{}
    foreach ($entry in $heygenEntries) {
        if ($entry -match "(\d+)s elapsed") {
            $elapsed = [int]$matches[1]
            # Group by approximate elapsed time ranges (videos will have different elapsed times)
            $key = [math]::Floor($elapsed / 100) * 100  # Group by 100s ranges
            if (-not $videos.ContainsKey($key)) {
                $videos[$key] = @()
            }
            $videos[$key] += $entry
        }
    }
    
    # Show each video's latest progress
    $videoNum = 1
    foreach ($key in ($videos.Keys | Sort-Object -Descending)) {
        $latest = $videos[$key] | Select-Object -Last 1
        Write-Host "`n--- Video $videoNum (HeyGen) ---" -ForegroundColor Yellow
        Write-Host $latest -ForegroundColor White
        $videoNum++
    }
    
    # Show D-ID progress
    $didEntry = Get-LatestProgress "D-ID"
    Write-Host "`n--- D-ID ---" -ForegroundColor Yellow
    if ($didEntry) {
        Write-Host $didEntry -ForegroundColor White
    } else {
        Write-Host "  (Not started yet)" -ForegroundColor Gray
    }
}

try {
    while ($true) {
        Show-Progress
        Start-Sleep -Seconds $updateInterval
    }
} catch {
    Write-Host "`nMonitoring stopped." -ForegroundColor Gray
}

