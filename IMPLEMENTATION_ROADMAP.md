# Implementation Roadmap
## The Talking Heads - Phase 1 MVP

## Current Status: ✅ Project Setup Complete

**Created:**
- ✅ Project directory structure
- ✅ Configuration files (config.yaml, personas.yaml, scenes.yaml)
- ✅ CLI framework (basic commands)
- ✅ Requirements.txt with dependencies
- ✅ Example scripts
- ✅ Documentation (README, ARCHITECTURE, PROJECT_SETUP, START_HERE)

## Next Steps: Phase 1 Implementation

### Step 1: Core Script Parser (Week 1, Days 1-2)

**File:** `src/core/script_parser.py`

**Implementation:**
```python
class ScriptParser:
    def parse(self, script_text: str) -> Dict:
        # 1. Parse title (first line with #)
        # 2. Detect persona tags (ALICE:, BOB:, etc.)
        # 3. Segment script by persona
        # 4. Extract expressions/gestures from annotations
        # 5. Return structured data with segments
```

**Features:**
- Detect persona tags using regex
- Handle multi-line dialogue
- Extract expressions: `[EXPRESSION:happy]`
- Extract gestures: `[GESTURE:point]`
- Generate timeline with speaker assignments

**Testing:**
- Unit tests for script parsing
- Edge cases (missing tags, empty lines, etc.)

---

### Step 2: Persona Engine (Week 1, Days 3-4)

**File:** `src/core/persona_engine.py`

**Implementation:**
```python
class PersonaEngine:
    def load_personas(self, config_path: Path):
        # Load from config/personas.yaml
    
    def get_persona(self, name: str) -> Persona:
        # Get persona configuration
    
    def validate_personas(self, script_segments: List[Segment]):
        # Ensure all personas in script are configured
```

