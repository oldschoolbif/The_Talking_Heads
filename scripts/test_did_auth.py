"""
Test different D-ID authentication methods.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests
import base64

def test_did_auth_methods():
    """Test different D-ID authentication methods."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        print("DID_API_KEY not found")
        return
    
    base_url = "https://api.d-id.com"
    
    print("Testing D-ID Authentication Methods")
    print("=" * 60)
    print(f"API Key format: {'username:password' if ':' in api_key else 'other'}")
    print(f"API Key length: {len(api_key)}")
    print()
    
    # Method 1: Basic auth with base64 encoded key
    print("Method 1: Basic auth with base64 encoded key")
    if ":" in api_key:
        encoded_key = base64.b64encode(api_key.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json"
        }
    else:
        headers = {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json"
        }
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  [OK] SUCCESS!")
            data = response.json()
            print(f"  Response: {str(data)[:200]}")
            return True
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Method 2: API key in header (not Basic auth)
    print("\nMethod 2: API key in X-API-Key header")
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  [OK] SUCCESS!")
            return True
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Method 3: Bearer token
    print("\nMethod 3: Bearer token")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  [OK] SUCCESS!")
            return True
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print("\n" + "=" * 60)
    print("All authentication methods failed.")
    print("Check D-ID API documentation: https://docs.d-id.com")
    return False

if __name__ == "__main__":
    sys.exit(0 if test_did_auth_methods() else 1)

