"""
Monitor process timeout and investigate if it exceeds expected duration.
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.console_output import safe_print

# Timeout thresholds
WEBHOOK_WAIT_TIMEOUT = 30  # seconds
POLLING_TIMEOUT = 15 * 60  # 15 minutes
DOWNLOAD_TIMEOUT = 2 * 60  # 2 minutes
TOTAL_TIMEOUT = 20 * 60  # 20 minutes total

def check_process_status():
    """Check if process is running and how long it's been."""
    try:
        import psutil
        python_processes = [
            p for p in psutil.process_iter(['pid', 'name', 'create_time', 'cpu_percent'])
            if 'python' in p.info['name'].lower()
        ]
        
        # Filter to recent processes (last 30 minutes)
        recent_processes = []
        for proc in python_processes:
            try:
                create_time = datetime.fromtimestamp(proc.info['create_time'])
                if create_time > datetime.now() - timedelta(minutes=30):
                    recent_processes.append((proc, create_time))
            except:
                pass
        
        if not recent_processes:
            return None, None
        
        # Get the most recent one
        most_recent = max(recent_processes, key=lambda x: x[1])
        proc, start_time = most_recent
        runtime = datetime.now() - start_time
        
        return proc, runtime
    except ImportError:
        safe_print("[WARN] psutil not available, using basic process check")
        return None, None

def check_log_file():
    """Check log file for latest activity."""
    log_file = project_root / ".cache" / "progress.log"
    if not log_file.exists():
        return None, None
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return None, None
            
            last_line = lines[-1].strip()
            # Extract timestamp
            if '[' in last_line and ']' in last_line:
                timestamp_str = last_line.split('[')[1].split(']')[0]
                try:
                    log_time = datetime.strptime(timestamp_str, "%H:%M:%S").replace(
                        year=datetime.now().year,
                        month=datetime.now().month,
                        day=datetime.now().day
                    )
                    time_since = datetime.now() - log_time
                    return last_line, time_since
                except:
                    pass
    except Exception as e:
        safe_print(f"[ERROR] Could not read log file: {e}")
    
    return None, None

def investigate_timeout(runtime_minutes, last_log_entry, time_since_log):
    """Investigate why process is taking too long."""
    safe_print("\n" + "="*60)
    safe_print("TIMEOUT INVESTIGATION")
    safe_print("="*60)
    
    safe_print(f"\nProcess runtime: {runtime_minutes:.1f} minutes")
    safe_print(f"Last log entry: {last_log_entry[:80] if last_log_entry else 'None'}")
    if time_since_log:
        safe_print(f"Time since last log: {time_since_log.total_seconds():.0f} seconds")
    
    # Check for common issues
    issues = []
    
    if runtime_minutes > TOTAL_TIMEOUT:
        issues.append(f"Process exceeded total timeout ({TOTAL_TIMEOUT/60:.0f} minutes)")
    
    if time_since_log and time_since_log.total_seconds() > 120:
        issues.append(f"No log updates for {time_since_log.total_seconds():.0f} seconds - process may be hung")
    
    if last_log_entry and "webhook" in last_log_entry.lower() and runtime_minutes > 1:
        issues.append("Process stuck waiting for webhook (should fallback to polling after 30s)")
    
    if last_log_entry and "polling" in last_log_entry.lower() and runtime_minutes > POLLING_TIMEOUT/60:
        issues.append(f"Polling exceeded expected time ({POLLING_TIMEOUT/60:.0f} minutes)")
    
    if issues:
        safe_print("\n[ISSUES DETECTED]")
        for issue in issues:
            safe_print(f"  - {issue}")
        
        safe_print("\n[RECOMMENDATIONS]")
        safe_print("  1. Check if process is actually running (not hung)")
        safe_print("  2. Check HeyGen API status")
        safe_print("  3. Check network connectivity")
        safe_print("  4. Consider killing and restarting")
    else:
        safe_print("\n[OK] Process appears to be running normally")
        safe_print("     Video generation can take 10-20 minutes for HeyGen")
    
    safe_print("="*60)

def main():
    """Monitor process and check for timeouts."""
    safe_print("="*60)
    safe_print("Process Timeout Monitor")
    safe_print("="*60)
    
    proc, runtime = check_process_status()
    
    if not proc:
        safe_print("\n[INFO] No active process found")
        return
    
    runtime_minutes = runtime.total_seconds() / 60
    
    safe_print(f"\nProcess PID: {proc.info['pid']}")
    safe_print(f"Runtime: {runtime_minutes:.1f} minutes")
    
    # Check log file
    last_log, time_since_log = check_log_file()
    
    # Check if exceeded timeout
    if runtime_minutes > TOTAL_TIMEOUT / 60:
        safe_print(f"\n[ALERT] Process exceeded {TOTAL_TIMEOUT/60:.0f} minute timeout!")
        investigate_timeout(runtime_minutes, last_log, time_since_log)
    elif time_since_log and time_since_log.total_seconds() > 120:
        safe_print(f"\n[WARN] No log updates for {time_since_log.total_seconds():.0f} seconds")
        investigate_timeout(runtime_minutes, last_log, time_since_log)
    else:
        safe_print(f"\n[OK] Process within expected timeframe")
        safe_print(f"     Expected: 6-17 minutes")
        safe_print(f"     Current: {runtime_minutes:.1f} minutes")
        if last_log:
            safe_print(f"     Last activity: {last_log[:60]}...")

if __name__ == "__main__":
    main()

