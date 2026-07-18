"""
List available ElevenLabs voices.

This script helps you find real voice IDs to use in personas.yaml.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests

def main():
    """List available ElevenLabs voices."""
    # Get API key from environment or config
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("[X] Error: ELEVENLABS_API_KEY not found in environment")
        print("Make sure your .env file has ELEVENLABS_API_KEY set")
        return 1
    
    print("Fetching available voices from ElevenLabs...")
    print("=" * 60)
    
    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {
            "Accept": "application/json",
            "xi-api-key": api_key
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        voices = data.get("voices", [])
        
        if not voices:
            print("[!] No voices found in your account")
            return 1
        
        print(f"\n[OK] Found {len(voices)} voice(s):\n")
        
        for i, voice in enumerate(voices, 1):
            voice_id = voice.get("voice_id")
            name = voice.get("name", "Unknown")
            description = voice.get("description", "")
            category = voice.get("category", "")
            
            print(f"{i}. {name}")
            print(f"   ID: {voice_id}")
            if description:
                print(f"   Description: {description}")
            if category:
                print(f"   Category: {category}")
            print()
        
        print("=" * 60)
        print("\nTo use these voices, update config/personas.yaml:")
        print("  voice_id: \"<voice_id_from_above>\"")
        print("\nExample:")
        if voices:
            example_voice = voices[0]
            print(f"  voice_id: \"{example_voice.get('voice_id')}\"")
        
        return 0
        
    except requests.exceptions.RequestException as e:
        print(f"[X] Error fetching voices: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return 1
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

