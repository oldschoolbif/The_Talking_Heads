"""
Test HeyGen v2 video generation endpoint.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests

def test_heygen_v2_video():
    """Test HeyGen v2 video generation."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return False
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    print("Testing HeyGen v2 Video Generation...")
    print("=" * 60)
    
    # First, try to list avatars
    print("\n1. Listing avatars...")
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            avatars = data.get("data", {}).get("avatars", []) or data.get("avatars", [])
            print(f"   [OK] Found {len(avatars)} avatars")
            if avatars:
                print(f"   Sample avatar ID: {avatars[0].get('avatar_id', avatars[0].get('id', 'N/A'))}")
                return True
        else:
            print(f"   [X] Status {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"   [X] Error: {e}")
    
    # Try alternative endpoint
    print("\n2. Trying alternative endpoints...")
    endpoints = ["/video/avatars", "/avatars/list", "/video/list"]
    for ep in endpoints:
        try:
            response = requests.get(f"{base_url}{ep}", headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"   [OK] {ep} works!")
                data = response.json()
                print(f"   Response: {str(data)[:200]}")
                return True
        except Exception:
            continue
    
    print("\n" + "=" * 60)
    print("Could not find working avatar endpoint.")
    print("Check HeyGen documentation: https://docs.heygen.com")
    return False

if __name__ == "__main__":
    sys.exit(0 if test_heygen_v2_video() else 1)

