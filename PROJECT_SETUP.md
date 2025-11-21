# The Talking Heads - Project Setup Guide
## AI-Generated Podcast with Multiple Personas

## Project Overview

**The Talking Heads** is an AI-powered podcast generation system that creates multi-persona video podcasts from a script. 

### Key Features
- **1-5 Different Personas** per episode
- **Multi-Voice Support** with distinct voices for each persona
- **Animated Avatars** with expressions and gestures
- **Background Scenes** with customizable environments
- **Phased Visual Evolution:** Start cartoon → Evolve to realistic
- **Script-Driven** workflow with persona assignments

### Target Use Cases
- **Podcast Production:** Automated multi-host podcasts
- **Educational Content:** Interactive lessons with multiple instructors
- **Corporate Training:** Multi-presenter video content
- **Entertainment:** Talk shows, debates, interviews

---

## Project Phases

### Phase 1: MVP - Cartoon Avatars (Weeks 1-4)
**Goal:** Working multi-persona podcast with cartoon-style avatars

**Features:**
- ✅ 2-3 personas per episode
- ✅ Cartoon/stylized avatars (2D illustrated style)
- ✅ Basic expressions (happy, neutral, surprised)
- ✅ Simple gestures (point, wave)
- ✅ Background scenes (static or animated)
- ✅ Script parsing with persona assignments
- ✅ Multi-voice TTS (different voices per persona)

**Technology Stack:**
- **Avatar:** Cloud API (HeyGen/D-ID Creative Reality) with cartoon avatar selection
- **TTS:** Multiple voices (ElevenLabs, Azure, or Coqui)
- **Composition:** FFmpeg for multi-avatar layout
- **Script:** Markdown with persona tags

### Phase 2: Enhanced Cartoon (Weeks 5-8)
**Goal:** Richer cartoon experience with more expressions/gestures

**Features:**
- ✅ 3-5 personas support
- ✅ Advanced expressions (happy, sad, excited, concerned, thinking)
- ✅ Expanded gesture library (10+ gestures)
- ✅ Animated backgrounds
- ✅ Smooth transitions between speakers
- ✅ Audio-driven automatic expressions

### Phase 3: Realistic Transition (Weeks 9-12)
**Goal:** Add realistic avatar option alongside cartoon

**Features:**
- ✅ Realistic avatar option (photorealistic)
- ✅ User choice: cartoon or realistic
- ✅ Seamless switching between styles
- ✅ Same features work for both styles

### Phase 4: Advanced Realistic (Weeks 13-16)
**Goal:** Full realistic experience with advanced features

**Features:**
- ✅ High-quality realistic avatars
- ✅ Advanced expressions and micro-expressions
- ✅ Context-aware gestures
- ✅ Emotion detection from audio
- ✅ Professional-grade output

---

## Technology Stack

### Phase 1 MVP Stack

**Avatar Generation:**
- **Primary:** HeyGen API (cartoon avatars) or D-ID Creative Reality
- **Alternative:** Ready Player Me (3D cartoon avatars)
- **Local Option (Future):** 2D rigging (Live2D, Adobe Character Animator)

**Text-to-Speech:**
- **Primary:** ElevenLabs (multiple voices, excellent quality)
- **Alternative:** Azure Speech Service (multiple voices)
- **Local Option:** Coqui TTS (multiple speakers)

**Video Composition:**
- **FFmpeg** for multi-avatar layout
- **OpenCV** for image processing
- **PIL/Pillow** for image manipulation

**Script Processing:**
- **Markdown parser** for persona tags
- **Python** for processing logic

**Audio Processing:**
- **pydub** for audio mixing
- **librosa** for audio analysis (for future emotion detection)

---

## Project Structure

```
The_Talking_Heads/
├── src/
│   ├── core/
│   │   ├── script_parser.py       # Parse script with persona assignments
│   │   ├── persona_engine.py      # Persona management and coordination
│   │   ├── avatar_generator.py    # Generate avatars (cartoon/realistic)
│   │   ├── tts_engine.py          # Multi-voice TTS generation
│   │   ├── audio_mixer.py         # Mix multiple persona audio tracks
│   │   ├── video_composer.py      # Compose multi-avatar video
│   │   └── scene_manager.py       # Background scene management
│   ├── models/
│   │   ├── persona.py             # Persona data models
│   │   ├── script.py              # Script data models
│   │   └── scene.py               # Scene data models
│   ├── utils/
│   │   ├── config.py              # Configuration management
│   │   ├── api_clients.py         # API client wrappers
│   │   └── file_utils.py          # File handling utilities
│   └── cli/
│       └── main.py                # CLI interface
├── config/
│   ├── config.yaml                # Main configuration
│   ├── personas.yaml              # Persona definitions
│   └── scenes.yaml                # Scene definitions
├── examples/
│   ├── scripts/                   # Example scripts
│   └── outputs/                   # Generated videos
├── tests/
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
├── docs/
│   ├── API.md                     # API documentation
│   ├── PERSONAS.md                # Persona creation guide
│   └── SCRIPT_FORMAT.md           # Script format documentation
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup
├── README.md                      # Project readme
└── .env.example                   # Environment variables template
```

