"""
Test script to verify HeyGen and D-ID API connectivity and functionality.
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
import time
import json
from src.utils.console_output import safe_print

def print_status(success: bool, message: str):
    """Print status with OK/X prefix."""
    prefix = "[OK]" if success else "[X]"
    safe_print(f"{prefix} {message}")

def test_heygen_api():
    """Test HeyGen API connectivity and video generation."""
    print("\n" + "="*60)
    print("Testing HeyGen API")
    print("="*60)
    
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print_status(False, "HEYGEN_API_KEY not found in environment")
        return False
    
    print_status(True, f"API Key found (starts with: {api_key[:10]}...)")
    
    base_url = "https://api.heygen.com/v2"
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    
    # Test 1: Create a video
    print("\n1. Testing video creation...")
    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": "Abigail_expressive_2024112501",
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": "This is a test video to verify the HeyGen API integration.",
                    "voice_id": "e0cc82c22f414c95b1f25696c732f058",
                    "speed": 1.0
                }
            }
        ],
        "dimension": {
            "width": 1920,
            "height": 1080
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/video/generate",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            video_id = data.get("data", {}).get("video_id")
            if video_id:
                print_status(True, f"Video creation successful! Video ID: {video_id}")
                
                # Test 2: Poll for status
                print("\n2. Testing video status polling...")
                print("   (This may take 30-60 seconds for video to be ready)")
                
                poll_endpoints = [
                    f"{base_url}/video/{video_id}",
                    f"{base_url}/videos/{video_id}",
                ]
                
                max_wait = 120  # 2 minutes for testing
                poll_interval = 5
                start_time = time.time()
                poll_count = 0
                
                while time.time() - start_time < max_wait:
                    poll_count += 1
                    elapsed = time.time() - start_time
                    
                    for endpoint in poll_endpoints:
                        try:
                            poll_response = requests.get(endpoint, headers=headers, timeout=10)
                            print(f"   [{poll_count}] Trying {endpoint}: {poll_response.status_code}", end="")
                            
                            if poll_response.status_code == 200:
                                poll_data = poll_response.json()
                                status = poll_data.get("data", {}).get("status") or poll_data.get("status")
                                print(f" - Status: {status}")
                                
                                if status in ["completed", "done"]:
                                    video_url = (
                                        poll_data.get("data", {}).get("video_url")
                                        or poll_data.get("data", {}).get("url")
                                        or poll_data.get("video_url")
                                        or poll_data.get("url")
                                    )
                                    if video_url:
                                        print_status(True, f"Video ready! URL: {video_url[:50]}...")
                                        print_status(True, f"Completed in {elapsed:.1f} seconds")
                                        return True
                                elif status in ["failed", "error"]:
                                    error = poll_data.get("data", {}).get("error") or poll_data.get("error")
                                    print_status(False, f"Video generation failed: {error}")
                                    return False
                                else:
                                    print(f" - Still processing ({status})...")
                            elif poll_response.status_code == 404:
                                print(" - 404 (video not ready yet)")
                            else:
                                print(f" - Error: {poll_response.status_code}")
                        except Exception as e:
                            print(f" - Exception: {str(e)[:50]}")
                    
                    if poll_count % 3 == 0:
                        print(f"   [{elapsed:.0f}s elapsed] Continuing to poll...")
                    
                    time.sleep(poll_interval)
                
                print_status(False, f"Polling timed out after {max_wait} seconds")
                print(f"   Video ID: {video_id} - You can check it manually later")
                return False
                
            else:
                print_status(False, "Video creation response missing video_id")
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
                return False
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                error_msg = str(error_data.get("error", error_data))
            except Exception:
                error_msg = response.text[:200] if response.text else error_msg
            
            print_status(False, f"Video creation failed: {error_msg}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(False, f"Request failed: {str(e)}")
        return False
    except Exception as e:
        print_status(False, f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_did_api():
    """Test D-ID API connectivity and authentication."""
    print("\n" + "="*60)
    print("Testing D-ID API")
    print("="*60)
    
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        print_status(False, "DID_API_KEY not found in environment")
        return False
    
    print_status(True, f"API Key found (length: {len(api_key)})")
    
    # Check API key format
    if ":" in api_key:
        access_key, secret_key = api_key.split(":", 1)
        print_status(True, f"API Key format: access_key:secret_key (detected)")
        print(f"   Access key length: {len(access_key)}")
        print(f"   Secret key length: {len(secret_key)}")
    else:
        secret_key = os.getenv("DID_API_SECRET", "")
        if secret_key:
            access_key = api_key
            print_status(True, f"API Key format: separate key and secret (from env)")
        else:
            print_status(False, "D-ID API key format unclear. Expected 'access_key:secret_key' or DID_API_SECRET env var")
            return False
    
    base_url = "https://api.d-id.com"
    
    # Test 1: Try AWS Signature V4 authentication
    print("\n1. Testing AWS Signature V4 authentication...")
    try:
        from requests_aws4auth import AWS4Auth
        
        # Try different regions - D-ID might use a different region
        regions_to_try = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        service = "execute-api"
        
        auth = None
        working_region = None
        
        for region in regions_to_try:
            try:
                test_auth = AWS4Auth(access_key, secret_key, region, service)
                # Test with a simple request
                test_response = requests.get(
                    f"{base_url}/avatars",
                    headers={"Content-Type": "application/json"},
                    auth=test_auth,
                    timeout=10
                )
                if test_response.status_code == 200:
                    auth = test_auth
                    working_region = region
                    print_status(True, f"Found working region: {region}")
                    break
                elif test_response.status_code != 403:
                    # If it's not 403, the region might be right but there's another issue
                    auth = test_auth
                    working_region = region
                    print(f"   Trying {region}: {test_response.status_code}")
            except Exception as e:
                print(f"   Region {region} failed: {str(e)[:50]}")
                continue
        
        if not auth:
            # Default to us-east-1 if none work
            region = "us-east-1"
            auth = AWS4Auth(access_key, secret_key, region, service)
            print(f"   Using default region: {region}")
        else:
            region = working_region
        
        print_status(True, "AWS4Auth initialized successfully")
        
        # Test with /avatars endpoint (simpler than creating a talk)
        headers = {"Content-Type": "application/json"}
        print("\n2. Testing /avatars endpoint...")
        
        try:
            response = requests.get(
                f"{base_url}/avatars",
                headers=headers,
                auth=auth,
                timeout=30
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                avatar_count = len(data) if isinstance(data, list) else 0
                print_status(True, f"Authentication successful! Found {avatar_count} avatars")
                return True
            elif response.status_code == 403:
                error_msg = response.text[:200] if response.text else "Forbidden"
                print_status(False, f"Authentication failed (403): {error_msg}")
                print("   This suggests the API key format or credentials are incorrect")
                return False
            else:
                error_msg = response.text[:200] if response.text else f"HTTP {response.status_code}"
                print_status(False, f"Request failed: {error_msg}")
                return False
                
        except requests.exceptions.RequestException as e:
            print_status(False, f"Request failed: {str(e)}")
            return False
            
    except ImportError:
        print_status(False, "requests-aws4auth not installed")
        print("   Install with: pip install requests-aws4auth")
        return False
    except Exception as e:
        print_status(False, f"AWS4Auth setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all API tests."""
    print("="*60)
    print("Avatar API Connectivity Test")
    print("="*60)
    
    results = {}
    
    # Test HeyGen
    results["heygen"] = test_heygen_api()
    
    # Test D-ID
    results["did"] = test_did_api()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for service, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "[OK]" if passed else "[X]"
        print(f"{symbol} {service.upper():10s}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n[OK] All API tests passed! Ready to generate output.")
        return 0
    else:
        print("\n[X] Some API tests failed. Please check the errors above.")
        print("\nNext steps:")
        if not results.get("heygen"):
            print("  - HeyGen: Check API key and verify video polling endpoint")
        if not results.get("did"):
            print("  - D-ID: Verify API key format (access_key:secret_key) and AWS credentials")
        return 1


if __name__ == "__main__":
    sys.exit(main())

