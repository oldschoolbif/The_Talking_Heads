"""
Check progress of comprehensive test generation.
Run this after updating Cursor or anytime to see test status.
"""

import sys
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.console_output import safe_print

# Test configurations
TEST_CONFIGS = [
    "HeyGen_Studio",
    "HeyGen_Office",
    "DID_Studio",
    "DID_Office",
]

def format_size(bytes_size):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def check_test_progress():
    """Check progress of all test generations."""
    safe_print("="*60)
    safe_print("Comprehensive Test Progress Checker")
    safe_print("="*60)
    safe_print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    output_dir = project_root / "examples" / "outputs" / "comprehensive_tests"
    
    if not output_dir.exists():
        safe_print("[!] Test output directory not found yet.")
        safe_print(f"    Expected: {output_dir}")
        safe_print("\n    Tests may not have started yet.")
        return
    
    results = []
    total_size = 0
    
    for test_name in TEST_CONFIGS:
        test_dir = output_dir / test_name
        output_file = test_dir / f"{test_name}_test_output.mp4"
        
        status = "PENDING"
        size = 0
        modified = None
        
        if output_file.exists():
            status = "COMPLETE"
            size = output_file.stat().st_size
            modified = datetime.fromtimestamp(output_file.stat().st_mtime)
            total_size += size
        elif test_dir.exists():
            # Check for temp files indicating progress
            temp_files = list(test_dir.glob("*"))
            if temp_files:
                status = "IN PROGRESS"
                # Find most recent file
                most_recent = max(temp_files, key=lambda p: p.stat().st_mtime)
                modified = datetime.fromtimestamp(most_recent.stat().st_mtime)
        
        results.append({
            "name": test_name,
            "status": status,
            "size": size,
            "modified": modified,
        })
    
    # Display results
    safe_print("Test Status:")
    safe_print("-" * 60)
    
    for result in results:
        status_icon = {
            "COMPLETE": "[OK]",
            "IN PROGRESS": "[...]",
            "PENDING": "[  ]",
        }.get(result["status"], "[?]")
        
        safe_print(f"{status_icon} {result['name']:<20} {result['status']}")
        
        if result["status"] == "COMPLETE":
            safe_print(f"     Size: {format_size(result['size'])}")
            safe_print(f"     Completed: {result['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        elif result["status"] == "IN PROGRESS" and result["modified"]:
            elapsed = datetime.now() - result["modified"]
            safe_print(f"     Last activity: {elapsed.total_seconds():.0f} seconds ago")
        
        safe_print()
    
    # Summary
    completed = sum(1 for r in results if r["status"] == "COMPLETE")
    in_progress = sum(1 for r in results if r["status"] == "IN PROGRESS")
    pending = sum(1 for r in results if r["status"] == "PENDING")
    
    safe_print("-" * 60)
    safe_print(f"Summary: {completed} complete, {in_progress} in progress, {pending} pending")
    if total_size > 0:
        safe_print(f"Total output size: {format_size(total_size)}")
    safe_print("="*60)
    
    # Check for running Python process
    try:
        import psutil
        python_processes = [
            p for p in psutil.process_iter(['pid', 'name', 'create_time', 'cpu_percent'])
            if 'python' in p.info['name'].lower()
        ]
        
        if python_processes:
            safe_print("\n[INFO] Python processes running:")
            for proc in python_processes[:3]:  # Show up to 3
                try:
                    runtime = datetime.now() - datetime.fromtimestamp(proc.info['create_time'])
                    safe_print(f"  PID {proc.info['pid']}: Running for {runtime.total_seconds()/60:.1f} minutes")
                except:
                    pass
    except ImportError:
        pass  # psutil not available, skip
    
    return completed == len(TEST_CONFIGS)

if __name__ == "__main__":
    try:
        all_complete = check_test_progress()
        if all_complete:
            safe_print("\n[OK] All tests complete!")
            sys.exit(0)
        else:
            safe_print("\n[INFO] Tests still in progress. Run again to check status.")
            sys.exit(0)
    except KeyboardInterrupt:
        safe_print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        safe_print(f"\n[X] Error: {e}")
        import traceback
        safe_print(traceback.format_exc())
        sys.exit(1)

