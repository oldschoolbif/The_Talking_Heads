"""
Monitor active process and watch for failure symptoms.
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.console_output import safe_print

LOG_FILE = project_root / ".cache" / "progress.log"
CHECK_INTERVAL = 30  # Check every 30 seconds
STALL_THRESHOLD = 120  # Alert if no updates for 2 minutes
TOTAL_TIMEOUT = 20 * 60  # 20 minutes total timeout

def get_latest_log_entry():
    """Get the latest log entry and its timestamp."""
    if not LOG_FILE.exists():
        return None, None, None
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                return None, None, None
            
            last_line = lines[-1].strip()
            # Extract timestamp
            if '[' in last_line and ']' in last_line:
                parts = last_line.split('[')
                if len(parts) >= 2:
                    timestamp_str = parts[1].split(']')[0]
                    try:
                        log_time = datetime.strptime(timestamp_str, "%H:%M:%S").replace(
                            year=datetime.now().year,
                            month=datetime.now().month,
                            day=datetime.now().day
                        )
                        time_since = datetime.now() - log_time
                        return last_line, log_time, time_since
                    except:
                        pass
    except Exception as e:
        safe_print(f"[ERROR] Could not read log: {e}")
    
    return None, None, None

def check_for_failure_symptoms(last_line, time_since_log, runtime_minutes):
    """Check for symptoms of failure."""
    symptoms = []
    
    # Check for error keywords
    if last_line:
        error_keywords = ["error", "failed", "exception", "timeout", "403", "401", "500", "502", "503"]
        lower_line = last_line.lower()
        for keyword in error_keywords:
            if keyword in lower_line:
                symptoms.append(f"Error keyword detected: '{keyword}'")
    
    # Check for stall
    if time_since_log and time_since_log.total_seconds() > STALL_THRESHOLD:
        symptoms.append(f"No log updates for {time_since_log.total_seconds():.0f} seconds (stall threshold: {STALL_THRESHOLD}s)")
    
    # Check for timeout
    if runtime_minutes > TOTAL_TIMEOUT / 60:
        symptoms.append(f"Process exceeded {TOTAL_TIMEOUT/60:.0f} minute timeout")
    
    # Check for repeated 404s (might indicate API issue)
    if last_line and "404" in last_line:
        # Count recent 404s
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                recent_lines = f.readlines()[-20:]  # Last 20 lines
                recent_404s = [l for l in recent_lines if "404" in l]
                if len(recent_404s) > 15:  # More than 15 404s in last 20 lines
                    symptoms.append(f"Excessive 404 responses ({len(recent_404s)} in last 20 log entries) - API may be having issues")
        except:
            pass
    
    return symptoms

def monitor_process():
    """Monitor the process and watch for failure symptoms."""
    safe_print("="*60)
    safe_print("Active Process Monitor")
    safe_print("="*60)
    safe_print(f"Monitoring log: {LOG_FILE}")
    safe_print(f"Check interval: {CHECK_INTERVAL} seconds")
    safe_print(f"Stall threshold: {STALL_THRESHOLD} seconds")
    safe_print("Press Ctrl+C to stop monitoring\n")
    
    try:
        import psutil
        has_psutil = True
    except ImportError:
        has_psutil = False
        safe_print("[WARN] psutil not available, using basic monitoring")
    
    check_count = 0
    
    try:
        while True:
            check_count += 1
            now = datetime.now()
            
            # Get process info
            runtime_minutes = 0
            process_found = False
            if has_psutil:
                try:
                    python_processes = [
                        p for p in psutil.process_iter(['pid', 'name', 'create_time'])
                        if 'python' in p.info['name'].lower()
                    ]
                    recent_processes = []
                    for proc in python_processes:
                        try:
                            create_time = datetime.fromtimestamp(proc.info['create_time'])
                            if create_time > datetime.now() - timedelta(minutes=30):
                                recent_processes.append((proc, create_time))
                        except:
                            pass
                    
                    if recent_processes:
                        most_recent = max(recent_processes, key=lambda x: x[1])
                        proc, start_time = most_recent
                        runtime_minutes = (now - start_time).total_seconds() / 60
                        process_found = True
                except:
                    pass
            
            # Get latest log entry
            last_line, log_time, time_since_log = get_latest_log_entry()
            
            # Check for symptoms
            symptoms = check_for_failure_symptoms(last_line, time_since_log, runtime_minutes)
            
            # Display status
            if check_count % 2 == 0 or symptoms:  # Show every other check, or immediately if symptoms
                safe_print(f"\n[{now.strftime('%H:%M:%S')}] Check #{check_count}")
                if process_found:
                    safe_print(f"  Process runtime: {runtime_minutes:.1f} minutes")
                if last_line:
                    safe_print(f"  Last log: {last_line[:70]}...")
                    if time_since_log:
                        safe_print(f"  Time since log: {time_since_log.total_seconds():.0f} seconds")
                
                if symptoms:
                    safe_print(f"\n  [ALERT] Failure symptoms detected:")
                    for symptom in symptoms:
                        safe_print(f"    - {symptom}")
                else:
                    safe_print(f"  [OK] No failure symptoms detected")
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        safe_print("\n[INFO] Monitoring stopped by user")
    except Exception as e:
        safe_print(f"\n[ERROR] Monitor error: {e}")

if __name__ == "__main__":
    monitor_process()

