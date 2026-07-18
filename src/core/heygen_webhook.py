"""
HeyGen Webhook Handler

Handles webhook callbacks from HeyGen API for video status updates.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass
from threading import Lock
import logging

logger = logging.getLogger(__name__)


@dataclass
class HeyGenWebhookEvent:
    """HeyGen webhook event data."""
    video_id: str
    status: str  # "completed", "failed", "processing", etc.
    video_url: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[float] = None


class HeyGenWebhookHandler:
    """
    Handles HeyGen webhook callbacks for video status updates.
    
    This allows HeyGen to notify us when videos are ready instead of polling.
    """
    
    def __init__(self, callback_base_url: Optional[str] = None):
        """
        Initialize webhook handler.
        
        Args:
            callback_base_url: Base URL for webhook callbacks (e.g., "https://your-domain.com")
                              If None, webhooks will not be used
        """
        self.callback_base_url = callback_base_url
        self.pending_videos: Dict[str, HeyGenWebhookEvent] = {}
        self.completed_videos: Dict[str, HeyGenWebhookEvent] = {}
        self.lock = Lock()
        self.callbacks: Dict[str, Callable[[HeyGenWebhookEvent], None]] = {}
        
    def get_callback_url(self, video_id: str) -> Optional[str]:
        """
        Get callback URL for a video generation request.
        
        Args:
            video_id: Video ID (can be placeholder, will be replaced by HeyGen)
            
        Returns:
            Callback URL or None if webhooks not configured
        """
        if not self.callback_base_url:
            return None
        
        # HeyGen will POST to this URL when video is ready
        callback_path = f"/webhooks/heygen/video/{video_id}"
        return f"{self.callback_base_url.rstrip('/')}{callback_path}"
    
    def register_callback(self, video_id: str, callback: Callable[[HeyGenWebhookEvent], None]):
        """
        Register a callback function for a specific video.
        
        Args:
            video_id: Video ID to watch
            callback: Function to call when video status updates
        """
        with self.lock:
            self.callbacks[video_id] = callback
    
    def handle_webhook(self, video_id: str, payload: Dict[str, Any]) -> HeyGenWebhookEvent:
        """
        Handle incoming webhook from HeyGen.
        
        This should be called by your web server when receiving POST from HeyGen.
        
        Args:
            video_id: Video ID from the webhook URL
            payload: JSON payload from HeyGen
            
        Returns:
            HeyGenWebhookEvent with status information
        """
        # Parse HeyGen webhook payload
        # Format may vary, but typically includes:
        # - status: "completed", "failed", "processing"
        # - video_url: URL to download video (when completed)
        # - error: Error message (when failed)
        
        data = payload.get("data", payload)
        status = data.get("status") or payload.get("status", "unknown")
        video_url = (
            data.get("video_url")
            or data.get("url")
            or payload.get("video_url")
            or payload.get("url")
        )
        error = data.get("error") or payload.get("error")
        
        event = HeyGenWebhookEvent(
            video_id=video_id,
            status=status,
            video_url=video_url,
            error=error,
            timestamp=time.time()
        )
        
        with self.lock:
            if status in ["completed", "done"]:
                self.completed_videos[video_id] = event
                if video_id in self.pending_videos:
                    del self.pending_videos[video_id]
            elif status in ["failed", "error"]:
                self.completed_videos[video_id] = event
                if video_id in self.pending_videos:
                    del self.pending_videos[video_id]
            else:
                self.pending_videos[video_id] = event
            
            # Call registered callback if exists
            if video_id in self.callbacks:
                try:
                    self.callbacks[video_id](event)
                except Exception as e:
                    logger.error(f"Error in webhook callback for {video_id}: {e}")
        
        return event
    
    def wait_for_video(self, video_id: str, timeout: float = 300.0, poll_interval: float = 1.0) -> Optional[HeyGenWebhookEvent]:
        """
        Wait for a video to complete (webhook or polling fallback).
        
        Args:
            video_id: Video ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between checks in seconds
            
        Returns:
            HeyGenWebhookEvent when video completes, None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.lock:
                if video_id in self.completed_videos:
                    return self.completed_videos[video_id]
            
            time.sleep(poll_interval)
        
        return None
    
    def get_video_status(self, video_id: str) -> Optional[HeyGenWebhookEvent]:
        """
        Get current status of a video.
        
        Args:
            video_id: Video ID to check
            
        Returns:
            HeyGenWebhookEvent if found, None otherwise
        """
        with self.lock:
            if video_id in self.completed_videos:
                return self.completed_videos[video_id]
            elif video_id in self.pending_videos:
                return self.pending_videos[video_id]
        return None


# Flask/FastAPI webhook endpoint example
"""
Example Flask endpoint:

from flask import Flask, request, jsonify
from src.core.heygen_webhook import HeyGenWebhookHandler

app = Flask(__name__)
webhook_handler = HeyGenWebhookHandler(callback_base_url="https://your-domain.com")

@app.route('/webhooks/heygen/video/<video_id>', methods=['POST'])
def heygen_webhook(video_id):
    payload = request.json
    event = webhook_handler.handle_webhook(video_id, payload)
    return jsonify({"status": "received"}), 200

Example FastAPI endpoint:

from fastapi import FastAPI, Request
from src.core.heygen_webhook import HeyGenWebhookHandler

app = FastAPI()
webhook_handler = HeyGenWebhookHandler(callback_base_url="https://your-domain.com")

@app.post("/webhooks/heygen/video/{video_id}")
async def heygen_webhook(video_id: str, request: Request):
    payload = await request.json()
    event = webhook_handler.handle_webhook(video_id, payload)
    return {"status": "received"}
"""

