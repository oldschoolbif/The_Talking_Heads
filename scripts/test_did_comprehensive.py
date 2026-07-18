"""
Comprehensive D-ID API authentication test.

Tests multiple authentication methods and regions to find the correct configuration.
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

def test_did_comprehensive():
    """Comprehensive D-ID authentication test."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        safe_print("[X] DID_API_KEY not found in environment")
        return False
    
    base_url = "https://api.d-id.com"
    
    safe_print("="*60)
    safe_print("Comprehensive D-ID API Authentication Test")
    safe_print("="*60)
    safe_print(f"API Key format: {'username:password' if ':' in api_key else 'single key'}")
    safe_print(f"API Key length: {len(api_key)}")
    safe_print()
    
    success = False
    
    # Test 1: Basic Auth (Base64 encoded)
    safe_print("[TEST 1] Basic Auth (Base64 encoded)...")
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
        safe_print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("[OK] Basic Auth works!")
            success = True
        else:
            safe_print(f"   Response: {response.text[:200]}")
    except Exception as e:
        safe_print(f"   Error: {e}")
    
    # Test 2: X-API-Key header
    safe_print("\n[TEST 2] X-API-Key header...")
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        safe_print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("[OK] X-API-Key works!")
            success = True
        else:
            safe_print(f"   Response: {response.text[:200]}")
    except Exception as e:
        safe_print(f"   Error: {e}")
    
    # Test 3: Bearer token
    safe_print("\n[TEST 3] Bearer token...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        safe_print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("[OK] Bearer token works!")
            success = True
        else:
            safe_print(f"   Response: {response.text[:200]}")
    except Exception as e:
        safe_print(f"   Error: {e}")
    
    # Test 4: AWS Signature V4 (if key has colon)
    if ":" in api_key and not success:
        safe_print("\n[TEST 4] AWS Signature V4 (multiple regions)...")
        try:
            from requests_aws4auth import AWS4Auth
            
            access_key, secret_key = api_key.split(":", 1)
            service = "execute-api"
            
            regions_to_try = [
                "us-east-1", "us-east-2", "us-west-1", "us-west-2",
                "eu-west-1", "eu-west-2", "eu-central-1",
                "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
                "sa-east-1", "ca-central-1"
            ]
            
            for region in regions_to_try:
                try:
                    auth = AWS4Auth(access_key, secret_key, region, service)
                    headers = {"Content-Type": "application/json"}
                    
                    response = requests.get(
                        f"{base_url}/avatars",
                        headers=headers,
                        auth=auth,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        safe_print(f"[OK] AWS SigV4 works with region: {region}")
                        success = True
                        break
                    elif response.status_code != 403:
                        # If not 403, might be a different issue
                        safe_print(f"   Region {region}: Status {response.status_code}")
                except Exception as e:
                    continue
            
            if not success:
                safe_print("   No working AWS region found")
        except ImportError:
            safe_print("   requests-aws4auth not installed (pip install requests-aws4auth)")
        except Exception as e:
            safe_print(f"   Error: {e}")
    
    # Test 5: Check D-ID API documentation endpoint
    safe_print("\n[TEST 5] Checking D-ID API status...")
    try:
        # Try a simple GET to root or health endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        safe_print(f"   Root endpoint status: {response.status_code}")
    except Exception as e:
        safe_print(f"   Error: {e}")
    
    safe_print("\n" + "="*60)
    if success:
        safe_print("[OK] At least one authentication method works!")
    else:
        safe_print("[X] No working authentication method found")
        safe_print("\nRecommendations:")
        safe_print("1. Verify your D-ID API key is correct")
        safe_print("2. Check D-ID API documentation: https://docs.d-id.com")
        safe_print("3. Contact D-ID support for authentication guidance")
        safe_print("4. Ensure your API key has the correct format")
    safe_print("="*60)
    
    return success

if __name__ == "__main__":
    success = test_did_comprehensive()
    sys.exit(0 if success else 1)

