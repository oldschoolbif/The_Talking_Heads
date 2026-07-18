#!/usr/bin/env python3
"""
Smoke tests for all local TTS and Avatar providers.

Tests basic functionality of each provider to ensure they're ready for use.
"""

import sys
import tempfile
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

def test_bark():
    """Smoke test Bark TTS."""
    print("\n" + "="*60)
    print("Smoke Test: Bark TTS")
    print("="*60)
    
    try:
        from src.core.bark_provider import BarkProvider
        
        config = {
            "bark_path": "~/bark",
            "python_exec": "python",
            "output_dir": str(Path(tempfile.mkdtemp(prefix="bark_smoke_"))),
        }
        
        provider = BarkProvider(config)
        
        if not provider.is_available():
            print("[FAIL] Bark not available")
            return False
        
        print("[OK] Bark provider initialized")
        
        # Generate a short test audio
        output_path = Path(tempfile.mkdtemp(prefix="bark_output_")) / "smoke_test.wav"
        print("[INFO] Generating test audio...")
        
        audio_bytes, duration = provider.generate(
            text="This is a smoke test of Bark text to speech.",
            voice_id="v2/en_speaker_0",
            output_path=str(output_path)
        )
        
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"[OK] Audio generated: {output_path}")
            print(f"[OK] Duration: {duration:.2f}s, Size: {output_path.stat().st_size} bytes")
            return True
        else:
            print("[FAIL] Audio file not created")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_xtts():
    """Smoke test XTTS-v2 (requires reference audio)."""
    print("\n" + "="*60)
    print("Smoke Test: XTTS-v2")
    print("="*60)
    
    try:
        from src.core.xtts_provider import XTTSProvider
        from TTS.api import TTS
        import torch
        
        config = {
            "xtts_path": "~/xtts",
            "python_exec": "python",
            "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
            "output_dir": str(Path(tempfile.mkdtemp(prefix="xtts_smoke_"))),
        }
        
        provider = XTTSProvider(config)
        
        if not provider.is_available():
            print("[FAIL] XTTS not available")
            print("[INFO] Ensure TTS is installed: pip install coqui-tts")
            return False
        
        print("[OK] XTTS provider initialized")
        
        # Check if model is available (may require ToS acceptance)
        try:
            use_gpu = torch.cuda.is_available()
            print(f"[INFO] GPU available: {use_gpu}")
            print("[INFO] Checking if XTTS-v2 model is downloaded...")
            
            # Try to load model (this will fail if ToS not accepted)
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
            print("[OK] XTTS-v2 model is available")
            
        except Exception as e:
            error_str = str(e).lower()
            if "tos" in error_str or "terms" in error_str or "eof" in error_str:
                print("[WARN] Model requires ToS acceptance")
                print("[INFO] Run: python scripts/accept_coqui_tos.py")
                return False
            else:
                print(f"[WARN] Model check failed: {e}")
                return False
        
        print("[OK] XTTS-v2 is ready (requires reference audio for generation)")
        return True
        
    except ImportError:
        print("[FAIL] TTS library not installed")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dreamtalk():
    """Smoke test DreamTalk avatar provider."""
    print("\n" + "="*60)
    print("Smoke Test: DreamTalk")
    print("="*60)
    
    try:
        import yaml
        from src.core.dreamtalk_provider import DreamTalkProvider
        
        config_path = project_root / "config" / "config.yaml"
        if not config_path.exists():
            print("[FAIL] Config file not found")
            return False
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        dreamtalk_config = config.get("dreamtalk", {})
        provider = DreamTalkProvider(dreamtalk_config)
        
        is_available = provider.is_available()
        
        if is_available:
            print("[OK] DreamTalk provider initialized")
            print(f"[INFO] Path: {dreamtalk_config.get('dreamtalk_path', 'Not configured')}")
            return True
        else:
            print("[FAIL] DreamTalk not available")
            print("[INFO] Ensure DreamTalk is installed and path configured in config.yaml")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gpu():
    """Test GPU availability."""
    print("\n" + "="*60)
    print("Smoke Test: GPU Availability")
    print("="*60)
    
    try:
        import torch
        
        print(f"[INFO] PyTorch version: {torch.__version__}")
        print(f"[INFO] CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"[OK] GPU Count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"[OK] GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"[OK] CUDA Version: {torch.version.cuda}")
            return True
        else:
            print("[WARN] CUDA not available - providers will use CPU (slower)")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("\n" + "="*60)
    print("Local Provider Smoke Tests")
    print("="*60)
    print(f"Project Root: {project_root}")
    
    results = {}
    
    # Test GPU first
    results["GPU"] = test_gpu()
    
    # Test TTS providers
    results["Bark"] = test_bark()
    results["XTTS-v2"] = test_xtts()
    
    # Test Avatar providers
    results["DreamTalk"] = test_dreamtalk()
    
    # Summary
    print("\n" + "="*60)
    print("Smoke Test Summary")
    print("="*60)
    
    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] All smoke tests passed!")
        print("[INFO] All providers are ready for use.")
    else:
        print("[WARN] Some smoke tests failed")
        print("\nNext steps:")
        if not results.get("XTTS-v2", False):
            print("  - Run: python scripts/accept_coqui_tos.py (to accept ToS and download model)")
        if not results.get("DreamTalk", False):
            print("  - Install DreamTalk and configure path in config.yaml")
        if not results.get("GPU", False):
            print("  - GPU not available (providers will use CPU)")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

