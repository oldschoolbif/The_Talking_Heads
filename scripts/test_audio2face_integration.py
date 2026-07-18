"""
Test Audio2Face Integration

Tests the Audio2Face provider to verify it's working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.audio2face_provider import Audio2FaceProvider
import yaml


def test_audio2face_availability():
    """Test if Audio2Face is available."""
    print("=== Testing Audio2Face Availability ===\n")
    
    # Load config
    config_path = project_root / "config" / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Create provider
    provider = Audio2FaceProvider(config)
    
    # Check availability
    print("1. Checking Audio2Face availability...")
    is_available = provider.is_available()
    
    if is_available:
        print("   [OK] Audio2Face is available!")
        print(f"   [PATH] Omniverse path: {provider.omniverse_path}")
        print(f"   [PATH] Output dir: {provider.output_dir}")
    else:
        print("   [FAIL] Audio2Face is NOT available")
        print("\n   Troubleshooting:")
        print("   1. Is Audio2Face installed?")
        print("   2. Is py_audio2face installed? (pip install py-audio2face)")
        print("   3. Is Audio2Face headless server running?")
        print("   4. Is Omniverse installed?")
    
    return is_available


def test_py_audio2face():
    """Test py_audio2face package."""
    print("\n2. Testing py_audio2face package...")
    
    try:
        from py_audio2face import Audio2FaceClient
        print("   [OK] py_audio2face is installed")
        
        # Try to create client
        try:
            client = Audio2FaceClient(server_url="http://localhost:8000")
            print("   [OK] Can create Audio2FaceClient")
            print("   [INFO] Server URL: http://localhost:8000")
        except Exception as e:
            print(f"   [WARN] Cannot connect to server: {e}")
            print("   [INFO] Make sure Audio2Face headless server is running")
        
        return True
    except ImportError:
        print("   [FAIL] py_audio2face is NOT installed")
        print("   [INFO] Install with: pip install py-audio2face")
        return False


def test_omniverse_api():
    """Test Omniverse Python API."""
    print("\n3. Testing Omniverse Python API...")
    
    try:
        import sys
        from pathlib import Path
        
        # Try to find Omniverse paths
        appdata = Path.home() / "AppData" / "Local" / "ov" / "pkg"
        if not appdata.exists():
            appdata = Path(os.getenv('LOCALAPPDATA', '')) / "ov" / "pkg"
        
        if appdata.exists():
            print(f"   [OK] Found Omniverse at: {appdata}")
            
            # Try importing
            try:
                import omni.audio2face as a2f
                print("   [OK] Can import omni.audio2face")
                return True
            except ImportError as e:
                print(f"   [WARN] Cannot import omni.audio2face: {e}")
                print("   [INFO] Audio2Face extension may not be installed")
        else:
            print("   [FAIL] Omniverse not found")
            print("   [INFO] Install Omniverse or Audio2Face standalone")
        
        return False
    except Exception as e:
        print(f"   [FAIL] Error checking Omniverse: {e}")
        return False


def main():
    """Run all tests."""
    print("Audio2Face Integration Test\n")
    print("=" * 50)
    
    # Test 1: Provider availability
    available = test_audio2face_availability()
    
    # Test 2: py_audio2face
    py_a2f_available = test_py_audio2face()
    
    # Test 3: Omniverse API
    omniverse_available = test_omniverse_api()
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Audio2Face Provider: {'[OK] Available' if available else '[FAIL] Not Available'}")
    print(f"  py_audio2face: {'[OK] Installed' if py_a2f_available else '[FAIL] Not Installed'}")
    print(f"  Omniverse API: {'[OK] Available' if omniverse_available else '[FAIL] Not Available'}")
    
    if available:
        print("\n[OK] Audio2Face integration is ready!")
        print("\nNext steps:")
        print("1. Ensure Audio2Face headless server is running (if using py_audio2face)")
        print("2. Configure character USD files in config")
        print("3. Test generation with a sample audio file")
    else:
        print("\n[FAIL] Audio2Face integration needs setup")
        print("\nTo set up:")
        print("1. Install Audio2Face: https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html")
        print("2. Install py_audio2face: pip install py-audio2face")
        print("3. Start Audio2Face headless server (if available)")
        print("4. Run this test again")


if __name__ == "__main__":
    import os
    main()

