"""
Analyze D-ID API endpoint to determine the correct AWS region.

D-ID uses AWS API Gateway, which means the region might be embedded in the endpoint.
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
import socket
from src.utils.console_output import safe_print

def analyze_did_endpoint():
    """Analyze D-ID endpoint to find AWS region."""
    base_url = "https://api.d-id.com"
    
    safe_print("="*60)
    safe_print("D-ID API Endpoint Analysis")
    safe_print("="*60)
    safe_print(f"Base URL: {base_url}")
    safe_print()
    
    # DNS lookup
    safe_print("[STEP 1] DNS Resolution...")
    try:
        hostname = "api.d-id.com"
        ip_address = socket.gethostbyname(hostname)
        safe_print(f"  Hostname: {hostname}")
        safe_print(f"  IP Address: {ip_address}")
        safe_print()
    except Exception as e:
        safe_print(f"  Error: {e}")
        safe_print()
    
    # Check response headers for clues
    safe_print("[STEP 2] Checking response headers for region clues...")
    try:
        response = requests.get(base_url, timeout=5)
        safe_print(f"  Status: {response.status_code}")
        safe_print("  Headers:")
        for key, value in response.headers.items():
            if any(x in key.lower() or x in value.lower() for x in ['region', 'aws', 'amazon', 'x-amz']):
                safe_print(f"    {key}: {value}")
        safe_print()
    except Exception as e:
        safe_print(f"  Error: {e}")
        safe_print()
    
    # Try OPTIONS request
    safe_print("[STEP 3] Trying OPTIONS request...")
    try:
        response = requests.options(f"{base_url}/avatars", timeout=5)
        safe_print(f"  Status: {response.status_code}")
        safe_print("  Headers:")
        for key, value in response.headers.items():
            safe_print(f"    {key}: {value}")
        safe_print()
    except Exception as e:
        safe_print(f"  Error: {e}")
        safe_print()
    
    # Try to make an unauthenticated request and analyze error
    safe_print("[STEP 4] Analyzing error response for region hints...")
    try:
        response = requests.get(f"{base_url}/avatars", timeout=5)
        safe_print(f"  Status: {response.status_code}")
        safe_print(f"  Response: {response.text}")
        safe_print()
        
        # Check if error message contains region information
        if "region" in response.text.lower():
            safe_print("  [INFO] Error message mentions 'region'")
            # Try to extract region from error
            import re
            region_match = re.search(r'region["\s:]*([a-z]+-[a-z]+-\d+)', response.text.lower())
            if region_match:
                suggested_region = region_match.group(1)
                safe_print(f"  [INFO] Possible region from error: {suggested_region}")
    except Exception as e:
        safe_print(f"  Error: {e}")
    
    safe_print("="*60)
    safe_print("ANALYSIS COMPLETE")
    safe_print()
    safe_print("D-ID uses AWS API Gateway with custom authentication.")
    safe_print("The API requires AWS Signature V4, but the specific region")
    safe_print("is not standard and may be configured by D-ID.")
    safe_print()
    safe_print("Recommendation: Contact D-ID support for:")
    safe_print("1. Correct AWS region for SigV4")
    safe_print("2. Service name (if not 'execute-api')")
    safe_print("3. Any special SigV4 parameters")
    safe_print("="*60)

if __name__ == "__main__":
    analyze_did_endpoint()

