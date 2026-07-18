"""
E2E Test: Generate a complete video with 2 personas talking.
This test verifies the full pipeline including final video composition.
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
    """Run E2E test with 2 personas."""
    safe_print("="*70)
    safe_print("E2E Test: 2-Persona Complete Video Generation")
    safe_print("="*70)
    safe_print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load base config
    config_path = project_root / "config" / "config.yaml"
    if not config_path.exists():
        safe_print(f"\n[X] Config file not found: {config_path}")
        sys.exit(1)
    
    base_config = load_config(config_path, project_root)
    
    # Use medium 2-persona script (longer test)
    script_path = project_root / "examples" / "scripts" / "test_medium_2personas.txt"
    
    if not script_path.exists():
        safe_print(f"\n[X] Test script not found: {script_path}")
        sys.exit(1)
    
    # Output directory
    output_dir = project_root / "examples" / "outputs" / "e2e_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Clear progress log
    progress_log = project_root / ".cache" / "progress.log"
    progress_log.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize log file
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        with open(progress_log, 'w', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [START] E2E Test: 2-Persona Complete Video Generation\n")
            f.write(f"[{timestamp}] Script: {script_path.name}\n")
            f.write(f"[{timestamp}] Output directory: {output_dir}\n")
            f.flush()
    except Exception as e:
        safe_print(f"[WARN] Could not initialize log file: {e}")
    
    safe_print(f"Script: {script_path.name}")
    safe_print(f"Output directory: {output_dir}")
    safe_print(f"Progress log: {progress_log}\n")
    
    # Set output directory in config
    base_config["storage"] = base_config.get("storage", {})
    base_config["storage"]["outputs_dir"] = str(output_dir)
    
    # Ensure HeyGen is used (not D-ID for this test)
    base_config["avatar"] = base_config.get("avatar", {})
    base_config["avatar"]["engine"] = "heygen"
    
    # Use fastest/lowest quality for testing
    base_config["avatar"]["resolution"] = {
        "width": 640,
        "height": 360
    }
    
    # Initialize pipeline
    pipeline = Pipeline(base_config, project_root=project_root)
    
    # Progress callback that writes to log file
    def progress_callback(message: str, progress: float):
        timestamp = datetime.now().strftime("%H:%M:%S")
        progress_percent = int(progress * 100)
        log_message = f"[{timestamp}] [{progress_percent:3d}%] {message}"
        
        # Print to console
        safe_print(log_message)
        
        # Write to progress log file
        try:
            with open(progress_log, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
                f.flush()
        except Exception as e:
            safe_print(f"[WARN] Could not write to progress log: {e}")
    
    pipeline.set_progress_callback(progress_callback)
    
    # Output filename
    output_filename = f"e2e_2personas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    safe_print("\n" + "="*70)
    safe_print("Starting video generation...")
    safe_print("="*70 + "\n")
    
    try:
        start_time = time.time()
        
        # Generate complete video (all 7 steps including final composition)
        output_path = pipeline.create_podcast(
            script_path=script_path,
            scene_name="studio",
            layout="switching",  # Show active speaker
            output_name=output_filename,
            cleanup_temp=False,  # Keep temp files for debugging
        )
        
        elapsed = time.time() - start_time
        
        # Verify output exists
        if output_path and output_path.exists():
            file_size = output_path.stat().st_size / 1024 / 1024  # MB
            safe_print("\n" + "="*70)
            safe_print("[OK] E2E Test Completed Successfully!")
            safe_print("="*70)
            safe_print(f"Output file: {output_path}")
            safe_print(f"File size: {file_size:.2f} MB")
            safe_print(f"Duration: {elapsed/60:.1f} minutes")
            safe_print(f"\nThis video should contain BOTH avatars (ALICE and BOB)")
            safe_print(f"switching between speakers based on the script.")
            safe_print("="*70)
            
            # Log success
            timestamp = datetime.now().strftime("%H:%M:%S")
            try:
                with open(progress_log, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] [OK] Test completed successfully!\n")
                    f.write(f"[{timestamp}] Output: {output_path}\n")
                    f.write(f"[{timestamp}] Size: {file_size:.2f} MB\n")
                    f.write(f"[{timestamp}] Duration: {elapsed/60:.1f} minutes\n")
                    f.flush()
            except Exception:
                pass
            
            return output_path
        else:
            safe_print("\n" + "="*70)
            safe_print("[X] E2E Test Failed: Output file not found")
            safe_print("="*70)
            safe_print(f"Expected: {output_path}")
            safe_print("The pipeline may have failed at Step 7 (video composition).")
            safe_print("Check the logs above for errors.")
            sys.exit(1)
            
    except Exception as e:
        error_msg = f"\n[X] E2E Test Failed: {e}"
        safe_print(error_msg)
        import traceback
        tb = traceback.format_exc()
        safe_print(tb)
        
        # Log error
        timestamp = datetime.now().strftime("%H:%M:%S")
        try:
            with open(progress_log, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [ERROR] {error_msg}\n")
                f.write(f"[{timestamp}] [TRACEBACK]\n{tb}\n")
                f.flush()
        except Exception:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        safe_print(f"\n[X] Fatal error: {e}")
        import traceback
        safe_print(traceback.format_exc())
        sys.exit(1)

