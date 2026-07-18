"""
Test D-ID with manually constructed Basic Auth header.
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
from src.utils.console_output import safe_print

def test_did_manual_basic():
    """Test D-ID with manually constructed Basic Auth."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key or ":" not in api_key:
        safe_print("[X] Invalid API key format")
        return False
    
    username, password = api_key.split(":", 1)
    base_url = "https://api.d-id.com"
    
    safe_print("="*60)
    safe_print("D-ID Manual Basic Auth Test")
    safe_print("="*60)
    safe_print()
    
    # Method 1: Base64 encoded Basic Auth
    safe_print("[METHOD 1] Basic Auth with base64 encoding...")
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        safe_print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("[OK] Success with Basic Auth!")
            return True
        else:
            safe_print(f"  Error: {response.text[:150]}")
    except Exception as e:
        safe_print(f"  Exception: {e}")
    
    # Method 2: Try us-west-2 region (from IP analysis)
    safe_print("\n[METHOD 2] AWS SigV4 with us-west-2 (from IP analysis)...")
    try:
        from requests_aws4auth import AWS4Auth
        
        auth = AWS4Auth(username, password, "us-west-2", "execute-api")
        headers = {"Content-Type": "application/json"}
        
        response = requests.get(
            f"{base_url}/avatars",
            headers=headers,
            auth=auth,
            timeout=10
        )
        
        safe_print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("[OK] Success with us-west-2!")
            return True
        else:
            safe_print(f"  Error: {response.text[:150]}")
    except ImportError:
        safe_print("  requests-aws4auth not installed")
    except Exception as e:
        safe_print(f"  Exception: {e}")
    
    # Method 3: Try with just the API key directly in header
    safe_print("\n[METHOD 3] Direct API key in x-api-key header...")
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        safe_print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("[OK] Success with x-api-key!")
            return True
        else:
            safe_print(f"  Error: {response.text[:150]}")
    except Exception as e:
        safe_print(f"  Exception: {e}")
    
    safe_print("\n" + "="*60)
    safe_print("[X] All methods failed")
    safe_print()
    safe_print("CONCLUSION:")
    safe_print("D-ID API requires AWS SigV4 but the correct region is unknown.")
    safe_print("The API is hosted on AWS API Gateway (us-west-2 based on IP),")
    safe_print("but authentication still fails.")
    safe_print()
    safe_print("NEXT STEPS:")
    safe_print("1. Verify API key is valid and active in D-ID dashboard")
    safe_print("2. Check D-ID documentation for any recent API changes")
    safe_print("3. Contact D-ID support for correct authentication parameters")
    safe_print("="*60)
    
    return False

if __name__ == "__main__":
    success = test_did_manual_basic()
    sys.exit(0 if success else 1)

