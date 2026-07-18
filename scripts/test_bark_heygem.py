"""
Test script for Bark TTS + HeyGem avatar generation (fully local GPU).
Tests the complete pipeline with progress indicators.
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
    """Progress callback with visual indicators."""
    progress_pct = int(progress * 100)
    bar_length = 40
    filled = int(bar_length * progress)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r[{progress_pct:3d}%] {bar} {message}", end="", flush=True)
    if progress >= 1.0:
        print()  # New line when complete

def main():
    """Run test with Bark TTS + HeyGem avatars."""
    print("="*70)
    print("TALKINGHEADS PIPELINE TEST - BARK TTS + HEYGEM AVATARS")
    print("="*70)
    print("\nThis test uses:")
    print("  * Bark for Text-to-Speech (local GPU)")
    print("  * HeyGem for Avatar Generation (local GPU)")
    print("  * Fully local, no cloud services")
    print("="*70)
    
    # Load config
    config_path = project_root / "config" / "config.yaml"
    if not config_path.exists():
        print(f"[FAIL] Error: Config file not found at {config_path}")
        return 1
    
    config = load_config(config_path)
    
    # Create short test script
    test_script = project_root / ".cache" / "test_bark_heygem.txt"
    test_script.parent.mkdir(parents=True, exist_ok=True)
    
    script_content = """# Test Script - Bark + HeyGem

ALICE: Hello! This is a test of the Bark text-to-speech system.

BOB: And this is Bob. We're testing HeyGem for avatar generation.

ALICE: Everything is running locally on GPU. No cloud services needed!
"""
    
    test_script.write_text(script_content, encoding='utf-8')
    print(f"\n[OK] Test script created: {test_script}")
    
    # Ensure config uses Bark and HeyGem
    config["tts"] = config.get("tts", {})
    config["tts"]["engine"] = "bark"
    
    config["avatar"] = config.get("avatar", {})
    config["avatar"]["engine"] = "heygem"
    
    # Load and override personas to use Bark + HeyGem
    personas_config = project_root / "config" / "personas.yaml"
    if personas_config.exists():
        with open(personas_config) as f:
            personas_data = yaml.safe_load(f)
    else:
        personas_data = {}
    
    # Set both personas to use Bark + HeyGem
    for persona_name in ["ALICE", "BOB"]:
        if persona_name not in personas_data:
            personas_data[persona_name] = {}
        
        if "voice" not in personas_data[persona_name]:
            personas_data[persona_name]["voice"] = {}
        personas_data[persona_name]["voice"]["engine"] = "bark"
        
        if "avatar" not in personas_data[persona_name]:
            personas_data[persona_name]["avatar"] = {}
        personas_data[persona_name]["avatar"]["engine"] = "heygem"
    
    # Save temporary personas config
    temp_personas = project_root / ".cache" / "test_personas_bark_heygem.yaml"
    temp_personas.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_personas, 'w') as f:
        yaml.dump(personas_data, f)
    
    config["personas_config"] = str(temp_personas)
    
    print(f"[OK] Configuration prepared")
    print(f"  TTS Engine: Bark (local GPU)")
    print(f"  Avatar Engine: HeyGem (local GPU)")
    
    # Check if HeyGem model videos exist
    heygem_data_dir = Path(config.get("heygem", {}).get("data_dir", "D:/heygem_data/face2face"))
    model_videos = []
    if heygem_data_dir.exists():
        model_videos = list(heygem_data_dir.glob("*.mp4")) + list(heygem_data_dir.glob("*.avi"))
    
    if not model_videos:
        print(f"\n[!] WARNING: No model videos found in {heygem_data_dir}")
        print("HeyGem requires video files of people speaking as avatar models.")
        print("For this test, we'll demonstrate Bark TTS working.")
        print("Avatar generation will fail without model videos, but that's expected.\n")
    
    # Create pipeline
    print(f"\n{'='*70}")
    print("STARTING PIPELINE")
    print("="*70)
    
    pipeline = Pipeline(config, project_root=project_root)
    pipeline.set_progress_callback(progress_callback)
    
    try:
        output_path = pipeline.create_podcast(
            script_path=test_script,
            scene_name="studio",
            layout="switching",
            output_name="test_bark_heygem_output.mp4",
            output_dir=project_root / "examples" / "outputs"
        )
        
        print(f"\n{'='*70}")
        print("[OK] TEST COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📁 Output video: {output_path}")
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"📊 File size: {size_mb:.2f} MB")
        print(f"\n Bark + HeyGem pipeline is working!")
        
        return 0
        
    except Exception as e:
        print(f"\n{'='*70}")
        print("[FAIL] TEST FAILED")
        print("="*70)
        print(f"\nError: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

