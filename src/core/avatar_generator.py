"""
Avatar Generator for The Talking Heads

Generates animated avatar videos for personas using HeyGen or D-ID APIs.
"""

import os
import time
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.persona_engine import Persona
from src.core.tts_engine import AudioSegment
from src.core.script_parser import ScriptSegment
from src.core.avatar_provider_base import AvatarProvider
from src.core.dreamtalk_provider import DreamTalkProvider
from src.core.audio2face_provider import Audio2FaceProvider
from src.core.sadtalker_provider import SadTalkerProvider
from src.core.tddfa_provider import TDDFAProvider
from src.core.tddfa_a2f_provider import TDDFA_A2FProvider
# HeyGem disabled - using Audio2Face instead
# from src.core.heygem_provider import HeyGemProvider


@dataclass
class AvatarVideo:
    """Represents a generated avatar video with metadata."""

    segment: ScriptSegment
    video_path: Path
    duration: float  # Duration in seconds
    provider: str  # Avatar provider used
    persona: str
    expression: Optional[str] = None
    gesture: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert avatar video to dictionary."""
        return {
            "segment": self.segment.to_dict(),
            "video_path": str(self.video_path),
            "duration": self.duration,
            "provider": self.provider,
            "persona": self.persona,
            "expression": self.expression,
            "gesture": self.gesture,
        }


# AvatarProvider is now imported from avatar_provider_base.py to avoid circular imports


class HeyGenProvider(AvatarProvider):
    """HeyGen API provider for avatar generation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize HeyGen provider."""
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("HEYGEN_API_KEY")
        # Try v2 first, fallback to v1 if needed
        self.base_url = config.get("base_url", "https://api.heygen.com/v2")
        self._client = None

    def is_available(self) -> bool:
        """Check if HeyGen is available."""
        if not self.api_key:
            return False
        try:
            import requests
            return True
        except ImportError:
            return False

    def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            import requests
            self._client = requests
        return self._client

    def generate(
        self, audio_path: Path, avatar_id: str, expression: Optional[str] = None, gesture: Optional[str] = None, text: Optional[str] = None, **kwargs
    ) -> tuple[Path, float]:
        """
        Generate avatar video using HeyGen API.

        Args:
            audio_path: Path to audio file (used for duration estimation, not uploaded)
            avatar_id: HeyGen avatar ID
            expression: Expression to apply
            gesture: Gesture to apply
            text: Text to speak (required for HeyGen v2 API)
            **kwargs: Additional parameters

        Returns:
            Tuple of (video_path, duration_seconds)

        Raises:
            ValueError: If API key is missing or inputs are invalid
            RuntimeError: If API request fails with detailed error information
            requests.exceptions.RequestException: For network-related errors
        """
        # Input validation with detailed error messages
        if not self.api_key:
            raise ValueError("HeyGen API key is required. Set HEYGEN_API_KEY environment variable or configure in config.yaml")

        if not self.is_available():
            raise RuntimeError("HeyGen provider is not available. Install 'requests' package: pip install requests")

        if not audio_path or not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_path}. Ensure the file exists and path is correct.")

        if not text or not text.strip():
            raise ValueError(
                f"HeyGen v2 API requires 'text' parameter for video generation. "
                f"Got: '{text}' (type: {type(text)}). "
                f"Text must be a non-empty string."
            )
        
        if not avatar_id or not avatar_id.strip():
            raise ValueError(f"Avatar ID is required. Got: '{avatar_id}'. Use a valid HeyGen avatar ID.")

        text_input = text.strip()
        requests = self._get_client()
        headers = {"X-Api-Key": self.api_key, "Content-Type": "application/json"}

        # Retry logic for transient errors
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # HeyGen v2 format: video_inputs is an array
                # HeyGen v2: voice field should be one of: text, audio, or silence
                # Since we have text, use type: "text" with voice_id
                voice_id = kwargs.get("voice_id") or "e0cc82c22f414c95b1f25696c732f058"  # Default: Cassidy
                
                # Get resolution from config (default to 720p for faster processing)
                avatar_config = self.config.get("avatar", {})
                resolution_config = avatar_config.get("resolution", {})
                video_width = kwargs.get("width") or resolution_config.get("width", 1280)  # Default 720p
                video_height = kwargs.get("height") or resolution_config.get("height", 720)  # Default 720p
                
                payload = {
                    "video_inputs": [
                        {
                            "character": {
                                "type": "avatar",
                                "avatar_id": avatar_id,
                                "avatar_style": "normal"
                            },
                            "voice": {
                                "type": "text",
                                "input_text": text_input,
                                "voice_id": voice_id,
                                "speed": 1.0
                            }
                        }
                    ],
                    "dimension": {
                        "width": video_width,
                        "height": video_height
                    }
                }
                
                # Add callback_url if provided (webhook support)
                # HeyGen will POST to this URL when video is ready
                webhook_server = kwargs.get("webhook_server")
                callback_url = kwargs.get("callback_url")
                
                # Note: We'll generate callback URL after we get the video_id
                # HeyGen requires the actual video_id in the callback URL
                
                if callback_url:
                    payload["callback_url"] = callback_url
                    print(f"[INFO] Using webhook callback: {callback_url}")
                
                # Add expression if supported
                if expression and expression != "neutral":
                    payload["video_inputs"][0]["expression"] = expression
                
                # Add gesture if supported
                if gesture and gesture != "none":
                    payload["video_inputs"][0]["gesture"] = gesture

                # Make API request with comprehensive error handling
                try:
                    response = requests.post(
                        f"{self.base_url}/video/generate",
                        headers=headers,
                        json=payload,
                        timeout=60
                    )
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        print(f"[WARN] HeyGen API timeout (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    raise RuntimeError(
                        f"HeyGen API request timed out after {max_retries} attempts. "
                        f"This may indicate the HeyGen API service is slow or unavailable. "
                        f"Check HeyGen API status at https://status.heygen.com or try again later."
                    )
                except requests.exceptions.ConnectionError as e:
                    if attempt < max_retries - 1:
                        print(f"[WARN] HeyGen API connection error (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    raise RuntimeError(
                        f"HeyGen API connection failed after {max_retries} attempts: {str(e)}. "
                        f"This may indicate the HeyGen API service is unavailable or experiencing issues. "
                        f"Check HeyGen API status at https://status.heygen.com or try again later."
                    )
                except requests.exceptions.RequestException as e:
                    raise RuntimeError(
                        f"HeyGen API request failed: {str(e)}. "
                        f"This may indicate the HeyGen API service is experiencing issues. "
                        f"Check HeyGen API status at https://status.heygen.com or try again later."
                    )
                
                # Handle HTTP response codes with detailed error messages
                if response.status_code == 401:
                    raise RuntimeError(
                        "HeyGen API authentication failed (401 Unauthorized). "
                        f"Check that your API key is correct. Key starts with: {self.api_key[:10] if self.api_key else 'None'}..."
                    )
                elif response.status_code == 403:
                    raise RuntimeError(
                        "HeyGen API access forbidden (403 Forbidden). "
                        "Your API key may not have permission for this operation or your subscription may be insufficient."
                    )
                elif response.status_code == 404:
                    raise RuntimeError(
                        f"HeyGen API endpoint not found (404 Not Found): {self.base_url}/video/generate. "
                        "The API endpoint may have changed. Check HeyGen API documentation for the latest endpoint."
                    )
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", retry_delay)
                    if attempt < max_retries - 1:
                        wait_time = int(retry_after) if retry_after.isdigit() else retry_delay
                        print(f"[WARN] HeyGen API rate limited (429), waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                        retry_delay *= 2
                        continue
                    raise RuntimeError(
                        "HeyGen API rate limit exceeded (429 Too Many Requests). "
                        "Wait before making more requests or upgrade your subscription plan."
                    )
                elif response.status_code == 500:
                    if attempt < max_retries - 1:
                        print(f"[WARN] HeyGen API server error (500), retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    raise RuntimeError(
                        "HeyGen API server error (500 Internal Server Error). "
                        "This is a temporary issue on HeyGen's side. Please try again later."
                    )
                elif response.status_code not in [200, 201, 202]:
                    # Try to extract detailed error message
                    error_msg = f"HTTP {response.status_code}"
                    error_details = None
                    
                    try:
                        error_data = response.json()
                        if isinstance(error_data, dict):
                            error_msg = error_data.get("error", {}).get("message", str(error_data.get("error", error_msg)))
                            error_details = error_data.get("error", {}).get("details", error_data.get("details"))
                        else:
                            error_msg = str(error_data)
                    except (ValueError, KeyError, AttributeError):
                        error_msg = response.text[:500] if response.text else error_msg
                    
                    error_message = f"HeyGen API error ({response.status_code}): {error_msg}"
                    if error_details:
                        error_message += f"\nDetails: {error_details}"
                    
                    # For 400 errors, provide more context
                    if response.status_code == 400:
                        error_message += (
                            f"\n\nCommon causes:"
                            f"\n- Invalid avatar_id: '{avatar_id}'"
                            f"\n- Invalid voice_id: '{voice_id}'"
                            f"\n- Text too long or contains invalid characters"
                            f"\n- Missing required fields in payload"
                        )
                    
                    raise RuntimeError(error_message)

                # Parse response with error handling
                try:
                    task_data = response.json()
                except ValueError as e:
                    raise RuntimeError(
                        f"HeyGen API returned invalid JSON response: {str(e)}. "
                        f"Response text: {response.text[:200]}"
                    )
                
                # Check for API-level errors in response
                if task_data.get("error") is not None:
                    error_info = task_data.get("error", {})
                    if isinstance(error_info, dict):
                        error_msg = error_info.get("message", str(error_info))
                        error_code = error_info.get("code", "unknown")
                        raise RuntimeError(
                            f"HeyGen API error (code: {error_code}): {error_msg}"
                        )
                    else:
                        raise RuntimeError(f"HeyGen API error: {error_info}")
                
                # Extract video_id from response
                data = task_data.get("data", {})
                task_id = data.get("video_id")
                
                if not task_id:
                    # Try alternative locations
                    task_id = (
                        data.get("id")
                        or task_data.get("video_id")
                        or task_data.get("id")
                    )

                if not task_id:
                    raise RuntimeError(
                        f"HeyGen API did not return video_id in response. "
                        f"Response structure: {json.dumps(task_data, indent=2)[:500]}"
                    )

                # Report progress: Video creation request submitted (include resolution info)
                resolution_str = f"{video_width}x{video_height}"
                self._report_progress(f"HeyGen: Video creation request submitted (ID: {task_id[:8]}..., {resolution_str})", 0.1)

                # Register webhook callback if server is available
                webhook_server = kwargs.get("webhook_server")
                if webhook_server:
                    # Generate callback URL with actual video_id
                    base_url = webhook_server.get_base_url()
                    callback_url = f"{base_url}/webhooks/heygen/video/{task_id}"
                    
                    # Register callback for this video_id
                    def on_video_ready(event):
                        print(f"[INFO] HeyGen webhook: Video {event.event_id} status: {event.status}")
                    
                    webhook_server.register_callback(task_id, on_video_ready, source="heygen")
                    print(f"[INFO] Registered webhook callback for video {task_id} at {callback_url}")
                    
                    # Note: For future requests, we can include callback_url in the initial payload
                    # For now, HeyGen will use webhooks if configured on their side
                
                # Use webhook if available, otherwise poll
                if webhook_server:
                    # Try webhook first - wait for callback with progress updates
                    self._report_progress(f"HeyGen: Waiting for webhook callback (ID: {task_id[:8]}...)", 0.2)
                    print(f"[INFO] Waiting for HeyGen webhook callback for video {task_id}...")
                    print(f"[INFO] Webhook endpoint: {callback_url}")
                    
                    # Wait for webhook with periodic progress updates
                    import time as time_module
                    webhook_timeout = min(60, kwargs.get("max_wait", 1200))  # Max 60s for webhook, then fallback to polling
                    self._report_progress(f"HeyGen: Starting webhook wait (timeout: {webhook_timeout}s)...", 0.2)
                    start_time = time_module.time()
                    event = None
                    last_update_time = -1
                    
                    while time_module.time() - start_time < webhook_timeout:
                        event = webhook_server.get_event("heygen", task_id)
                        if event and event.status == "completed":
                            break
                        
                        elapsed = time_module.time() - start_time
                        elapsed_int = int(elapsed)
                        
                        # Update every 5 seconds
                        if elapsed_int > 0 and elapsed_int % 5 == 0 and elapsed_int != last_update_time:
                            last_update_time = elapsed_int
                            progress_pct = min(0.2 + (elapsed / webhook_timeout) * 0.3, 0.5)
                            self._report_progress(f"HeyGen: Still waiting for webhook... ({elapsed_int}s elapsed)", progress_pct)
                        
                        time_module.sleep(1)
                    
                    # Check if we timed out
                    elapsed_final = time_module.time() - start_time
                    if elapsed_final >= webhook_timeout and (not event or event.status != "completed"):
                        self._report_progress(f"HeyGen: Webhook wait completed ({int(elapsed_final)}s), checking result...", 0.5)
                    
                    # If webhook didn't arrive, fall through to polling
                    if event and event.status == "completed":
                        video_url = event.data.get("video_url")
                        if video_url:
                            print(f"[OK] HeyGen video ready via webhook: {video_url[:50]}...")
                        else:
                            # Fallback to polling if webhook doesn't have URL
                            print("[WARN] Webhook event missing video_url, falling back to polling...")
                            video_url = self._poll_task_status(task_id, requests, max_wait=kwargs.get("max_wait", 1200), progress_callback=self.progress_callback, webhook_server=webhook_server)
                    elif event and event.status in ["failed", "error"]:
                        error = event.data.get("error", "Unknown error")
                        raise RuntimeError(f"HeyGen video generation failed: {error}")
                    else:
                        # Webhook timeout - fallback to polling
                        self._report_progress(f"HeyGen: Webhook timeout after 30s, falling back to polling...", 0.5)
                        print(f"[WARN] Webhook timeout, falling back to polling for video {task_id}...")
                        video_url = self._poll_task_status(task_id, requests, max_wait=kwargs.get("max_wait", 1200), progress_callback=self.progress_callback, webhook_server=webhook_server)
                else:
                    # Fallback to polling
                    self._report_progress(f"HeyGen: Polling for video status (ID: {task_id[:8]}...)", 0.2)
                    try:
                        video_url = self._poll_task_status(task_id, requests, max_wait=kwargs.get("max_wait", 1200), progress_callback=self.progress_callback, webhook_server=webhook_server)
                    except RuntimeError as e:
                        raise RuntimeError(
                            f"HeyGen video generation failed during polling: {str(e)}. "
                            f"Video ID: {task_id}. "
                            f"Consider using webhooks for more reliable status updates."
                        )

                if not video_url:
                    raise RuntimeError(
                        f"HeyGen polling completed but no video URL was returned. "
                        f"Video ID: {task_id}"
                    )

                # Download video with error handling
                self._report_progress(f"HeyGen: Downloading video...", 0.9)
                try:
                    video_response = requests.get(video_url, timeout=300, stream=True)
                    video_response.raise_for_status()
                except requests.exceptions.Timeout:
                    raise RuntimeError(
                        f"Timeout downloading HeyGen video from {video_url}. "
                        f"The video URL may have expired or the download is too large."
                    )
                except requests.exceptions.RequestException as e:
                    raise RuntimeError(
                        f"Failed to download HeyGen video from {video_url}: {str(e)}. "
                        f"Video may have expired or URL is invalid."
                    )

                # Save video to temporary location with error handling
                output_path = kwargs.get("output_path")
                if not output_path:
                    output_path = audio_path.parent / f"{audio_path.stem}_avatar.mp4"
                else:
                    output_path = Path(output_path)

                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    # Write video content with progress
                    total_size = int(video_response.headers.get('content-length', 0))
                    downloaded = 0
                    with open(output_path, "wb") as f:
                        for chunk in video_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0 and downloaded % (1024 * 1024) == 0:  # Report every MB
                                    progress = 0.9 + (downloaded / total_size) * 0.1
                                    self._report_progress(f"HeyGen: Downloading... {downloaded / 1024 / 1024:.1f} MB", progress)
                except IOError as e:
                    raise RuntimeError(
                        f"Failed to save HeyGen video to {output_path}: {str(e)}. "
                        f"Check disk space and file permissions."
                    )

                # Estimate duration (use audio duration if available)
                duration = kwargs.get("duration", 0.0)
                if duration == 0.0:
                    # Try to get duration from video file or estimate
                    try:
                        from pydub import AudioSegment
                        audio_seg = AudioSegment.from_file(str(audio_path))
                        duration = len(audio_seg) / 1000.0
                    except Exception:
                        # Fallback: estimate based on file size (very rough)
                        file_size = output_path.stat().st_size
                        duration = max(1.0, file_size / 1000000.0)  # Rough estimate: 1MB per second

                return output_path, duration
                
            except RuntimeError:
                # Re-raise RuntimeErrors as-is (they already have detailed messages)
                raise
            except ValueError as e:
                # Re-raise ValueErrors as-is
                raise
            except Exception as e:
                # Wrap unexpected errors with context
                error_type = type(e).__name__
                raise RuntimeError(
                    f"Unexpected error in HeyGen video generation ({error_type}): {str(e)}. "
                    f"Avatar ID: {avatar_id}, Text length: {len(text_input)}. "
                    f"Check HeyGen API status and your configuration."
                ) from e
        
        # If we get here, all retries failed
        raise RuntimeError(f"HeyGen API request failed after {max_retries} attempts")

    def _poll_task_status(self, task_id: str, requests, max_wait: int = 1200, poll_interval: int = 5, progress_callback: Optional[callable] = None, webhook_server=None) -> str:
        """
        Poll HeyGen API for task completion with progress reporting.
        
        Uses adaptive timeout: resets timeout when progress is detected.
        Only times out if no progress is made for a sustained period.
        
        Args:
            task_id: Task ID to poll
            requests: Requests client
            max_wait: Maximum time to wait in seconds (base timeout, resets on progress)
            poll_interval: Time between polls in seconds
            progress_callback: Optional progress callback (uses instance callback if None)
            webhook_server: Optional webhook server for late callback checks
            
        Returns:
            Video URL when complete
        """
        # Use provided callback or fall back to instance callback
        if progress_callback is None:
            progress_callback = self.progress_callback
        start_time = time.time()
        last_progress_time = start_time  # Track when we last saw REAL progress (status change)
        last_progress_pct = 0.5  # Track last progress percentage
        last_status_code = None  # Track last HTTP status code
        no_progress_timeout = 300  # 5 minutes of no progress = timeout
        
        # Report that polling has started
        if progress_callback:
            progress_callback("HeyGen: Starting to poll for video status...", 0.5)
        else:
            self._report_progress("HeyGen: Starting to poll for video status...", 0.5)
        
        headers = {"X-Api-Key": self.api_key, "Content-Type": "application/json"}
        bearer_headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        # HeyGen v2 polling endpoint
        # According to HeyGen docs, they recommend webhooks, but polling should work
        # The endpoint might be /v2/video/{video_id} or might need to wait longer
        # Try the most likely endpoint first, with longer wait times
        poll_endpoint = f"{self.base_url}/video/{task_id}"  # Try singular 'video' first

        response = None
        last_error = None
        poll_count = 0
        
        while True:  # Loop until timeout or completion
            poll_count += 1
            current_time = time.time()
            elapsed = current_time - start_time
            time_since_progress = current_time - last_progress_time
            
            # Check for timeout:
            # - If progress is incrementing, reset last_progress_time keeps time_since_progress small
            # - Only timeout if NO progress for no_progress_timeout (5 minutes of stalled progress)
            # - Don't timeout based on total elapsed time if progress is happening
            if time_since_progress >= no_progress_timeout:
                # No progress for no_progress_timeout - timeout (stuck)
                break
            
            try:
                # Try X-Api-Key first
                try:
                    response = requests.get(poll_endpoint, headers=headers, timeout=30)
                except requests.exceptions.Timeout:
                    last_error = f"Timeout polling endpoint {poll_endpoint}"
                    # Report progress for timeouts too (less frequently)
                    if poll_count % 6 == 0:
                        progress_pct = min(0.5 + (elapsed / max_wait) * 0.3, 0.8)
                        video_id_short = task_id[:8] + "..." if len(task_id) > 8 else task_id
                        message = f"HeyGen: Polling timeout, retrying... (ID: {video_id_short}, {elapsed:.0f}s elapsed)"
                        if progress_callback:
                            progress_callback(message, progress_pct)
                        else:
                            self._report_progress(message, progress_pct)
                        print(f"[INFO] HeyGen polling timeout, {elapsed:.0f}s elapsed, continuing...")
                    time.sleep(poll_interval)
                    continue
                except requests.exceptions.ConnectionError as e:
                    last_error = f"Connection error polling {poll_endpoint}: {str(e)}"
                    # Report progress for connection errors too (less frequently)
                    if poll_count % 6 == 0:
                        progress_pct = min(0.5 + (elapsed / max_wait) * 0.3, 0.8)
                        video_id_short = task_id[:8] + "..." if len(task_id) > 8 else task_id
                        message = f"HeyGen: Connection error, retrying... (ID: {video_id_short}, {elapsed:.0f}s elapsed)"
                        if progress_callback:
                            progress_callback(message, progress_pct)
                        else:
                            self._report_progress(message, progress_pct)
                        print(f"[INFO] HeyGen polling connection error, {elapsed:.0f}s elapsed, continuing...")
                    time.sleep(poll_interval)
                    continue
                except Exception as e:
                    last_error = f"Error polling {poll_endpoint}: {str(e)}"
                    # Report progress for other errors too (less frequently)
                    if poll_count % 6 == 0:
                        progress_pct = min(0.5 + (elapsed / max_wait) * 0.3, 0.8)
                        video_id_short = task_id[:8] + "..." if len(task_id) > 8 else task_id
                        message = f"HeyGen: Polling error, retrying... (ID: {video_id_short}, {elapsed:.0f}s elapsed)"
                        if progress_callback:
                            progress_callback(message, progress_pct)
                        else:
                            self._report_progress(message, progress_pct)
                        print(f"[INFO] HeyGen polling error, {elapsed:.0f}s elapsed, continuing...")
                    time.sleep(poll_interval)
                    continue
                
                # If 404, try alternative endpoint format
                if response.status_code == 404:
                    # Try plural 'videos' endpoint
                    alt_endpoint = f"{self.base_url}/videos/{task_id}"
                    try:
                        alt_response = requests.get(alt_endpoint, headers=headers, timeout=30)
                        if alt_response.status_code == 200:
                            response = alt_response
                        elif alt_response.status_code != 404:
                            # If it's not 404, use this response
                            response = alt_response
                    except Exception:
                        pass  # Continue with original response
                    
                # Handle different HTTP status codes
                if response.status_code == 404:
                    # Video might not be ready yet, this is normal initially
                    # Calculate progress - even 404s show we're actively checking
                    progress_pct = min(0.5 + (elapsed / (max_wait * 1.5)) * 0.3, 0.8)
                    
                    # CRITICAL FIX: Reset progress timer on EVERY successful API response (even 404s)
                    # A 404 means the API is working and the video is still processing - this IS progress
                    # We're actively checking and the system is responsive, so reset the timeout timer
                    # This prevents premature timeouts when videos take longer than expected
                    last_progress_time = current_time
                    if last_status_code != 404:
                        last_status_code = 404
                    last_progress_pct = progress_pct
                    
                    # Report progress for 404s - update more frequently for better UI feedback
                    # Report every poll, but only log to console every 3 polls or 10 seconds
                    video_id_short = task_id[:8] + "..." if len(task_id) > 8 else task_id
                    should_log = poll_count == 1 or poll_count % 3 == 0 or int(elapsed) % 10 == 0
                    message = f"HeyGen: Video not ready yet (404), polling... (ID: {video_id_short}, {elapsed:.0f}s elapsed, poll #{poll_count})"
                    if progress_callback:
                        progress_callback(message, progress_pct)
                    else:
                        self._report_progress(message, progress_pct)
                    if should_log:
                        print(f"[INFO] HeyGen video not ready yet (404), {elapsed:.0f}s elapsed, continuing to poll...")
                    time.sleep(poll_interval)
                    continue
                elif response.status_code == 401:
                    raise RuntimeError(
                        "HeyGen API authentication failed during polling (401). "
                        "Your API key may have been revoked or expired."
                    )
                elif response.status_code == 403:
                    raise RuntimeError(
                        "HeyGen API access forbidden during polling (403). "
                        "You may not have permission to access this video."
                    )
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", poll_interval * 2)
                    wait_time = int(retry_after) if retry_after.isdigit() else poll_interval * 2
                    print(f"[WARN] HeyGen rate limited during polling, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = str(error_data.get("error", error_data))
                    except Exception:
                        error_msg = response.text[:200] if response.text else error_msg
                    
                    if response.status_code >= 500:
                        # Server error, retry
                        if poll_count % 3 == 0:
                            print(f"[WARN] HeyGen server error {response.status_code} during polling, retrying...")
                        time.sleep(poll_interval)
                        continue
                    else:
                        raise RuntimeError(
                            f"HeyGen API error during polling ({response.status_code}): {error_msg}"
                        )

                # Parse response with error handling
                try:
                    task_data = response.json()
                except ValueError as e:
                    raise RuntimeError(
                        f"HeyGen API returned invalid JSON during polling: {str(e)}. "
                        f"Response: {response.text[:200]}"
                    )
                
                # Check for API-level errors
                if task_data.get("error") is not None:
                    error_info = task_data.get("error", {})
                    if isinstance(error_info, dict):
                        error_msg = error_info.get("message", str(error_info))
                        raise RuntimeError(f"HeyGen API error during polling: {error_msg}")
                    else:
                        raise RuntimeError(f"HeyGen API error during polling: {error_info}")
                
                # Extract status and video URL
                data = task_data.get("data", {})
                status = data.get("status") or task_data.get("status")

                # Got a valid response (200) - this is real progress, reset timer
                if response.status_code == 200:
                    last_progress_time = current_time
                    last_status_code = 200
                
                if status == "completed" or status == "done":
                    # HeyGen v2 returns video_url in data.video_url
                    video_url = (
                        data.get("video_url")
                        or data.get("url")
                        or task_data.get("video_url")
                        or task_data.get("url")
                    )
                    if video_url:
                        if progress_callback:
                            progress_callback(f"HeyGen: Video ready! Downloading...", 0.85)
                        else:
                            self._report_progress(f"HeyGen: Video ready! Downloading...", 0.85)
                        print(f"[OK] HeyGen video generation completed in {elapsed:.1f}s")
                        return video_url
                    else:
                        raise RuntimeError(
                            f"HeyGen video status is 'completed' but no video_url found. "
                            f"Response: {json.dumps(task_data, indent=2)[:500]}"
                        )
                elif status == "failed" or status == "error":
                    error = data.get("error") or task_data.get("error") or "Unknown error"
                    error_details = data.get("error_details") or task_data.get("error_details")
                    error_msg = f"HeyGen video generation failed: {error}"
                    if error_details:
                        error_msg += f"\nDetails: {error_details}"
                    raise RuntimeError(error_msg)
                elif status in ["pending", "processing", "generating", "queued"]:
                    # Still processing, continue polling
                    # Calculate progress based on elapsed time (adaptive)
                    # Progress increases as we wait, showing we're making forward progress
                    progress_pct = min(0.5 + (elapsed / (max_wait * 1.5)) * 0.3, 0.8)  # 50% to 80% during polling
                    
                    # Only reset progress timer if status code changed (moved from 404 to 200 = real progress!)
                    # If status is still "processing" (200 response), don't reset timer - no real progress
                    if last_status_code != response.status_code:
                        # Status code changed (e.g., 404 -> 200) - this is real progress
                        last_progress_time = current_time
                        last_status_code = response.status_code
                    last_progress_pct = progress_pct
                    
                    # Report progress every poll for better UI feedback, but only log to console periodically
                    should_log = (poll_count == 1) or (poll_count % 3 == 0) or (int(elapsed) % 10 == 0 and int(elapsed) > 0)
                    message = f"HeyGen: Video {status}... ({elapsed:.0f}s elapsed, poll #{poll_count})"
                    if progress_callback:
                        progress_callback(message, progress_pct)
                    else:
                        self._report_progress(message, progress_pct)
                    if should_log:
                        print(f"[INFO] HeyGen video status: {status}, {elapsed:.0f}s elapsed...")
                elif status is None:
                    # No status field - might be a different response format
                    if poll_count == 1:
                        print(f"[WARN] HeyGen polling response has no status field, response structure: {list(task_data.keys())}")
                else:
                    # Unknown status, log and continue
                    if poll_count % 6 == 0:
                        print(f"[WARN] Unknown HeyGen status: '{status}', continuing to poll...")

                time.sleep(poll_interval)

            except RuntimeError:
                # Re-raise RuntimeErrors (they have detailed messages)
                raise
            except requests.exceptions.RequestException as e:
                # Network errors - continue polling
                last_error = f"Network error during polling: {str(e)}"
                if poll_count % 6 == 0:
                    print(f"[WARN] {last_error}, continuing to poll...")
                time.sleep(poll_interval)
                continue
            except Exception as e:
                # Unexpected errors - log and continue polling
                last_error = f"Unexpected error during polling: {str(e)}"
                if poll_count % 6 == 0:
                    print(f"[WARN] {last_error}, continuing to poll...")
                time.sleep(poll_interval)
                continue

        # Timeout reached - check why we timed out
        elapsed_minutes = elapsed / 60
        no_progress_minutes = time_since_progress / 60
        
        # If webhook server is available, check for late callback
        if webhook_server:
            self._report_progress(f"HeyGen: Timeout reached, checking webhook for late callback...", 0.85)
            event = webhook_server.get_event("heygen", task_id)
            if event and event.status == "completed":
                video_url = event.data.get("video_url")
                if video_url:
                    self._report_progress(f"HeyGen: Video ready via late webhook callback!", 0.9)
                    print(f"[OK] HeyGen video ready via late webhook: {video_url[:50]}...")
                    return video_url
        
        # Determine timeout reason
        if time_since_progress >= no_progress_timeout:
            timeout_reason = f"no progress for {no_progress_minutes:.1f} minutes"
        else:
            timeout_reason = f"maximum wait time of {elapsed_minutes:.1f} minutes exceeded"
        
        error_msg = f"HeyGen video generation timed out after {elapsed_minutes:.1f} minutes ({elapsed:.0f}s) - {timeout_reason} (video_id: {task_id})"
        if last_error:
            error_msg += f". Last error: {last_error}"
        error_msg += (
            f"\n\nHeyGen videos typically take 5-20 minutes to generate. "
            f"The video may still be processing on HeyGen's servers. "
            f"\n\nTo check status manually, use the video_id: {task_id}"
            f"\nOr use the check_video_status utility script."
        )
        raise RuntimeError(error_msg)


class DIDProvider(AvatarProvider):
    """D-ID Creative Reality API provider for avatar generation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize D-ID provider."""
        super().__init__(config)
        api_key_raw = config.get("api_key") or os.getenv("DID_API_KEY")
        # D-ID API key - try multiple formats
        self.api_key_raw = api_key_raw
        # Store both formats for testing
        if api_key_raw and ":" in api_key_raw:
            import base64
            self.api_key_b64 = base64.b64encode(api_key_raw.encode()).decode()
        else:
            self.api_key_b64 = api_key_raw
        self.api_key = api_key_raw  # Use raw key by default, will try different auth methods
        self.base_url = config.get("base_url", "https://api.d-id.com")
        # D-ID region - try to detect from config or use default
        # Common regions: us-east-1, eu-west-1, ap-southeast-1
        self.aws_region = config.get("aws_region") or os.getenv("DID_AWS_REGION", "us-east-1")

    def is_available(self) -> bool:
        """Check if D-ID is available."""
        if not self.api_key:
            return False
        try:
            import requests
            return True
        except ImportError:
            return False

    def generate(
        self, audio_path: Path, avatar_id: str, expression: Optional[str] = None, gesture: Optional[str] = None, text: Optional[str] = None, **kwargs
    ) -> tuple[Path, float]:
        """
        Generate avatar video using D-ID API.

        Args:
            audio_path: Path to audio file
            avatar_id: D-ID avatar ID or source URL
            expression: Expression to apply
            gesture: Gesture to apply (may not be supported)
            text: Text to speak (optional, D-ID can use audio or text)
            **kwargs: Additional parameters

        Returns:
            Tuple of (video_path, duration_seconds)

        Raises:
            ValueError: If API key is missing
            RuntimeError: If API request fails
        """
        if not self.api_key:
            raise ValueError("D-ID API key is required")

        if not self.is_available():
            raise RuntimeError("D-ID provider is not available (requests not installed)")

        if not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        import requests

        try:
            # D-ID API authentication
            # D-ID supports both Basic Auth (username:password) and Bearer token
            # Try Bearer token first (simpler, recommended), fall back to Basic Auth
            import base64
            
            headers = {
                "Accept": "application/json",
            }
            
            # Try Bearer token authentication first (if API key doesn't contain ':')
            if ":" not in self.api_key:
                # Bearer token format
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["Content-Type"] = "application/json"
            else:
                # Basic Auth format (username:password)
                encoded_credentials = base64.b64encode(self.api_key.encode('utf-8')).decode('utf-8')
                headers["Authorization"] = f"Basic {encoded_credentials}"
                headers["Content-Type"] = "application/json"

            # D-ID API: Create talk with audio file upload
            # D-ID supports multipart/form-data with audio file
            # Avatar ID must be a valid image URL (jpg/jpeg/png) or use D-ID's preset avatars
            # For preset avatars, use format: "preset://{preset_name}" or direct image URL
            
            # Convert avatar_id to proper format for D-ID
            # D-ID requires actual image URLs (jpg/jpeg/png) - not preset names
            # If it's already a URL, use it directly
            # Otherwise, we need to map HeyGen avatar IDs to D-ID image URLs
            # For now, use a default D-ID preset image URL if avatar_id is not a URL
            if avatar_id.startswith("http"):
                source_url = avatar_id
            else:
                # Map common avatar names to D-ID preset image URLs
                # D-ID preset avatars are available at S3 URLs
                # Common presets: amy, sara, john, etc.
                avatar_mapping = {
                    "amy": "https://d-id-public-bucket.s3.amazonaws.com/amy.jpg",
                    "sara": "https://d-id-public-bucket.s3.amazonaws.com/sara.jpg",
                    "john": "https://d-id-public-bucket.s3.amazonaws.com/john.jpg",
                }
                
                # Try to extract avatar name from HeyGen ID (e.g., "Abigail_*" -> "amy")
                avatar_name = avatar_id.lower().split("_")[0] if "_" in avatar_id else avatar_id.lower()
                
                # Use mapped URL or default to amy
                source_url = avatar_mapping.get(avatar_name, avatar_mapping["amy"])
                
                # Log the mapping for debugging
                print(f"[INFO] D-ID: Mapped avatar '{avatar_id}' to image URL: {source_url}")
            
            # D-ID API: Use text-to-speech (more reliable than audio uploads)
            # If text is provided, use it. Otherwise, audio upload may work but is less reliable.
            if text:
                # Use text-to-speech (recommended approach)
                payload = {
                    "source_url": source_url,
                    "script": {
                        "type": "text",
                        "input": text
                    }
                }
                
                if expression:
                    payload["expression"] = expression
                
                # Make request with JSON payload (text-to-speech)
                response = requests.post(
                    f"{self.base_url}/talks", json=payload, headers=headers, timeout=60
                )
            else:
                # Fallback: Try audio file upload (less reliable, may return 500)
                print("[WARN] D-ID: No text provided, attempting audio file upload (may be unreliable)")
                with open(audio_path, "rb") as f:
                    files = {
                        "audio": (audio_path.name, f, "audio/mpeg")
                    }
                    data = {
                        "source_url": source_url,
                    }

                    if expression:
                        data["expression"] = expression

                    # Remove Content-Type header - requests will set it automatically for multipart
                    multipart_headers = {k: v for k, v in headers.items() if k.lower() != "content-type"}
                    multipart_headers["Authorization"] = headers["Authorization"]  # Keep auth
                    
                    # Make request with multipart/form-data
                    response = requests.post(
                        f"{self.base_url}/talks", files=files, data=data, headers=multipart_headers, timeout=60
                    )
                
                if response.status_code not in [200, 201, 202]:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = str(error_data.get("error", error_data.get("message", error_msg)))
                    except Exception:
                        error_msg = response.text[:200] if response.text else error_msg
                    
                    if response.status_code == 403:
                        raise RuntimeError(
                            f"D-ID API authentication failed (403 Forbidden): {error_msg}. "
                            f"Ensure your API key is in format 'username:password' and is valid for your subscription plan."
                        )
                    response.raise_for_status()

            talk_data = response.json()
            talk_id = talk_data.get("id")

            if not talk_id:
                raise RuntimeError("D-ID API did not return talk ID")

            # Report progress: Video creation submitted
            talk_id_short = talk_id[:8] + "..." if len(talk_id) > 8 else talk_id
            progress_callback = kwargs.get("progress_callback") or getattr(self, 'progress_callback', None)
            
            message = f"D-ID: Video creation request submitted (ID: {talk_id_short})"
            if progress_callback:
                progress_callback(message, 0.1)
            else:
                self._report_progress(message, 0.1)

            # Poll for completion (use Basic Auth)
            video_url = self._poll_talk_status(talk_id, requests, progress_callback=progress_callback)

            # Download video
            message = f"D-ID: Downloading video... (ID: {talk_id_short})"
            if progress_callback:
                progress_callback(message, 0.9)
            else:
                self._report_progress(message, 0.9)
            video_response = requests.get(video_url, timeout=300, stream=True)
            video_response.raise_for_status()

            # Save video
            output_path = kwargs.get("output_path")
            if not output_path:
                output_path = audio_path.parent / f"{audio_path.stem}_avatar.mp4"
            else:
                output_path = Path(output_path)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Write video with progress
            total_size = int(video_response.headers.get('content-length', len(video_response.content)))
            downloaded = 0
            with open(output_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and downloaded % (1024 * 1024) == 0:  # Report every MB
                            progress = 0.9 + (downloaded / total_size) * 0.1
                            self._report_progress(f"D-ID: Downloading... {downloaded / 1024 / 1024:.1f} MB", progress)

            # Estimate duration
            duration = kwargs.get("duration", 0.0)
            if duration == 0.0:
                duration = len(video_response.content) / 100000.0

            return output_path, duration

        except Exception as e:
            # Log error with progress callback if available
            progress_callback = kwargs.get("progress_callback") or getattr(self, 'progress_callback', None)
            error_msg = f"D-ID: Error generating video: {str(e)}"
            if progress_callback:
                progress_callback(error_msg, 0.0)
            else:
                self._report_progress(error_msg, 0.0)
            raise RuntimeError(f"D-ID API request failed: {e}") from e

    def _poll_talk_status(self, talk_id: str, requests, max_wait: int = 300, poll_interval: int = 5, progress_callback: Optional[callable] = None) -> str:
        """
        Poll D-ID API for talk completion with progress reporting.

        Args:
            talk_id: Talk ID to poll
            requests: Requests client
            max_wait: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds
            progress_callback: Optional callback function for progress updates

        Returns:
            URL of completed video

        Raises:
            RuntimeError: If talk fails or times out
        """
        import base64
        
        start_time = time.time()
        poll_count = 0
        talk_id_short = talk_id[:8] + "..." if len(talk_id) > 8 else talk_id
        
        # Use same auth method as initial request
        headers = {
            "Accept": "application/json",
        }
        
        if ":" not in self.api_key:
            # Bearer token
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            # Basic Auth
            encoded_credentials = base64.b64encode(self.api_key.encode('utf-8')).decode('utf-8')
            headers["Authorization"] = f"Basic {encoded_credentials}"
        
        headers["Content-Type"] = "application/json"

        while time.time() - start_time < max_wait:
            try:
                poll_count += 1
                response = requests.get(f"{self.base_url}/talks/{talk_id}", headers=headers, timeout=30)
                
                elapsed = time.time() - start_time
                
                # Handle different HTTP status codes
                if response.status_code == 404:
                    # Talk might not be ready yet, this is normal initially
                    progress_pct = min(0.5 + (elapsed / (max_wait * 1.5)) * 0.3, 0.8)
                    # Report progress for 404s - first poll immediately, then every 3 polls or every 10 seconds
                    if poll_count == 1 or poll_count % 3 == 0 or int(elapsed) % 10 == 0:
                        message = f"D-ID: Video not ready yet (404), polling... (ID: {talk_id_short}, {elapsed:.0f}s elapsed, poll #{poll_count})"
                        if progress_callback:
                            progress_callback(message, progress_pct)
                        else:
                            self._report_progress(message, progress_pct)
                    time.sleep(poll_interval)
                    continue
                
                response.raise_for_status()

                talk_data = response.json()
                status = talk_data.get("status")
                
                if status == "done":
                    message = f"D-ID: Video ready! Downloading... (ID: {talk_id_short}, {elapsed:.0f}s elapsed)"
                    if progress_callback:
                        progress_callback(message, 0.85)
                    else:
                        self._report_progress(message, 0.85)
                    return talk_data.get("result_url")
                elif status == "error":
                    error = talk_data.get("error", "Unknown error")
                    raise RuntimeError(f"D-ID video generation failed: {error}")
                elif status in ["pending", "processing", "generating"]:
                    # Report progress during polling - first poll immediately, then every 3 polls or every 10 seconds
                    progress_pct = min(0.5 + (elapsed / (max_wait * 1.5)) * 0.3, 0.8)
                    should_report = (poll_count == 1) or (poll_count % 3 == 0) or (int(elapsed) % 10 == 0 and int(elapsed) > 0)
                    if should_report:
                        message = f"D-ID: Video {status}... (ID: {talk_id_short}, {elapsed:.0f}s elapsed, poll #{poll_count})"
                        if progress_callback:
                            progress_callback(message, progress_pct)
                        else:
                            self._report_progress(message, progress_pct)

                time.sleep(poll_interval)

            except Exception as e:
                if "error" in str(e).lower() or "failed" in str(e).lower():
                    raise
                # Continue polling on other errors

        raise RuntimeError(f"D-ID talk timed out after {max_wait} seconds")


class MockAvatarProvider(AvatarProvider):
    """Mock avatar provider for testing - creates placeholder videos."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize mock provider."""
        super().__init__(config)
        self.output_dir = Path(config.get("output_dir", "outputs/avatars"))

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def generate(
        self, audio_path: Path, avatar_id: str, expression: Optional[str] = None, gesture: Optional[str] = None, text: Optional[str] = None, **kwargs
    ) -> tuple[Path, float]:
        """
        Generate placeholder avatar video using FFmpeg.

        Creates a simple video with a colored background and the audio file.
        This is useful for testing when real avatar APIs are unavailable.

        Args:
            audio_path: Path to audio file
            avatar_id: Avatar identifier (used for color selection)
            expression: Expression (ignored in mock)
            gesture: Gesture (ignored in mock)
            text: Text (ignored in mock, uses audio file)
            **kwargs: Additional parameters

        Returns:
            Tuple of (video_path, duration_seconds)
        """
        import subprocess
        from pydub import AudioSegment

        if not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        # Get audio duration
        try:
            audio_seg = AudioSegment.from_file(str(audio_path))
            duration = len(audio_seg) / 1000.0  # Convert ms to seconds
        except Exception:
            duration = 5.0  # Default duration if can't read audio

        # Generate output path
        output_path = kwargs.get("output_path")
        if not output_path:
            output_path = self.output_dir / f"{audio_path.stem}_avatar.mp4"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create a simple colored background video with audio
        # Use avatar_id to select a color (simple hash to pick from predefined colors)
        colors = ["red", "blue", "green", "yellow", "purple", "orange", "cyan", "magenta"]
        color_index = hash(avatar_id) % len(colors)
        color = colors[color_index]

        # FFmpeg command to create a video with colored background and audio
        ffmpeg_cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c={color}:size=1920x1080:duration={duration}",
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-y",  # Overwrite output file
            str(output_path),
        ]

        try:
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300,
                check=True,
            )
            return output_path, duration
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg failed to create mock avatar video: {e.stderr}") from e
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg to use mock avatar provider.")


