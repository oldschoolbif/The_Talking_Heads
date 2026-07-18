"""
Get real HeyGen avatar IDs from the API.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests

def get_heygen_avatars():
    """Get list of HeyGen avatars."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return None
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            avatars = data.get("data", {}).get("avatars", []) or data.get("avatars", [])
            return avatars
        else:
            print(f"[X] Failed: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"[X] Error: {e}")
        return None

if __name__ == "__main__":
    avatars = get_heygen_avatars()
    if avatars:
        print(f"\n[OK] Found {len(avatars)} avatars")
        print("\nFirst 10 avatars:")
        for i, avatar in enumerate(avatars[:10], 1):
            avatar_id = avatar.get("avatar_id") or avatar.get("id")
            name = avatar.get("name", "N/A")
            print(f"  {i}. {name} (ID: {avatar_id})")
        
        # Suggest avatars for Alice and Bob
        print("\nSuggested avatars for personas:")
        if len(avatars) >= 2:
            alice_avatar = avatars[0]
            bob_avatar = avatars[1] if len(avatars) > 1 else avatars[0]
            print(f"  Alice: {alice_avatar.get('avatar_id') or alice_avatar.get('id')}")
            print(f"  Bob: {bob_avatar.get('avatar_id') or bob_avatar.get('id')}")
    else:
        print("[X] Could not retrieve avatars")

