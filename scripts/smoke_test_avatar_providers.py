"""
Smoke test script for Avatar providers.
Tests DreamTalk and HeyGen/D-ID with short audio samples.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.console_setup import setup_console_encoding
setup_console_encoding()

import yaml
import tempfile
from datetime import datetime

def test_dreamtalk():
    """Test DreamTalk provider."""
    print("\n" + "="*60)
    print("SMOKE TEST: DreamTalk")
    print("="*60)
    
    try:
        from src.core.dreamtalk_provider import DreamTalkProvider
        
        # Load config
        config_path = project_root / "config" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        provider = DreamTalkProvider(config.get("dreamtalk", {}))
        
        if not provider.is_available():
            print("[FAIL] DreamTalk is not available")
            print("  Check: docs/DREAMTALK_SETUP.md")
            return False
        
        print("[OK] DreamTalk provider initialized")
        
        # Create test audio file
        test_audio = project_root / ".cache" / "smoke_tests" / "test_audio.wav"
        test_audio.parent.mkdir(parents=True, exist_ok=True)
        
        # Use existing TTS output if available, otherwise create simple test audio
        if (project_root / ".cache" / "smoke_tests" / "xtts_test.wav").exists():
            test_audio = project_root / ".cache" / "smoke_tests" / "xtts_test.wav"
            print(f"[INFO] Using existing audio: {test_audio}")
        else:
            print("[WARN] No test audio found. Creating placeholder...")
            # Create a simple silent audio file for testing
            import wave
            import numpy as np
            sample_rate = 16000
            duration = 2.0
            samples = int(sample_rate * duration)
            audio_data = np.zeros(samples, dtype=np.int16)
            with wave.open(str(test_audio), 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            print(f"[INFO] Created placeholder audio: {test_audio}")
        
        # Find test image - check multiple locations
        test_image = None
        test_image_paths = [
            # Primary location: examples/test_assets/
            project_root / "examples" / "test_assets" / "test_image.jpg",
            project_root / "examples" / "test_assets" / "test_image.png",
            project_root / "examples" / "test_assets" / "test_image.jpeg",
            # Secondary locations: examples/personas/
            project_root / "examples" / "personas" / "alice.jpg",
            project_root / "examples" / "personas" / "alice.png",
            project_root / "examples" / "personas" / "bob.jpg",
            project_root / "examples" / "personas" / "bob.png",
            # Fallback: user Pictures folder
            Path.home() / "Pictures" / "test.jpg",
        ]
        
        for img_path in test_image_paths:
            if img_path.exists():
                test_image = img_path
                break
        
        if not test_image:
            print("[WARN] No test image found. DreamTalk requires source image.")
            print("  Please place a test image at one of these locations:")
            for img_path in test_image_paths[:4]:
                print(f"    - {img_path}")
            print("  Skipping DreamTalk test - requires image file")
            return False
        
        print(f"[INFO] Using test image: {test_image}")
        print(f"[INFO] Using test audio: {test_audio}")
        print("[INFO] Generating video (this may take a while)...")
        
        video_path, duration = provider.generate(
            audio_path=test_audio,
            avatar_id="test",
            image_path=test_image
        )
        
        print(f"[OK] Video generated successfully")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Output: {video_path}")
        print(f"  File size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_heygen():
    """Test HeyGen provider."""
    print("\n" + "="*60)
    print("SMOKE TEST: HeyGen")
    print("="*60)
    
    try:
        from src.core.avatar_generator import AvatarGenerator
        
        # Load config
        config_path = project_root / "config" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        generator = AvatarGenerator(config)
        
        # Check if HeyGen is available
        try:
            provider = generator._get_provider("heygen")
            if not provider.is_available():
                print("[FAIL] HeyGen is not available (check API key)")
                return False
        except RuntimeError as e:
            print(f"[FAIL] HeyGen not available: {e}")
            return False
        
        print("[OK] HeyGen provider initialized")
        
        # Create test audio file
        test_audio = project_root / ".cache" / "smoke_tests" / "test_audio.wav"
        test_audio.parent.mkdir(parents=True, exist_ok=True)
        
        # Use existing TTS output if available
        if (project_root / ".cache" / "smoke_tests" / "xtts_test.wav").exists():
            test_audio = project_root / ".cache" / "smoke_tests" / "xtts_test.wav"
            print(f"[INFO] Using existing audio: {test_audio}")
        else:
            print("[WARN] No test audio found. Creating placeholder...")
            import wave
            import numpy as np
            sample_rate = 16000
            duration = 2.0
            samples = int(sample_rate * duration)
            audio_data = np.zeros(samples, dtype=np.int16)
            with wave.open(str(test_audio), 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            print(f"[INFO] Created placeholder audio: {test_audio}")
        
        # Use a test avatar ID (from personas.yaml)
        avatar_id = "Abigail_expressive_2024112501"  # Default HeyGen avatar
        
        print(f"[INFO] Using avatar ID: {avatar_id}")
        print(f"[INFO] Using test audio: {test_audio}")
        print("[INFO] Generating video (this may take 5-20 minutes)...")
        print("[INFO] Note: HeyGen v2 API requires text parameter, using audio transcription...")
        
        # Set progress callback
        def progress_callback(message, progress):
            if progress:
                print(f"  Progress: {progress*100:.1f}% - {message}")
            else:
                print(f"  {message}")
        
        provider.set_progress_callback(progress_callback)
        
        # HeyGen v2 requires text parameter - use a simple test text
        test_text = "Hello, this is a test of HeyGen avatar generation."
        
        video_path, duration = provider.generate(
            audio_path=test_audio,
            avatar_id=avatar_id,
            text=test_text  # HeyGen v2 requires text
        )
        
        print(f"[OK] Video generated successfully")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Output: {video_path}")
        print(f"  File size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_did():
    """Test D-ID provider."""
    print("\n" + "="*60)
    print("SMOKE TEST: D-ID")
    print("="*60)
    
    try:
        from src.core.avatar_generator import AvatarGenerator
        
        # Load config
        config_path = project_root / "config" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        generator = AvatarGenerator(config)
        
        # Check if D-ID is available
        try:
            provider = generator._get_provider("did")
            if not provider.is_available():
                print("[FAIL] D-ID is not available (check API key)")
                return False
        except RuntimeError as e:
            print(f"[FAIL] D-ID not available: {e}")
            return False
        
        print("[OK] D-ID provider initialized")
        
        # Create test audio file
        test_audio = project_root / ".cache" / "smoke_tests" / "test_audio.wav"
        test_audio.parent.mkdir(parents=True, exist_ok=True)
        
        # Use existing TTS output if available
        if (project_root / ".cache" / "smoke_tests" / "xtts_test.wav").exists():
            test_audio = project_root / ".cache" / "smoke_tests" / "xtts_test.wav"
            print(f"[INFO] Using existing audio: {test_audio}")
        else:
            print("[WARN] No test audio found. Creating placeholder...")
            import wave
            import numpy as np
            sample_rate = 16000
            duration = 2.0
            samples = int(sample_rate * duration)
            audio_data = np.zeros(samples, dtype=np.int16)
            with wave.open(str(test_audio), 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            print(f"[INFO] Created placeholder audio: {test_audio}")
        
        # Use a test avatar (D-ID compatible image URL)
        avatar_id = "amy"  # Will be mapped to D-ID image URL
        
        print(f"[INFO] Using avatar ID: {avatar_id}")
        print(f"[INFO] Using test audio: {test_audio}")
        print("[INFO] Generating video (this may take a few minutes)...")
        print("[INFO] Note: D-ID works best with text-to-speech, using test text...")
        
        # Set progress callback
        def progress_callback(message, progress):
            if progress:
                print(f"  Progress: {progress*100:.1f}% - {message}")
            else:
                print(f"  {message}")
        
        provider.set_progress_callback(progress_callback)
        
        # D-ID works better with text parameter
        test_text = "Hello, this is a test of D-ID avatar generation."
        
        video_path, duration = provider.generate(
            audio_path=test_audio,
            avatar_id=avatar_id,
            text=test_text  # D-ID prefers text-to-speech
        )
        
        print(f"[OK] Video generated successfully")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Output: {video_path}")
        print(f"  File size: {video_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Avatar smoke tests (LOCAL PROVIDERS ONLY)."""
    print("="*60)
    print("AVATAR PROVIDERS SMOKE TEST")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNote: DreamTalk requires checkpoints that must be requested via email.")
    print("DreamTalk is EXCLUDED from testing until checkpoints are available.")
    print("See docs/HOW_TO_GET_DREAMTALK_CHECKPOINTS.md for details.")
    
    results = {}
    
    # Test DreamTalk - SKIPPED (requires checkpoints)
    print("\n[SKIP] DreamTalk test skipped - checkpoints required")
    print("       See docs/HOW_TO_GET_DREAMTALK_CHECKPOINTS.md")
    results['dreamtalk'] = False
    
    # HeyGen and D-ID tests REMOVED - local providers only
    
    # Summary
    print("\n" + "="*60)
    print("SMOKE TEST SUMMARY")
    print("="*60)
    
    for provider, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {provider.upper()}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} providers passed")
    
    if passed == total:
        print("\n[SUCCESS] All Avatar providers are working!")
    else:
        print(f"\n[WARN] {total - passed} provider(s) failed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

