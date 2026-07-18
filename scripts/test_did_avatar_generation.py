"""
Test D-ID avatar generation with the updated Basic Auth.
"""

import os
import sys
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.core.avatar_generator import DIDProvider
from src.utils.console_output import safe_print
from src.utils.config_loader import load_config

# Load environment variables
load_dotenv()

def test_did_avatar_generation():
    """Test D-ID avatar generation with Basic Auth."""
    safe_print("="*60)
    safe_print("Testing D-ID Avatar Generation")
    safe_print("="*60)
    
    # Load config
    config_path = project_root / "config" / "config.yaml"
    config = load_config(config_path)
    
    # Get D-ID config
    did_config = config.get("api", {}).get("did", {})
    api_key = did_config.get("api_key") or os.getenv("DID_API_KEY")
    
    if not api_key:
        safe_print("[X] D-ID API key not found")
        sys.exit(1)
    
    # Initialize provider
    safe_print("\n[STEP 1] Initializing D-ID provider...")
    provider = DIDProvider(did_config)
    
    if not provider.is_available():
        safe_print("[X] D-ID provider not available")
        sys.exit(1)
    
    safe_print("[OK] D-ID provider initialized")
    
    # Create a test audio file (very short)
    safe_print("\n[STEP 2] Creating test audio file...")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        # Create a minimal MP3 file (just a placeholder)
        # In real usage, this would be actual audio from TTS
        test_audio_path = Path(f.name)
        # Write minimal MP3 header (this is just for testing)
        f.write(b'\xff\xfb\x90\x00')  # Minimal MP3 header
        f.write(b'\x00' * 1000)  # Some dummy data
    
    safe_print(f"[OK] Test audio created: {test_audio_path}")
    
    try:
        # Test with a D-ID avatar (you'll need to use a real avatar ID or URL)
        # For now, let's just test the authentication by listing avatars
        safe_print("\n[STEP 3] Testing authentication by listing avatars...")
        
        import requests
        import base64
        
        encoded_credentials = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        response = requests.get("https://api.d-id.com/avatars", headers=headers, timeout=10)
        
        if response.status_code == 200:
            safe_print("[OK] Authentication successful!")
            avatars = response.json()
            safe_print(f"     Found {len(avatars.get('avatars', []))} avatars")
            
            # Show first few avatars if available
            avatar_list = avatars.get('avatars', [])[:3]
            if avatar_list:
                safe_print("\n     Sample avatars:")
                for avatar in avatar_list:
                    avatar_id = avatar.get('id') or avatar.get('name', 'Unknown')
                    safe_print(f"       - {avatar_id}")
        else:
            safe_print(f"[X] Authentication failed: {response.status_code}")
            safe_print(f"     Response: {response.text[:200]}")
            sys.exit(1)
        
        safe_print("\n" + "="*60)
        safe_print("[OK] D-ID API is working with Basic Auth!")
        safe_print("="*60)
        safe_print("\nNext: Test full avatar generation with a real audio file")
        
    except Exception as e:
        safe_print(f"\n[X] Error: {e}")
        import traceback
        safe_print(traceback.format_exc())
        sys.exit(1)
    finally:
        # Cleanup
        if test_audio_path.exists():
            test_audio_path.unlink()

if __name__ == "__main__":
    test_did_avatar_generation()

