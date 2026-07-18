"""
Quick script to verify API keys are configured correctly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config_loader import load_config

def main():
    """Verify API keys are configured."""
    print("=" * 60)
    print("API Keys Verification")
    print("=" * 60)
    
    try:
        config = load_config(Path("config/config.yaml"), project_root=Path("."))
        api = config.get("api", {})
        
        print("\nAvatar Generation Keys:")
        heygen = api.get("heygen", {}).get("api_key")
        did = api.get("did", {}).get("api_key")
        print(f"  HeyGen: {'[OK] Configured' if heygen else '[X] Not set'}")
        print(f"  D-ID:   {'[OK] Configured' if did else '[X] Not set'}")
        
        print("\nText-to-Speech Keys:")
        elevenlabs = api.get("elevenlabs", {}).get("api_key")
        azure_key = api.get("azure", {}).get("speech_key")
        azure_region = api.get("azure", {}).get("speech_region")
        print(f"  ElevenLabs: {'[OK] Configured' if elevenlabs else '[X] Not set'}")
        print(f"  Azure Key:  {'[OK] Configured' if azure_key else '[X] Not set'}")
        print(f"  Azure Region: {'[OK] Configured (' + azure_region + ')' if azure_region else '[X] Not set'}")
        
        print("\n" + "=" * 60)
        
        # Check if we have minimum required
        has_avatar = bool(heygen or did)
        has_tts = bool(elevenlabs or azure_key)
        
        if has_avatar and has_tts:
            print("[OK] Status: READY TO GENERATE PODCASTS")
            print("\nYou have all required keys configured!")
            print("You can now run: python scripts/generate_real_output.py")
        elif has_avatar:
            print("[!] Status: Missing TTS key")
            print("Avatar generation will work, but TTS will use gTTS fallback.")
        elif has_tts:
            print("[!] Status: Missing Avatar key")
            print("TTS will work, but avatar generation will fail.")
        else:
            print("[X] Status: No API keys configured")
            print("Please run: python scripts/setup_api_keys.py")
        
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

