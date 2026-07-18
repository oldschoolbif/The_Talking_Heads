"""
Test D-ID API with simple authentication methods (non-AWS).
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import requests
import base64

def test_did_simple_auth():
    """Test D-ID API with simple authentication (not AWS SigV4)."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        print("[X] DID_API_KEY not found")
        return False
    
    base_url = "https://api.d-id.com"
    
    print("Testing D-ID API with simple authentication methods...")
    print("="*60)
    
    # Test 1: X-Api-Key header
    print("\n1. Testing X-Api-Key header...")
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] X-Api-Key authentication works!")
            return True
        elif response.status_code == 401:
            print("   [X] Unauthorized")
        elif response.status_code == 403:
            print(f"   [X] Forbidden: {response.text[:100]}")
        else:
            print(f"   [X] Error: {response.text[:100]}")
    except Exception as e:
        print(f"   [X] Error: {str(e)[:50]}")
    
    # Test 2: Authorization: Bearer
    print("\n2. Testing Bearer token...")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] Bearer token authentication works!")
            return True
        elif response.status_code == 401:
            print("   [X] Unauthorized")
        elif response.status_code == 403:
            print(f"   [X] Forbidden: {response.text[:100]}")
        else:
            print(f"   [X] Error: {response.text[:100]}")
    except Exception as e:
        print(f"   [X] Error: {str(e)[:50]}")
    
    # Test 3: Basic auth (if key has colon)
    if ":" in api_key:
        print("\n3. Testing Basic auth...")
        api_key_b64 = base64.b64encode(api_key.encode()).decode()
        headers = {"Authorization": f"Basic {api_key_b64}", "Content-Type": "application/json"}
        try:
            response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   [OK] Basic auth works!")
                return True
            elif response.status_code == 401:
                print("   [X] Unauthorized")
            elif response.status_code == 403:
                print(f"   [X] Forbidden: {response.text[:100]}")
            else:
                print(f"   [X] Error: {response.text[:100]}")
        except Exception as e:
            print(f"   [X] Error: {str(e)[:50]}")
    
    # Test 4: Try without colon (just the key itself)
    print("\n4. Testing API key without colon...")
    if ":" in api_key:
        simple_key = api_key.split(":")[0]  # Just the access key part
    else:
        simple_key = api_key
    
    headers = {"X-Api-Key": simple_key, "Content-Type": "application/json"}
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] Simple API key works!")
            return True
        elif response.status_code == 401:
            print("   [X] Unauthorized")
        elif response.status_code == 403:
            print(f"   [X] Forbidden: {response.text[:100]}")
        else:
            print(f"   [X] Error: {response.text[:100]}")
    except Exception as e:
        print(f"   [X] Error: {str(e)[:50]}")
    
    print("\n[X] None of the simple authentication methods worked.")
    print("    D-ID may require AWS Signature V4 with a specific region.")
    print("    Check D-ID API documentation for the correct authentication method.")
    return False


if __name__ == "__main__":
    sys.exit(0 if test_did_simple_auth() else 1)

