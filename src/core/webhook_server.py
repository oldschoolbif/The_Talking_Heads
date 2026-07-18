"""
Webhook Server for External API Callbacks

Handles webhook callbacks from HeyGen and other APIs for real-time status updates.
"""

import threading
import time
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class WebhookEvent:
    """Webhook event data."""
    source: str  # "heygen", "did", etc.
    event_id: str  # video_id, talk_id, etc.
    status: str  # "completed", "failed", "processing", etc.
    data: Dict[str, Any]  # Additional event data
    timestamp: float


class WebhookServer:
    """
    Simple webhook server for receiving API callbacks.
    
    This can be used with Flask/FastAPI or run standalone.
    """
    
    def __init__(self, port: int = 5000, host: str = "0.0.0.0"):
        """
        Initialize webhook server.
        
        Args:
            port: Port to listen on
            host: Host to bind to
        """
        self.port = port
        self.host = host
        self.events: Dict[str, WebhookEvent] = {}
        self.callbacks: Dict[str, Callable[[WebhookEvent], None]] = {}
        self.lock = threading.Lock()
        self._server_thread: Optional[threading.Thread] = None
        self._app = None
        self._running = False
        
    def get_base_url(self) -> str:
        """
        Get base URL for webhook callbacks.
        
        Returns:
            Base URL (for localhost or ngrok)
        """
        # Check if ngrok is running
        ngrok_url = self._detect_ngrok_url()
        if ngrok_url:
            return ngrok_url
        
        # Default to localhost (requires ngrok for external access)
        return f"http://localhost:{self.port}"
    
    def _detect_ngrok_url(self) -> Optional[str]:
        """Try to detect ngrok URL."""
        try:
            import requests
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get("tunnels", [])
                for tunnel in tunnels:
                    if tunnel.get("proto") == "https":
                        return tunnel.get("public_url", "").rstrip("/")
        except Exception:
            pass
        return None
    
    def register_callback(self, event_id: str, callback: Callable[[WebhookEvent], None], source: str = "heygen"):
        """
        Register a callback for a specific event.
        
        Args:
            event_id: Event ID (video_id, talk_id, etc.)
            source: Event source ("heygen", "did", etc.)
            callback: Function to call when event received
        """
        key = f"{source}:{event_id}"
        with self.lock:
            self.callbacks[key] = callback
    
    def handle_webhook(self, source: str, event_id: str, payload: Dict[str, Any]) -> WebhookEvent:
        """
        Handle incoming webhook.
        
        Args:
            source: Source of webhook ("heygen", "did", etc.)
            event_id: Event ID from payload or URL
            payload: Webhook payload
            
        Returns:
            WebhookEvent
        """
        # Parse payload based on source
        if source == "heygen":
            status = payload.get("data", {}).get("status") or payload.get("status", "unknown")
            video_url = (
                payload.get("data", {}).get("video_url")
                or payload.get("data", {}).get("url")
                or payload.get("video_url")
                or payload.get("url")
            )
            error = payload.get("data", {}).get("error") or payload.get("error")
            
            event = WebhookEvent(
                source=source,
                event_id=event_id,
                status=status,
                data={
                    "video_url": video_url,
                    "error": error,
                    **payload
                },
                timestamp=time.time()
            )
        else:
            # Generic event
            event = WebhookEvent(
                source=source,
                event_id=event_id,
                status=payload.get("status", "unknown"),
                data=payload,
                timestamp=time.time()
            )
        
        with self.lock:
            self.events[f"{source}:{event_id}"] = event
            
            # Call registered callback
            key = f"{source}:{event_id}"
            if key in self.callbacks:
                try:
                    self.callbacks[key](event)
                except Exception as e:
                    logger.error(f"Error in webhook callback for {key}: {e}")
        
        return event
    
    def get_event(self, source: str, event_id: str) -> Optional[WebhookEvent]:
        """Get event by source and ID."""
        key = f"{source}:{event_id}"
        with self.lock:
            return self.events.get(key)
    
    def wait_for_event(
        self, 
        source: str, 
        event_id: str, 
        timeout: float = 300.0, 
        poll_interval: float = 1.0,
        expected_status: Optional[str] = None
    ) -> Optional[WebhookEvent]:
        """
        Wait for a webhook event.
        
        Args:
            source: Event source
            event_id: Event ID
            timeout: Maximum time to wait
            poll_interval: Time between checks
            expected_status: Expected status (e.g., "completed")
            
        Returns:
            WebhookEvent if received, None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            event = self.get_event(source, event_id)
            if event:
                if expected_status is None or event.status == expected_status:
                    return event
            time.sleep(poll_interval)
        
        return None
    
    def start_flask_server(self):
        """Start Flask webhook server."""
        try:
            from flask import Flask, request, jsonify
        except ImportError:
            raise RuntimeError("Flask not installed. Install with: pip install flask")
        
        app = Flask(__name__)
        
        @app.route('/webhooks/heygen/video/<video_id>', methods=['POST'])
        def heygen_webhook(video_id: str):
            """Handle HeyGen webhook."""
            payload = request.json or {}
            event = self.handle_webhook("heygen", video_id, payload)
            logger.info(f"HeyGen webhook received for {video_id}: {event.status}")
            return jsonify({"status": "received", "event_id": video_id}), 200
        
        @app.route('/webhooks/did/talk/<talk_id>', methods=['POST'])
        def did_webhook(talk_id: str):
            """Handle D-ID webhook."""
            payload = request.json or {}
            event = self.handle_webhook("did", talk_id, payload)
            logger.info(f"D-ID webhook received for {talk_id}: {event.status}")
            return jsonify({"status": "received", "event_id": talk_id}), 200
        
        @app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({"status": "ok", "events": len(self.events)}), 200
        
        self._app = app
        self._running = True
        
        def run_server():
            app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
        
        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(1)
        
        logger.info(f"Webhook server started on http://{self.host}:{self.port}")
        
    def stop(self):
        """Stop webhook server."""
        self._running = False
        # Flask server will stop when main thread exits (daemon thread)


# Global webhook server instance
_webhook_server: Optional[WebhookServer] = None


def get_webhook_server(port: int = 5000, host: str = "0.0.0.0") -> WebhookServer:
    """
    Get or create global webhook server instance.
    
    Args:
        port: Port to listen on
        host: Host to bind to
        
    Returns:
        WebhookServer instance
    """
    global _webhook_server
    if _webhook_server is None:
        _webhook_server = WebhookServer(port=port, host=host)
    return _webhook_server

