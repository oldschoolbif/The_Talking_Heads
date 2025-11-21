# The Talking Heads - System Architecture

## Overview

**The Talking Heads** generates multi-persona video podcasts from scripts. The system coordinates multiple personas (1-5), each with their own voice, avatar, expressions, and gestures, into a cohesive video podcast.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Script Input                             │
│         (Markdown with persona assignments)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Script Parser                               │
│   - Parse persona assignments (ALICE:, BOB:, etc.)          │
│   - Segment script by persona                                │
│   - Extract dialogue, expressions, gestures                  │
│   - Generate timeline with speaker assignments               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Persona Engine                               │
│   - Load persona configurations                              │
│   - Coordinate multiple personas                             │
│   - Manage persona states                                    │
│   - Handle transitions                                       │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬───────────────┬───────────────┐
    ▼                 ▼               ▼               ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ TTS     │    │ TTS     │    │ TTS     │    │ TTS     │
│ Engine  │    │ Engine  │    │ Engine  │    │ Engine  │
│ (Alice) │    │ (Bob)   │    │ (Charlie│    │ (etc.)  │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │               │              │
     └──────────────┴───────────────┴──────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│               Audio Mixer                                   │
│   - Concatenate persona audio tracks                        │
│   - Apply timing and synchronization                        │
│   - Mix with background music (optional)                    │
│   - Generate final audio track                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Avatar Generator (Parallel)                       │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│   │ Avatar  │  │ Avatar  │  │ Avatar  │  │ Avatar  │      │
│   │(Alice)  │  │ (Bob)   │  │(Charlie)│  │ (etc.)  │      │
│   │         │  │         │  │         │  │         │      │
│   │ Voice   │  │ Voice   │  │ Voice   │  │ Voice   │      │
│   │ + Expr  │  │ + Expr  │  │ + Expr  │  │ + Expr  │      │
│   │ + Gest  │  │ + Gest  │  │ + Gest  │  │ + Gest  │      │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘      │
└────────┼────────────┼────────────┼────────────┼───────────┘
         │            │            │            │
         └────────────┴────────────┴────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Video Composer                                  │
│   - Load background scene                                    │
│   - Position multiple avatars (layout)                       │
│   - Synchronize avatar switching with audio                 │
│   - Apply transitions                                        │
│   - Generate final video                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Output Video                               │
│            (Multi-persona podcast)                           │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Script Parser (`src/core/script_parser.py`)

**Purpose:** Parse script with persona assignments and extract dialogue segments.

**Responsibilities:**
- Detect persona tags (ALICE:, BOB:, etc.)
- Segment script by persona
- Extract expressions and gestures from annotations
- Generate timeline with speaker assignments
- Validate script format

**Output:**
```python
{
  "title": "Episode Title",
  "segments": [
    {
      "persona": "ALICE",
      "text": "Hello everyone!",
      "expression": "happy",
      "gesture": None,
      "timestamp": 0.0,
      "duration": 2.5
    },
    {
      "persona": "BOB",
      "text": "Thanks for having us.",
      "expression": "neutral",
      "gesture": "wave",
      "timestamp": 2.5,
      "duration": 1.8
    }
  ]
}
```

### 2. Persona Engine (`src/core/persona_engine.py`)

**Purpose:** Manage multiple personas and coordinate their interactions.

**Responsibilities:**
- Load persona configurations from `config/personas.yaml`
- Coordinate persona state (who's speaking, who's active)
- Handle persona transitions
- Map expressions/gestures to persona capabilities
- Manage persona-specific settings

**Key Features:**
- Persona registry (load all configured personas)
- Active persona tracking
- Transition logic (fade, cut, overlap)
- Expression/gesture mapping

### 3. TTS Engine (`src/core/tts_engine.py`)

**Purpose:** Generate speech for multiple personas with distinct voices.

**Responsibilities:**
- Support multiple TTS providers (ElevenLabs, Azure, Coqui)
- Generate audio for each persona segment
- Apply persona-specific voice settings
- Track timing for each audio segment
- Cache generated audio

**Multi-Voice Support:**
- Each persona can use different TTS provider
- Each persona has distinct voice ID/settings
- Generate segments in parallel (optional)
- Return audio tracks with timing metadata

### 4. Audio Mixer (`src/core/audio_mixer.py`)

**Purpose:** Combine multiple persona audio tracks into final audio.

**Responsibilities:**
- Concatenate persona audio segments with proper timing
- Handle silence/padding between segments
- Mix with background music (optional)
- Apply ducking/volume normalization
- Generate final synchronized audio track

**Timing Critical:**
- Must preserve exact timing for video sync
- Handle overlapping speech (if supported)
- Apply crossfades for smooth transitions

### 5. Avatar Generator (`src/core/avatar_generator.py`)

**Purpose:** Generate animated avatar videos for each persona.

**Responsibilities:**
- Integrate with avatar APIs (HeyGen, D-ID Creative Reality)
- Generate avatar video for each persona segment
- Apply expressions and gestures
- Handle cartoon vs realistic styles
- Return avatar videos with timing metadata

**Phase 1 (Cartoon):**
- Use HeyGen/D-ID with cartoon avatar selection
- Basic expressions (happy, neutral, surprised)
- Simple gestures (point, wave, emphasize)

**Phase 3+ (Realistic):**
- Switch to realistic avatar option
- Advanced expressions
- Expanded gesture library

### 6. Scene Manager (`src/core/scene_manager.py`)

**Purpose:** Manage background scenes for podcasts.

**Responsibilities:**
- Load scene configurations from `config/scenes.yaml`
- Provide scene images/animations
- Handle scene transitions (if animated)
- Apply scene-specific layouts

**Scene Types:**
- Static images (studio, classroom, living room)
- Animated backgrounds (future)
- Custom scene uploads

### 7. Video Composer (`src/core/video_composer.py`)

**Purpose:** Compose final video with multiple avatars and background.

**Responsibilities:**
- Load background scene
- Position multiple avatars (layout system)
- Switch between active avatars based on timeline
- Apply transitions (fade, cut, smooth)
- Synchronize with audio track
- Generate final video

**Layout Options:**
- **Side-by-Side:** All avatars visible simultaneously
- **Picture-in-Picture:** Active speaker large, others small
- **Single Speaker:** Show only active speaker (switching)
- **Grid Layout:** All avatars in grid (for 3+ personas)

**Switching Logic:**
- Track which persona is speaking at each timestamp
- Show/hide avatars based on active speaker
- Apply smooth transitions between speakers
- Handle rapid speaker changes

## Data Flow

### 1. Script Input → Parsed Segments
```
Script Text
  → Script Parser
  → Persona Segments (with timing, expressions, gestures)
```

### 2. Parsed Segments → Audio Tracks
```
Persona Segments
  → TTS Engine (per persona)
  → Individual Audio Tracks (per persona)
  → Audio Mixer
  → Final Audio Track (synchronized)
```

### 3. Parsed Segments + Audio → Avatar Videos
```
Persona Segments + Audio
  → Avatar Generator (per persona, parallel)
  → Avatar Videos (per persona, with expressions/gestures)
```

### 4. Avatar Videos + Audio + Scene → Final Video
```
Avatar Videos + Audio + Scene
  → Video Composer
  → Layout + Switching Logic
  → Final Video (multi-persona podcast)
```

## Configuration System

### Persona Configuration (`config/personas.yaml`)

Each persona has:
- **Name:** Display name
- **Voice:** TTS engine and voice settings
- **Avatar:** Avatar engine and appearance settings
- **Expressions:** Enabled expressions and preferences
- **Gestures:** Enabled gestures and frequency

### Scene Configuration (`config/scenes.yaml`)

Each scene has:
- **Name:** Display name
- **Background:** Image/URL for background
- **Style:** Visual style (professional, casual, etc.)
- **Lighting:** Lighting characteristics

### Main Configuration (`config/config.yaml`)

Global settings:
- **API Keys:** HeyGen, D-ID, ElevenLabs, Azure
- **Default Settings:** Default persona, scene, quality
- **Output Settings:** Video quality, format, resolution
- **Layout Settings:** Default avatar layout

## Technology Choices

### Phase 1 MVP

**Avatar Generation:**
- **HeyGen API** or **D-ID Creative Reality API**
- Cartoon avatar selection
- Cloud-based (no local models)

**TTS:**
- **ElevenLabs API** (multiple voices, excellent quality)
- **Azure Speech Service** (alternative)
- **Coqui TTS** (local option)

**Video Composition:**
- **FFmpeg** for video processing
- **OpenCV** for image manipulation
- **PIL/Pillow** for image processing

### Phase 3+ (Realistic)

**Avatar Generation:**
- Same APIs with realistic avatar selection
- Or move to local models (VideoRetalking, GeneFace++)

**Enhanced Features:**
- Audio-driven emotion detection
- Context-aware gestures
- Advanced expression blending

## Performance Considerations

### Parallel Processing

- **Avatar Generation:** Generate multiple avatars in parallel
- **TTS Generation:** Generate persona audio in parallel (optional)
- **Video Composition:** Process frames in parallel

### Caching

- **TTS Cache:** Cache generated audio by text + voice
- **Avatar Cache:** Cache avatar videos by audio + persona
- **Scene Cache:** Cache processed scene images

### Optimization

- **API Rate Limits:** Batch API calls, implement retry logic
- **Video Encoding:** Use GPU encoding (NVENC) if available
- **Memory Management:** Process in chunks for long episodes

## Testing Strategy

### Unit Tests
- Script parser with various formats
- Persona engine coordination
- Audio mixer concatenation
- Video composer layout

### Integration Tests
- End-to-end pipeline with 2-3 personas
- API integration (mock responses)
- Multi-avatar video composition

### E2E Tests
- Full podcast generation
- Different persona counts (1-5)
- Different layouts
- Different scenes

## Future Enhancements

- **Real-time Generation:** Generate podcasts in real-time
- **Interactive Mode:** User can trigger expressions/gestures
- **Custom Avatars:** User-uploaded avatar images
- **Animation Library:** Expandable gesture/expression library
- **AI-Powered Gestures:** LLM-driven gesture selection
- **Live Streaming:** Stream generated podcasts live

