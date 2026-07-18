"""
E2E D-ID test with proper image URL handling.
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.config_loader import load_config
from src.core.pipeline import Pipeline
from src.utils.console_output import safe_print

load_dotenv()

def main():
    """Test D-ID with a simple 2-persona script."""
    safe_print("="*70)
    safe_print("D-ID E2E Test")
    safe_print("="*70)
    
    # Load config
    config_path = project_root / "config" / "config.yaml"
    base_config = load_config(config_path, project_root)
    
    # Set D-ID as engine
    base_config["avatar"]["engine"] = "did"
    base_config["avatar"]["engine_override"] = "did"  # Override persona settings
    
    # Use short script
    script_path = project_root / "examples" / "scripts" / "test_short_2personas.txt"
    
    # Output directory
    output_dir = project_root / "examples" / "outputs" / "did_tests"
    output_dir.mkdir(parents=True, exist_ok=True)
    base_config["storage"]["outputs_dir"] = str(output_dir)
    
    # Initialize pipeline
    pipeline = Pipeline(base_config, project_root=project_root)
    
    # Progress callback
    def progress_callback(message: str, progress: float):
        safe_print(f"[{int(progress*100):3d}%] {message}")
    
    pipeline.set_progress_callback(progress_callback)
    
    # Generate
    try:
        output_path = pipeline.create_podcast(
            script_path=script_path,
            scene_name="studio",
            layout="switching",
            output_name="did_test_output.mp4",
            cleanup_temp=False,
        )
        
        if output_path and output_path.exists():
            safe_print(f"\n[OK] D-ID test completed!")
            safe_print(f"Output: {output_path}")
            return output_path
        else:
            safe_print(f"\n[X] D-ID test failed: Output not found")
            return None
    except Exception as e:
        safe_print(f"\n[X] D-ID test failed: {e}")
        import traceback
        safe_print(traceback.format_exc())
        return None

if __name__ == "__main__":
    main()

