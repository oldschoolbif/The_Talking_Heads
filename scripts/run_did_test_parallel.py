"""
Run D-ID test with 5 personas script in parallel.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.config_loader import load_config
from src.core.pipeline import Pipeline
from src.utils.console_output import safe_print

# Load environment variables
load_dotenv()

def main():
    """Run D-ID test with 5 personas."""
    safe_print("="*60)
    safe_print("D-ID Test - 5 Personas (Parallel)")
    safe_print("="*60)
    safe_print("\nThis will run a D-ID test with 5 personas in parallel with other tests.")
    
    # Load base config
    config_path = project_root / "config" / "config.yaml"
    if not config_path.exists():
        safe_print(f"\n[X] Config file not found: {config_path}")
        sys.exit(1)
    
    base_config = load_config(config_path)
    
    # Update config for D-ID
    config = base_config.copy()
    config["avatar"] = config.get("avatar", {}).copy()
    config["avatar"]["engine"] = "did"
    
    # Test script path (using the 5 personas script)
    script_path = project_root / "examples" / "scripts" / "test_long_5personas.txt"
    
    if not script_path.exists():
        safe_print(f"\n[X] Test script not found: {script_path}")
        sys.exit(1)
    
    # Output directory
    output_dir = project_root / "examples" / "outputs" / "progressive_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create output directory for this test
    test_output_dir = output_dir / "DID_Long_5Personas"
    test_output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_print(f"\nOutput directory: {test_output_dir}")
    safe_print(f"Test script: {script_path}")
    safe_print(f"\nStarting D-ID test...\n")
    time.sleep(1)
    
    # Initialize pipeline
    pipeline = Pipeline(config, project_root=project_root)
    
    # Set up progress callback with file logging
    log_file = project_root / ".cache" / "progress.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def progress_callback(message: str, progress: float):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{int(progress*100):3d}%] {message}"
        
        # Print to console
        safe_print(log_message)
        
        # Append to log file (don't overwrite - we have multiple tests)
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
                f.flush()
                try:
                    os.fsync(f.fileno())
                except AttributeError:
                    pass
        except Exception as e:
            try:
                error_log = project_root / ".cache" / "progress_error.log"
                with open(error_log, 'a', encoding='utf-8') as ef:
                    ef.write(f"[{timestamp}] ERROR writing to progress.log: {e}\n")
                    ef.flush()
            except:
                pass
    
    pipeline.set_progress_callback(progress_callback)
    
    # Write initial log entry
    try:
        start_time = datetime.now().strftime("%H:%M:%S")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{start_time}] [START] D-ID test (5 personas) started\n")
            f.flush()
    except Exception:
        pass
    
    # Generate output filename
    output_name = "DID_Long_5Personas.mp4"
    
    try:
        # Run pipeline
        start_time = time.time()
        output_path = pipeline.create_podcast(
            script_path=script_path,
            scene_name="studio",
            layout="switching",
            output_name=output_name,
            cleanup_temp=False,
        )
        elapsed = time.time() - start_time
        
        # Move output to test directory
        final_path = test_output_dir / output_name
        if output_path.exists():
            output_path.rename(final_path)
            safe_print(f"\n[OK] Generated: {final_path}")
            safe_print(f"     Duration: {elapsed:.1f} seconds")
            safe_print(f"     Size: {final_path.stat().st_size / 1024 / 1024:.2f} MB")
            return final_path
        else:
            safe_print(f"\n[X] Output file not found: {output_path}")
            return None
            
    except Exception as e:
        error_msg = f"\n[X] Error generating D-ID test: {e}"
        safe_print(error_msg)
        import traceback
        tb = traceback.format_exc()
        safe_print(tb)
        
        # Log error to file
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {error_msg}\n")
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [TRACEBACK]\n{tb}\n")
                f.flush()
        except Exception:
            pass
        
        return None


if __name__ == "__main__":
    main()

