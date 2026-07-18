# 🚀 The Talking Heads - Getting Started

Welcome to **The Talking Heads**! This guide will help you get started with creating AI-generated multi-persona podcasts.

## 📋 Prerequisites

1. **Python 3.10+** installed
2. **FFmpeg** installed (for video processing)
3. **API Keys** for avatar and TTS services:
   - HeyGen API key (or D-ID API key)
   - ElevenLabs API key (or Azure Speech Service key)

## 🔧 Installation

### 1. Clone and Navigate

```bash
cd The_Talking_Heads
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure API Keys

✅ **API keys are already configured!** Your `.env` file contains:
- HeyGen API Key
- D-ID API Key
- ElevenLabs API Key
- Azure Speech Key and Region

If you need to update keys, run:
```bash
python scripts/setup_api_keys.py
```

Or manually edit `.env` file:
```bash
# Edit .env and update your API keys
# - HEYGEN_API_KEY or DID_API_KEY
# - ELEVENLABS_API_KEY or AZURE_SPEECH_KEY
```

### 5. Verify Installation

```bash
python -m src.cli.main version
python -m src.cli.main list_personas
python -m src.cli.main list_scenes
```

## 📝 Create Your First Script

Create a script file (e.g., `my_podcast.txt`):

```markdown
# My First Podcast

ALICE: Hello everyone, welcome to The Talking Heads!
BOB: Thanks for joining us!
ALICE: Today we'll discuss AI and technology.
BOB: That sounds great!
```

## 🎬 Generate Your Podcast

```bash
python -m src.cli.main create my_podcast.txt --scene studio --layout switching
```

## 📚 Next Steps

1. **Read Documentation:**
   - [PROJECT_SETUP.md](PROJECT_SETUP.md) - Full setup and architecture
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) - Step-by-step implementation guide
   - [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project summary
   - [docs/SCRIPT_FORMAT.md](docs/SCRIPT_FORMAT.md) - Script format guide

2. **Customize Personas:**
   - Edit `config/personas.yaml` to define your personas
   - Configure voices and avatars

3. **Customize Scenes:**
   - Edit `config/scenes.yaml` to add background scenes
   - Add your own background images

4. **Try Examples:**
   - See `examples/scripts/` for example scripts
   - Modify them to create your own content

## 🐛 Troubleshooting

### API Key Issues
- Make sure `.env` file exists and has correct keys
- Verify API keys are active and have credits

### FFmpeg Not Found
- Install FFmpeg: https://ffmpeg.org/download.html
- Make sure it's in your system PATH

### Python Version
- Requires Python 3.10 or higher
- Check with: `python --version`

## 📖 Documentation

- [PROJECT_SETUP.md](PROJECT_SETUP.md) - Project setup and configuration
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) - Step-by-step implementation guide
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project summary
- [README.md](README.md) - Project overview

## 🤝 Getting Help

- Check the documentation in the `docs/` directory
- Review example scripts in `examples/scripts/`
- Check configuration files in `config/`

## 🎯 Current Status

**Phase 1: MVP - Cartoon Avatars** (In Progress)
- ✅ Project structure created
- ✅ Configuration system set up
- ✅ CLI framework in place
- ⏳ Core modules implementation (next step)
- ⏳ API integration (next step)
- ⏳ Video composition (next step)

See [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) for full roadmap.

