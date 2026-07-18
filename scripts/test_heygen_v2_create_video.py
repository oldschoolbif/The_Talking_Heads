"""
Test HeyGen v2 video creation endpoint.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests
import json

def test_heygen_v2_create():
    """Test HeyGen v2 video creation."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return False
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    print("Testing HeyGen v2 Video Creation...")
    print("=" * 60)
    
    # Get an avatar ID first
    print("\n1. Getting avatar ID...")
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            avatars = data.get("data", {}).get("avatars", []) or data.get("avatars", [])
            if not avatars:
                print("   [X] No avatars found")
                return False
            avatar_id = avatars[0].get("avatar_id") or avatars[0].get("id")
            print(f"   [OK] Using avatar: {avatar_id}")
        else:
            print(f"   [X] Failed to get avatars: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False
    
    # Try different video creation endpoints
    print("\n2. Testing video creation endpoints...")
    endpoints = [
        "/video/generate",
        "/videos",
        "/video/create",
        "/videos/create",
    ]
    
    # Test payload (minimal)
    test_payload = {
        "avatar_id": avatar_id,
        "text": "Hello, this is a test.",
    }
    
    for endpoint in endpoints:
        try:
            print(f"   Trying POST {endpoint}...", end=" ")
            response = requests.post(
                f"{base_url}{endpoint}",
                headers=headers,
                json=test_payload,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"[OK] SUCCESS!")
                data = response.json()
                print(f"      Response: {str(data)[:300]}")
                return True
            elif response.status_code == 400:
                print(f"[!] 400 Bad Request (endpoint exists, check payload)")
                print(f"      Response: {response.text[:200]}")
            elif response.status_code == 401:
                print(f"[X] 401 Unauthorized")
            elif response.status_code == 404:
                print(f"[X] 404 Not Found")
            else:
                print(f"[X] {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"[X] Error: {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print("Could not find working video creation endpoint.")
    return False

if __name__ == "__main__":
    sys.exit(0 if test_heygen_v2_create() else 1)

