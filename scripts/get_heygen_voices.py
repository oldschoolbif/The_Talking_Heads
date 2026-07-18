"""
Get real HeyGen voice IDs from the API.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests

def get_heygen_voices():
    """Get list of HeyGen voices."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return None
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    try:
        response = requests.get(f"{base_url}/voices", headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            voices = data.get("data", {}).get("voices", []) or data.get("voices", [])
            return voices
        else:
            print(f"[X] Failed: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"[X] Error: {e}")
        return None

if __name__ == "__main__":
    voices = get_heygen_voices()
    if voices:
        print(f"\n[OK] Found {len(voices)} voices")
        print("\nFirst 10 voices:")
        for i, voice in enumerate(voices[:10], 1):
            voice_id = voice.get("voice_id") or voice.get("id")
            name = voice.get("name", "N/A")
            print(f"  {i}. {name} (ID: {voice_id})")
        
        # Suggest a default voice
        if voices:
            default_voice = voices[0]
            print(f"\nSuggested default voice: {default_voice.get('voice_id') or default_voice.get('id')}")
    else:
        print("[X] Could not retrieve voices")

