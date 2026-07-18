"""
Start webhook server for receiving API callbacks.

Run this in a separate terminal before generating videos.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.webhook_server import get_webhook_server
from src.utils.console_output import safe_print

def main():
    """Start webhook server."""
    safe_print("="*60)
    safe_print("Starting Webhook Server")
    safe_print("="*60)
    
    server = get_webhook_server(port=5000)
    
    try:
        server.start_flask_server()
        base_url = server.get_base_url()
        
        safe_print(f"\n[OK] Webhook server started!")
        safe_print(f"Base URL: {base_url}")
        safe_print(f"\nEndpoints:")
        safe_print(f"  - HeyGen: {base_url}/webhooks/heygen/video/<video_id>")
        safe_print(f"  - D-ID:   {base_url}/webhooks/did/talk/<talk_id>")
        safe_print(f"  - Health:  {base_url}/health")
        safe_print(f"\n[INFO] Server is running. Press Ctrl+C to stop.")
        safe_print(f"[INFO] For external access, use ngrok:")
        safe_print(f"       ngrok http 5000")
        
        # Keep server running
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        safe_print("\n[INFO] Stopping webhook server...")
        server.stop()
        safe_print("[OK] Server stopped")
    except Exception as e:
        safe_print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

