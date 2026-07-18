"""
Test D-ID API with Basic Auth on /talks endpoint (as per official docs).
"""

import os
import sys
from pathlib import Path
import base64
import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.console_output import safe_print

# Load environment variables
load_dotenv()

def test_did_basic_auth_talks():
    """Test D-ID /talks endpoint with Basic Auth (as per official docs)."""
    api_key = os.getenv("DID_API_KEY")
    
    if not api_key:
        safe_print("[X] DID_API_KEY not found in .env")
        sys.exit(1)
    
    if ":" not in api_key:
        safe_print("[X] D-ID API key must be in format 'username:password'")
        sys.exit(1)
    
    base_url = "https://api.d-id.com"
    
    safe_print("="*60)
    safe_print("Testing D-ID /talks endpoint with Basic Auth")
    safe_print("="*60)
    safe_print(f"API Key format: username:password")
    safe_print(f"Base URL: {base_url}\n")
    
    # Encode API key as per D-ID docs
    encoded_credentials = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    safe_print("[TEST 1] Testing /talks endpoint (list talks)...")
    try:
        response = requests.get(f"{base_url}/talks", headers=headers, timeout=10)
        safe_print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("  [OK] SUCCESS! Basic Auth works!")
            safe_print(f"  Response: {response.text[:200]}")
            return True
        else:
            safe_print(f"  [X] Failed: {response.status_code}")
            safe_print(f"  Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        safe_print(f"  [X] Request failed: {e}")
    
    safe_print("\n[TEST 2] Testing /avatars endpoint...")
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        safe_print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("  [OK] SUCCESS! /avatars works with Basic Auth!")
            safe_print(f"  Response: {response.text[:200]}")
            return True
        else:
            safe_print(f"  [X] Failed: {response.status_code}")
            safe_print(f"  Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        safe_print(f"  [X] Request failed: {e}")
    
    safe_print("\n" + "="*60)
    safe_print("[X] Basic Auth test failed")
    safe_print("="*60)
    return False

if __name__ == "__main__":
    success = test_did_basic_auth_talks()
    sys.exit(0 if success else 1)

