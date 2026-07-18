"""
List available D-ID avatars.

This script helps you find real avatar IDs to use in personas.yaml.
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
import base64

def main():
    """List available D-ID avatars."""
    # Get API key from environment
    api_key = os.getenv("DID_API_KEY")
    
    if not api_key:
        print("[X] Error: DID_API_KEY not found in environment")
        print("Make sure your .env file has DID_API_KEY set")
        return 1
    
    print("Fetching available avatars from D-ID...")
    print("=" * 60)
    
    try:
        # D-ID uses Basic auth with base64 encoded key
        url = "https://api.d-id.com/avatars"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {api_key}"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        avatars = data.get("avatars", [])
        
        if not avatars:
            print("[!] No avatars found in your account")
            print("\nNote: D-ID also supports using image URLs as avatars.")
            print("You can use any publicly accessible image URL as avatar_id.")
            return 1
        
        print(f"\n[OK] Found {len(avatars)} avatar(s):\n")
        
        for i, avatar in enumerate(avatars, 1):
            avatar_id = avatar.get("id") or avatar.get("avatar_id")
            name = avatar.get("name", "Unknown")
            created_at = avatar.get("created_at", "")
            
            print(f"{i}. {name}")
            print(f"   ID: {avatar_id}")
            if created_at:
                print(f"   Created: {created_at}")
            print()
        
        print("=" * 60)
        print("\nTo use these avatars, update config/personas.yaml:")
        print("  avatar_id: \"<avatar_id_from_above>\"")
        print("\nExample:")
        if avatars:
            example_avatar = avatars[0]
            example_id = example_avatar.get("id") or example_avatar.get("avatar_id")
            print(f"  avatar_id: \"{example_id}\"")
        
        print("\nNote: D-ID also supports image URLs as avatars.")
        print("You can use any publicly accessible image URL.")
        
        return 0
        
    except requests.exceptions.RequestException as e:
        print(f"[X] Error fetching avatars: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        print("\nNote: If you don't have custom avatars, you can:")
        print("1. Use D-ID's preset avatars (check D-ID documentation)")
        print("2. Upload an image and use its URL as avatar_id")
        return 1
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

