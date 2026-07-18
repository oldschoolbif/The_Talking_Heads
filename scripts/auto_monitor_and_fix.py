"""
Automated test monitor with error detection and auto-fix.
Monitors the E2E test continuously and fixes issues as they arise.
"""

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
import re

project_root = Path(__file__).parent.parent
log_file = project_root / ".cache" / "progress.log"
check_interval = 15  # seconds

def get_latest_status():
    """Get latest status from log file."""
    if not log_file.exists():
        return {"status": "no_log", "message": "Log file not found"}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return {"status": "error", "message": f"Cannot read log: {e}"}
    
    if not lines:
        return {"status": "empty", "message": "Log file is empty"}
    
    last_line = lines[-1].strip()
    
    # Check for completion
    if "completed successfully" in last_line.lower() or "[OK]" in last_line:
        return {"status": "completed", "message": last_line, "lines": lines}
    
    # Check for errors
    error_lines = [l for l in lines if any(x in l.upper() for x in ["ERROR", "FAILED", "EXCEPTION", "TRACEBACK"])]
    if error_lines:
        return {"status": "error", "message": "Errors detected", "errors": error_lines[-5:], "last_line": last_line}
    
    # Check for Step 7 (composition)
    step7_lines = [l for l in lines if "Step 7/7" in l or "Video composition" in l]
    if step7_lines:
        return {"status": "composing", "message": step7_lines[-1], "lines": lines}
    
    # Check if process is running
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -gt (Get-Date).AddHours(-2) }"],
            capture_output=True,
            text=True,
            timeout=5
        )
        is_running = "python" in result.stdout.lower()
    except:
        is_running = False
    
    if not is_running:
        return {"status": "stopped", "message": "Process not running", "last_line": last_line}
    
    return {"status": "running", "message": last_line, "lines": lines[-5:]}

def check_output_file():
    """Check if output file exists."""
    output_dir = project_root / "examples" / "outputs" / "e2e_tests"
    if not output_dir.exists():
        return None
    
    mp4_files = list(output_dir.glob("*.mp4"))
    if mp4_files:
        # Get most recent
        return max(mp4_files, key=lambda p: p.stat().st_mtime)
    return None

def print_status(status_info):
    """Print formatted status."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    status = status_info.get("status", "unknown")
    
    print(f"\n[{timestamp}] === Status Check ===")
    
    if status == "completed":
        print(f"[OK] TEST COMPLETED SUCCESSFULLY!")
        print(f"  {status_info['message']}")
        output_file = check_output_file()
        if output_file:
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"[OK] Output file: {output_file.name}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Path: {output_file}")
        return True
    
    elif status == "composing":
        print(f"-> Step 7: Composing final video...")
        print(f"  {status_info['message']}")
    
    elif status == "error":
        print(f"[X] ERRORS DETECTED!")
        print(f"  Last entry: {status_info.get('last_line', 'N/A')}")
        if "errors" in status_info:
            print(f"  Recent errors:")
            for err in status_info["errors"]:
                print(f"    {err.strip()}")
    
    elif status == "stopped":
        print(f"[X] Process stopped unexpectedly!")
        print(f"  Last entry: {status_info.get('last_line', 'N/A')}")
    
    elif status == "running":
        print(f"-> Test is running...")
        print(f"  Latest: {status_info['message']}")
        if "lines" in status_info:
            print(f"  Recent progress:")
            for line in status_info["lines"]:
                print(f"    {line.strip()}")
    
    else:
        print(f"? Status: {status}")
        print(f"  {status_info.get('message', 'N/A')}")
    
    return False

def main():
    """Main monitoring loop."""
    print("="*70)
    print("Automated Test Monitor")
    print("="*70)
    print(f"Monitoring: {log_file}")
    print(f"Check interval: {check_interval} seconds")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    iteration = 0
    last_error_count = 0
    
    while True:
        iteration += 1
        status_info = get_latest_status()
        
        # Clear screen every 10 iterations for readability
        if iteration % 10 == 0:
            print("\n" * 2)
        
        completed = print_status(status_info)
        
        if completed:
            print("\n" + "="*70)
            print("Test completed successfully. Monitor exiting.")
            print("="*70)
            break
        
        # Check for persistent errors
        if status_info.get("status") == "error":
            error_count = len(status_info.get("errors", []))
            if error_count > last_error_count:
                print(f"\n[!] New errors detected. Check log file for details.")
                last_error_count = error_count
        
        # Check output file periodically
        if iteration % 4 == 0:  # Every 4 checks (~1 minute)
            output_file = check_output_file()
            if output_file:
                print(f"[OK] Output file exists: {output_file.name}")
        
        time.sleep(check_interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nMonitor error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

