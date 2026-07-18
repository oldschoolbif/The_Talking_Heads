"""
Run fast tests with lowest quality/fastest settings for HeyGen and D-ID.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any
import time
from datetime import datetime
import subprocess
import threading

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.config_loader import load_config
from src.core.pipeline import Pipeline
from src.utils.console_output import safe_print

# Load environment variables
load_dotenv()

# Test configurations
HEYGEN_TEST = {
    "name": "HeyGen_Fast",
    "script": "test_short_2personas.txt",
    "description": "Short test - fastest/lowest quality HeyGen",
    "provider": "heygen",
    "resolution": {"width": 640, "height": 360},  # Lowest reasonable resolution
}

DID_TEST = {
    "name": "DID_Quick",
    "script": "test_short_2personas.txt",
    "description": "Short test - D-ID parallel",
    "provider": "did",
}

def generate_test(
    test_config: Dict[str, Any],
    base_config: Dict[str, Any],
    output_dir: Path,
) -> Path:
    """Generate a test output."""
    # Progress log file
    progress_log = project_root / ".cache" / "progress.log"
    progress_log.parent.mkdir(parents=True, exist_ok=True)
    
    # Write test start to log
    timestamp = datetime.now().strftime("%H:%M:%S")
    start_message = f"[{timestamp}] [START] Test {test_config['name']} started"
    safe_print(f"\n{'='*60}")
    safe_print(f"Test: {test_config['name']}")
    safe_print(f"Description: {test_config['description']}")
    safe_print(f"{'='*60}")
    
    # Write to log file
    try:
        with open(progress_log, 'a', encoding='utf-8') as f:
            f.write(start_message + '\n')
            f.flush()
    except Exception as e:
        safe_print(f"[WARN] Could not write to progress log: {e}")
    
    # Prepare config for this test
    test_config_dict = base_config.copy()
    
    # Set provider
    test_config_dict["avatar"] = test_config_dict.get("avatar", {})
    test_config_dict["avatar"]["engine"] = test_config["provider"]
    
    # For D-ID tests, override all persona avatar engines to use D-ID
    if test_config["provider"] == "did":
        test_config_dict["avatar"]["engine_override"] = "did"
        safe_print(f"Using D-ID for all personas (engine override)")
    
    # Set resolution for HeyGen (fastest/lowest quality)
    if test_config["provider"] == "heygen" and "resolution" in test_config:
        test_config_dict["avatar"]["resolution"] = test_config["resolution"]
        safe_print(f"Resolution: {test_config['resolution']['width']}x{test_config['resolution']['height']} (fastest)")
    
    # Script path
    script_path = project_root / "examples" / "scripts" / test_config["script"]
    
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    # Output filename
    output_filename = f"{test_config['name']}_output.mp4"
    
    # Set output directory in config
    test_config_dict["storage"] = test_config_dict.get("storage", {})
    test_config_dict["storage"]["outputs_dir"] = str(output_dir)
    
    # Initialize pipeline
    pipeline = Pipeline(test_config_dict, project_root=project_root)
    
    # Progress callback that writes to log file
    progress_log = project_root / ".cache" / "progress.log"
    progress_log.parent.mkdir(parents=True, exist_ok=True)
    
    def progress_callback(message: str, progress: float):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{int(progress*100):3d}%] {message}"
        safe_print(log_message)
        
        # Write to progress log file
        try:
            with open(progress_log, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
                f.flush()
        except Exception as e:
            safe_print(f"[WARN] Could not write to progress log: {e}")
    
    pipeline.progress_callback = progress_callback
    
    # Generate
    try:
        safe_print(f"Starting generation...")
        output_path = pipeline.create_podcast(
            script_path=script_path,
            output_name=output_filename,
        )
        safe_print(f"\n[OK] Test {test_config['name']} completed successfully!")
        safe_print(f"Output: {output_path}")
        return output_path
    except Exception as e:
        # Log full error to progress log
        import traceback
        error_trace = traceback.format_exc()
        timestamp = datetime.now().strftime("%H:%M:%S")
        error_message = f"[{timestamp}] [ERROR] Test {test_config['name']} failed: {str(e)}"
        error_trace_message = f"[{timestamp}] [ERROR] Traceback:\n{error_trace}"
        safe_print(f"\n[X] Test {test_config['name']} failed: {e}")
        safe_print(f"Traceback:\n{error_trace}")
        
        # Write to progress log
        try:
            with open(progress_log, 'a', encoding='utf-8') as f:
                f.write(error_message + '\n')
                f.write(error_trace_message + '\n')
                f.flush()
        except Exception as log_err:
            safe_print(f"[WARN] Could not write error to progress log: {log_err}")
        safe_print(f"\n[X] Error generating {test_config['name']}: {e}")
        import traceback
        safe_print(traceback.format_exc())
        raise

def run_heygen_test():
    """Run HeyGen fast test."""
    try:
        base_config = load_config(project_root / "config" / "config.yaml", project_root)
        output_dir = project_root / "examples" / "outputs" / "fast_tests"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generate_test(HEYGEN_TEST, base_config, output_dir)
    except Exception as e:
        safe_print(f"[X] HeyGen test failed: {e}")

def run_did_test():
    """Run D-ID quick test."""
    try:
        base_config = load_config(project_root / "config" / "config.yaml", project_root)
        output_dir = project_root / "examples" / "outputs" / "fast_tests"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generate_test(DID_TEST, base_config, output_dir)
    except Exception as e:
        safe_print(f"[X] D-ID test failed: {e}")

def main():
    """Run tests in parallel."""
    safe_print("="*60)
    safe_print("Fast Tests - Lowest Quality / Fastest Generation")
    safe_print("="*60)
    safe_print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Clear progress log
    progress_log = project_root / ".cache" / "progress.log"
    if progress_log.exists():
        progress_log.write_text(f"[{datetime.now().strftime('%H:%M:%S')}] [START] Fast tests started\n")
    
    # Run tests in parallel using threads
    heygen_thread = threading.Thread(target=run_heygen_test, name="HeyGenTest")
    did_thread = threading.Thread(target=run_did_test, name="DIDTest")
    
    safe_print("Starting HeyGen test (fastest/lowest quality)...")
    safe_print("Starting D-ID test (parallel)...")
    safe_print("")
    
    heygen_thread.start()
    time.sleep(2)  # Small delay to separate log entries
    did_thread.start()
    
    # Wait for both to complete
    heygen_thread.join()
    did_thread.join()
    
    safe_print("\n" + "="*60)
    safe_print("All tests completed")
    safe_print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        safe_print(f"\n[X] Error: {e}")
        import traceback
        safe_print(traceback.format_exc())
        sys.exit(1)

