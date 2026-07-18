# Monitor video generation progress with clear, persistent display
# Shows all active videos without losing information on refresh

$logFile = "$PSScriptRoot/../.cache/progress.log"
$updateInterval = 3

function Show-Progress {
    Clear-Host
    Write-Host "=== The Talking Heads - Video Generation Monitor ===" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    # Check for running Python processes
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -gt (Get-Date).AddHours(-1) }
    $processCount = ($pythonProcesses | Measure-Object).Count
    
    if ($processCount -gt 0) {
        Write-Host "[OK] Python process(es) running:" -ForegroundColor Green
        foreach ($proc in $pythonProcesses) {
            $runtime = ((Get-Date) - $proc.StartTime).ToString('hh\:mm\:ss')
            Write-Host "  PID: $($proc.Id) | Started: $($proc.StartTime.ToString('HH:mm:ss')) | Runtime: $runtime" -ForegroundColor White
        }
    } else {
        Write-Host "[!] No Python processes running" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Read and parse log file
    if (-not (Test-Path $logFile)) {
        Write-Host "[!] No progress log found at: $logFile" -ForegroundColor Yellow
        return
    }
    
    $log = Get-Content $logFile -ErrorAction SilentlyContinue
    if (-not $log) {
        Write-Host "[!] Progress log is empty" -ForegroundColor Yellow
        return
    }
    
    # Extract test names
    $testStarts = $log | Select-String -Pattern "\[START\] Test (\w+) started"
    $testNames = @()
    foreach ($start in $testStarts) {
        if ($start -match "Test (\w+) started") {
            $testNames += $matches[1]
        }
    }
    
    if ($testNames.Count -gt 0) {
        Write-Host "--- Tests Detected ---" -ForegroundColor Cyan
        Write-Host "  $($testNames -join ', ')" -ForegroundColor White
        Write-Host ""
    }
    
    # Show HeyGen videos
    $heygenCreated = $log | Select-String -Pattern "HeyGen:.*Video creation request submitted.*ID:\s*([a-f0-9]+)"
    $heygenVideos = @{}
    foreach ($entry in $heygenCreated) {
        if ($entry.Line -match "ID:\s*([a-f0-9]{8})") {
            $videoId = $matches[1]
            if (-not $heygenVideos.ContainsKey($videoId)) {
                $heygenVideos[$videoId] = @()
            }
        }
    }
    
    # Get all HeyGen entries for each video
    foreach ($videoId in $heygenVideos.Keys) {
        $entries = $log | Select-String -Pattern "HeyGen:.*$videoId"
        $heygenVideos[$videoId] = $entries
    }
    
    if ($heygenVideos.Count -gt 0) {
        Write-Host "--- HeyGen Videos ---" -ForegroundColor Yellow
        $videoNum = 1
        foreach ($videoId in ($heygenVideos.Keys | Sort-Object)) {
            $entries = $heygenVideos[$videoId]
            $latest = $entries | Select-Object -Last 1
            $latestLine = if ($latest -is [Microsoft.PowerShell.Commands.MatchInfo]) { $latest.Line } else { $latest.ToString() }
            
            # Extract timestamp and status
            $timestamp = "N/A"
            $status = "Unknown"
            if ($latestLine -match "\[(\d{2}):(\d{2}):(\d{2})\]") {
                $timestamp = "$($matches[1]):$($matches[2]):$($matches[3])"
            }
            if ($latestLine -match "HeyGen: (.+)") {
                $status = $matches[1].Trim()
                # Truncate long status
                if ($status.Length -gt 70) {
                    $status = $status.Substring(0, 67) + "..."
                }
            }
            
            Write-Host "  Video $videoNum (ID: $videoId)" -ForegroundColor Cyan
            Write-Host "    [$timestamp] $status" -ForegroundColor White
            Write-Host ""
            $videoNum++
        }
    }
    
    # Show D-ID videos
    $didCreated = $log | Select-String -Pattern "D-ID:.*Video creation request submitted.*ID:\s*([a-f0-9]+)"
    $didVideos = @{}
    foreach ($entry in $didCreated) {
        if ($entry.Line -match "ID:\s*([a-f0-9]{8})") {
            $videoId = $matches[1]
            if (-not $didVideos.ContainsKey($videoId)) {
                $didVideos[$videoId] = @()
            }
        }
    }
    
    # Get all D-ID entries for each video
    foreach ($videoId in $didVideos.Keys) {
        $entries = $log | Select-String -Pattern "D-ID:.*$videoId"
        $didVideos[$videoId] = $entries
    }
    
    if ($didVideos.Count -gt 0) {
        Write-Host "--- D-ID Videos ---" -ForegroundColor Magenta
        $videoNum = 1
        foreach ($videoId in ($didVideos.Keys | Sort-Object)) {
            $entries = $didVideos[$videoId]
            $latest = $entries | Select-Object -Last 1
            $latestLine = if ($latest -is [Microsoft.PowerShell.Commands.MatchInfo]) { $latest.Line } else { $latest.ToString() }
            
            # Extract timestamp and status
            $timestamp = "N/A"
            $status = "Unknown"
            if ($latestLine -match "\[(\d{2}):(\d{2}):(\d{2})\]") {
                $timestamp = "$($matches[1]):$($matches[2]):$($matches[3])"
            }
            if ($latestLine -match "D-ID: (.+)") {
                $status = $matches[1].Trim()
                # Truncate long status
                if ($status.Length -gt 70) {
                    $status = $status.Substring(0, 67) + "..."
                }
            }
            
            Write-Host "  Video $videoNum (ID: $videoId)" -ForegroundColor Cyan
            Write-Host "    [$timestamp] $status" -ForegroundColor White
            Write-Host ""
            $videoNum++
        }
    } elseif ($testNames -contains "DID_Quick") {
        Write-Host "--- D-ID Videos ---" -ForegroundColor Magenta
        Write-Host "  Test started but no video created yet" -ForegroundColor Yellow
        
        # Check for D-ID errors
        $didErrors = $log | Select-String -Pattern "D-ID:.*Error|RuntimeError.*D-ID" | Select-Object -Last 1
        if ($didErrors) {
            $errorLine = if ($didErrors -is [Microsoft.PowerShell.Commands.MatchInfo]) { $didErrors.Line } else { $didErrors.ToString() }
            if ($errorLine.Length -gt 100) {
                $errorLine = $errorLine.Substring(0, 97) + "..."
            }
            Write-Host "  [ERROR] $errorLine" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    # Show summary
    Write-Host "--- Summary ---" -ForegroundColor Cyan
    Write-Host "  HeyGen videos: $($heygenVideos.Count) created, $(($log | Select-String -Pattern 'HeyGen:.*polling' | Measure-Object).Count) polling entries" -ForegroundColor White
    Write-Host "  D-ID videos: $($didVideos.Count) created, $(($log | Select-String -Pattern 'D-ID:.*polling' | Measure-Object).Count) polling entries" -ForegroundColor White
    
    # Check for recent output files
    $outputFiles = Get-ChildItem -Path "examples/outputs","outputs" -Recurse -Filter "*.mp4" -ErrorAction SilentlyContinue | 
        Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-30) } | 
        Sort-Object -Property LastWriteTime -Descending
    
    if ($outputFiles) {
        Write-Host "  Completed videos: $($outputFiles.Count)" -ForegroundColor Green
        foreach ($file in $outputFiles | Select-Object -First 3) {
            $size = [math]::Round($file.Length / 1MB, 2)
            Write-Host "    - $($file.Name) ($size MB) at $($file.LastWriteTime.ToString('HH:mm:ss'))" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
}

try {
    while ($true) {
        Show-Progress
        Start-Sleep -Seconds $updateInterval
    }
} catch {
    Write-Host "`nMonitoring stopped." -ForegroundColor Gray
}

