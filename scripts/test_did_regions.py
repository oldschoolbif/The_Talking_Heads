"""
Test script to find the correct D-ID AWS region.
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

def test_did_regions():
    """Test different AWS regions for D-ID API."""
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        print("[X] DID_API_KEY not found")
        return None
    
    if ":" not in api_key:
        print("[X] D-ID API key must be in format 'access_key:secret_key'")
        return None
    
    access_key, secret_key = api_key.split(":", 1)
    
    try:
        from requests_aws4auth import AWS4Auth
    except ImportError:
        print("[X] requests-aws4auth not installed. Install with: pip install requests-aws4auth")
        return None
    
    base_url = "https://api.d-id.com"
    service = "execute-api"
    
    # Common AWS regions to try
    regions = [
        "us-east-1",      # US East (N. Virginia)
        "us-west-1",      # US West (N. California)
        "us-west-2",      # US West (Oregon)
        "eu-west-1",      # Europe (Ireland)
        "eu-central-1",   # Europe (Frankfurt)
        "ap-southeast-1", # Asia Pacific (Singapore)
        "ap-southeast-2", # Asia Pacific (Sydney)
        "ap-northeast-1", # Asia Pacific (Tokyo)
        "sa-east-1",     # South America (São Paulo)
    ]
    
    print("Testing D-ID API regions...")
    print("="*60)
    
    for region in regions:
        try:
            auth = AWS4Auth(access_key, secret_key, region, service)
            headers = {"Content-Type": "application/json"}
            
            response = requests.get(
                f"{base_url}/avatars",
                headers=headers,
                auth=auth,
                timeout=10
            )
            
            print(f"{region:15s}: {response.status_code}", end="")
            
            if response.status_code == 200:
                print(" [OK] SUCCESS! This is the correct region.")
                return region
            elif response.status_code == 403:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", "")
                    if "region" in error_msg.lower():
                        print(f" - Wrong region: {error_msg[:50]}")
                    else:
                        print(f" - Auth issue: {error_msg[:50]}")
                except Exception:
                    print(" - 403 Forbidden")
            else:
                print(f" - {response.status_code}")
                
        except Exception as e:
            print(f"{region:15s}: Error - {str(e)[:50]}")
    
    print("\n[X] No working region found. D-ID API may require different authentication.")
    return None


if __name__ == "__main__":
    working_region = test_did_regions()
    if working_region:
        print(f"\n[OK] Use this region in config: aws_region: \"{working_region}\"")
        sys.exit(0)
    else:
        sys.exit(1)

