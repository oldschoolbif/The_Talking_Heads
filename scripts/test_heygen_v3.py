"""
Test HeyGen v3 API to find correct endpoint format.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests
import json

def test_heygen_v3():
    """Test HeyGen v3 API endpoints."""
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return False
    
    base_urls = [
        "https://api.heygen.com/v3",
        "https://api.heygen.com/v2",
        "https://api.heygen.com/v1",
    ]
    
    # Try different authentication methods
    auth_methods = [
        ("Bearer", f"Bearer {api_key}"),
        ("X-Api-Key", api_key),
        ("Authorization", f"Bearer {api_key}"),
    ]
    
    endpoints_to_try = [
        "/avatars",
        "/video/avatars",
        "/video/generate",
        "/videos",
        "/templates",
    ]
    
    print("Testing HeyGen API...")
    print("=" * 60)
    
    for base_url in base_urls:
        print(f"\nTrying base URL: {base_url}")
        for auth_name, auth_value in auth_methods:
            print(f"  Auth: {auth_name}")
            headers = {auth_name: auth_value, "Content-Type": "application/json"}
            
            for endpoint in endpoints_to_try:
                try:
                    url = f"{base_url}{endpoint}"
                    print(f"    GET {endpoint}...", end=" ")
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        print(f"[OK] SUCCESS!")
                        data = response.json()
                        print(f"      Response: {str(data)[:200]}")
                        return True
                    elif response.status_code == 401:
                        print(f"[X] 401 Unauthorized")
                        break  # Try next auth method
                    elif response.status_code == 404:
                        print(f"[X] 404 Not Found")
                        continue  # Try next endpoint
                    else:
                        print(f"[X] {response.status_code}: {response.text[:100]}")
                except Exception as e:
                    print(f"[X] Error: {str(e)[:50]}")
                    continue
    
    print("\n" + "=" * 60)
    print("All endpoints failed. Check HeyGen documentation:")
    print("https://docs.heygen.com")
    return False

if __name__ == "__main__":
    sys.exit(0 if test_heygen_v3() else 1)

