# Monitor progress for all videos running in parallel
# Shows progress for each video separately with auto-refresh

$logFile = ".cache\progress.log"
$updateInterval = 5  # seconds

Write-Host "`n=== All Videos Progress Monitor ===" -ForegroundColor Green
Write-Host "Monitoring: $logFile" -ForegroundColor Cyan
Write-Host "Updates every $updateInterval seconds" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

function Show-AllProgress {
    Clear-Host
    Write-Host "`n=== Progress Update - $(Get-Date -Format 'HH:mm:ss') ===" -ForegroundColor Cyan
    
    if (-not (Test-Path $logFile)) {
        Write-Host "No log file found" -ForegroundColor Yellow
        return
    }
    
    $log = Get-Content $logFile -ErrorAction SilentlyContinue
    if (-not $log) { return }
    
    # Check if test is still running
    $isRunning = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -gt (Get-Date).AddMinutes(-60) } | Measure-Object | Select-Object -ExpandProperty Count
    
    # Group HeyGen videos by video ID (only if still running)
    if ($isRunning -gt 0) {
        # First, find all video IDs from creation requests (both HeyGen and D-ID)
        $creationEntries = $log | Select-String -Pattern "(HeyGen|D-ID):.*Video creation request submitted.*ID:\s*([a-f0-9]+)"
        $videoIds = @()
        foreach ($entry in $creationEntries) {
            $entryLine = if ($entry -is [Microsoft.PowerShell.Commands.MatchInfo]) { $entry.Line } else { $entry.ToString() }
            if ($entryLine -match "ID:\s*([a-f0-9]+)") {
                $videoIds += $matches[1]
            }
        }
        
        # Group videos by ID (from creation or polling messages)
        $videos = @{}
        $videoStartTimes = @{}  # Track when each video started (by ID)
        
        # First, get IDs from creation requests and their timestamps
        foreach ($entry in $creationEntries) {
            $entryLine = if ($entry -is [Microsoft.PowerShell.Commands.MatchInfo]) { $entry.Line } else { $entry.ToString() }
            if ($entryLine -match "\[(\d{2}):(\d{2}):(\d{2})\].*(HeyGen|D-ID):.*ID:\s*([a-f0-9]+)") {
                $provider = $matches[4]
                $videoId = $matches[5]
                $timestamp = $matches[1] + ":" + $matches[2] + ":" + $matches[3]
                $videoStartTimes[$videoId] = $timestamp
                if (-not $videos.ContainsKey($videoId)) {
                    $videos[$videoId] = @()
                }
            }
        }
        
        # Get all avatar provider polling entries (HeyGen and D-ID)
        # Also include D-ID entries that might not have ID yet (e.g., "Video creation request submitted")
        $allAvatarEntries = $log | Select-String -Pattern "(HeyGen|D-ID):.*(?:ID:\s*([a-f0-9]+)|polling.*(\d+)s elapsed|Video creation request|Video not ready|Video.*status|Error generating)"
        
        foreach ($entry in $allAvatarEntries) {
            $entryLine = if ($entry -is [Microsoft.PowerShell.Commands.MatchInfo]) { $entry.Line } else { $entry.ToString() }
            
            # Check if entry has ID in message (normalized format for both HeyGen and D-ID)
            if ($entryLine -match "(HeyGen|D-ID):.*ID:\s*([a-f0-9]+)") {
                $provider = $matches[1]
                $videoId = $matches[2]
                if (-not $videos.ContainsKey($videoId)) {
                    $videos[$videoId] = @()
                }
                $videos[$videoId] += $entryLine
            }
            # For entries without ID, match by timestamp proximity to creation times
            elseif ($entryLine -match "\[(\d{2}):(\d{2}):(\d{2})\]") {
                $entryTime = $matches[1] + ":" + $matches[2] + ":" + $matches[3]
                $matchedId = $null
                $minTimeDiff = 999999
                
                # Find closest creation entry within 60 seconds
                foreach ($videoId in $videoStartTimes.Keys) {
                    $createTime = $videoStartTimes[$videoId]
                    $timeDiff = [Math]::Abs(([TimeSpan]::Parse($entryTime) - [TimeSpan]::Parse($createTime)).TotalSeconds)
                    if ($timeDiff -lt 60 -and $timeDiff -lt $minTimeDiff) {
                        $minTimeDiff = $timeDiff
                        $matchedId = $videoId
                    }
                }
                
                if ($matchedId) {
                    if (-not $videos.ContainsKey($matchedId)) {
                        $videos[$matchedId] = @()
                    }
                    $videos[$matchedId] += $entryLine
                }
            }
        }
        
        # Check for completed/errored videos
        $completedVideoIds = @()
        $errorEntries = $log | Select-String -Pattern "ERROR.*video_id:\s*([a-f0-9]+)|Failed.*video_id:\s*([a-f0-9]+)"
        foreach ($err in $errorEntries) {
            $errLine = if ($err -is [Microsoft.PowerShell.Commands.MatchInfo]) { $err.Line } else { $err.ToString() }
            if ($errLine -match "video_id:\s*([a-f0-9]+)") {
                $completedVideoIds += $matches[1]
            }
        }
        $successEntries = $log | Select-String -Pattern "(HeyGen|D-ID):.*Video ready.*ID:\s*([a-f0-9]+)"
        foreach ($succ in $successEntries) {
            $succLine = if ($succ -is [Microsoft.PowerShell.Commands.MatchInfo]) { $succ.Line } else { $succ.ToString() }
            if ($succLine -match "ID:\s*([a-f0-9]+)") {
                $completedVideoIds += $matches[1]
            }
        }
        
        # Show each HeyGen video (only active ones - not completed/errored and recently updated)
        $videoNum = 1
        $currentTime = Get-Date
        $maxStaleTime = [TimeSpan]::FromMinutes(10)  # Videos not updated in 10 minutes are considered stale
        
        foreach ($videoId in ($videos.Keys | Sort-Object)) {
            $latest = $videos[$videoId] | Select-Object -Last 1
            $latestLine = if ($latest -is [string]) { $latest } else { $latest.ToString() }
            
            # Extract timestamp from latest entry
            $isRecent = $false
            if ($latestLine -match "\[(\d{2}):(\d{2}):(\d{2})\]") {
                $entryTime = [TimeSpan]::Parse($matches[1] + ":" + $matches[2] + ":" + $matches[3])
                $nowTime = $currentTime.TimeOfDay
                $timeDiff = if ($entryTime -le $nowTime) { $nowTime - $entryTime } else { $nowTime + ([TimeSpan]::FromDays(1) - $entryTime) }
                
                # Only show if updated within last 10 minutes
                if ($timeDiff -le $maxStaleTime) {
                    $isRecent = $true
                }
            }
            
            $elapsed = if ($latestLine -match "(\d+)s elapsed") { [int]$matches[1] } else { 0 }
            $minutes = [math]::Round($elapsed / 60, 1)
            
            # Check if this video has completed/errored by checking video_id
            $isCompleted = $false
            if ($completedVideoIds -contains $videoId) {
                $isCompleted = $true
            }
            
            # Also check if recent entries show this video is done
            $recentErrors = $log | Select-Object -Last 50 | Select-String -Pattern "ERROR|Failed|timed out.*video_id:\s*$videoId|video_id:\s*$videoId.*ERROR|video_id:\s*$videoId.*Failed"
            if ($recentErrors) {
                $isCompleted = $true
            }
            
            # Only show if not completed AND recently updated
            if (-not $isCompleted -and $isRecent) {
                # Detect provider from message
                $provider = "Unknown"
                if ($latestLine -match "(HeyGen|D-ID):") {
                    $provider = $matches[1]
                }
                Write-Host "`n--- Video $videoNum ($provider - ~$minutes min) ---" -ForegroundColor Yellow
                Write-Host "  $latestLine" -ForegroundColor White
                $videoNum++
            }
        }
        
        if ($videos.Count -eq 0) {
            Write-Host "`n--- Avatar Videos (HeyGen/D-ID) ---" -ForegroundColor Yellow
            
            # Check if D-ID test started but hasn't created video yet
            $didStarted = $log | Select-String -Pattern "\[START\] Test DID_Quick started"
            $didProgress = $log | Select-String -Pattern "Step 5.*Generating avatar.*DID|D-ID.*Video creation|D-ID.*Error"
            
            if ($didStarted -and -not $didProgress) {
                Write-Host "  D-ID test started but no video creation yet" -ForegroundColor Yellow
                Write-Host "  (May be processing or encountered an error)" -ForegroundColor Gray
            } else {
                Write-Host "  (No polling activity yet)" -ForegroundColor Gray
            }
        }
    } else {
        # No Python processes running - check test status
        
        # Check for actual output files created recently (last 2 hours)
        $outputFiles = Get-ChildItem -Path "outputs","examples\outputs" -Recurse -Filter "*.mp4" -ErrorAction SilentlyContinue | 
            Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-2) }
        $outputCount = ($outputFiles | Measure-Object).Count
        
        # Get all test start entries
        $testStarts = $log | Select-String -Pattern "\[START\] Test (\w+) started"
        $testNames = @()
        foreach ($start in $testStarts) {
            if ($start -match "Test (\w+) started") {
                $testNames += $matches[1]
            }
        }
        
        # Check for progress entries after test starts
        $hasProgress = $log | Select-String -Pattern "Step \d+/7|Parsed|Loading|Generating|Video creation request|polling|ready" | Measure-Object | Select-Object -ExpandProperty Count
        
        # Check for success messages in log
        $hasSuccess = $log | Select-String -Pattern "successfully|completed.*Output|Video composition complete|created successfully" -CaseSensitive:$false | Measure-Object | Select-Object -ExpandProperty Count
        
        # Check for explicit errors (not just tracebacks)
        $hasErrors = $log | Select-String -Pattern "^\[ERROR\]|\[X\] Error generating|TypeError|RuntimeError.*Error generating" | Measure-Object | Select-Object -ExpandProperty Count
        
        if ($testNames.Count -gt 0) {
            Write-Host "`n--- Tests Detected: $($testNames -join ', ') ---" -ForegroundColor Cyan
            
            if ($hasProgress -gt 0) {
                Write-Host "  Progress entries: $hasProgress" -ForegroundColor Gray
            }
        }
        
        if ($outputCount -gt 0) {
            Write-Host "`n--- Test Results ---" -ForegroundColor Green
            Write-Host "  [OK] Videos created: $outputCount" -ForegroundColor Green
            foreach ($file in $outputFiles | Select-Object -First 5) {
                $size = [math]::Round($file.Length / 1MB, 2)
                Write-Host "      $($file.Name) ($size MB) - $($file.LastWriteTime.ToString('HH:mm:ss'))" -ForegroundColor Gray
            }
            if ($hasErrors -gt 0) {
                Write-Host "  [!] Some videos failed (partial success)" -ForegroundColor Yellow
            }
        } elseif ($hasSuccess -gt 0 -and $outputCount -eq 0) {
            Write-Host "`n--- Test Status ---" -ForegroundColor Yellow
            Write-Host "  [?] Test reported success but no output files found" -ForegroundColor Yellow
        } elseif ($hasErrors -gt 0) {
            Write-Host "`n--- Test Status ---" -ForegroundColor Red
            Write-Host "  [X] Test failed - errors detected" -ForegroundColor Red
            $errorLines = $log | Select-String -Pattern "^\[ERROR\]|\[X\] Error|TypeError|RuntimeError.*Error generating" | Select-Object -Last 3
            foreach ($err in $errorLines) {
                $errMsg = if ($err -is [Microsoft.PowerShell.Commands.MatchInfo]) { $err.Line } else { $err.ToString() }
                if ($errMsg -match "\[(\d{2}):(\d{2}):(\d{2})\].*?Error(?: generating)? (\w+):\s*(.+)") {
                    Write-Host "      $($matches[4]): $($matches[5].Substring(0, [Math]::Min(60, $matches[5].Length)))..." -ForegroundColor Red
                } elseif ($errMsg.Length -gt 0) {
                    $shortErr = $errMsg.Substring(0, [Math]::Min(80, $errMsg.Length))
                    Write-Host "      $shortErr" -ForegroundColor Red
                }
            }
        } elseif ($hasProgress -gt 0) {
            Write-Host "`n--- Test Status ---" -ForegroundColor Yellow
            Write-Host "  Tests completed - no output files found" -ForegroundColor Yellow
            Write-Host "  Progress was logged: $hasProgress entries" -ForegroundColor Gray
        } else {
            Write-Host "`n--- Test Status ---" -ForegroundColor Yellow
            if ($testNames.Count -gt 0) {
                Write-Host "  Tests started but no progress logged yet" -ForegroundColor Yellow
                Write-Host "  Waiting for initial progress..." -ForegroundColor Gray
            } else {
                Write-Host "  No tests detected in log" -ForegroundColor Gray
            }
        }
        
        # Show recent activity (last 5 meaningful entries)
        $recentEntries = $log | Where-Object { 
            $_ -notmatch "^Traceback|^File.*\.py.*line|^The above exception|^\s+raise |^\s+\^" -and
            $_.Trim().Length -gt 0 -and
            $_ -match "\[START\]|Step|Parsed|Loading|Generating|Video|ERROR|Error|\[OK\]|completed"
        } | Select-Object -Last 5
        
        if ($recentEntries.Count -gt 0) {
            Write-Host "`n--- Recent Activity ---" -ForegroundColor Cyan
            foreach ($entry in $recentEntries) {
                $entryMsg = $entry.Trim()
                if ($entryMsg.Length -gt 90) { $entryMsg = $entryMsg.Substring(0, 87) + "..." }
                Write-Host "  $entryMsg" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host "`n" -ForegroundColor Gray
}

try {
    while ($true) {
        Show-AllProgress
        Start-Sleep -Seconds $updateInterval
    }
} catch {
    Write-Host "`nMonitoring stopped." -ForegroundColor Gray
}

