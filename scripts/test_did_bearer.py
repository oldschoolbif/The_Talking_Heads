"""
Test D-ID API with Bearer token authentication.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import requests
import base64

def test_did_bearer():
    """Test D-ID API with Bearer token."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        print("[X] DID_API_KEY not found")
        return False
    
    base_url = "https://api.d-id.com"
    
    print("Testing D-ID API with Bearer token...")
    print("=" * 60)
    
    # Method 1: Bearer token (direct)
    print("\nMethod 1: Bearer token (direct)")
    headers = {
        "Authorization": f"Bearer {api_key}",
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
    
    # Method 2: Bearer token (if API key is username:password format)
    if ":" in api_key:
        print("\nMethod 2: Bearer token (base64 encoded username:password)")
        encoded = base64.b64encode(api_key.encode()).decode()
        headers = {
            "Authorization": f"Bearer {encoded}",
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
    print("Bearer token authentication failed.")
    print("Check D-ID documentation: https://docs.d-id.com")
    return False

if __name__ == "__main__":
    sys.exit(0 if test_did_bearer() else 1)

