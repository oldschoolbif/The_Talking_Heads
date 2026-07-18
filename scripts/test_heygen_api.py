"""
Test HeyGen API connectivity and find correct endpoints.
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

def test_endpoints():
    """Test various HeyGen API endpoints."""
    api_key = os.getenv("HEYGEN_API_KEY")
    
    if not api_key:
        print("[X] HEYGEN_API_KEY not found")
        return
    
    print("Testing HeyGen API endpoints...")
    print("=" * 60)
    
    base_urls = [
        "https://api.heygen.com/v1",
        "https://api.heygen.com/v2",
        "https://api.heygen.com",
    ]
    
    endpoints = [
        "/avatars",
        "/v1/avatars",
        "/v2/avatars",
        "/video/generate",
        "/v1/video/generate",
        "/v2/video/generate",
        "/talks",
        "/v1/talks",
    ]
    
    headers = {"X-Api-Key": api_key}
    
    for base_url in base_urls:
        print(f"\nTesting base URL: {base_url}")
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                # Try GET first
                r = requests.get(url, headers=headers, timeout=5)
                print(f"  GET {endpoint}: {r.status_code}")
                if r.status_code != 404:
                    print(f"    Response: {r.text[:100]}")
            except Exception as e:
                print(f"  GET {endpoint}: Error - {type(e).__name__}")
    
    print("\n" + "=" * 60)
    print("If all endpoints return 404, HeyGen API may be decommissioned.")
    print("Consider using D-ID instead (already configured).")

if __name__ == "__main__":
    test_endpoints()

