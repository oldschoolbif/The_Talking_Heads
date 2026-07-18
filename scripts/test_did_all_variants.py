"""
Ultimate D-ID authentication test - tries every possible variant.
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

def test_all_variants():
    """Try every possible authentication variant."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        safe_print("[X] DID_API_KEY not found")
        return False
    
    base_url = "https://api.d-id.com"
    test_endpoint = "/avatars"
    
    safe_print("="*60)
    safe_print("D-ID Ultimate Authentication Test")
    safe_print("Testing ALL possible authentication methods...")
    safe_print("="*60)
    safe_print()
    
    variants = []
    
    # If key has colon, split it
    if ":" in api_key:
        username, password = api_key.split(":", 1)
        
        # Variant 1: HTTPBasicAuth style
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        variants.append(("HTTPBasicAuth (requests library)", None, {"Authorization": f"Basic {encoded}"}))
        
        # Variant 2: Just username in x-api-key
        variants.append(("Username in x-api-key", None, {"x-api-key": username}))
        
        # Variant 3: Just password in x-api-key
        variants.append(("Password in x-api-key", None, {"x-api-key": password}))
        
        # Variant 4: Full key in x-api-key
        variants.append(("Full key in x-api-key", None, {"x-api-key": api_key}))
        
        # Variant 5: Username as Bearer
        variants.append(("Username as Bearer", None, {"Authorization": f"Bearer {username}"}))
        
        # Variant 6: Password as Bearer
        variants.append(("Password as Bearer", None, {"Authorization": f"Bearer {password}"}))
        
        # Variant 7: Full key as Bearer
        variants.append(("Full key as Bearer", None, {"Authorization": f"Bearer {api_key}"}))
        
        # Variant 8: Authorization with just the key (no Basic prefix)
        variants.append(("Direct auth header", None, {"Authorization": api_key}))
        
        # Variant 9: Custom D-ID header variations
        variants.append(("x-d-id-key", None, {"x-d-id-key": api_key}))
        variants.append(("d-id-api-key", None, {"d-id-api-key": api_key}))
        
        # Variant 10: Try HTTPBasicAuth from requests
        try:
            from requests.auth import HTTPBasicAuth
            variants.append(("HTTPBasicAuth object", HTTPBasicAuth(username, password), {}))
        except ImportError:
            pass
    else:
        # Single key format
        variants.append(("Key in x-api-key", None, {"x-api-key": api_key}))
        variants.append(("Key as Bearer", None, {"Authorization": f"Bearer {api_key}"}))
        variants.append(("Key direct", None, {"Authorization": api_key}))
    
    # Add common headers to all
    common_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    safe_print(f"Testing {len(variants)} authentication variants...")
    safe_print()
    
    for i, (name, auth_obj, headers) in enumerate(variants, 1):
        safe_print(f"[{i}/{len(variants)}] {name}...")
        
        # Merge headers
        test_headers = {**common_headers, **headers}
        
        try:
            if auth_obj:
                response = requests.get(
                    f"{base_url}{test_endpoint}",
                    auth=auth_obj,
                    headers=test_headers,
                    timeout=10
                )
            else:
                response = requests.get(
                    f"{base_url}{test_endpoint}",
                    headers=test_headers,
                    timeout=10
                )
            
            if response.status_code == 200:
                safe_print(f"      [OK] SUCCESS! Status: {response.status_code}")
                safe_print()
                safe_print("="*60)
                safe_print(f"FOUND WORKING METHOD: {name}")
                safe_print("="*60)
                safe_print()
                safe_print("Authentication headers:")
                for key, value in headers.items():
                    if "auth" in key.lower() or "key" in key.lower():
                        safe_print(f"  {key}: {value[:20]}..." if len(value) > 20 else f"  {key}: {value}")
                safe_print()
                if auth_obj:
                    safe_print(f"Auth object: {type(auth_obj).__name__}")
                safe_print()
                return True
            else:
                # Show concise error
                error_msg = response.text[:80] if response.text else "No error message"
                safe_print(f"      Status {response.status_code}: {error_msg}")
        
        except Exception as e:
            error_msg = str(e)[:60]
            safe_print(f"      Error: {error_msg}")
    
    safe_print()
    safe_print("="*60)
    safe_print("[X] No working authentication method found")
    safe_print("="*60)
    safe_print()
    safe_print("CONCLUSION:")
    safe_print("The current API key format is not compatible with D-ID API.")
    safe_print()
    safe_print("NEXT STEPS:")
    safe_print("1. Check D-ID dashboard for AWS IAM credentials")
    safe_print("   - Follow guide: docs/DID_DASHBOARD_CHECKLIST.md")
    safe_print()
    safe_print("2. Contact D-ID support for proper credentials")
    safe_print("   - Template in: docs/DID_CREDENTIAL_CHECK_GUIDE.md")
    safe_print()
    safe_print("3. Use alternative for immediate testing:")
    safe_print("   - MockAvatarProvider (free, immediate)")
    safe_print("   - HeyGen (paid, production-ready)")
    safe_print()
    
    return False

if __name__ == "__main__":
    success = test_all_variants()
    sys.exit(0 if success else 1)

