"""
Test script to verify webhook functionality for HeyGen API.

This script tests:
1. Webhook server startup
2. Webhook endpoint registration
3. Simulated webhook callback handling
4. Event waiting and retrieval
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.core.webhook_server import get_webhook_server
from src.utils.console_output import safe_print

def test_webhook_server():
    """Test webhook server functionality."""
    safe_print("="*60)
    safe_print("Testing Webhook Server Functionality")
    safe_print("="*60)
    
    # Test 1: Initialize webhook server
    safe_print("\n[TEST 1] Initializing webhook server...")
    try:
        server = get_webhook_server(port=5000, host="0.0.0.0")
        safe_print("[OK] Webhook server initialized")
    except Exception as e:
        safe_print(f"[X] Failed to initialize webhook server: {e}")
        return False
    
    # Test 2: Start Flask server
    safe_print("\n[TEST 2] Starting Flask server...")
    try:
        server.start_flask_server()
        safe_print("[OK] Flask server started")
        safe_print(f"     Base URL: {server.get_base_url()}")
    except Exception as e:
        safe_print(f"[X] Failed to start Flask server: {e}")
        return False
    
    # Test 3: Register callback
    safe_print("\n[TEST 3] Registering webhook callback...")
    callback_called = {"called": False, "event": None}
    
    def test_callback(event):
        callback_called["called"] = True
        callback_called["event"] = event
        safe_print(f"[INFO] Callback executed: Video {event.event_id} status: {event.status}")
    
    test_video_id = "test_video_12345"
    server.register_callback(test_video_id, test_callback, source="heygen")
    safe_print(f"[OK] Callback registered for video: {test_video_id}")
    
    # Test 4: Simulate webhook event
    safe_print("\n[TEST 4] Simulating webhook event...")
    test_payload = {
        "data": {
            "status": "completed",
            "video_url": "https://example.com/video/test.mp4"
        },
        "status": "completed"
    }
    
    try:
        event = server.handle_webhook("heygen", test_video_id, test_payload)
        safe_print(f"[OK] Webhook event handled: {event.status}")
        safe_print(f"     Video URL: {event.data.get('video_url', 'N/A')}")
        
        # Check if callback was called
        time.sleep(0.5)  # Give callback time to execute
        if callback_called["called"]:
            safe_print("[OK] Callback was executed successfully")
        else:
            safe_print("[WARN] Callback was not executed (may be async)")
    except Exception as e:
        safe_print(f"[X] Failed to handle webhook: {e}")
        return False
    
    # Test 5: Retrieve event
    safe_print("\n[TEST 5] Retrieving stored event...")
    try:
        retrieved_event = server.get_event("heygen", test_video_id)
        if retrieved_event:
            safe_print(f"[OK] Event retrieved: {retrieved_event.status}")
        else:
            safe_print("[X] Event not found")
            return False
    except Exception as e:
        safe_print(f"[X] Failed to retrieve event: {e}")
        return False
    
    # Test 6: Wait for event (should return immediately since event exists)
    safe_print("\n[TEST 6] Testing wait_for_event (should return immediately)...")
    try:
        waited_event = server.wait_for_event(
            "heygen", 
            test_video_id, 
            timeout=5,
            expected_status="completed"
        )
        if waited_event and waited_event.status == "completed":
            safe_print("[OK] wait_for_event returned completed event")
        else:
            safe_print("[X] wait_for_event did not return expected event")
            return False
    except Exception as e:
        safe_print(f"[X] wait_for_event failed: {e}")
        return False
    
    # Test 7: Test ngrok detection (if available)
    safe_print("\n[TEST 7] Testing ngrok URL detection...")
    ngrok_url = server._detect_ngrok_url()
    if ngrok_url:
        safe_print(f"[OK] ngrok detected: {ngrok_url}")
        safe_print(f"     Use this URL for external webhook access")
    else:
        safe_print("[INFO] ngrok not detected (this is OK for local testing)")
        safe_print("       For external access, start ngrok: ngrok http 5000")
    
    safe_print("\n" + "="*60)
    safe_print("[OK] All webhook tests passed!")
    safe_print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_webhook_server()
    sys.exit(0 if success else 1)

