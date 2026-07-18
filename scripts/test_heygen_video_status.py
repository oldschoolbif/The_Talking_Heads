"""
Test HeyGen video status endpoint to find correct polling method.
"""

import sys
import os
from dotenv import load_dotenv
load_dotenv()

import requests
import time
import json

def test_heygen_video_creation_and_status():
    """Test HeyGen video creation and find correct status endpoint."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return False
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    # Create a video
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
                    "input_text": "This is a test video to check the status endpoint.",
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
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)[:500]}")
        
        if response.status_code != 200:
            return False
        
        data = response.json()
        video_id = data.get("data", {}).get("video_id") or data.get("data", {}).get("id")
        
        if not video_id:
            print("   [X] No video_id in response")
            return False
        
        print(f"   [OK] Video ID: {video_id}")
        
        # Try different status endpoints
        print("\n2. Testing status endpoints...")
        endpoints_to_try = [
            f"{base_url}/videos/{video_id}",
            f"{base_url}/video/{video_id}",
            f"{base_url}/videos/{video_id}/status",
            f"{base_url}/video/{video_id}/status",
            f"{base_url}/video/generate/{video_id}",
            f"{base_url}/video/generate/{video_id}/status",
        ]
        
        # Wait a bit for video to start processing
        print("   Waiting 5 seconds for video to start processing...")
        time.sleep(5)
        
        for endpoint in endpoints_to_try:
            try:
                print(f"\n   Trying: {endpoint}")
                status_response = requests.get(endpoint, headers=headers, timeout=10)
                print(f"      Status: {status_response.status_code}")
                
                if status_response.status_code == 200:
                    print(f"      [OK] SUCCESS!")
                    print(f"      Response: {json.dumps(status_response.json(), indent=2)[:500]}")
                    return True
                elif status_response.status_code == 404:
                    print(f"      [X] 404 Not Found")
                else:
                    print(f"      Response: {status_response.text[:200]}")
            except Exception as e:
                print(f"      [X] Error: {str(e)[:100]}")
        
        # Check if the initial response has status info
        print("\n3. Checking initial response for status information...")
        initial_data = response.json()
        if "data" in initial_data:
            data_section = initial_data["data"]
            print(f"   Data keys: {list(data_section.keys())}")
            if "status" in data_section:
                print(f"   Initial status: {data_section['status']}")
            if "video_url" in data_section:
                print(f"   Video URL in initial response: {data_section['video_url']}")
                return True
        
        return False
        
    except Exception as e:
        print(f"[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sys.exit(0 if test_heygen_video_creation_and_status() else 1)

