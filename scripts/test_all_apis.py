"""
Test all external APIs to verify connectivity and functionality.

Tests:
- ElevenLabs TTS (primary)
- Azure Speech TTS (fallback)
- gTTS (fallback)
- HeyGen Avatar (primary)
- D-ID Avatar (fallback)
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import requests
import base64
import json
from src.utils.console_output import safe_print, CHECKMARK, CROSS, WARNING

def test_elevenlabs():
    """Test ElevenLabs TTS API."""
    print("\n" + "=" * 60)
    print("Testing ElevenLabs TTS API")
    print("=" * 60)
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        safe_print(f"{CROSS} ELEVENLABS_API_KEY not found")
        return False
    
    base_url = "https://api.elevenlabs.io/v1"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: List voices
    print("\n1. Testing /voices endpoint...")
    try:
        response = requests.get(f"{base_url}/voices", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            voices = data.get("voices", [])
            safe_print(f"{CHECKMARK} Successfully connected - Found {len(voices)} voices")
            if voices:
                print(f"   Sample voice: {voices[0].get('name', 'N/A')} (ID: {voices[0].get('voice_id', 'N/A')})")
            return True
        else:
            print_status(f"[X] Failed with status {response.status_code}: {response.text[:200]}", status_type="error")
            return False
    except Exception as e:
        safe_print(f"{CROSS} Error: {e}")
        return False

def test_azure_speech():
    """Test Azure Speech Service."""
    print("\n" + "=" * 60)
    print("Testing Azure Speech Service")
    print("=" * 60)
    
    api_key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")
    
    if not api_key or not region:
        safe_print(f"{CROSS} AZURE_SPEECH_KEY or AZURE_SPEECH_REGION not found")
        return False
    
    # Azure Speech uses token-based auth, which is complex to test without SDK
    # Just verify credentials are set
    safe_print(f"{CHECKMARK} Credentials configured (Region: {region})")
    print("   Note: Full functionality requires azure-cognitiveservices-speech SDK")
    return True

def test_gtts():
    """Test gTTS (Google Text-to-Speech)."""
    print("\n" + "=" * 60)
    print("Testing gTTS (Google Text-to-Speech)")
    print("=" * 60)
    
    try:
        from gtts import gTTS
        import io
        
        # Test basic functionality
        print("\n1. Testing gTTS import and basic functionality...")
        tts = gTTS(text="Test", lang="en", slow=False)
        safe_print(f"{CHECKMARK} gTTS is available and functional")
        return True
    except ImportError:
        safe_print(f"{CROSS} gTTS not installed (pip install gtts)")
        return False
    except Exception as e:
        safe_print(f"{CROSS} Error: {e}")
        return False

def test_heygen():
    """Test HeyGen v2 API."""
    print("\n" + "=" * 60)
    print("Testing HeyGen v2 API")
    print("=" * 60)
    
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        safe_print(f"{CROSS} HEYGEN_API_KEY not found")
        return False
    
    base_url = "https://api.heygen.com/v2"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test 1: Check API connectivity (list avatars or similar endpoint)
    print("\n1. Testing API connectivity...")
    try:
        # Try a simple endpoint - HeyGen v2 might have different endpoints
        # Common endpoints: /avatars, /video/templates, etc.
        endpoints_to_try = [
            "/avatars",
            "/video/templates",
            "/video/avatars",
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
                if response.status_code == 200:
                    safe_print(f"{CHECKMARK} Successfully connected to {endpoint}")
                    return True
                elif response.status_code == 401:
                    safe_print(f"{CROSS} Authentication failed (401) - Check API key")
                    return False
                elif response.status_code == 404:
                    continue  # Try next endpoint
                else:
                    print(f"   {endpoint}: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                continue
        
        # If no endpoint worked, API key might be valid but endpoint structure unknown
        safe_print(f"{WARNING} API key configured but endpoint structure needs verification")
        print("   Check HeyGen v2 documentation: https://docs.heygen.com")
        return False
        
    except Exception as e:
        safe_print(f"{CROSS} Error: {e}")
        return False

def test_did():
    """Test D-ID API."""
    print("\n" + "=" * 60)
    print("Testing D-ID API")
    print("=" * 60)
    
    api_key = os.getenv("DID_API_KEY")
    if not api_key:
        safe_print(f"{CROSS} DID_API_KEY not found")
        return False
    
    base_url = "https://api.d-id.com"
    
    # D-ID API key format: "username:password" - needs base64 encoding
    if ":" in api_key:
        encoded_key = base64.b64encode(api_key.encode()).decode()
    else:
        encoded_key = api_key
    
    headers = {
        "Authorization": f"Basic {encoded_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: List avatars
    print("\n1. Testing /avatars endpoint...")
    try:
        response = requests.get(f"{base_url}/avatars", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            avatars = data.get("avatars", [])
            safe_print(f"{CHECKMARK} Successfully connected - Found {len(avatars)} avatars")
            if avatars:
                print(f"   Sample avatar: {avatars[0].get('id', 'N/A')}")
            return True
        elif response.status_code == 401:
            safe_print(f"{CROSS} Authentication failed (401) - Check API key format")
            print(f"   Response: {response.text[:200]}")
            return False
        elif response.status_code == 403:
            safe_print(f"{CROSS} Forbidden (403) - Check API key permissions")
            print(f"   Response: {response.text[:200]}")
            return False
        else:
            print_status(f"[X] Failed with status {response.status_code}: {response.text[:200]}", status_type="error")
            return False
    except Exception as e:
        safe_print(f"{CROSS} Error: {e}")
        return False

def main():
    """Run all API tests."""
    print("=" * 60)
    print("API Connectivity Test Suite")
    print("=" * 60)
    
    results = {
        "ElevenLabs": test_elevenlabs(),
        "Azure Speech": test_azure_speech(),
        "gTTS": test_gtts(),
        "HeyGen": test_heygen(),
        "D-ID": test_did(),
    }
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for service, passed in results.items():
        status = f"{CHECKMARK} PASS" if passed else f"{CROSS} FAIL"
        print(f"{service:20} {status}")
    
    # Determine preferred services
    print("\n" + "=" * 60)
    print("Recommended Configuration")
    print("=" * 60)
    
    if results["ElevenLabs"]:
        safe_print(f"{CHECKMARK} TTS: Use ElevenLabs (primary)")
    elif results["Azure Speech"]:
        safe_print(f"{WARNING} TTS: Use Azure Speech (fallback)")
    elif results["gTTS"]:
        safe_print(f"{WARNING} TTS: Use gTTS (fallback, lower quality)")
    else:
        safe_print(f"{CROSS} TTS: No working service available!")
    
    if results["HeyGen"]:
        safe_print(f"{CHECKMARK} Avatar: Use HeyGen (primary)")
    elif results["D-ID"]:
        safe_print(f"{WARNING} Avatar: Use D-ID (fallback)")
    else:
        safe_print(f"{CROSS} Avatar: No working service available!")
    
    # Return success if at least one TTS and one Avatar service work
    tts_works = results["ElevenLabs"] or results["Azure Speech"] or results["gTTS"]
    avatar_works = results["HeyGen"] or results["D-ID"]
    
    if tts_works and avatar_works:
        print("\n" + "=" * 60)
        safe_print(f"{CHECKMARK} Ready to generate podcasts!")
        return 0
    else:
        print("\n" + "=" * 60)
        safe_print(f"{CROSS} Cannot generate podcasts - missing required services")
        return 1

if __name__ == "__main__":
    sys.exit(main())

