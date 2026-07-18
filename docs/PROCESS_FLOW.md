# The Talking Heads - Process Flow Documentation

## Overview

This document describes the complete process flow for generating multi-persona podcast videos, including all external API services, data transformations, and pipeline steps.

## External API Services

### 1. **ElevenLabs API** (Text-to-Speech)
- **Purpose:** Primary TTS provider for generating natural-sounding voice audio
- **Base URL:** `https://api.elevenlabs.io/v1`
- **API Key:** Configured in `config.yaml` → `api.elevenlabs.api_key`
- **Endpoints Used:**
  - `POST /text-to-speech/{voice_id}` - Generate speech from text
- **Usage:** Step 3 of pipeline - generates audio for each persona segment
- **Input:** Text string, voice ID
- **Output:** MP3 audio bytes
- **Cost:** Pay-per-character (varies by plan)
- **Rate Limits:** Varies by subscription tier
- **Documentation:** https://elevenlabs.io/docs

### 2. **Azure Speech Service** (Text-to-Speech - Alternative)
- **Purpose:** Alternative TTS provider (fallback option)
- **Base URL:** Region-specific (e.g., `eastus`)
- **API Key:** Configured in `config.yaml` → `api.azure.speech_key`
- **Region:** Configured in `config.yaml` → `api.azure.speech_region`
- **Usage:** Optional alternative to ElevenLabs
- **Input:** Text string, voice configuration
- **Output:** Audio bytes
- **Cost:** Pay-per-character
- **Documentation:** https://learn.microsoft.com/azure/cognitive-services/speech-service/

### 3. **HeyGen API** (Avatar Video Generation)
- **Purpose:** Cloud-based avatar video generation with lip-sync
- **Base URL:** `https://api.heygen.com/v2`
- **API Key:** Configured in `config.yaml` → `api.heygen.api_key`
- **Endpoints Used:**
  - `POST /v2/video/generate` - Create video generation task
  - `GET /v2/video/{video_id}` - Check video status
  - `GET /v2/videos/{video_id}` - Alternative status endpoint
- **Usage:** Step 5 of pipeline - generates talking head videos
- **Input:** Audio file, avatar ID, text, expressions, gestures
- **Output:** MP4 video URL (downloaded to local file)
- **Cost:** Pay-per-video (varies by resolution/quality)
- **Processing Time:** 5-20 minutes per video
- **Features:** Expressions, gestures, multiple avatar styles
- **Documentation:** https://docs.heygen.com

### 4. **D-ID API** (Avatar Video Generation - Alternative)
- **Purpose:** Alternative cloud-based avatar video generation
- **Base URL:** `https://api.d-id.com`
- **API Key:** Configured in `config.yaml` → `api.did.api_key`
- **Authentication:** Bearer token or Basic Auth (username:password)
- **Endpoints Used:**
  - `POST /talks` - Create talking head video
  - `GET /talks/{talk_id}` - Check talk status
- **Usage:** Step 5 of pipeline - alternative to HeyGen
- **Input:** Audio file OR text, source image URL
- **Output:** MP4 video URL (downloaded to local file)
- **Cost:** Pay-per-video
- **Processing Time:** 1-5 minutes per video
- **Features:** Text-to-speech or audio-driven, image-based avatars
- **Documentation:** https://docs.d-id.com

### 5. **DreamTalk** (Local Avatar Generation)
- **Purpose:** Local GPU-based avatar video generation (no API)
- **Type:** Local Python subprocess (not an API service)
- **Path:** Configured in `config.yaml` → `dreamtalk.dreamtalk_path`
- **Usage:** Step 5 of pipeline - local alternative to cloud APIs
- **Input:** Audio file, source image path
- **Output:** MP4 video file (local)
- **Cost:** None (runs locally)
- **Processing Time:** 30-90 seconds per minute of video (on GPU)
- **Requirements:** CUDA, PyTorch, DreamTalk checkpoints
- **Documentation:** https://github.com/ali-vilab/dreamtalk

