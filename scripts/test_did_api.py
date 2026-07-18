"""
Test D-ID API connectivity and request format.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import requests
import base64

def test_did_api():
    """Test D-ID API with a simple request."""
    api_key = os.getenv("DID_API_KEY")
    
    if not api_key:
        print("[X] DID_API_KEY not found")
        return
    
    # D-ID API key format: "username:password" - needs base64 encoding
    if ":" in api_key:
        encoded_key = base64.b64encode(api_key.encode()).decode()
    else:
        encoded_key = api_key
    
    base_url = "https://api.d-id.com"
    headers = {
        "Authorization": f"Basic {encoded_key}",
        "Content-Type": "application/json"
    }
    
    print("Testing D-ID API...")
    print("=" * 60)
    
    # Test 1: List avatars
    print("\n1. Testing /avatars endpoint...")
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {str(data)[:200]}")
            if data.get("avatars"):
                print(f"   Found {len(data['avatars'])} avatars")
                if len(data['avatars']) > 0:
                    print(f"   First avatar ID: {data['avatars'][0].get('id', 'N/A')}")
        else:
            print(f"   Error: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check talks endpoint format
    print("\n2. Checking /talks endpoint documentation format...")
    print("   D-ID API typically expects:")
    print("   - source_url: URL to image or avatar ID")
    print("   - script: Text to speak (not audio file upload)")
    print("   - OR: source_url + audio_url (URL to hosted audio)")
    print("\n   Note: D-ID may not support direct audio file uploads.")
    print("   You may need to:")
    print("   1. Upload audio to a public URL first")
    print("   2. Use text-to-speech (script parameter) instead")
    print("   3. Use a different API format")
    
    print("\n" + "=" * 60)
    print("Check D-ID documentation: https://docs.d-id.com")

if __name__ == "__main__":
    test_did_api()

