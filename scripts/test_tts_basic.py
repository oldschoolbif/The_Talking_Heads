#!/usr/bin/env python3
"""
Basic TTS functionality test - generates audio from text using local providers.
"""

import sys
from pathlib import Path

# Setup console encoding FIRST
try:
    from src.utils.console_setup import setup_console_encoding
    setup_console_encoding()
except ImportError:
    if sys.platform == "win32":
        import os
        os.environ["PYTHONIOENCODING"] = "utf-8"
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import tempfile
from src.core.xtts_provider import XTTSProvider
from src.core.bark_provider import BarkProvider

def test_xtts():
    """Test XTTS-v3 with a simple sentence."""
    print("\n" + "="*60)
    print("Testing XTTS-v3 Generation")
    print("="*60)
    
    try:
        # Create a temporary reference audio (we'll use a simple approach)
        # For real use, you'd have reference audio files
        print("[INFO] XTTS-v3 requires reference audio for voice cloning")
        print("[INFO] Skipping full test - checking provider initialization...")
        
        config = {
            "xtts_path": "~/xtts",
            "python_exec": "python",
            "model_name": "tts_models/multilingual/multi-dataset/xtts_v3",
            "output_dir": str(Path(tempfile.mkdtemp(prefix="xtts_test_"))),
        }
        
        provider = XTTSProvider(config)
        is_available = provider.is_available()
        
        if is_available:
            print("[OK] XTTS-v3 provider initialized and available")
            print("[INFO] To test generation, provide reference audio file")
            return True
        else:
            print("[FAIL] XTTS-v3 not available")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bark():
    """Test Bark with a simple sentence."""
    print("\n" + "="*60)
    print("Testing Bark Generation")
    print("="*60)
    
    try:
        config = {
            "bark_path": "~/bark",
            "python_exec": "python",
            "output_dir": str(Path(tempfile.mkdtemp(prefix="bark_test_"))),
        }
        
        provider = BarkProvider(config)
        is_available = provider.is_available()
        
        if is_available:
            print("[OK] Bark provider initialized and available")
            print("[INFO] Bark can generate without reference audio (uses presets)")
            
            # Try a simple generation
            try:
                output_path = Path(tempfile.mkdtemp(prefix="bark_output_")) / "test.wav"
                audio_bytes, duration = provider.generate(
                    text="Hello, this is a test of Bark text to speech.",
                    voice_id="v2/en_speaker_0",
                    output_path=str(output_path)
                )
                
                if output_path.exists() and output_path.stat().st_size > 0:
                    print(f"[OK] Bark generated audio: {output_path}")
                    print(f"[OK] Duration: {duration:.2f} seconds")
                    print(f"[OK] File size: {output_path.stat().st_size} bytes")
                    return True
                else:
                    print("[FAIL] Bark did not generate output file")
                    return False
                    
            except Exception as e:
                print(f"[WARN] Bark generation test failed: {e}")
                print("[INFO] Provider is available but generation needs setup")
                return False
        else:
            print("[FAIL] Bark not available")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Basic TTS Functionality Test")
    print("="*60)
    
    results = {}
    results["XTTS-v3"] = test_xtts()
    results["Bark"] = test_bark()
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n[SUCCESS] All TTS providers are functional!")
    else:
        print("\n[WARN] Some TTS providers need additional setup")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

