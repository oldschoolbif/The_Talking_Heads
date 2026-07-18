#!/usr/bin/env python3
"""
Check for dependency version conflicts.
"""

import sys
import subprocess
from pathlib import Path

# Setup console encoding
try:
    from src.utils.console_setup import setup_console_encoding
    setup_console_encoding()
except ImportError:
    if sys.platform == "win32":
        import os
        os.environ["PYTHONIOENCODING"] = "utf-8"
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_package(package_name):
    """Check if package is installed and get version."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        return None
    except Exception:
        return None

def check_import(package_name, import_name=None):
    """Check if package can be imported."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False
    except Exception:
        return True  # Other errors mean it's installed but has issues

def main():
    print("\n" + "="*60)
    print("Dependency Conflict Check")
    print("="*60)
    
    # Key packages to check
    packages = {
        "torch": ("torch", "torch"),
        "numpy": ("numpy", "numpy"),
        "scipy": ("scipy", "scipy"),
        "librosa": ("librosa", "librosa"),
        "soundfile": ("soundfile", "soundfile"),
        "pydub": ("pydub", "pydub"),
        "TTS": ("TTS", "TTS"),
        "bark": ("bark", "bark"),
    }
    
    print("\nInstalled Versions:")
    print("-" * 60)
    installed = {}
    for pkg_name, (pip_name, import_name) in packages.items():
        version = check_package(pip_name)
        can_import = check_import(import_name)
        installed[pkg_name] = {"version": version, "importable": can_import}
        status = "[OK]" if can_import else "[FAIL]"
        version_str = version if version else "NOT INSTALLED"
        print(f"{status} {pkg_name:15} {version_str}")
    
    # Check for conflicts
    print("\n" + "="*60)
    print("Potential Conflicts:")
    print("="*60)
    
    conflicts = []
    
    # Check PyTorch CUDA
    if installed.get("torch", {}).get("version"):
        import torch
        if not torch.cuda.is_available():
            conflicts.append({
                "package": "torch",
                "issue": "CPU-only version installed, GPU not available",
                "current": installed["torch"]["version"],
                "solutions": [
                    "Keep CPU version (slower, but works)",
                    "Install CUDA version: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
                ]
            })
    
    # Check TTS installation
    if not installed.get("TTS", {}).get("version"):
        conflicts.append({
            "package": "TTS",
            "issue": "Coqui TTS not installed",
            "current": "NOT INSTALLED",
            "solutions": [
                "Try: pip install TTS",
                "Try: pip install coqui-tts",
                "Try: pip install git+https://github.com/coqui-ai/TTS.git",
                "Manual installation from source"
            ]
        })
    
    # Check numpy/scipy compatibility
    if installed.get("numpy", {}).get("version") and installed.get("scipy", {}).get("version"):
        try:
            import numpy as np
            import scipy
            # Check if versions are compatible
            numpy_version = tuple(map(int, np.__version__.split('.')[:2]))
            if numpy_version >= (2, 0):
                conflicts.append({
                    "package": "numpy/scipy",
                    "issue": "NumPy 2.0+ may have compatibility issues with some packages",
                    "current": f"numpy {np.__version__}, scipy {scipy.__version__}",
                    "solutions": [
                        "Keep current versions (may work)",
                        "Downgrade numpy: pip install 'numpy<2.0'",
                        "Upgrade scipy: pip install --upgrade scipy"
                    ]
                })
        except Exception:
            pass
    
    # Check librosa/soundfile compatibility
    if installed.get("librosa", {}).get("version") and installed.get("soundfile", {}).get("version"):
        try:
            import librosa
            import soundfile
            # librosa typically needs soundfile >= 0.12.0
            sf_version = tuple(map(int, soundfile.__version__.split('.')[:2]))
            if sf_version < (0, 12):
                conflicts.append({
                    "package": "soundfile",
                    "issue": "soundfile version too old for librosa",
                    "current": f"soundfile {soundfile.__version__}",
                    "solutions": [
                        "Upgrade soundfile: pip install --upgrade soundfile"
                    ]
                })
        except Exception:
            pass
    
    if not conflicts:
        print("[OK] No conflicts detected")
    else:
        for i, conflict in enumerate(conflicts, 1):
            print(f"\n{i}. {conflict['package'].upper()}")
            print(f"   Issue: {conflict['issue']}")
            print(f"   Current: {conflict['current']}")
            print(f"   Solutions:")
            for j, solution in enumerate(conflict['solutions'], 1):
                print(f"      {j}. {solution}")
    
    print("\n" + "="*60)
    return conflicts

if __name__ == "__main__":
    conflicts = main()
    sys.exit(0 if not conflicts else 1)