## Complete Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: Script File                           │
│              (examples/scripts/*.txt)                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Parse Script                                           │
│  ─────────────────────                                          │
│  Component: ScriptParser                                        │
│  External APIs: None                                            │
│  Output: ParsedScript with segments                            │
│                                                                 │
│  • Parse markdown-style script                                  │
│  • Extract persona names, text, expressions, gestures         │
│  • Validate format                                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Load Personas                                         │
│  ─────────────────────                                          │
│  Component: PersonaEngine                                       │
│  External APIs: None                                            │
│  Output: Persona objects with voice/avatar config               │
│                                                                 │
│  • Load from config/personas.yaml                              │
│  • Validate personas exist                                      │
│  • Extract voice IDs, avatar IDs, expressions                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Generate TTS Audio                                    │
│  ─────────────────────                                          │
│  Component: TTSEngine                                           │
│  External APIs: ElevenLabs API (or Azure Speech)                │
│  Output: AudioSegment objects (MP3 files)                       │
│                                                                 │
│  For each script segment:                                      │
│  1. Check cache (.cache/tts/)                                  │
│  2. If not cached:                                            │
│     • Call ElevenLabs API: POST /text-to-speech/{voice_id}    │
│     • Send: text, voice_id, model, stability, etc.           │
│     • Receive: MP3 audio bytes                                 │
│     • Save to cache                                            │
│  3. Create AudioSegment with path and duration                │
│                                                                 │
│  Parallel Processing: Sequential (can be parallelized)        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Mix Audio Segments                                    │
│  ─────────────────────                                          │
│  Component: AudioMixer                                          │
│  External APIs: None                                            │
│  Output: Single mixed audio file (MP3/WAV)                      │
│                                                                 │
│  • Concatenate audio segments in order                         │
│  • Use pydub for audio processing                              │
│  • Add silence/padding if needed                               │
│  • Export to single audio file                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Generate Avatar Videos                                │
│  ─────────────────────                                          │
│  Component: AvatarGenerator                                     │
│  External APIs: HeyGen API, D-ID API, or DreamTalk (local)     │
│  Output: AvatarVideo objects (MP4 files)                        │
│                                                                 │
│  Provider Selection (based on config):                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Option A: HeyGen API                                     │  │
│  │ ─────────────────────                                     │  │
│  │ 1. POST /v2/video/generate                               │  │
│  │    • Send: avatar_id, text, audio, expressions          │  │
│  │    • Receive: video_id                                   │  │
│  │ 2. Start webhook server (optional)                       │  │
│  │ 3. Poll GET /v2/video/{video_id}                        │  │
│  │    • Wait for status: "completed"                        │  │
│  │    • Receive: video_url                                 │  │
│  │ 4. Download video from URL                              │  │
│  │ Processing Time: 5-20 minutes                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Option B: D-ID API                                       │  │
│  │ ─────────────────────                                     │  │
│  │ 1. POST /talks                                           │  │
│  │    • Send: source_url (image), script (text) OR audio   │  │
│  │    • Receive: talk_id                                    │  │
│  │ 2. Poll GET /talks/{talk_id}                            │  │
│  │    • Wait for status: "done"                             │  │
│  │    • Receive: result_url                                 │  │
│  │ 3. Download video from URL                              │  │
│  │ Processing Time: 1-5 minutes                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Option C: DreamTalk (Local)                              │  │
│  │ ─────────────────────                                     │  │
│  │ 1. Run: python inference.py                             │  │
│  │    • Args: --driven_audio, --source_image               │  │
│  │    • Process locally on GPU                              │  │
│  │ 2. Wait for subprocess completion                        │  │
│  │ 3. Locate output video file                             │  │
│  │ Processing Time: 30-90 sec per minute                    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Parallel Processing: Yes (ThreadPoolExecutor)                │
│  Max Workers: 3-5 (configurable)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Load Scene                                            │
│  ─────────────────────                                          │
│  Component: SceneManager                                       │
│  External APIs: None                                            │
│  Output: Scene object with background image                    │
│                                                                 │
│  • Load scene config from config/scenes.yaml                   │
│  • Load background image                                        │
│  • Prepare scene for composition                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Compose Final Video                                   │
│  ─────────────────────                                          │
│  Component: VideoComposer                                      │
│  External APIs: None (uses FFmpeg locally)                    │
│  Output: Final MP4 video file                                  │
│                                                                 │
│  Layout Options:                                               │
│  • Switching: Show one avatar at a time                        │
│  • Side-by-side: Multiple avatars simultaneously               │
│  • Picture-in-picture: Main + inset                            │
│  • Grid: All avatars in grid layout                           │
│                                                                 │
│  Process:                                                      │
│  1. Load avatar videos                                         │
│  2. Load background scene                                      │
│  3. Apply layout logic (switching/transitions)                 │
│  4. Use FFmpeg to compose:                                    │
│     • Overlay avatars on background                            │
│     • Sync with audio                                          │
│     • Apply transitions                                        │
│     • Encode to MP4 (H.264)                                   │
│  5. Save final video                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT: Final Video                          │
│              (examples/outputs/*.mp4)                           │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
Script File
    │
    ├─→ ScriptParser
    │       │
    │       └─→ ParsedScript (segments)
    │               │
    │               ├─→ PersonaEngine
    │               │       │
    │               │       └─→ Persona Objects
    │               │               │
    │               │               ├─→ Voice Config (ElevenLabs voice_id)
    │               │               └─→ Avatar Config (HeyGen/D-ID/DreamTalk)
    │               │
    │               └─→ TTSEngine
    │                       │
    │                       ├─→ ElevenLabs API ──→ MP3 Audio Files
    │                       │       (or Azure Speech)
    │                       │
    │                       └─→ AudioMixer ──→ Mixed Audio File
    │
    └─→ AvatarGenerator
            │
            ├─→ HeyGen API ──→ MP4 Video Files
            │       (or D-ID API)
            │       (or DreamTalk local)
            │
            └─→ VideoComposer
                    │
                    ├─→ SceneManager ──→ Background Image
                    │
                    └─→ FFmpeg ──→ Final MP4 Video
```

## API Call Sequence (Example: HeyGen)

```
1. User initiates generation
   │
2. Pipeline starts
   │
3. Script parsed (no API calls)
   │
4. Personas loaded (no API calls)
   │
5. TTS Generation (ElevenLabs API)
   │   ├─→ POST /text-to-speech/{voice_id} (segment 1)
   │   ├─→ POST /text-to-speech/{voice_id} (segment 2)
   │   └─→ ... (one call per segment)
   │
6. Audio mixed (no API calls)
   │
7. Avatar Generation (HeyGen API)
   │   ├─→ POST /v2/video/generate (avatar 1)
   │   │   └─→ Receive: video_id_1
   │   ├─→ POST /v2/video/generate (avatar 2)
   │   │   └─→ Receive: video_id_2
   │   │
   │   ├─→ GET /v2/video/{video_id_1} (polling)
   │   │   └─→ Status: "processing"
   │   ├─→ GET /v2/video/{video_id_2} (polling)
   │   │   └─→ Status: "processing"
   │   │
   │   ├─→ GET /v2/video/{video_id_1} (polling)
   │   │   └─→ Status: "completed", video_url_1
   │   ├─→ GET /v2/video/{video_id_2} (polling)
   │   │   └─→ Status: "completed", video_url_2
   │   │
   │   └─→ Download videos from URLs
   │
8. Scene loaded (no API calls)
   │
9. Video composed (FFmpeg - local)
   │
10. Final video ready
```

## API Dependencies

### Critical Path Dependencies
1. **ElevenLabs API** → Required for TTS (unless using Azure)
2. **HeyGen/D-ID/DreamTalk** → Required for avatar generation
3. **FFmpeg** → Required for video composition (local, not API)

### Optional Dependencies
- **Azure Speech Service** → Alternative TTS (if ElevenLabs unavailable)
- **Webhook Server** → For real-time HeyGen callbacks (optional, falls back to polling)

## Error Handling

### API Failures
- **ElevenLabs Failure:** Falls back to Azure Speech (if configured)
- **HeyGen Failure:** No fallback (errors immediately per user requirement)
- **D-ID Failure:** No fallback (errors immediately per user requirement)
- **DreamTalk Failure:** No fallback (errors immediately per user requirement)

### Retry Logic
- **HeyGen:** 3 retries with exponential backoff for transient errors
- **D-ID:** No retry logic (fails immediately)
- **ElevenLabs:** No retry logic (fails immediately)

## Performance Characteristics

### Processing Times (Approximate)
- **Script Parsing:** < 1 second
- **Persona Loading:** < 1 second
- **TTS Generation:** 1-5 seconds per segment (ElevenLabs)
- **Audio Mixing:** < 1 second
- **Avatar Generation:**
  - HeyGen: 5-20 minutes per video
  - D-ID: 1-5 minutes per video
  - DreamTalk: 30-90 seconds per minute of video
- **Video Composition:** 10-60 seconds (depends on video length)

### Parallelization
- **TTS Generation:** Sequential (can be parallelized)
- **Avatar Generation:** Parallel (3-5 workers by default)
- **Video Composition:** Sequential (single final video)

## Cost Considerations

### API Costs (Per Video Generation)
- **ElevenLabs:** ~$0.18 per 1000 characters (varies by plan)
- **HeyGen:** ~$0.10-0.50 per video (varies by resolution/quality)
- **D-ID:** ~$0.05-0.20 per video (varies by plan)
- **DreamTalk:** $0 (runs locally)
- **Azure Speech:** ~$0.015 per 1000 characters

### Example Cost Calculation
For a 5-minute podcast with 2 personas:
- **Script:** ~500 words = ~2500 characters
- **ElevenLabs:** ~$0.45 (2500 chars × $0.18/1000)
- **HeyGen:** ~$0.20-1.00 (2 videos)
- **Total:** ~$0.65-1.45 per video

## Configuration Files

### API Keys Location
- **Primary:** `config/config.yaml` → `api.*.api_key`
- **Environment Variables:** `.env` file (overrides config)
- **Priority:** Environment variables > config.yaml

### Provider Selection
- **TTS:** `config.yaml` → `tts.engine` (default: "elevenlabs")
- **Avatar:** `config.yaml` → `avatar.engine` (default: "dreamtalk")
- **Per-Persona Override:** `config/personas.yaml` → `persona.avatar.engine`

## Monitoring and Logging

### Progress Tracking
- Progress logged to `.cache/progress.log`
- Real-time progress callbacks (0.0-1.0)
- Timestamped log entries

### API Monitoring
- HeyGen: Polling with progress updates
- D-ID: Polling with progress updates
- DreamTalk: Subprocess output streaming

## Security Considerations

### API Key Storage
- **Never commit API keys to git**
- Use `.env` file (in `.gitignore`)
- Or use environment variables

### Data Privacy
- **ElevenLabs:** Text sent to cloud API
- **HeyGen:** Audio/text sent to cloud API
- **D-ID:** Audio/text sent to cloud API
- **DreamTalk:** All processing local (no data leaves machine)

## Troubleshooting

### Common Issues
1. **API Key Invalid:** Check `config.yaml` or `.env`
2. **Rate Limiting:** Wait or upgrade API plan
3. **Network Timeout:** Check internet connection
4. **DreamTalk Not Found:** Verify installation path
5. **FFmpeg Missing:** Install FFmpeg system dependency

### Debug Steps
1. Check `.cache/progress.log` for detailed errors
2. Verify API keys with test scripts
3. Test individual components separately
4. Check API status pages for outages

## Future Enhancements

### Planned Improvements
- Parallel TTS generation
- Better error recovery
- Cost tracking and reporting
- API usage analytics
- Local TTS options (Coqui TTS)

