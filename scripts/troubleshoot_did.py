"""
Step-by-step D-ID troubleshooting script.
Run this to diagnose D-ID API issues systematically.
"""

import sys
import os
from pathlib import Path
import requests
import base64
import json
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def print_step(step_num, title):
    """Print a formatted step header."""
    print("\n" + "="*70)
    print(f"STEP {step_num}: {title}")
    print("="*70)

def print_result(success, message):
    """Print a formatted result."""
    symbol = "[OK]" if success else "[FAIL]"
    # Use simple formatting for Windows compatibility
    print(f"{symbol} {message}")

def step1_check_api_key():
    """Step 1: Verify API key exists and format."""
    print_step(1, "Check API Key")
    
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        print_result(False, "DID_API_KEY not found in .env file")
        print("\nAction: Add DID_API_KEY to your .env file")
        return None
    
    print_result(True, f"API key found (length: {len(api_key)})")
    
    # Check format
    if ":" in api_key:
        username, password = api_key.split(":", 1)
        print(f"  Format: username:password")
        print(f"  Username: {username}")
        print(f"  Password: {'*' * len(password)}")
    else:
        print(f"  Format: Bearer token (single value)")
    
    return api_key

def step2_test_authentication(api_key):
    """Step 2: Test authentication with D-ID API."""
    print_step(2, "Test Authentication")
    
    base_url = "https://api.d-id.com"
    
    # Setup auth headers
    if ":" in api_key:
        encoded = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {encoded}",
            "Accept": "application/json"
        }
        auth_method = "Basic Auth"
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        auth_method = "Bearer Token"
    
    print(f"Using: {auth_method}")
    
    # Test 1: List talks (simple GET request)
    try:
        response = requests.get(f"{base_url}/talks", headers=headers, timeout=10)
        print(f"\nTest: GET /talks")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            print_result(True, "Authentication successful!")
            talks = response.json().get("talks", [])
            print(f"  Found {len(talks)} existing talks")
            return True, headers
        elif response.status_code == 401:
            print_result(False, "Authentication failed (401 Unauthorized)")
            print("  -> API key is invalid or expired")
            return False, None
        elif response.status_code == 403:
            print_result(False, "Access forbidden (403)")
            print("  -> API key may not have required permissions")
            return False, None
        else:
            print_result(False, f"Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        print_result(False, f"Connection error: {e}")
        return False, None

def step3_check_account_status(headers):
    """Step 3: Check account status and credits."""
    print_step(3, "Check Account Status")
    
    base_url = "https://api.d-id.com"
    
    # Try to get account info (if endpoint exists)
    endpoints_to_try = [
        "/credits",
        "/account",
        "/user",
        "/me",
    ]
    
    account_info_found = False
    for endpoint in endpoints_to_try:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                print_result(True, f"Account endpoint found: {endpoint}")
                try:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)[:500]}")
                    account_info_found = True
                    break
                except:
                    print(f"  Response: {response.text[:200]}")
                    account_info_found = True
                    break
        except:
            continue
    
    if not account_info_found:
        print("  -> No account status endpoint found (this is normal)")
        print("  -> Check your D-ID dashboard at https://studio.d-id.com for credits")
    
    print("\nAction Required:")
    print("  1. Go to https://studio.d-id.com")
    print("  2. Log in to your account")
    print("  3. Check 'Credits' or 'Usage' section")
    print("  4. Verify you have credits available")
    print("  5. Check if your subscription plan is active")

def step4_test_image_urls():
    """Step 4: Verify D-ID image URLs are accessible."""
    print_step(4, "Test Image URLs")
    
    test_urls = [
        "https://d-id-public-bucket.s3.amazonaws.com/amy.jpg",
        "https://d-id-public-bucket.s3.amazonaws.com/sara.jpg",
        "https://d-id-public-bucket.s3.amazonaws.com/john.jpg",
    ]
    
    accessible_urls = []
    for url in test_urls:
        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print_result(True, f"Image accessible: {url}")
                accessible_urls.append(url)
            else:
                print_result(False, f"Image not accessible: {url} (Status: {response.status_code})")
        except Exception as e:
            print_result(False, f"Image check failed: {url} ({e})")
    
    if accessible_urls:
        print(f"\n[OK] Found {len(accessible_urls)} accessible image URLs")
        return accessible_urls[0]  # Return first working URL
    else:
        print("\n[FAIL] No accessible image URLs found")
        print("  -> D-ID may have changed their image URLs")
        print("  -> Check D-ID documentation for current image URLs")
        return None

