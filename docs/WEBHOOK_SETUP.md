# HeyGen Webhook Setup Guide

## Overview

HeyGen API v2 recommends using webhooks instead of polling for video status updates. This provides more reliable and efficient video status notifications.

## Webhook Handler

The `HeyGenWebhookHandler` class in `src/core/heygen_webhook.py` manages webhook callbacks from HeyGen.

## Setup Options

### Option 1: Local Development with ngrok (Recommended for Testing)

1. **Install ngrok**: Download from https://ngrok.com/

2. **Start your webhook server** (see examples below)

3. **Expose your local server**:
   ```bash
   ngrok http 5000
   ```

4. **Use the ngrok URL** as your `callback_base_url`:
   ```python
   webhook_handler = HeyGenWebhookHandler(
       callback_base_url="https://your-ngrok-url.ngrok.io"
   )
   ```

### Option 2: Production Server

1. Deploy a webhook endpoint on your server
2. Use your public domain as `callback_base_url`
3. Ensure HTTPS is enabled (HeyGen requires HTTPS for webhooks)

## Integration Examples

### Flask Example

```python
from flask import Flask, request, jsonify
from src.core.heygen_webhook import HeyGenWebhookHandler

app = Flask(__name__)
webhook_handler = HeyGenWebhookHandler(
    callback_base_url="https://your-domain.com"
)

@app.route('/webhooks/heygen/video/<video_id>', methods=['POST'])
def heygen_webhook(video_id):
    """Handle HeyGen webhook callback."""
    payload = request.json
    event = webhook_handler.handle_webhook(video_id, payload)
    
    if event.status == "completed":
        print(f"Video {video_id} is ready: {event.video_url}")
    elif event.status == "failed":
        print(f"Video {video_id} failed: {event.error}")
    
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### FastAPI Example

```python
from fastapi import FastAPI, Request
from src.core.heygen_webhook import HeyGenWebhookHandler

app = FastAPI()
webhook_handler = HeyGenWebhookHandler(
    callback_base_url="https://your-domain.com"
)

@app.post("/webhooks/heygen/video/{video_id}")
async def heygen_webhook(video_id: str, request: Request):
    """Handle HeyGen webhook callback."""
    payload = await request.json()
    event = webhook_handler.handle_webhook(video_id, payload)
    
    if event.status == "completed":
        print(f"Video {video_id} is ready: {event.video_url}")
    elif event.status == "failed":
        print(f"Video {video_id} failed: {event.error}")
    
    return {"status": "received"}
```

## Using Webhooks in Avatar Generator

When generating videos, pass the callback URL:

```python
from src.core.avatar_generator import HeyGenProvider
from src.core.heygen_webhook import HeyGenWebhookHandler

# Initialize webhook handler
webhook_handler = HeyGenWebhookHandler(
    callback_base_url="https://your-domain.com"
)

# Generate video with webhook
provider = HeyGenProvider(config)
video_id = "..."  # From initial API response

callback_url = webhook_handler.get_callback_url(video_id)

video_path, duration = provider.generate(
    audio_path=audio_path,
    avatar_id=avatar_id,
    text=text,
    callback_url=callback_url  # Enable webhook
)

# Register callback to handle completion
def on_video_ready(event):
    print(f"Video ready: {event.video_url}")

webhook_handler.register_callback(video_id, on_video_ready)

# Wait for webhook (with polling fallback)
event = webhook_handler.wait_for_video(video_id, timeout=300)
if event and event.status == "completed":
    # Download video from event.video_url
    pass
```

## Webhook Payload Format

HeyGen webhook payloads typically include:

```json
{
  "data": {
    "video_id": "abc123...",
    "status": "completed",
    "video_url": "https://...",
    "error": null
  }
}
```

Or for failures:

```json
{
  "data": {
    "video_id": "abc123...",
    "status": "failed",
    "error": "Error message"
  }
}
```

## Security Considerations

1. **Verify webhook authenticity**: HeyGen may include signature headers
2. **Use HTTPS**: Required for production webhooks
3. **Validate video_id**: Ensure the video_id matches your pending requests
4. **Rate limiting**: Implement rate limiting on webhook endpoints

## Fallback to Polling

If webhooks are not configured, the system will automatically fall back to polling. The polling logic handles 404s gracefully and continues checking until the video is ready.

## Testing

Use the test script to verify webhook setup:

```bash
python scripts/test_avatar_apis.py
```

This will test both webhook-enabled and polling fallback scenarios.

