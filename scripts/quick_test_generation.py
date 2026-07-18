"""
Quick test generation - 2 videos to verify system functionality.
Uses very short script for fast testing.
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

# Quick test configurations (just 2)
QUICK_TEST_CONFIGS = [
    {
        "name": "HeyGen_Quick",
        "description": "HeyGen avatars - quick verification",
        "avatar_engine": "heygen",
        "scene": "studio",
        "layout": "switching",
    },
    {
        "name": "DID_Quick",
        "description": "D-ID avatars - quick verification",
        "avatar_engine": "did",
        "scene": "studio",
        "layout": "switching",
    },
]


def update_config_for_test(config: Dict[str, Any], test_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update config for a specific test."""
    config_copy = config.copy()
    config_copy["avatar"] = config_copy.get("avatar", {}).copy()
    config_copy["avatar"]["engine"] = test_config["avatar_engine"]
    return config_copy


def generate_quick_test(
    test_config: Dict[str, Any],
    script_path: Path,
    base_config: Dict[str, Any],
    output_dir: Path,
) -> Path:
    """Generate a quick test output."""
    safe_print(f"\n{'='*60}")
    safe_print(f"Generating: {test_config['name']}")
    safe_print(f"Description: {test_config['description']}")
    safe_print(f"{'='*60}")
    
    # Update config for this test
    test_config_dict = update_config_for_test(base_config, test_config)
    
    # Create output directory for this test
    test_output_dir = output_dir / test_config["name"]
    test_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize pipeline
    pipeline = Pipeline(test_config_dict, project_root=project_root)
    
    # Set up progress callback with file logging
    log_file = project_root / ".cache" / "progress.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Delete old log file completely (not just clear)
    try:
        if log_file.exists():
            log_file.unlink()
    except Exception:
        pass
    
    # Create new log file with initial entry
    try:
        start_time = datetime.now().strftime("%H:%M:%S")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"[{start_time}] [START] Log file initialized for {test_config['name']}\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:
        safe_print(f"[WARN] Could not initialize log file: {e}")
    
    def progress_callback(message: str, progress: float):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{int(progress*100):3d}%] {message}"
        
        # Print to console
        safe_print(log_message)
        
        # Write to log file (always, even if console fails)
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
                f.flush()  # Ensure immediate write
                try:
                    os.fsync(f.fileno())  # Force write to disk
                except AttributeError:
                    pass  # os.fsync not available on all systems
        except Exception as e:
            # Try to log the error itself to a different location
            try:
                error_log = project_root / ".cache" / "progress_error.log"
                with open(error_log, 'a', encoding='utf-8') as ef:
                    ef.write(f"[{timestamp}] ERROR writing to progress.log: {e}\n")
                    ef.flush()
            except:
                pass
    
    pipeline.set_progress_callback(progress_callback)
    
    # Test that logging works immediately
    try:
        test_time = datetime.now().strftime("%H:%M:%S")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{test_time}] [TEST] Progress callback registered for {test_config['name']}\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except AttributeError:
                pass
        safe_print(f"[TEST] Log file test write successful: {log_file}")
    except Exception as e:
        safe_print(f"[ERROR] Log file test write failed: {e}")
    
    # Also log test start
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [START] Generating {test_config['name']}\n")
            f.flush()
    except Exception:
        pass
    
    # Generate output filename
    output_name = f"{test_config['name']}_quick_test.mp4"
    
    try:
        # Run pipeline
        start_time = time.time()
        output_path = pipeline.create_podcast(
            script_path=script_path,
            scene_name=test_config["scene"],
            layout=test_config["layout"],
            output_name=output_name,
            cleanup_temp=False,  # Keep temp files for debugging
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
        error_msg = f"\n[X] Error generating {test_config['name']}: {e}"
        safe_print(error_msg)
        import traceback
        tb = traceback.format_exc()
        safe_print(tb)
        
        # Log error to file
        try:
            log_file = project_root / ".cache" / "progress.log"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {error_msg}\n")
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [TRACEBACK]\n{tb}\n")
                f.flush()
        except Exception:
            pass
        
        return None


def main():
    """Generate quick test outputs."""
    safe_print("="*60)
    safe_print("Quick System Verification Test")
    safe_print("="*60)
    safe_print("\nThis will generate 2 short videos to verify system functionality:")
    safe_print("  1. HeyGen avatars")
    safe_print("  2. D-ID avatars")
    safe_print("\nUsing a very short script for fast testing.")
    
    # Load base config
    config_path = project_root / "config" / "config.yaml"
    if not config_path.exists():
        safe_print(f"\n[X] Config file not found: {config_path}")
        sys.exit(1)
    
    base_config = load_config(config_path)
    
    # Test script path
    script_path = project_root / "examples" / "scripts" / "quick_test_script.txt"
    
    if not script_path.exists():
        safe_print(f"\n[X] Test script not found: {script_path}")
        sys.exit(1)
    
    # Output directory
    output_dir = project_root / "examples" / "outputs" / "quick_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_print(f"\nOutput directory: {output_dir}")
    safe_print(f"Test script: {script_path}")
    safe_print(f"\nStarting quick test generation...\n")
    time.sleep(1)
    
    # Generate each test
    results = []
    start_time = time.time()
    
    for idx, test_config in enumerate(QUICK_TEST_CONFIGS, 1):
        safe_print(f"\n[TEST {idx}/{len(QUICK_TEST_CONFIGS)}]")
        result = generate_quick_test(test_config, script_path, base_config, output_dir)
        results.append({
            "config": test_config,
            "success": result is not None,
            "output_path": result,
        })
        
        # Brief pause between tests
        if idx < len(QUICK_TEST_CONFIGS):
            safe_print("\nWaiting 3 seconds before next test...")
            time.sleep(3)
    
    # Summary
    total_time = time.time() - start_time
    safe_print("\n\n" + "="*60)
    safe_print("Quick Test Summary")
    safe_print("="*60)
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    safe_print(f"\nTotal tests: {len(results)}")
    safe_print(f"Successful: {successful}")
    safe_print(f"Failed: {failed}")
    safe_print(f"Total time: {total_time/60:.1f} minutes")
    
    safe_print("\nResults:")
    for result in results:
        status = "[OK]" if result["success"] else "[X]"
        safe_print(f"  {status} {result['config']['name']}")
        if result["success"] and result["output_path"]:
            safe_print(f"      Output: {result['output_path']}")
    
    safe_print("\n" + "="*60)
    if successful == len(results):
        safe_print("[OK] All quick tests passed! System is functioning.")
    else:
        safe_print("[X] Some tests failed. Check errors above.")
    safe_print("="*60)
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

