"""
Simple D-ID test to diagnose issues.
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import requests
import base64
from pathlib import Path

# Get API key
api_key = os.getenv("DID_API_KEY")
if not api_key:
    print("ERROR: DID_API_KEY not found in .env")
    sys.exit(1)

print(f"API Key format: {'username:password' if ':' in api_key else 'single value'}")
print(f"API Key length: {len(api_key)}")

# Test authentication - try both Bearer and Basic Auth
base_url = "https://api.d-id.com"

# Try Bearer token first (if no ':')
if ":" not in api_key:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    auth_method = "Bearer"
else:
    encoded_credentials = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    auth_method = "Basic"

print(f"Using {auth_method} authentication")

# Test 1: Check API status/health
print("\n=== Test 1: API Health Check ===")
try:
    response = requests.get(f"{base_url}/talks", headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: List available avatars (if endpoint exists)
print("\n=== Test 2: List Avatars ===")
try:
    response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        avatars = response.json()
        print(f"Found {len(avatars.get('results', []))} avatars")
        if avatars.get('results'):
            print(f"First avatar: {avatars['results'][0]}")
    else:
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try creating a talk with text (simpler than audio)
print("\n=== Test 3: Create Talk with Text ===")
try:
    # D-ID requires actual image URLs. Let's try with a public image URL or preset
    # Common D-ID preset avatars use image URLs like:
    # https://d-id-public-bucket.s3.amazonaws.com/amy.jpg
    # Or we can use preset format if supported
    
    # Try with a known D-ID preset image URL
    # D-ID typically uses S3 URLs for preset avatars
    test_image_url = "https://d-id-public-bucket.s3.amazonaws.com/amy.jpg"
    
    payload = {
        "source_url": test_image_url,
        "script": {
            "type": "text",
            "input": "Hello, this is a test."
        }
    }
    
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"
    
    response = requests.post(f"{base_url}/talks", json=payload, headers=json_headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code in [200, 201, 202]:
        talk_data = response.json()
        print(f"[OK] Talk created successfully!")
        print(f"  Talk ID: {talk_data.get('id')}")
        print(f"  Status: {talk_data.get('status')}")
        print(f"  Result URL: {talk_data.get('result_url', 'N/A')}")
    elif response.status_code == 400:
        print(f"[X] Validation error - checking response details...")
        try:
            error_data = response.json()
            print(f"  Error: {error_data}")
        except:
            pass
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Try creating a talk with audio file upload
print("\n=== Test 4: Create Talk with Audio File ===")
try:
    # Create a simple test audio file
    test_audio_path = project_root / ".cache" / "test_audio.mp3"
    test_audio_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if we have any existing audio files to test with
    audio_files = list((project_root / ".cache" / "tts").glob("*.mp3")) if (project_root / ".cache" / "tts").exists() else []
    
    if not audio_files:
        print("  No audio files found for testing. Skipping audio upload test.")
        print("  (Would need to generate TTS audio first)")
    else:
        test_audio = audio_files[0]
        print(f"  Using audio file: {test_audio.name}")
        
        test_image_url = "https://d-id-public-bucket.s3.amazonaws.com/amy.jpg"
        
        with open(test_audio, "rb") as f:
            files = {"audio": (test_audio.name, f, "audio/mpeg")}
            data = {"source_url": test_image_url}
            
            # Remove Content-Type - requests will set it for multipart
            multipart_headers = {k: v for k, v in headers.items() if k.lower() != "content-type"}
            multipart_headers["Authorization"] = headers["Authorization"]
            
            response = requests.post(f"{base_url}/talks", files=files, data=data, headers=multipart_headers, timeout=60)
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            
            if response.status_code in [200, 201, 202]:
                talk_data = response.json()
                print(f"  [OK] Talk created with audio!")
                print(f"    Talk ID: {talk_data.get('id')}")
                print(f"    Status: {talk_data.get('status')}")
except Exception as e:
    print(f"  Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Tests Complete ===")

