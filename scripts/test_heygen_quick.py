"""
Quick test of HeyGen API to check response structure.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests
import time

def test_heygen_quick():
    """Quick test of HeyGen video generation."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return False
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    print("Testing HeyGen video generation...")
    
    # Create video
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
                    "input_text": "Hello, this is a quick test.",
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
        print("1. Creating video...")
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
        
        # Poll for status (quick test - only 3 polls)
        print("2. Polling status (3 attempts)...")
        for i in range(3):
            time.sleep(2)
            poll_response = requests.get(
                f"{base_url}/videos/{video_id}",
                headers=headers,
                timeout=30
            )
            
            if poll_response.status_code == 200:
                poll_data = poll_response.json()
                status = poll_data.get("data", {}).get("status")
                print(f"   Poll {i+1}: Status = {status}")
                
                if status == "completed":
                    video_url = poll_data.get("data", {}).get("video_url")
                    print(f"   [OK] Video URL: {video_url}")
                    return True
                elif status == "failed":
                    print(f"   [X] Video generation failed")
                    return False
            else:
                print(f"   [X] Poll failed: {poll_response.status_code}")
        
        print("   [!] Still processing (this is normal, videos take time)")
        return True  # API is working, just not done yet
        
    except Exception as e:
        print(f"[X] Error: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_heygen_quick() else 1)

