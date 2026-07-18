"""
Generate comprehensive test outputs for all API combinations.
This script creates separate podcast outputs for each API configuration.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import time

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
        "name": "HeyGen_Studio",
        "description": "HeyGen avatars with studio background, switching layout",
        "avatar_engine": "heygen",
        "scene": "studio",
        "layout": "switching",
    },
    {
        "name": "HeyGen_Office",
        "description": "HeyGen avatars with office background, side-by-side layout",
        "avatar_engine": "heygen",
        "scene": "office",
        "layout": "side_by_side",
    },
    {
        "name": "DID_Studio",
        "description": "D-ID avatars with studio background, switching layout",
        "avatar_engine": "did",
        "scene": "studio",
        "layout": "switching",
    },
    {
        "name": "DID_Office",
        "description": "D-ID avatars with office background, picture-in-picture layout",
        "avatar_engine": "did",
        "scene": "office",
        "layout": "picture_in_picture",
    },
]


def update_config_for_test(config: Dict[str, Any], test_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update config for a specific test."""
    config_copy = config.copy()
    config_copy["avatar"] = config_copy.get("avatar", {}).copy()
    config_copy["avatar"]["engine"] = test_config["avatar_engine"]
    return config_copy


def generate_test_output(
    test_config: Dict[str, Any],
    script_path: Path,
    base_config: Dict[str, Any],
    output_dir: Path,
) -> Path:
    """Generate a test output for a specific configuration."""
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
    
    # Set up progress callback
    def progress_callback(message: str, progress: float):
        safe_print(f"[{int(progress*100):3d}%] {message}")
    
    pipeline.set_progress_callback(progress_callback)
    
    # Generate output filename
    output_name = f"{test_config['name']}_test_output.mp4"
    
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
        safe_print(f"\n[X] Error generating {test_config['name']}: {e}")
        import traceback
        safe_print(traceback.format_exc())
        return None


def main():
    """Generate all test outputs."""
    safe_print("="*60)
    safe_print("Comprehensive API Test Generation")
    safe_print("="*60)
    safe_print("\nThis will generate separate outputs for each API configuration.")
    safe_print("Each test includes:")
    safe_print("  - Multiple personas (Alice & Bob)")
    safe_print("  - Expressions (happy, neutral, surprised, concerned, thinking)")
    safe_print("  - Gestures (wave, point, emphasize, thinking)")
    safe_print("  - Different backgrounds (studio, office)")
    safe_print("  - Different layouts (switching, side-by-side, picture-in-picture)")
    safe_print("  - Real API calls (no mocking)")
    
    # Load base config
    config_path = project_root / "config" / "config.yaml"
    base_config = load_config(config_path)
    
    # Test script path
    script_path = project_root / "examples" / "scripts" / "comprehensive_test_script.txt"
    
    if not script_path.exists():
        safe_print(f"\n[X] Test script not found: {script_path}")
        sys.exit(1)
    
    # Output directory
    output_dir = project_root / "examples" / "outputs" / "comprehensive_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    safe_print(f"\nOutput directory: {output_dir}")
    safe_print(f"Test script: {script_path}")
    safe_print(f"\nTotal tests: {len(TEST_CONFIGS)}")
    
    # Confirm
    safe_print("\nStarting test generation...")
    time.sleep(2)
    
    # Generate each test
    results = []
    start_time = time.time()
    
    for idx, test_config in enumerate(TEST_CONFIGS, 1):
        safe_print(f"\n\n[TEST {idx}/{len(TEST_CONFIGS)}]")
        result = generate_test_output(test_config, script_path, base_config, output_dir)
        results.append({
            "config": test_config,
            "success": result is not None,
            "output_path": result,
        })
        
        # Brief pause between tests
        if idx < len(TEST_CONFIGS):
            safe_print("\nWaiting 5 seconds before next test...")
            time.sleep(5)
    
    # Summary
    total_time = time.time() - start_time
    safe_print("\n\n" + "="*60)
    safe_print("Test Generation Summary")
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
    safe_print("All tests complete!")
    safe_print("="*60)
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()

