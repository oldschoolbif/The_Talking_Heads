"""
Run progressive tests: short, medium, and long with different persona counts.
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

# Test configurations
TEST_CONFIGS = [
    {
        "name": "Short_2Personas",
        "script": "test_short_2personas.txt",
        "description": "Very short test - 2 sentences, 2 personas",
    },
    {
        "name": "Medium_2Personas",
        "script": "test_medium_2personas.txt",
        "description": "Medium test - several lines each, 2 personas",
    },
    {
        "name": "Long_5Personas",
        "script": "test_long_5personas.txt",
        "description": "Long test - several lines each, 5 personas",
    },
]

def generate_test(
    test_config: Dict[str, Any],
    base_config: Dict[str, Any],
    output_dir: Path,
) -> Path:
    """Generate a test output."""
    safe_print(f"\n{'='*60}")
    safe_print(f"Test: {test_config['name']}")
    safe_print(f"Description: {test_config['description']}")
    safe_print(f"{'='*60}")
    
    # Update config for HeyGen
    config = base_config.copy()
    config["avatar"] = config.get("avatar", {}).copy()
    config["avatar"]["engine"] = "heygen"
    
    # Test script path
    script_path = project_root / "examples" / "scripts" / test_config["script"]
    
    if not script_path.exists():
        safe_print(f"\n[X] Test script not found: {script_path}")
        return None
    
    # Create output directory for this test
    test_output_dir = output_dir / test_config["name"]
    test_output_dir.mkdir(parents=True, exist_ok=True)
    
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
            f.write(f"[{start_time}] [START] Test {test_config['name']} started\n")
            f.flush()
    except Exception:
        pass
    
    # Generate output filename
    output_name = f"{test_config['name']}.mp4"
    
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
        error_msg = f"\n[X] Error generating {test_config['name']}: {e}"
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


def main():
    """Run progressive tests."""
    safe_print("="*60)
    safe_print("Progressive Test Suite")
    safe_print("="*60)
    safe_print("\nThis will run three tests sequentially:")
    for idx, test in enumerate(TEST_CONFIGS, 1):
        safe_print(f"  {idx}. {test['name']}: {test['description']}")
    
    # Load base config
    config_path = project_root / "config" / "config.yaml"
    if not config_path.exists():
        safe_print(f"\n[X] Config file not found: {config_path}")
        sys.exit(1)
    
    base_config = load_config(config_path)
    
    # Output directory
    output_dir = project_root / "examples" / "outputs" / "progressive_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_print(f"\nOutput directory: {output_dir}")
    safe_print(f"\nStarting progressive tests...\n")
    time.sleep(2)
    
    # Run each test sequentially
    results = []
    total_start_time = time.time()
    
    for idx, test_config in enumerate(TEST_CONFIGS, 1):
        safe_print(f"\n{'='*60}")
        safe_print(f"TEST {idx}/{len(TEST_CONFIGS)}: {test_config['name']}")
        safe_print(f"{'='*60}")
        
        result = generate_test(test_config, base_config, output_dir)
        results.append({
            "config": test_config,
            "success": result is not None,
            "output_path": result,
        })
        
        # Pause between tests
        if idx < len(TEST_CONFIGS):
            safe_print(f"\nWaiting 5 seconds before next test...")
            time.sleep(5)
    
    # Summary
    total_time = time.time() - total_start_time
    safe_print("\n\n" + "="*60)
    safe_print("Progressive Test Summary")
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
        safe_print("[OK] All progressive tests passed!")
    else:
        safe_print("[X] Some tests failed. Check errors above.")
    safe_print("="*60)
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

