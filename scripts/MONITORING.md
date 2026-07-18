# Monitoring Video Generation Tests

## Quick Reference

**For monitoring tests in real-time, use:**
```powershell
.\scripts\monitor_all_progress.ps1
```

This PowerShell script:
- Auto-refreshes every 5 seconds
- Groups videos by ID
- Shows progress for HeyGen and D-ID
- Filters out stale/completed videos
- Shows final success/failure status

## Alternative Monitoring Scripts

1. **`monitor_progress.py`** - Python script for watching log file
   ```bash
   python scripts/monitor_progress.py --watch
   ```
   - Shows raw log output
   - Good for debugging
   - Requires `--watch` flag for real-time monitoring

2. **`check_status.ps1`** - Quick status check
   ```powershell
   .\scripts\check_status.ps1
   ```
   - One-time status snapshot
   - Shows running processes and latest entries

3. **`monitor_all_progress.ps1`** - **RECOMMENDED**
   ```powershell
   .\scripts\monitor_all_progress.ps1
   ```
   - Best for monitoring active tests
   - Groups videos correctly
   - Shows meaningful summaries

## Log File Location

Progress is logged to: `.cache\progress.log`

## Test Scripts

- `scripts/run_fast_tests.py` - Fast tests (lowest quality)
- `scripts/run_progressive_tests.py` - Progressive tests (short, medium, long)
- `scripts/quick_test_generation.py` - Quick test generation