def step5_test_minimal_talk_creation(headers, image_url):
    """Step 5: Test creating a talk with minimal payload."""
    print_step(5, "Test Minimal Talk Creation")
    
    base_url = "https://api.d-id.com"
    
    if not image_url:
        print("Skipping - no valid image URL available")
        return False
    
    # Test with absolute minimal payload
    payload = {
        "source_url": image_url,
        "script": {
            "type": "text",
            "input": "Hello"
        }
    }
    
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"\nMaking request...")
    
    try:
        response = requests.post(
            f"{base_url}/talks",
            json=payload,
            headers=json_headers,
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Body (text): {response.text[:500]}")
        
        if response.status_code in [200, 201, 202]:
            print_result(True, "Talk created successfully!")
            talk_id = response_data.get("id")
            if talk_id:
                print(f"  Talk ID: {talk_id}")
                return True, talk_id
            return True, None
        elif response.status_code == 400:
            print_result(False, "Bad Request (400)")
            print("  -> Check payload format and required fields")
            if isinstance(response_data, dict):
                errors = response_data.get("details", {})
                if errors:
                    print(f"  Validation errors: {json.dumps(errors, indent=2)}")
            return False, None
        elif response.status_code == 402:
            print_result(False, "Payment Required (402)")
            print("  -> Account credits exhausted or payment required")
            return False, None
        elif response.status_code == 403:
            print_result(False, "Forbidden (403)")
            print("  -> API key doesn't have permission to create talks")
            return False, None
        elif response.status_code == 429:
            print_result(False, "Rate Limited (429)")
            print("  -> Too many requests, wait before retrying")
            return False, None
        elif response.status_code == 500:
            print_result(False, "Internal Server Error (500)")
            print("  -> D-ID server-side error")
            print("\nPossible causes:")
            print("  1. D-ID servers are experiencing issues")
            print("  2. Account credits exhausted")
            print("  3. Account subscription expired")
            print("  4. Image URL is invalid or inaccessible")
            print("  5. API endpoint format changed")
            return False, None
        else:
            print_result(False, f"Unexpected status: {response.status_code}")
            return False, None
            
    except requests.exceptions.Timeout:
        print_result(False, "Request timed out")
        return False, None
    except Exception as e:
        print_result(False, f"Request failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def step6_check_did_documentation():
    """Step 6: Provide links to check D-ID documentation."""
    print_step(6, "Check D-ID Documentation")
    
    print("Review D-ID API documentation for current requirements:")
    print("\n1. API Documentation:")
    print("   https://docs.d-id.com/")
    
    print("\n2. Talks API Endpoint:")
    print("   https://docs.d-id.com/reference/talks-create")
    
    print("\n3. Authentication:")
    print("   https://docs.d-id.com/reference/authentication")
    
    print("\n4. Account Dashboard:")
    print("   https://studio.d-id.com/")
    
    print("\n5. Support:")
    print("   https://support.d-id.com/")
    
    print("\nThings to verify:")
    print("  * Current API endpoint format")
    print("  * Required request fields")
    print("  * Image URL format requirements")
    print("  * Account subscription status")
    print("  * Available credits")

def step7_get_valid_image_url(headers):
    """Step 7: Try to get/create a valid image URL."""
    print_step(7, "Get Valid Image URL")
    
    base_url = "https://api.d-id.com"
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"
    
    # Option 1: Try to list/create avatars (if endpoint exists)
    print("\nOption 1: Check if we can list/create avatars")
    avatar_endpoints = ["/avatars", "/images", "/sources"]
    
    for endpoint in avatar_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=json_headers, timeout=10)
            if response.status_code == 200:
                print(f"[OK] Found endpoint: {endpoint}")
                try:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)[:500]}")
                    # Try to extract image URLs from response
                    if isinstance(data, dict):
                        results = data.get("results", data.get("avatars", data.get("images", [])))
                        if results and len(results) > 0:
                            first_item = results[0]
                            if isinstance(first_item, dict):
                                img_url = first_item.get("url") or first_item.get("source_url") or first_item.get("image_url")
                                if img_url:
                                    print(f"[OK] Found image URL: {img_url}")
                                    return img_url
                except:
                    pass
            elif response.status_code == 403:
                print(f"  Endpoint {endpoint} requires AWS Signature (403)")
            else:
                print(f"  Endpoint {endpoint}: Status {response.status_code}")
        except:
            continue
    
    # Option 2: Instructions for uploading image
    print("\nOption 2: Upload image via D-ID Studio")
    print("  -> To upload an image:")
    print("     1. Go to https://studio.d-id.com")
    print("     2. Navigate to 'Avatars' or 'Images' section")
    print("     3. Upload an image (jpg/jpeg/png)")
    print("     4. Copy the image URL from the dashboard")
    print("     5. Use that URL in your requests")
    
    # Option 3: Use a publicly accessible test image
    print("\nOption 3: Use publicly accessible test image")
    test_images = [
        "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400",
    ]
    
    for test_url in test_images:
        try:
            response = requests.head(test_url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                print(f"[OK] Test image accessible: {test_url}")
                print("  -> You can use this URL for testing")
                return test_url
        except:
            continue
    
    print("\n[FAIL] No valid image URLs found automatically")
    print("\nSOLUTION:")
    print("  1. Upload an image to D-ID Studio: https://studio.d-id.com")
    print("  2. Or use a publicly accessible image URL (jpg/jpeg/png)")
    print("  3. Or check D-ID docs for current preset image URLs")
    return None

def step8_test_alternative_formats(headers, image_url):
    """Step 8: Test alternative request formats."""
    print_step(8, "Test Alternative Request Formats")
    
    if not image_url:
        print("Skipping - no valid image URL")
        return
    
    base_url = "https://api.d-id.com"
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"
    
    # Format 1: Minimal with just source_url and script
    print("\nFormat 1: Minimal payload")
    payload1 = {
        "source_url": image_url,
        "script": {
            "type": "text",
            "input": "Test"
        }
    }
    test_format(base_url, json_headers, payload1, "Format 1")
    
    # Format 2: With driver (if supported)
    print("\nFormat 2: With driver parameter")
    payload2 = {
        "source_url": image_url,
        "script": {
            "type": "text",
            "input": "Test"
        },
        "driver": "text"
    }
    test_format(base_url, json_headers, payload2, "Format 2")
    
    # Format 3: Different script format
    print("\nFormat 3: Alternative script format")
    payload3 = {
        "source_url": image_url,
        "script": "Test"
    }
    test_format(base_url, json_headers, payload3, "Format 3")

def test_format(base_url, headers, payload, name):
    """Test a specific payload format."""
    try:
        response = requests.post(f"{base_url}/talks", json=payload, headers=headers, timeout=30)
        print(f"  {name}: Status {response.status_code}")
        if response.status_code in [200, 201, 202]:
            print_result(True, f"{name} succeeded!")
            return True
        elif response.status_code == 500:
            print(f"  -> Still 500 error")
        else:
            print(f"  -> Response: {response.text[:100]}")
    except Exception as e:
        print(f"  -> Error: {e}")
    return False

def main():
    """Run all troubleshooting steps."""
    print("\n" + "="*70)
    print("D-ID API Troubleshooting Guide")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check API key
    api_key = step1_check_api_key()
    if not api_key:
        print("\n[FAIL] Cannot continue without API key")
        return
    
    # Step 2: Test authentication
    auth_success, headers = step2_test_authentication(api_key)
    if not auth_success or not headers:
        print("\n[FAIL] Authentication failed. Fix API key before continuing.")
        return
    
    # Step 3: Check account status
    step3_check_account_status(headers)
    
    # Step 4: Test image URLs
    image_url = step4_test_image_urls()
    
    # Step 5: Test minimal talk creation (if we have image URL)
    if image_url:
        talk_created, talk_id = step5_test_minimal_talk_creation(headers, image_url)
        
        if talk_created:
            print("\n" + "="*70)
            print_result(True, "SUCCESS! D-ID API is working!")
            print("="*70)
            if talk_id:
                print(f"\nNext: Poll for talk completion with talk_id: {talk_id}")
            return
    else:
        print("\n[INFO] Skipping Step 5 - no valid image URL available")
        talk_created = False
        talk_id = None
    
    # Step 6: Check documentation
    step6_check_did_documentation()
    
    # Step 7: Try to get valid image URL
    valid_image_url = step7_get_valid_image_url(headers)
    if valid_image_url:
        print(f"\n[OK] Found valid image URL: {valid_image_url}")
        print("Retrying talk creation with valid URL...")
        talk_created, talk_id = step5_test_minimal_talk_creation(headers, valid_image_url)
        if talk_created:
            print("\n" + "="*70)
            print_result(True, "SUCCESS! D-ID API is working with valid image URL!")
            print("="*70)
            if talk_id:
                print(f"\nNext: Poll for talk completion with talk_id: {talk_id}")
            return
    
    # Step 8: Try alternative formats (if we have any image URL)
    test_url = image_url or valid_image_url
    if test_url:
        step8_test_alternative_formats(headers, test_url)
        
        print("\n" + "="*70)
        print("Troubleshooting Summary")
        print("="*70)
        print("\nIf all steps passed but you still get 500 errors:")
        print("  1. Check D-ID account credits at https://studio.d-id.com")
        print("  2. Verify subscription is active")
        print("  3. Contact D-ID support: https://support.d-id.com/")
        print("  4. Check D-ID status page for outages")
        print("  5. Try again later (may be temporary server issues)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTroubleshooting interrupted by user.")
    except Exception as e:
        print(f"\n\nError during troubleshooting: {e}")
        import traceback
        traceback.print_exc()

