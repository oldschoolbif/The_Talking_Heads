# Progress Tracking Guide

## Overview

The Talking Heads pipeline now includes comprehensive progress tracking across all 7 steps of podcast generation. This allows you to see real-time progress and understand exactly where the process is at any given time.

## Progress Steps

The pipeline is broken down into 7 distinct steps:

1. **Step 1/7: Parsing script** (0-10%)
   - Parses the input script file
   - Extracts segments, personas, expressions, and gestures

2. **Step 2/7: Loading personas** (15-20%)
   - Loads persona configurations from `config/personas.yaml`
   - Validates personas against script requirements
   - Builds persona dictionary

3. **Step 3/7: Generating TTS audio** (25-50%)
   - Generates audio for each segment
   - Shows progress per segment: "Generating audio X/Y for PERSONA..."
   - Uses configured TTS provider (ElevenLabs, Azure, gTTS)

4. **Step 4/7: Mixing audio tracks** (55-60%)
   - Combines all audio segments into a single mixed track
   - Applies normalization and timing adjustments

5. **Step 5/7: Generating avatars** (65-85%)
   - Generates avatar videos for each segment
   - Shows progress per avatar: "Generating avatar X/Y for PERSONA..."
   - Uses configured avatar provider (HeyGen, D-ID)
   - Supports webhook callbacks for real-time status updates

6. **Step 6/7: Loading scene** (87-88%)
   - Loads background scene configuration
   - Validates scene exists

7. **Step 7/7: Composing final video** (90-100%)
   - Combines all components into final video
   - Applies layout, transitions, and synchronization
   - Outputs final video file

## Using Progress Callbacks

### Basic Usage

```python
from src.core.pipeline import Pipeline
from src.utils.config_loader import load_config

config = load_config("config/config.yaml")
pipeline = Pipeline(config)

def progress_callback(message: str, progress: float):
    """Handle progress updates."""
    print(f"[{int(progress * 100)}%] {message}")

pipeline.set_progress_callback(progress_callback)

# Generate podcast
output_path = pipeline.create_podcast(script_path)
```

### Rich Progress Bar

For a more visual progress display, use the `scripts/generate_with_progress.py` script which uses Rich for beautiful progress bars:

```bash
python scripts/generate_with_progress.py
```

## Webhook Integration

When webhooks are enabled, you'll see additional progress information:

- **Webhook server status**: Shows if webhook server is running
- **Webhook callbacks**: Real-time notifications when avatar videos are ready
- **API status**: Updates on API request status

### Setting Up Webhooks

1. **Start webhook server** (optional, for local development):
   ```bash
   python scripts/start_webhook_server.py
   ```

2. **For external access** (production):
   - Use ngrok: `ngrok http 5000`
   - Or deploy to a public server
   - Update `config/config.yaml` with your webhook URL

3. **Webhook endpoints**:
   - HeyGen: `POST /webhooks/heygen/video/<video_id>`
   - D-ID: `POST /webhooks/did/talk/<talk_id>`
   - Health: `GET /health`

## Progress Messages

Progress messages follow this format:
- `Step X/7: [Action]...` - Main step progress
- `Step X/7: [Action] Y/Z for [Persona]...` - Per-item progress within a step
- `Step X/7: [Action] complete!` - Step completion

## Error Handling

If an error occurs during any step:
- Progress tracking stops
- Error message is displayed
- Temporary files are cleaned up (if `cleanup_temp=True`)
- Full traceback is available for debugging

## Configuration

Progress tracking is enabled by default. To disable:

```yaml
# config/config.yaml
webhook:
  enabled: false  # Disables webhook server (progress still works)
```

## Examples

See `scripts/generate_with_progress.py` for a complete example with Rich progress bars and error handling.

