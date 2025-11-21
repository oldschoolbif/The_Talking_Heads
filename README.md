# 🎙️ The Talking Heads
## AI-Generated Multi-Persona Podcast Creator

**The Talking Heads** is an AI-powered system that generates professional multi-persona video podcasts from a script. Create engaging podcasts with 1-5 different animated personas, each with their own voice, expressions, and gestures.

## ✨ Features

- **🎭 Multiple Personas:** 1-5 different characters per episode
- **🗣️ Distinct Voices:** Each persona has a unique voice
- **🎨 Animated Avatars:** Cartoon-style avatars with expressions and gestures
- **🎬 Background Scenes:** Customizable podcast environments
- **📝 Script-Driven:** Simple script format with persona assignments
- **🎨 Phased Evolution:** Start cartoon → Evolve to realistic

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/The_Talking_Heads.git
cd The_Talking_Heads

# Set up environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Create your first podcast
python -m src.cli.main create examples/scripts/multi_persona_episode.txt
```

## 📝 Script Format

```markdown
# Episode Title

ALICE: Hello everyone, welcome to The Talking Heads!
BOB: Thanks for having us, Alice. I'm Bob.
ALICE: Today we'll discuss AI with our guest, Charlie.
CHARLIE: Excited to be here! AI is fascinating.
ALICE: Let's dive right in.
```

## ⚙️ Configuration

See `config/personas.yaml` to define your personas:
- Voice settings
- Avatar appearance
- Expression preferences
- Gesture frequency

See `config/scenes.yaml` for background scenes.

## 🎯 Roadmap

### Phase 1: MVP - Cartoon Avatars (Current)
- [x] Project setup
- [ ] Script parser with persona detection
- [ ] Multi-voice TTS integration
- [ ] Cartoon avatar generation (API)
- [ ] Multi-avatar video composition
- [ ] Basic expressions and gestures

### Phase 2: Enhanced Cartoon
- [ ] 3-5 personas support
- [ ] Advanced expressions
- [ ] Expanded gesture library
- [ ] Animated backgrounds

### Phase 3: Realistic Transition
- [ ] Realistic avatar option
- [ ] Style switching
- [ ] Seamless integration

### Phase 4: Advanced Realistic
- [ ] High-quality realistic avatars
- [ ] Advanced expressions
- [ ] Context-aware gestures
- [ ] Emotion detection

## 📚 Documentation

- [START_HERE.md](START_HERE.md) - Getting started guide
- [PROJECT_SETUP.md](PROJECT_SETUP.md) - Project setup guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) - Step-by-step implementation guide
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project summary
- [docs/SCRIPT_FORMAT.md](docs/SCRIPT_FORMAT.md) - Script format guide

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- HeyGen, D-ID for avatar APIs
- ElevenLabs, Azure for TTS services
- Open source community for inspiration