---

## Initial Setup Steps

### 1. Create Project Directory Structure

```bash
mkdir The_Talking_Heads
cd The_Talking_Heads
mkdir -p src/{core,models,utils,cli}
mkdir -p config examples/{scripts,outputs} tests/{unit,integration,e2e} docs
```

### 2. Initialize Python Project

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install --upgrade pip
```

### 3. Install Initial Dependencies

Create `requirements.txt`:
- Core framework: `typer`, `rich`, `pydantic`
- API clients: `requests`, `httpx`
- Audio: `pydub`, `librosa`
- Video: `opencv-python`, `pillow`
- Config: `pyyaml`, `python-dotenv`

### 4. Set Up Configuration System

- Create `config/config.yaml` with default settings
- Create `config/personas.yaml` with initial persona templates
- Create `config/scenes.yaml` with background scenes
- Create `.env.example` for API keys

### 5. Set Up Script Format

Define script format with persona assignments:
```markdown
# Episode Title

ALICE: Hello everyone, welcome to the podcast!
BOB: Thanks for having us, Alice.
ALICE: Today we'll discuss AI with our guest, Charlie.
CHARLIE: Excited to be here!
```

### 6. Create Initial Core Modules

- `ScriptParser`: Parse script with persona tags
- `PersonaEngine`: Manage multiple personas
- `AvatarGenerator`: Generate avatars (start with API integration)
- `TTSEngine`: Multi-voice TTS
- `VideoComposer`: Multi-avatar video composition

---

## Configuration Examples

### `config/personas.yaml`

```yaml
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_abc123"
      style: "conversational"
    avatar:
      engine: "heygen"
      avatar_id: "cartoon_female_01"
      style: "cartoon"
    expressions:
      enabled: true
      default: "neutral"
    gestures:
      enabled: true
      frequency: "moderate"
  
  bob:
    name: "Bob"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_xyz789"
      style: "professional"
    avatar:
      engine: "heygen"
      avatar_id: "cartoon_male_01"
      style: "cartoon"
    expressions:
      enabled: true
      default: "neutral"
    gestures:
      enabled: true
      frequency: "moderate"
```

### `config/scenes.yaml`

```yaml
scenes:
  studio:
    name: "Podcast Studio"
    background_url: "scenes/studio_background.jpg"
    style: "professional"
    lighting: "warm"
  
  classroom:
    name: "Classroom"
    background_url: "scenes/classroom_background.jpg"
    style: "educational"
    lighting: "bright"
  
  living_room:
    name: "Living Room"
    background_url: "scenes/living_room_background.jpg"
    style: "casual"
    lighting: "cozy"
```

---

## Next Steps

1. **Create project structure** (done above)
2. **Set up Python environment** and install dependencies
3. **Create initial configuration files**
4. **Implement script parser** with persona detection
5. **Integrate first API** (HeyGen or D-ID for avatars)
6. **Implement multi-voice TTS** (ElevenLabs or Azure)
7. **Create video composition** for multi-avatar layout
8. **Test with example script** (2-3 personas)
9. **Iterate and refine**

---

## Resources

- **HeyGen API Docs:** https://docs.heygen.com
- **D-ID Creative Reality:** https://docs.d-id.com
- **ElevenLabs API:** https://elevenlabs.io/docs
- **Azure Speech Service:** https://azure.microsoft.com/speech
- **Ready Player Me:** https://readyplayer.me/docs

---

## Questions to Resolve

1. **Script Format:** Exact format for persona assignments?
2. **Avatar Layout:** Side-by-side, picture-in-picture, or switching?
3. **Transition Style:** Fade, cut, or smooth?
4. **API Priority:** Which API to integrate first (HeyGen vs D-ID)?
5. **Voice Priority:** Which TTS to use (ElevenLabs vs Azure)?

Let me know which direction you want to start with, and I'll help you set up the initial project structure and code!

