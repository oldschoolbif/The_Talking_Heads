"""
Smoke test script for TTS providers.
Tests XTTS-v2, Bark, and VALL-E X with short text samples.
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

def test_xtts():
    """Test XTTS-v2 provider."""
    print("\n" + "="*60)
    print("SMOKE TEST: XTTS-v2")
    print("="*60)
    
    try:
        from src.core.xtts_provider import XTTSProvider
        
        # Load config
        config_path = project_root / "config" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        provider = XTTSProvider(config.get("xtts", {}))
        
        if not provider.is_available():
            print("[FAIL] XTTS-v2 is not available")
            return False
        
        print("[OK] XTTS-v2 provider initialized")
        
        # Test generation
        test_text = "Hello, this is a test of XTTS-v2 text to speech."
        print(f"[INFO] Generating audio for: '{test_text}'")
        
        # Create a simple reference audio for voice cloning
        reference_audio = project_root / ".cache" / "smoke_tests" / "reference_audio.wav"
        reference_audio.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a simple reference audio file if it doesn't exist
        if not reference_audio.exists():
            print("[INFO] Creating reference audio for voice cloning...")
            import wave
            import numpy as np
            sample_rate = 22050
            duration = 3.0
            samples = int(sample_rate * duration)
            # Generate a simple tone
            t = np.linspace(0, duration, samples)
            frequency = 440  # A4 note
            audio_data = (np.sin(2 * np.pi * frequency * t) * 0.3 * 32767).astype(np.int16)
            with wave.open(str(reference_audio), 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
            print(f"[OK] Created reference audio: {reference_audio}")
        
        audio_bytes, duration = provider.generate(
            text=test_text,
            voice_id=str(reference_audio),
            reference_audio_path=reference_audio
        )
        
        # Save output
        output_file = project_root / ".cache" / "smoke_tests" / "xtts_test.wav"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"[OK] Audio generated successfully")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Output: {output_file}")
        print(f"  File size: {len(audio_bytes) / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bark():
    """Test Bark provider."""
    print("\n" + "="*60)
    print("SMOKE TEST: Bark")
    print("="*60)
    
    try:
        from src.core.bark_provider import BarkProvider
        
        # Load config
        config_path = project_root / "config" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        provider = BarkProvider(config.get("bark", {}))
        
        if not provider.is_available():
            print("[FAIL] Bark is not available")
            return False
        
        print("[OK] Bark provider initialized")
        
        # Test generation
        test_text = "Hello, this is a test of Bark text to speech."
        print(f"[INFO] Generating audio for: '{test_text}'")
        
        audio_bytes, duration = provider.generate(
            text=test_text,
            voice_id="default"
        )
        
        # Save output
        output_file = project_root / ".cache" / "smoke_tests" / "bark_test.wav"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"[OK] Audio generated successfully")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Output: {output_file}")
        print(f"  File size: {len(audio_bytes) / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_valle():
    """Test VALL-E X provider."""
    print("\n" + "="*60)
    print("SMOKE TEST: VALL-E X")
    print("="*60)
    
    try:
        from src.core.valle_provider import VALLEProvider
        
        # Load config
        config_path = project_root / "config" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        provider = VALLEProvider(config.get("valle", {}))
        
        if not provider.is_available():
            print("[FAIL] VALL-E X is not available")
            print("  Install dependencies: cd ~/valle && pip install -r requirements.txt")
            return False
        
        print("[OK] VALL-E X provider initialized")
        
        # Test generation - VALL-E needs reference audio
        test_text = "Hello, this is a test of VALL-E X text to speech."
        print(f"[INFO] Generating audio for: '{test_text}'")
        
        # VALL-E can work without prompt (uses default voice)
        # For now, test without prompt since VALL-E expects .npz files, not .wav
        print("[INFO] VALL-E: Testing without prompt (uses default voice)")
        print("[INFO] Note: Full voice cloning requires .npz prompt files")
        
        audio_bytes, duration = provider.generate(
            text=test_text,
            voice_id="default",  # VALL-E will use default voice without prompt
            reference_audio=None  # No prompt for now
        )
        
        # Save output
        output_file = project_root / ".cache" / "smoke_tests" / "valle_test.wav"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "wb") as f:
            f.write(audio_bytes)
        
        print(f"[OK] Audio generated successfully")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Output: {output_file}")
        print(f"  File size: {len(audio_bytes) / 1024:.2f} KB")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all TTS smoke tests."""
    print("="*60)
    print("TTS PROVIDERS SMOKE TEST")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test XTTS-v2
    results['xtts'] = test_xtts()
    
    # Test Bark
    results['bark'] = test_bark()
    
    # Test VALL-E X
    results['valle'] = test_valle()
    
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
        print("\n[SUCCESS] All TTS providers are working!")
    else:
        print(f"\n[WARN] {total - passed} provider(s) failed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

