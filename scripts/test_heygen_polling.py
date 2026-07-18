"""
Test HeyGen polling endpoint to find correct format.
"""

import sys
import os
from dotenv import load_dotenv
load_dotenv()

import requests
import time
import json

def test_heygen_polling():
    """Test different polling endpoint formats."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return False
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    # First create a video
    print("1. Creating test video...")
    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": "Abigail_expressive_2024112501",
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": "Test polling endpoint.",
                    "voice_id": "e0cc82c22f414c95b1f25696c732f058",
                    "speed": 1.0
                }
            }
        ],
        "dimension": {
            "width": 1920,
            "height": 1080
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/video/generate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"   [X] Failed: {response.status_code} - {response.text[:200]}")
            return False
        
        data = response.json()
        video_id = data.get("data", {}).get("video_id")
        print(f"   [OK] Video ID: {video_id}")
        
        # Try different polling endpoints
        print("\n2. Testing polling endpoints...")
        endpoints = [
            f"{base_url}/videos/{video_id}",
            f"{base_url}/video/{video_id}",
            f"{base_url}/videos/{video_id}/status",
            f"{base_url}/video/{video_id}/status",
            f"{base_url}/tasks/{video_id}",
            f"{base_url}/task/{video_id}",
        ]
        
        for endpoint in endpoints:
            try:
                print(f"   Trying: {endpoint}")
                poll_response = requests.get(endpoint, headers=headers, timeout=10)
                print(f"      Status: {poll_response.status_code}")
                if poll_response.status_code == 200:
                    print(f"      [OK] SUCCESS! Response: {json.dumps(poll_response.json(), indent=2)[:300]}")
                    return True
                elif poll_response.status_code == 404:
                    print(f"      [X] 404 Not Found")
                else:
                    print(f"      [X] {poll_response.status_code}: {poll_response.text[:100]}")
            except Exception as e:
                print(f"      [X] Error: {str(e)[:50]}")
        
        print("\n   [!] No working endpoint found. Waiting 5 seconds and retrying...")
        time.sleep(5)
        
        # Retry the most likely endpoint
        endpoint = f"{base_url}/videos/{video_id}"
        poll_response = requests.get(endpoint, headers=headers, timeout=10)
        if poll_response.status_code == 200:
            print(f"   [OK] Endpoint works after delay: {endpoint}")
            print(f"   Response: {json.dumps(poll_response.json(), indent=2)[:500]}")
            return True
        
        return False
        
    except Exception as e:
        print(f"[X] Error: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_heygen_polling() else 1)