**Features:**
- Load persona configurations from YAML
- Persona registry (lookup by name)
- Validation (ensure script personas exist)
- Persona state tracking (who's speaking)

**Testing:**
- Unit tests for persona loading
- Validation tests

---

### Step 3: TTS Engine Integration (Week 1, Days 5-7)

**File:** `src/core/tts_engine.py`

**Implementation:**
```python
class TTSEngine:
    def __init__(self, config: Dict):
        # Initialize API clients
    
    def generate_persona_audio(self, persona: Persona, text: str) -> Path:
        # Generate audio for specific persona
        # Return audio file path and duration
    
    def generate_multiple(self, segments: List[Segment]) -> List[AudioSegment]:
        # Generate audio for all personas
        # Return list of audio segments with timing
```

**Features:**
- Support ElevenLabs API (primary)
- Support Azure Speech Service (alternative)
- Support gTTS (fallback)
- Per-persona voice configuration
- Timing tracking for each segment
- Audio caching (cache by text + voice)

**API Integration:**
1. **ElevenLabs:**
   - Install: `pip install elevenlabs`
   - API: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
   - Docs: https://elevenlabs.io/docs

2. **Azure Speech:**
   - Install: `pip install azure-cognitiveservices-speech`
   - API: Azure Speech SDK
   - Docs: https://azure.microsoft.com/speech

**Testing:**
- Mock API responses
- Integration tests with real API (optional)
- Error handling (API failures, rate limits)

---

### Step 4: Audio Mixer (Week 2, Days 1-2)

**File:** `src/core/audio_mixer.py`

**Implementation:**
```python
class AudioMixer:
    def mix_persona_tracks(self, audio_segments: List[AudioSegment]) -> Path:
        # Concatenate persona audio tracks
        # Apply timing and synchronization
        # Handle silence/padding between segments
        # Generate final audio track
```

**Features:**
- Concatenate multiple audio files
- Preserve exact timing for video sync
- Add silence/padding between segments (optional)
- Mix with background music (future)
- Apply ducking/volume normalization

**Dependencies:**
- `pydub` for audio manipulation
- `ffmpeg` for audio processing

**Testing:**
- Unit tests for concatenation
- Timing accuracy tests

---

### Step 5: Avatar Generator Integration (Week 2, Days 3-5)

**File:** `src/core/avatar_generator.py`

**Implementation:**
```python
class AvatarGenerator:
    def __init__(self, config: Dict):
        # Initialize API clients (HeyGen/D-ID)
    
    def generate_persona_avatar(self, persona: Persona, audio_path: Path, 
                                 expression: str, gesture: str) -> Path:
        # Generate avatar video for persona
        # Apply expression and gesture
        # Return video file path
    
    def generate_multiple(self, segments: List[Segment], audio_segments: List[AudioSegment]) -> List[AvatarVideo]:
        # Generate avatars for all personas
        # Return list of avatar videos with timing
```

**Features:**
- Support HeyGen API (primary)
- Support D-ID Creative Reality API (alternative)
- Per-persona avatar configuration
- Expression application
- Gesture application
- Parallel generation (for multiple personas)

**API Integration:**
1. **HeyGen:**
   - API: `https://api.heygen.com/v1`
   - Docs: https://docs.heygen.com
   - Features: Cartoon avatars, expressions, gestures

2. **D-ID Creative Reality:**
   - API: `https://api.d-id.com`
   - Docs: https://docs.d-id.com
   - Features: Full-body avatars, expressions

**Testing:**
- Mock API responses
- Integration tests with real API (optional)
- Error handling (API failures, rate limits)

---

### Step 6: Scene Manager (Week 2, Day 6)

**File:** `src/core/scene_manager.py`

**Implementation:**
```python
class SceneManager:
    def load_scenes(self, config_path: Path):
        # Load from config/scenes.yaml
    
    def get_scene(self, name: str) -> Scene:
        # Get scene configuration
    
    def get_background_path(self, scene: Scene) -> Path:
        # Return path to background image
```

**Features:**
- Load scene configurations from YAML
- Scene registry (lookup by name)
- Background image loading
- Scene metadata (lighting, style, etc.)

**Testing:**
- Unit tests for scene loading
- File existence validation

---

### Step 7: Video Composer (Week 3, Days 1-4)

**File:** `src/core/video_composer.py`

**Implementation:**
```python
class VideoComposer:
    def compose(self, audio_path: Path, avatar_videos: List[AvatarVideo],
                scene: Scene, layout: str) -> Path:
        # Compose final video with multiple avatars
        # Handle layout (switching, side_by_side, etc.)
        # Apply transitions
        # Synchronize with audio
        # Generate final video
```

**Features:**
- Multiple layout modes:
  - **Switching:** Show only active speaker (recommended for MVP)
  - **Side-by-Side:** All avatars visible
  - **Picture-in-Picture:** Active speaker large, others small
  - **Grid:** All avatars in grid (3+ personas)
- Speaker switching based on timeline
- Transitions (fade, cut, smooth)
- Background scene overlay
- Audio synchronization

**FFmpeg Commands:**
- Multi-input video composition
- Overlay filters for avatars
- Transition effects
- Audio mapping

**Testing:**
- Unit tests for layout logic
- Integration tests with sample videos
- Timing synchronization tests

---

### Step 8: Main Pipeline Integration (Week 3, Days 5-7)

**File:** `src/core/pipeline.py` (new)

**Implementation:**
```python
class Pipeline:
    def create_podcast(self, script_path: Path, scene_name: str,
                       layout: str, output_name: str) -> Path:
        # 1. Parse script
        # 2. Load personas
        # 3. Generate TTS audio for all personas
        # 4. Mix audio tracks
        # 5. Generate avatars for all personas
        # 6. Compose final video
        # 7. Return output video path
```

**Features:**
- Orchestrate entire pipeline
- Error handling at each step
- Progress reporting
- Cleanup temporary files
- Return final video path

---

### Step 9: CLI Integration (Week 4, Days 1-2)

**File:** `src/cli/main.py` (update `create` command)

**Implementation:**
```python
@app.command()
def create(...):
    # 1. Load configuration
    # 2. Initialize pipeline
    # 3. Run pipeline
    # 4. Show success message
    # 5. Return output path
```

**Features:**
- Full CLI integration
- Progress bars (using `rich`)
- Error messages
- Output file location

---

### Step 10: Testing & Refinement (Week 4, Days 3-5)

**Tasks:**
- End-to-end tests
- Test with example scripts
- Bug fixes
- Performance optimization
- Documentation updates

---

## Quick Start Implementation Order

### Priority 1: Core Functionality
1. ✅ Script Parser (Step 1)
2. ✅ Persona Engine (Step 2)
3. ✅ TTS Engine (Step 3)
4. ✅ Audio Mixer (Step 4)
5. ✅ Main Pipeline (Step 8) - with placeholder avatar generation

### Priority 2: Avatar & Video
6. ✅ Avatar Generator (Step 5)
7. ✅ Scene Manager (Step 6)
8. ✅ Video Composer (Step 7)

### Priority 3: Integration & Polish
9. ✅ CLI Integration (Step 9)
10. ✅ Testing & Refinement (Step 10)

---

## API Keys Setup

### 1. HeyGen API
1. Sign up: https://www.heygen.com
2. Get API key from dashboard
3. Add to `.env`: `HEYGEN_API_KEY=your_key_here`
4. Check available cartoon avatars in dashboard

### 2. ElevenLabs API
1. Sign up: https://elevenlabs.io
2. Get API key from dashboard
3. Add to `.env`: `ELEVENLABS_API_KEY=your_key_here`
4. Create or select voices for each persona

### 3. D-ID API (Alternative)
1. Sign up: https://www.d-id.com
2. Get API key from dashboard
3. Add to `.env`: `DID_API_KEY=your_key_here`

---

## Testing Strategy

### Unit Tests
- Script parser with various formats
- Persona engine loading
- TTS engine API calls (mocked)
- Audio mixer concatenation
- Video composer layout logic

### Integration Tests
- End-to-end pipeline with 2 personas
- API integration (with test API keys)
- Multi-avatar video composition

### E2E Tests
- Full podcast generation
- Different persona counts (1-5)
- Different layouts
- Different scenes

---

## Next Phase: Phase 2 - Enhanced Cartoon

After Phase 1 MVP:
- Advanced expressions
- Expanded gesture library
- Animated backgrounds
- Audio-driven automatic expressions
- Support for 3-5 personas

---

## Resources

- **HeyGen API Docs:** https://docs.heygen.com
- **D-ID API Docs:** https://docs.d-id.com
- **ElevenLabs API Docs:** https://elevenlabs.io/docs
- **Azure Speech Docs:** https://azure.microsoft.com/speech
- **FFmpeg Docs:** https://ffmpeg.org/documentation.html
- **pydub Docs:** https://github.com/jiaaro/pydub

---

## Questions?

If you need help with implementation, check:
1. [PROJECT_SETUP.md](PROJECT_SETUP.md) - Setup details
2. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. [docs/SCRIPT_FORMAT.md](docs/SCRIPT_FORMAT.md) - Script format
4. API documentation links above

