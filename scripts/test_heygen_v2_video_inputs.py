"""
Test HeyGen v2 video generation with correct video_inputs format.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests
import json

def test_heygen_v2_video_inputs():
    """Test HeyGen v2 video generation with video_inputs."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return False
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    print("Testing HeyGen v2 Video Generation with video_inputs...")
    print("=" * 60)
    
    # Get an avatar ID
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
            print(f"   [X] Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False
    
    # Try different video_inputs formats
    print("\n2. Testing video_inputs formats...")
    
    formats_to_try = [
        # Format 1: Array with avatar and text
        {
            "video_inputs": [
                {
                    "avatar_id": avatar_id,
                    "text": "Hello, this is a test video."
                }
            ]
        },
        # Format 2: Single object
        {
            "video_inputs": {
                "avatar_id": avatar_id,
                "text": "Hello, this is a test video."
            }
        },
        # Format 3: With background
        {
            "video_inputs": [
                {
                    "avatar_id": avatar_id,
                    "text": "Hello, this is a test video.",
                    "background": {
                        "type": "color",
                        "value": "#000000"
                    }
                }
            ]
        },
    ]
    
    for i, payload in enumerate(formats_to_try, 1):
        try:
            print(f"   Format {i}...", end=" ")
            response = requests.post(
                f"{base_url}/video/generate",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"[OK] SUCCESS!")
                data = response.json()
                print(f"      Response keys: {list(data.keys())}")
                if "data" in data:
                    print(f"      Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'Not a dict'}")
                return True
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", response.text[:100])
                print(f"[!] 400: {error_msg}")
            else:
                print(f"[X] {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"[X] Error: {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print("Could not find correct video_inputs format.")
    print("Check HeyGen documentation: https://docs.heygen.com")
    return False

if __name__ == "__main__":
    sys.exit(0 if test_heygen_v2_video_inputs() else 1)

