#!/usr/bin/env python3
"""
Accept Coqui TTS Terms of Service and download XTTS model.

This script will download the XTTS-v2 model and accept the ToS interactively.
Run this once to pre-download the model and accept ToS.
"""

import sys
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

def main():
    print("\n" + "="*60)
    print("Coqui TTS Terms of Service Acceptance")
    print("="*60)
    print("\nThis script will download the XTTS-v2 model.")
    print("You will be prompted to accept Coqui's Terms of Service.")
    print("\nOptions:")
    print("  - Type 'y' to accept the non-commercial CPML license")
    print("  - Type 'n' to decline (model won't download)")
    print("\n" + "="*60 + "\n")
    
    try:
        from TTS.api import TTS
        import torch
        
        print("[INFO] Initializing TTS...")
        use_gpu = torch.cuda.is_available()
        print(f"[INFO] GPU available: {use_gpu}")
        
        print("\n[INFO] Downloading XTTS-v2 model...")
        print("[INFO] You will be prompted to accept the Terms of Service.")
        print("\n" + "-"*60)
        
        # This will prompt for ToS acceptance
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=use_gpu)
        
        print("\n" + "-"*60)
        print("[OK] XTTS-v2 model downloaded and ready!")
        print("[OK] Terms of Service accepted.")
        print("\nYou can now use XTTS-v2 without ToS prompts.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n[WARN] Interrupted by user")
        return 1
    except EOFError:
        print("\n[FAIL] ToS acceptance requires interactive input")
        print("[INFO] Run this script in an interactive terminal")
        return 1
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

