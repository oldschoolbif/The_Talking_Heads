"""
Script to generate a real podcast output for validation.

This script uses the actual pipeline with real API calls (if keys are configured).
Make sure you have API keys set in your environment or config.yaml.
"""

import sys
from pathlib import Path

# Handle Windows Unicode encoding
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# ASCII-safe symbols
CHECK = "[OK]"
CROSS = "[X]"

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.pipeline import Pipeline
from src.utils.config_loader import load_config

def main():
    """Generate a real podcast output."""
    # Load configuration
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config" / "config.yaml"
    
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}")
        print("Please ensure config/config.yaml exists with your API keys.")
        return 1
    
    config = load_config(config_path)
    
    # Check for API keys
    elevenlabs_key = config.get("api", {}).get("elevenlabs", {}).get("api_key") or None
    heygen_key = config.get("api", {}).get("heygen", {}).get("api_key") or None
    
    if not elevenlabs_key:
        print("Warning: ElevenLabs API key not found. TTS will use fallback (gTTS).")
    
    if not heygen_key:
        print("Warning: HeyGen API key not found. Avatar generation will fail.")
        return 1
    
    # Use the test script
    script_path = project_root / "scripts" / "test_episode.txt"
    
    if not script_path.exists():
        print(f"Error: Script file not found at {script_path}")
        return 1
    
    print(f"Loading script: {script_path}")
    print(f"Using config: {config_path}")
    print("\nGenerating podcast...")
    print("=" * 50)
    
    # Create pipeline
    pipeline = Pipeline(config, project_root=project_root)
    
    # Set up progress callback
    def progress_callback(message, progress):
        print(f"[{progress*100:.0f}%] {message}")
    
    pipeline.set_progress_callback(progress_callback)
    
    try:
        # Generate podcast
        output_path = pipeline.create_podcast(
            script_path,
            scene_name="studio",
            layout="switching",
            output_name="real_test_output.mp4"
        )
        
        print("\n" + "=" * 50)
        print(f"{CHECK} Podcast generated successfully!")
        print(f"  Output: {output_path}")
        print(f"  Size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        print("\nYou can now validate this video file.")
        
        return 0
        
    except Exception as e:
        print(f"\n{CROSS} Error generating podcast: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

