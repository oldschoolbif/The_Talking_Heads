"""
Test D-ID API with proper AWS IAM credentials.

Use this script AFTER you've found AWS credentials in D-ID dashboard.
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
from src.utils.console_output import safe_print

def test_did_aws_credentials():
    """Test D-ID with AWS IAM credentials."""
    # Check for AWS credentials
    aws_access_key = os.getenv("DID_AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("DID_AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("DID_AWS_REGION", "us-west-2")
    
    safe_print("="*60)
    safe_print("D-ID AWS IAM Credentials Test")
    safe_print("="*60)
    safe_print()
    
    # Validate credentials exist
    if not aws_access_key:
        safe_print("[X] DID_AWS_ACCESS_KEY_ID not found in .env")
        safe_print()
        safe_print("Add to .env file:")
        safe_print("DID_AWS_ACCESS_KEY_ID=AKIA****************")
        safe_print()
        return False
    
    if not aws_secret_key:
        safe_print("[X] DID_AWS_SECRET_ACCESS_KEY not found in .env")
        safe_print()
        safe_print("Add to .env file:")
        safe_print("DID_AWS_SECRET_ACCESS_KEY=****************************************")
        safe_print()
        return False
    
    safe_print("[OK] AWS credentials found")
    safe_print(f"     Access Key: {aws_access_key[:4]}***{aws_access_key[-4:] if len(aws_access_key) > 4 else '***'}")
    safe_print(f"     Secret Key: ****** (hidden)")
    safe_print(f"     Region: {aws_region}")
    safe_print()
    
    # Validate credential format
    if not aws_access_key.startswith("AKIA"):
        safe_print("[WARN] Access key doesn't start with 'AKIA'")
        safe_print("       This may not be a valid AWS Access Key ID")
        safe_print()
    
    # Test authentication
    safe_print("[TEST] Authenticating with D-ID API...")
    try:
        from requests_aws4auth import AWS4Auth
    except ImportError:
        safe_print("[X] requests-aws4auth not installed")
        safe_print("    Install with: pip install requests-aws4auth")
        return False
    
    base_url = "https://api.d-id.com"
    service = "execute-api"
    
    try:
        auth = AWS4Auth(aws_access_key, aws_secret_key, aws_region, service)
        headers = {"Content-Type": "application/json"}
        
        response = requests.get(
            f"{base_url}/avatars",
            headers=headers,
            auth=auth,
            timeout=10
        )
        
        safe_print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            safe_print()
            safe_print("[OK] AUTHENTICATION SUCCESSFUL!")
            safe_print()
            data = response.json()
            if isinstance(data, list):
                safe_print(f"  Found {len(data)} avatars")
            elif isinstance(data, dict):
                avatars = data.get('avatars', [])
                safe_print(f"  Found {len(avatars)} avatars")
            safe_print()
            safe_print("="*60)
            safe_print("[OK] D-ID authentication working!")
            safe_print(f"     Region: {aws_region}")
            safe_print(f"     Service: {service}")
            safe_print("="*60)
            return True
        else:
            safe_print()
            safe_print(f"[X] Authentication failed: {response.status_code}")
            safe_print(f"    Error: {response.text[:200]}")
            safe_print()
            
            if "region" in response.text.lower():
                safe_print("[!] Error mentions region - try different region")
                safe_print("    Add to .env: DID_AWS_REGION=<correct_region>")
            
            return False
            
    except Exception as e:
        safe_print()
        safe_print(f"[X] Error: {e}")
        safe_print()
        return False

if __name__ == "__main__":
    success = test_did_aws_credentials()
    sys.exit(0 if success else 1)

