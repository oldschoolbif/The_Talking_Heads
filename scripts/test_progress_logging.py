"""
Test script to verify progress logging works correctly.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.console_output import safe_print

def test_progress_logging():
    """Test that progress logging works."""
    log_file = project_root / ".cache" / "progress.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Clear log
    log_file.write_text("", encoding='utf-8')
    safe_print(f"[TEST] Cleared log file: {log_file}")
    
    # Test progress callback
    def progress_callback(message: str, progress: float):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{int(progress*100):3d}%] {message}"
        
        # Print to console
        safe_print(log_message)
        
        # Write to log file
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
                f.flush()
                import os
                os.fsync(f.fileno())
        except Exception as e:
            safe_print(f"[ERROR] Failed to write: {e}")
    
    # Simulate progress
    safe_print("\n[TEST] Simulating progress updates...")
    progress_callback("Test step 1: Starting", 0.0)
    import time
    time.sleep(0.5)
    
    progress_callback("Test step 2: Processing", 0.25)
    time.sleep(0.5)
    
    progress_callback("Test step 3: Almost done", 0.75)
    time.sleep(0.5)
    
    progress_callback("Test step 4: Complete", 1.0)
    
    # Verify log file
    safe_print(f"\n[TEST] Checking log file: {log_file}")
    if log_file.exists():
        content = log_file.read_text(encoding='utf-8')
        lines = content.strip().split('\n')
        safe_print(f"[OK] Log file exists with {len(lines)} lines")
        safe_print("\n[LOG CONTENT]")
        for line in lines:
            safe_print(f"  {line}")
        
        if len(lines) >= 4:
            safe_print("\n[OK] Progress logging is working!")
            return True
        else:
            safe_print(f"\n[X] Expected at least 4 lines, got {len(lines)}")
            return False
    else:
        safe_print("\n[X] Log file was not created!")
        return False

if __name__ == "__main__":
    success = test_progress_logging()
    sys.exit(0 if success else 1)

