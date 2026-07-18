"""
Debug D-ID API authentication with detailed logging.

This script attempts to reverse-engineer the correct D-ID authentication
by trying different combinations and logging detailed responses.
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
import json
from src.utils.console_output import safe_print

def test_did_debug():
    """Debug D-ID authentication with detailed logging."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        safe_print("[X] DID_API_KEY not found")
        return False
    
    base_url = "https://api.d-id.com"
    
    safe_print("="*60)
    safe_print("D-ID API Debug - Detailed Authentication Analysis")
    safe_print("="*60)
    safe_print(f"API Key format: {'username:password' if ':' in api_key else 'single key'}")
    safe_print(f"API Key length: {len(api_key)}")
    safe_print(f"Base URL: {base_url}")
    safe_print()
    
    # Test different service names with AWS SigV4
    if ":" in api_key:
        safe_print("[TEST] AWS Signature V4 with different service names...")
        safe_print()
        
        try:
            from requests_aws4auth import AWS4Auth
            
            access_key, secret_key = api_key.split(":", 1)
            
            # Test different service names
            service_names = [
                "execute-api",
                "d-id",
                "api",
                "d-id-api",
                "apigateway",
                "sts",
                "iam",
                "cognito-identity",
                "cognito-idp"
            ]
            
            # Test different regions
            regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]
            
            for service in service_names:
                for region in regions:
                    safe_print(f"Testing: service={service}, region={region}")
                    
                    try:
                        auth = AWS4Auth(access_key, secret_key, region, service)
                        headers = {"Content-Type": "application/json"}
                        
                        response = requests.get(
                            f"{base_url}/avatars",
                            headers=headers,
                            auth=auth,
                            timeout=5
                        )
                        
                        safe_print(f"  Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            safe_print(f"[OK] SUCCESS with service={service}, region={region}")
                            safe_print(f"  Response: {response.text[:200]}")
                            return True
                        else:
                            # Show detailed error for debugging
                            error_msg = response.text[:150]
                            safe_print(f"  Error: {error_msg}")
                            
                            # Check if error message gives us hints
                            if "Credential should be scoped" in error_msg:
                                # Extract expected region from error if present
                                safe_print("  [INFO] Error suggests incorrect region")
                            elif "service" in error_msg.lower():
                                safe_print("  [INFO] Error mentions service - might be wrong service name")
                    except Exception as e:
                        safe_print(f"  Exception: {str(e)[:100]}")
                    
                    safe_print()
            
            safe_print("[X] No working combination found")
            
        except ImportError:
            safe_print("[X] requests-aws4auth not installed")
        except Exception as e:
            safe_print(f"[X] Error: {e}")
    
    # Try alternative: Check if API key itself contains the token
    safe_print("\n[TEST] Direct API key as token...")
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        safe_print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            safe_print("[OK] Direct API key works!")
            return True
        else:
            safe_print(f"  Response: {response.text[:200]}")
    except Exception as e:
        safe_print(f"  Error: {e}")
    
    # Try splitting key differently if it has multiple colons
    if api_key.count(':') > 1:
        safe_print("\n[TEST] API key has multiple colons, trying different splits...")
        parts = api_key.split(':')
        safe_print(f"  Parts: {len(parts)}")
        
        # Try first two parts
        if len(parts) >= 2:
            test_key = f"{parts[0]}:{parts[1]}"
            safe_print(f"\n  Testing first two parts (length: {len(test_key)})...")
            
            try:
                from requests_aws4auth import AWS4Auth
                access_key, secret_key = parts[0], parts[1]
                
                for service in ["execute-api", "d-id"]:
                    for region in ["us-east-1", "eu-west-1"]:
                        auth = AWS4Auth(access_key, secret_key, region, service)
                        headers = {"Content-Type": "application/json"}
                        
                        response = requests.get(
                            f"{base_url}/avatars",
                            headers=headers,
                            auth=auth,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            safe_print(f"[OK] Success with {service}, {region}")
                            return True
            except Exception as e:
                safe_print(f"  Error: {e}")
    
    safe_print("\n" + "="*60)
    safe_print("[X] All authentication attempts failed")
    safe_print("\nD-ID API requires AWS Signature V4, but:")
    safe_print("1. The correct AWS region is unknown")
    safe_print("2. The correct service name is unknown")
    safe_print("3. May require special D-ID-specific SigV4 implementation")
    safe_print("\nRecommendation: Contact D-ID support or check their SDK implementation")
    safe_print("="*60)
    
    return False

if __name__ == "__main__":
    success = test_did_debug()
    sys.exit(0 if success else 1)

