"""
Monitor progress of running podcast generation.
Shows real-time progress from log file or process output.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.console_output import safe_print

LOG_FILE = project_root / ".cache" / "progress.log"
STATUS_FILE = project_root / ".cache" / "status.json"

def monitor_log_file():
    """Monitor progress log file."""
    if not LOG_FILE.exists():
        safe_print(f"[INFO] No progress log found at {LOG_FILE}")
        safe_print("[INFO] Progress logging will be enabled on next run.")
        return
    
    safe_print("="*60)
    safe_print("Progress Monitor")
    safe_print("="*60)
    safe_print(f"Monitoring: {LOG_FILE}")
    safe_print("Press Ctrl+C to stop monitoring\n")
    
    try:
        # Read existing content
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            for line in lines[-20:]:  # Show last 20 lines
                safe_print(line.rstrip())
        
        # Tail the file
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            # Go to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    safe_print(line.rstrip())
                else:
                    time.sleep(0.5)  # Wait for new content
                    
    except KeyboardInterrupt:
        safe_print("\n[INFO] Monitoring stopped.")
    except Exception as e:
        safe_print(f"[ERROR] Error monitoring log: {e}")

def show_status_file():
    """Show status from JSON file."""
    import json
    
    if not STATUS_FILE.exists():
        safe_print(f"[INFO] No status file found at {STATUS_FILE}")
        return
    
    try:
        with open(STATUS_FILE, 'r') as f:
            status = json.load(f)
        
        safe_print("="*60)
        safe_print("Current Status")
        safe_print("="*60)
        safe_print(f"Test: {status.get('test_name', 'Unknown')}")
        safe_print(f"Step: {status.get('step', 'Unknown')}")
        safe_print(f"Progress: {status.get('progress', 0)*100:.1f}%")
        safe_print(f"Message: {status.get('message', 'No message')}")
        safe_print(f"Last Update: {status.get('timestamp', 'Unknown')}")
        safe_print("="*60)
    except Exception as e:
        safe_print(f"[ERROR] Error reading status: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor podcast generation progress")
    parser.add_argument("--status", action="store_true", help="Show current status and exit")
    parser.add_argument("--watch", action="store_true", help="Watch log file in real-time")
    
    args = parser.parse_args()
    
    if args.status:
        show_status_file()
    elif args.watch:
        monitor_log_file()
    else:
        # Default: show status
        show_status_file()
        safe_print("\n[INFO] Use --watch to monitor in real-time")
        safe_print(f"[INFO] Use: python {Path(__file__).name} --watch")

