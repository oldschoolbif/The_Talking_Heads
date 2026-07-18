"""
Test D-ID API with correct Basic Authentication using HTTPBasicAuth.
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
from requests.auth import HTTPBasicAuth
from src.utils.console_output import safe_print

def test_did_basic_auth():
    """Test D-ID API with HTTPBasicAuth."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        safe_print("[X] DID_API_KEY not found")
        return False
    
    if ":" not in api_key:
        safe_print("[X] API key must be in format 'username:password'")
        return False
    
    username, password = api_key.split(":", 1)
    base_url = "https://api.d-id.com"
    
    safe_print("="*60)
    safe_print("D-ID API Test - HTTPBasicAuth (Correct Method)")
    safe_print("="*60)
    safe_print(f"Username length: {len(username)}")
    safe_print(f"Password length: {len(password)}")
    safe_print(f"Base URL: {base_url}")
    safe_print()
    
    # Test 1: List avatars
    safe_print("[TEST 1] Listing avatars with HTTPBasicAuth...")
    try:
        response = requests.get(
            f"{base_url}/avatars",
            auth=HTTPBasicAuth(username, password),
            timeout=10
        )
        
        safe_print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            safe_print("[OK] Authentication successful!")
            data = response.json()
            safe_print(f"  Response type: {type(data)}")
            if isinstance(data, list):
                safe_print(f"  Number of avatars: {len(data)}")
            elif isinstance(data, dict):
                avatars = data.get('avatars', [])
                safe_print(f"  Number of avatars: {len(avatars)}")
            safe_print()
            return True
        else:
            safe_print(f"[X] Failed: {response.text[:200]}")
            safe_print()
            return False
            
    except Exception as e:
        safe_print(f"[X] Error: {e}")
        safe_print()
        return False

if __name__ == "__main__":
    success = test_did_basic_auth()
    
    if success:
        safe_print("="*60)
        safe_print("[OK] D-ID authentication working!")
        safe_print("     Method: HTTPBasicAuth")
        safe_print("     Ready to update DIDProvider")
        safe_print("="*60)
    else:
        safe_print("="*60)
        safe_print("[X] Authentication still failing")
        safe_print("="*60)
    
    sys.exit(0 if success else 1)