class AvatarGenerator:
    """Main avatar generator with multi-provider support."""

    def __init__(self, config: Dict[str, Any], output_dir: Optional[Path] = None):
        """
        Initialize avatar generator.

        Args:
            config: Configuration dictionary with avatar and API settings
            output_dir: Directory for output video files (optional)
        """
        self.config = config
        self.avatar_config = config.get("avatar", {})
        self.api_config = config.get("api", {})

        # Setup output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            output_dir_str = config.get("storage", {}).get("outputs_dir", "outputs")
            self.output_dir = Path(output_dir_str) / "avatars"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize providers
        self.providers: Dict[str, AvatarProvider] = {}
        self._init_providers()

        # Set default engine (default to Audio2Face - NVIDIA Omniverse)
        # Local GPU providers: audio2face (NVIDIA Omniverse), dreamtalk (requires checkpoints)
        # External APIs: heygen, did
        self.engine = self.avatar_config.get("engine", "audio2face")
    
    def set_progress_callback(self, callback: callable):
        """Set progress callback for avatar generation.
        
        Args:
            callback: Function that takes (message: str, progress: float) where progress is 0.0-1.0
        """
        self.progress_callback = callback
        # Progress callback will be set on individual providers when they're used

    def _init_providers(self):
        """Initialize available avatar providers."""
        # Audio2Face (local GPU-based, default) - NVIDIA Omniverse Audio2Face
        a2f_config = self.config.get("audio2face", {})
        self.providers["audio2face"] = Audio2FaceProvider(a2f_config)
        
        # DreamTalk (local GPU-based, but shelved - requires checkpoints)
        dreamtalk_config = self.config.get("dreamtalk", {})
        self.providers["dreamtalk"] = DreamTalkProvider(dreamtalk_config)
        
        # SadTalker (local GPU-based, 2D headshot animation)
        sadtalker_config = self.config.get("sadtalker", {})
        self.providers["sadtalker"] = SadTalkerProvider(sadtalker_config)
        
        # 3DDFA (local GPU-based, 3D face reconstruction)
        tddfa_config = self.config.get("tddfa", {})
        self.providers["tddfa"] = TDDFAProvider(tddfa_config)
        
        # 3DDFA + Audio2Face (combined: 3D reconstruction + animation)
        tddfa_a2f_config = self.config.get("tddfa_a2f", {})
        # Merge tddfa and audio2face configs
        if not tddfa_a2f_config:
            tddfa_a2f_config = {
                "tddfa": tddfa_config,
                "audio2face": self.config.get("audio2face", {}),
                "usd_cache_dir": ".cache/usd_models"
            }
        self.providers["tddfa_a2f"] = TDDFA_A2FProvider(tddfa_a2f_config)
        
        # HeyGen (external API)
        heygen_config = self.api_config.get("heygen", {})
        self.providers["heygen"] = HeyGenProvider(heygen_config)

        # D-ID (external API)
        did_config = self.api_config.get("did", {})
        self.providers["did"] = DIDProvider(did_config)

        # Mock provider (for testing when APIs are unavailable)
        mock_config = {"output_dir": str(self.output_dir)}
        self.providers["mock"] = MockAvatarProvider(mock_config)
        
        # HeyGem disabled - using Audio2Face instead
        # heygem_config = self.config.get("heygem", {})
        # self.providers["heygem"] = HeyGemProvider(heygem_config)

    def _get_provider(self, engine: str) -> AvatarProvider:
        """
        Get avatar provider by engine name.

        Args:
            engine: Engine name ("dreamtalk", "heygen", "did")

        Returns:
            AvatarProvider instance

        Raises:
            ValueError: If engine is not supported
            RuntimeError: If provider is not available
        """
        if engine not in self.providers:
            raise ValueError(
                f"Unsupported avatar engine: {engine}. "
                f"Supported engines: {', '.join(self.providers.keys())}"
            )

        provider = self.providers[engine]
        if not provider.is_available():
            raise RuntimeError(
                f"Avatar engine '{engine}' is not available. "
                f"Please check configuration and ensure all dependencies are installed. "
                f"For Audio2Face: ensure NVIDIA Omniverse is installed and Audio2Face extension is available. "
                f"For DreamTalk: ensure it's installed and checkpoints are available. "
                f"For HeyGen/D-ID: ensure API keys are configured."
            )

        return provider

    def generate_persona_avatar(
        self,
        persona: Persona,
        audio_path: Path,
        expression: Optional[str] = None,
        gesture: Optional[str] = None,
        output_filename: Optional[str] = None,
        text: Optional[str] = None,
        webhook_server=None,
    ) -> AvatarVideo:
        """
        Generate avatar video for a persona.

        Args:
            persona: Persona configuration
            audio_path: Path to audio file for lip-sync
            expression: Expression to apply (defaults to persona's default or segment expression)
            gesture: Gesture to apply (defaults to persona's default or segment gesture)
            output_filename: Optional output filename

        Returns:
            AvatarVideo with video file path and metadata

        Raises:
            RuntimeError: If avatar generation fails
        """
        if not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        avatar_id = persona.avatar.avatar_id
        # Check for global engine override in config (for testing)
        global_engine_override = self.config.get("avatar", {}).get("engine_override")
        provider_name = global_engine_override or persona.avatar.engine or self.engine

        # For DreamTalk, we need image_path - try to get it from persona config or avatar_id
        image_path = None
        # Check if avatar_id is already a file path
        if Path(avatar_id).exists():
            image_path = Path(avatar_id)
        # Try to find image in common locations
        else:
            # Try relative to project root
            project_root = Path(__file__).parent.parent.parent
            possible_paths = [
                project_root / "examples" / "personas" / f"{avatar_id}.jpg",
                project_root / "examples" / "personas" / f"{avatar_id}.png",
                project_root / "examples" / "personas" / f"{persona.key.lower()}.jpg",
                project_root / "examples" / "personas" / f"{persona.key.lower()}.png",
            ]
            for path in possible_paths:
                if path.exists():
                    image_path = path
                    break

        # Get provider (no fallback - use selected provider or error)
        provider = self._get_provider(provider_name)

        # Use default expression/gesture if not provided
        if not expression:
            expression = persona.avatar.expressions.default if persona.avatar.expressions.enabled else None
        if not gesture:
            gesture = None  # Gestures are optional

        # Generate output path
        if output_filename:
            output_path = self.output_dir / output_filename
        else:
            output_path = self.output_dir / f"{persona.key}_{audio_path.stem}_avatar.mp4"

        # Get audio duration if available
        duration = 0.0
        try:
            from pydub import AudioSegment as PydubAudioSegment
            audio_file = PydubAudioSegment.from_file(str(audio_path))
            duration = len(audio_file) / 1000.0  # Convert ms to seconds
        except Exception:
            pass  # Duration estimation will be done by provider

        # Generate video (pass text for HeyGen API which needs it)
        # For HeyGen, we also need a voice_id - use a default for now
        # TODO: Map ElevenLabs voice_id to HeyGen voice_id, or use audio_url
        
        # Prepare kwargs for provider.generate
        generate_kwargs = {
            "output_path": output_path,
            "duration": duration,
            "voice_id": "e0cc82c22f414c95b1f25696c732f058",  # Default HeyGen voice
        }
        
        # Add image_path for DreamTalk (required)
        if image_path:
            generate_kwargs["image_path"] = image_path
        
        # Add webhook server if available
        if webhook_server:
            generate_kwargs["webhook_server"] = webhook_server
        
        # Pass progress callback to provider if available
        if hasattr(self, 'progress_callback') and self.progress_callback:
            provider.set_progress_callback(self.progress_callback)
        
        video_path, video_duration = provider.generate(
            audio_path, avatar_id, expression=expression, gesture=gesture, 
            text=text, **generate_kwargs
        )

        # Create a minimal segment for the avatar video
        from src.core.script_parser import ScriptSegment

        segment = ScriptSegment(persona=persona.key.upper(), text="")

        return AvatarVideo(
            segment=segment,
            video_path=video_path,
            duration=video_duration or duration,
            provider=provider_name,
            persona=persona.name,
            expression=expression,
            gesture=gesture,
        )

    def generate_multiple(
        self,
        segments: List[ScriptSegment],
        audio_segments: List[AudioSegment],
        personas: Dict[str, Persona],
        max_workers: int = 3,
        webhook_server=None,
    ) -> List[AvatarVideo]:
        """
        Generate avatar videos for multiple segments in parallel.

        Args:
            segments: List of script segments
            audio_segments: List of corresponding audio segments
            personas: Dictionary mapping persona names to Persona objects
            max_workers: Maximum number of parallel workers (default: 3)

        Returns:
            List of AvatarVideo objects with video files and timing
        """
        if len(segments) != len(audio_segments):
            raise ValueError("segments and audio_segments must have the same length")

        avatar_videos = []

        # Generate avatars in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for segment, audio_seg in zip(segments, audio_segments):
                persona_name = segment.persona.upper()
                persona = personas.get(persona_name)

                if not persona:
                    raise ValueError(f"Persona '{persona_name}' not found in personas dictionary")

                # Use expression and gesture from segment if available
                expression = segment.expression or None
                gesture = segment.gesture or None

                future = executor.submit(
                    self.generate_persona_avatar,
                    persona,
                    audio_seg.audio_path,
                    expression=expression,
                    gesture=gesture,
                    text=segment.text,  # Pass text for HeyGen API
                    webhook_server=webhook_server,  # Pass webhook server for callbacks
                )
                futures.append((future, segment, audio_seg))

            # Collect results
            for future, segment, audio_seg in futures:
                try:
                    avatar_video = future.result(timeout=900)  # 15 minute timeout per video (HeyGen can take 5-15 min)
                    # Update segment reference
                    avatar_video.segment = segment
                    avatar_videos.append(avatar_video)
                except Exception as e:
                    raise RuntimeError(f"Failed to generate avatar video: {e}") from e

        return avatar_videos

