#!/usr/bin/env python3
"""
Test script to verify local TTS and Avatar providers are installed and functional.

Tests:
- XTTS-v3 (TTS)
- Bark (TTS)
- VALL-E X (TTS)
- DreamTalk (Avatar)
"""

import sys
import subprocess
from pathlib import Path

# Setup console encoding for Windows compatibility (MUST be first)
try:
    from src.utils.console_setup import setup_console_encoding
    setup_console_encoding()
except ImportError:
    # Fallback: configure encoding manually
    if sys.platform == "win32":
        import os
        os.environ["PYTHONIOENCODING"] = "utf-8"
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_python_environment():
    """Test Python and PyTorch environment."""
    print("\n" + "="*60)
    print("Testing Python Environment")
    print("="*60)
    
    try:
        import torch
        print(f"[OK] Python: {sys.version.split()[0]}")
        print(f"[OK] PyTorch: {torch.__version__}")
        print(f"[OK] CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"[OK] CUDA Version: {torch.version.cuda}")
            print(f"[OK] GPU Count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  - GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("[WARN] CUDA not available - GPU acceleration disabled")
        return True
    except ImportError as e:
        print(f"[FAIL] PyTorch not installed: {e}")
        return False


def test_xtts():
    """Test XTTS-v3 installation."""
    print("\n" + "="*60)
    print("Testing XTTS-v3 (Coqui TTS)")
    print("="*60)
    
    # Check if TTS package is installed (can be coqui-tts or TTS)
    tts_package_installed = False
    try:
        import pkg_resources
        for pkg in pkg_resources.working_set:
            if pkg.project_name.lower() in ['coqui-tts', 'tts']:
                tts_package_installed = True
                print(f"[OK] Found package: {pkg.project_name} {pkg.version}")
                break
    except Exception:
        pass
    
    try:
        from TTS.api import TTS
        print("[OK] TTS library imported successfully")
        
        # Try to initialize XTTS-v3 with GPU support
        try:
            print("  Attempting to load XTTS model...")
            import torch
            use_gpu = torch.cuda.is_available()
            print(f"  Using GPU: {use_gpu}")
            # Try XTTS-v2 first (more stable), fall back to v3 if available
            try:
                tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
                print("[OK] XTTS-v2 model loaded successfully")
            except Exception:
                # Try v3 if v2 fails
                try:
                    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v3", gpu=use_gpu)
                    print("[OK] XTTS-v3 model loaded successfully")
                except Exception as e:
                    raise e
            print("[OK] XTTS-v3 model loaded successfully")
            if use_gpu:
                print("[OK] GPU acceleration enabled")
            return True
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower() or "model" in error_msg.lower():
                print(f"[WARN] XTTS-v3 model not downloaded: {e}")
                print("  Run: python -c 'from TTS.api import TTS; TTS(\"tts_models/multilingual/multi-dataset/xtts_v3\")'")
            else:
                print(f"[WARN] XTTS-v3 initialization issue: {e}")
            return False
    except ImportError:
        print("[FAIL] TTS library not installed")
        print("  Install with: pip install git+https://github.com/coqui-ai/TTS.git")
        print("  Or: pip install coqui-tts")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_bark():
    """Test Bark installation."""
    print("\n" + "="*60)
    print("Testing Bark")
    print("="*60)
    
    try:
        import bark
        print("[OK] Bark library imported successfully")
        
        # Try to check if models are available
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models
            print(f"[OK] Bark functions available (Sample Rate: {SAMPLE_RATE})")
            print("  Note: Models will be downloaded on first use")
            return True
        except Exception as e:
            print(f"[WARN] Bark setup incomplete: {e}")
            return False
    except ImportError:
        print("[FAIL] Bark not installed")
        print("  Install with: pip install bark")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_valle():
    """Test VALL-E X installation."""
    print("\n" + "="*60)
    print("Testing VALL-E X")
    print("="*60)
    
    # VALL-E X (Plachtaa) uses utils.generation module
    valle_paths = [
        Path.home() / "valle",
        project_root / "valle",
        Path("/opt/valle"),
    ]
    
    found = False
    for valle_path in valle_paths:
        if valle_path.exists():
            print(f"[OK] Found VALL-E directory: {valle_path}")
            # Check for utils/generation.py (VALL-E X pattern)
            generation_module = valle_path / "utils" / "generation.py"
            if generation_module.exists():
                print(f"[OK] Found generation module: {generation_module}")
                # Try to import it (must run from VALL-E directory)
                try:
                    import subprocess
                    result = subprocess.run(
                        ["python", "-c", "import sys; sys.path.insert(0, '.'); from utils.generation import generate_audio; print('OK')"],
                        cwd=str(valle_path),
                        capture_output=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        print("[OK] VALL-E generation module can be imported")
                        found = True
                        break
                    else:
                        print(f"[WARN] Cannot import VALL-E module: {result.stderr.decode()[:100]}")
                        print("  Install dependencies: pip install -r requirements.txt")
                        continue
                except Exception as e:
                    print(f"[WARN] Cannot import VALL-E module: {e}")
                    print("  Install dependencies: pip install -r requirements.txt")
                    continue
    
    if not found:
        print("[FAIL] VALL-E not found or not importable")
        print("  VALL-E requires manual installation")
        print("  Check: https://github.com/Plachtaa/VALL-E-X")
        print("  Install: cd ~/valle && pip install -r requirements.txt")
        return False
    
    return True


def test_dreamtalk():
    """Test DreamTalk installation."""
    print("\n" + "="*60)
    print("Testing DreamTalk")
    print("="*60)
    
    try:
        from src.core.dreamtalk_provider import DreamTalkProvider
        
        # Load config
        import yaml
        config_path = project_root / "config" / "config.yaml"
        if not config_path.exists():
            print("[X] Config file not found")
            return False
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        dreamtalk_config = config.get("dreamtalk", {})
        provider = DreamTalkProvider(dreamtalk_config)
        
        # Check if available
        is_available = provider.is_available()
        if is_available:
            print("[OK] DreamTalk provider initialized")
            print(f"  Path: {dreamtalk_config.get('dreamtalk_path', 'Not configured')}")
            print(f"  Python: {dreamtalk_config.get('python_exec', 'Not configured')}")
            return True
        else:
            print("[FAIL] DreamTalk not available")
            print("  Check configuration in config/config.yaml")
            print("  Ensure DreamTalk is installed and path is correct")
            return False
            
    except ImportError as e:
        print(f"[FAIL] DreamTalk provider import failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_ffmpeg():
    """Test FFmpeg installation."""
    print("\n" + "="*60)
    print("Testing FFmpeg")
    print("="*60)
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"[OK] FFmpeg: {version_line}")
            return True
        else:
            print("[FAIL] FFmpeg not found in PATH")
            return False
    except FileNotFoundError:
        print("[FAIL] FFmpeg not installed")
        print("  Install FFmpeg: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"[FAIL] Error checking FFmpeg: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Local Provider Installation Test")
    print("="*60)
    print(f"Project Root: {project_root}")
    
    results = {}
    
    # Test environment
    results["Python/PyTorch"] = test_python_environment()
    
    # Test TTS providers
    results["XTTS-v3"] = test_xtts()
    results["Bark"] = test_bark()
    results["VALL-E X"] = test_valle()
    
    # Test Avatar providers
    results["DreamTalk"] = test_dreamtalk()
    
    # Test utilities
    results["FFmpeg"] = test_ffmpeg()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] All local providers are installed and ready!")
    else:
        print("[WARN] Some providers are missing or not configured")
        print("\nInstallation commands:")
        print("  XTTS-v3: pip install TTS")
        print("  Bark: pip install bark")
        print("  FFmpeg: https://ffmpeg.org/download.html")
        print("  DreamTalk: See docs/DREAMTALK_SETUP.md")
        print("  VALL-E X: Manual installation required")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

