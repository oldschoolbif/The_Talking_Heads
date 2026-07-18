"""
Test script for full TalkingHeads pipeline with VALL-E and Bark TTS providers.
Tests both providers with a short script to verify end-to-end functionality.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.console_setup import setup_console_encoding
setup_console_encoding()

import yaml
from src.core.pipeline import Pipeline
from src.utils.config_loader import load_config

def progress_callback(message: str, progress: float):
    """Progress callback for pipeline."""
    progress_pct = int(progress * 100)
    print(f"[{progress_pct:3d}%] {message}")

def main():
    """Run test with VALL-E and Bark."""
    print("="*70)
    print("TALKINGHEADS PIPELINE TEST - VALL-E & BARK TTS")
    print("="*70)
    
    # Load config
    config_path = project_root / "config" / "config.yaml"
    config = load_config(config_path)
    
    # Create test script
    test_script = project_root / ".cache" / "test_script.txt"
    test_script.parent.mkdir(parents=True, exist_ok=True)
    
    script_content = """# Test Script for VALL-E and Bark

ALICE: Hello, this is Alice speaking. I'm testing the VALL-E text-to-speech system.

BOB: And this is Bob. I'm testing the Bark text-to-speech system. Both should work well.

ALICE: Great! Let's see how the full pipeline works with both providers.
"""
    
    test_script.write_text(script_content, encoding='utf-8')
    print(f"\nTest script: {test_script}")
    
    # Test 1: VALL-E
    print("\n" + "="*70)
    print("TEST 1: VALL-E X TTS")
    print("="*70)
    
    config_valle = config.copy()
    config_valle["tts"] = config_valle.get("tts", {}).copy()
    config_valle["tts"]["engine"] = "valle"
    
    # Override personas to use VALL-E
    personas_config = project_root / "config" / "personas.yaml"
    with open(personas_config) as f:
        personas_data = yaml.safe_load(f)
    
    # Set ALICE to use VALL-E (local GPU TTS)
    if "ALICE" in personas_data:
        if "voice" not in personas_data["ALICE"]:
            personas_data["ALICE"]["voice"] = {}
        personas_data["ALICE"]["voice"]["engine"] = "valle"
        # Override avatar to use local GPU provider (dreamtalk)
        if "avatar" not in personas_data["ALICE"]:
            personas_data["ALICE"]["avatar"] = {}
        personas_data["ALICE"]["avatar"]["engine"] = "dreamtalk"
    
    # Set BOB to use Bark (local GPU TTS)
    if "BOB" in personas_data:
        if "voice" not in personas_data["BOB"]:
            personas_data["BOB"]["voice"] = {}
        personas_data["BOB"]["voice"]["engine"] = "bark"
        # Override avatar to use local GPU provider (dreamtalk)
        if "avatar" not in personas_data["BOB"]:
            personas_data["BOB"]["avatar"] = {}
        personas_data["BOB"]["avatar"]["engine"] = "dreamtalk"
    
    # Save temporary personas config
    temp_personas = project_root / ".cache" / "test_personas.yaml"
    with open(temp_personas, 'w') as f:
        yaml.dump(personas_data, f)
    
    config_valle["personas_config"] = str(temp_personas)
    
    pipeline_valle = Pipeline(config_valle, project_root=project_root)
    pipeline_valle.set_progress_callback(progress_callback)
    
    try:
        output_path_valle = pipeline_valle.create_podcast(
            script_path=test_script,
            scene_name="studio",
            layout="switching",
            output_name="test_valle_bark_output.mp4",
            output_dir=project_root / "examples" / "outputs"
        )
        print(f"\n[OK] VALL-E test completed: {output_path_valle}")
    except Exception as e:
        print(f"\n[FAIL] VALL-E test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("[OK] VALL-E X: Tested in pipeline")
    print("[OK] Bark: Tested in pipeline")
    print(f"\n📁 Output: {output_path_valle}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

