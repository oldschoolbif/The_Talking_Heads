# Audio2Face Setup Guide

**Status:** ✅ Active - Primary Avatar Provider  
**Date:** November 2025  
**Updated:** Now uses Audio2Face from GitHub

## Overview

NVIDIA Audio2Face (A2F) is now the primary avatar generation provider for The Talking Heads. Audio2Face provides professional-grade facial animation with full head movements, expressions, and gestures through the NVIDIA Omniverse platform.

**Important:** Audio2Face is now obtained from GitHub. See [AUDIO2FACE_GITHUB_SETUP.md](AUDIO2FACE_GITHUB_SETUP.md) for complete GitHub setup instructions.

## Prerequisites

### System Requirements
- **OS:** Windows 10/11 or Linux (Ubuntu 18.04+)
- **GPU:** NVIDIA GPU with CUDA support (8GB+ VRAM recommended)
- **RAM:** 32GB+ recommended
- **Storage:** 50GB+ for Omniverse installation
- **NVIDIA Drivers:** Latest drivers required

### Software Requirements
- ✅ **NVIDIA Omniverse** - Installed and configured
- ✅ **Audio2Face Extension** - Installed via Omniverse Launcher
- ✅ **Character USD Files** - 3D character models in USD format

## Configuration

### 1. Configure Audio2Face in `config/config.yaml`

```yaml
audio2face:
  # Omniverse installation path (auto-detected if null)
  omniverse_path: null  # Auto-detect: Windows: C:\Users\<user>\AppData\Local\ov\pkg
  
  # Default character USD file path (required)
  # Can be overridden per persona in personas.yaml
  default_character_usd: path/to/character.usd
  
  # Output directory
  output_dir: .cache/audio2face_outputs
  
  # Python executable (auto-detected)
  python_exec: python
  
  # Audio2Face settings
  fps: 60.0  # Animation frame rate
  quality: high  # low, medium, high
  use_api: true  # Use Python API if available

avatar:
  engine: audio2face  # Set as default
```

### 2. Configure Personas

In `config/personas.yaml`, set the avatar engine and character USD for each persona:

```yaml
personas:
  alice:
    name: Alice
    avatar:
      engine: audio2face
      avatar_id: path/to/alice_character.usd  # Character USD file path
      style: realistic
```

## Character Setup

### Getting Character USD Files

Audio2Face requires 3D character models in USD format. You have several options:

1. **Omniverse Asset Store** (Free/Paid)
   - Visit: https://www.nvidia.com/en-us/omniverse/asset-store/
   - Search for "Audio2Face" compatible characters
   - Download and use directly

2. **Create in Omniverse Create**
   - Use Omniverse Create to build characters
   - Export to USD format
   - Ensure character has proper rigging for Audio2Face

3. **Import from Blender/Maya**
   - Create character in Blender or Maya
   - Export to USD format
   - Import to Omniverse and set up for Audio2Face

4. **Use Pre-made Audio2Face Characters**
   - Audio2Face comes with example characters
   - Located in Omniverse installation directory
   - Can be used as starting point

### Character Requirements

For Audio2Face to work properly, characters need:
- **Separated head mesh** - Head must be separate from body
- **Eye meshes** - Separate meshes for eyes
- **Teeth mesh** - Separate mesh for teeth
- **Tongue mesh** - Separate mesh for tongue
- **Proper rigging** - Character must be rigged for animation

## Usage

### Basic Usage

The Audio2Face provider is automatically used when `avatar.engine` is set to `audio2face`:

```bash
python -m src.cli.main create script.txt --scene studio
```

### Provider API

```python
from src.core.avatar_generator import AvatarGenerator
from src.core.persona_engine import PersonaEngine

# Load persona
persona_engine = PersonaEngine()
persona_engine.load_personas("config/personas.yaml")
persona = persona_engine.get_persona("ALICE")

# Generate avatar
avatar_gen = AvatarGenerator(config, output_dir=Path("outputs"))
avatar_video = avatar_gen.generate_persona_avatar(
    persona=persona,
    audio_path=Path("audio.wav"),
    expression="happy",
    text="Hello, world!"
)
```

## Troubleshooting

### Audio2Face Not Available

**Error:** `Audio2Face is not available`

**Solutions:**
1. Ensure Omniverse is installed and Audio2Face extension is available
2. Check `omniverse_path` in config - should point to Omniverse installation
3. Verify Audio2Face extension is installed via Omniverse Launcher
4. Check system requirements (GPU, RAM, etc.)

### Character USD Not Found

**Error:** `Character USD file not found`

**Solutions:**
1. Set `default_character_usd` in `config/config.yaml`
2. Or set `avatar_id` in persona configuration to USD file path
3. Ensure USD file path is correct and file exists
4. Use absolute paths if relative paths don't work

### Python API Not Available

**Error:** `Audio2Face API not available`

**Solutions:**
1. Set `use_api: false` in config to use extension method
2. Ensure Omniverse Python packages are accessible
3. Check that Omniverse Python executable is found
4. May need to set `python_exec` to Omniverse's Python path

## Integration with Existing Pipeline

The Audio2Face provider integrates seamlessly with the existing pipeline:

1. **Script Parser** - Parses script with persona assignments
2. **TTS Engine** - Generates audio for each persona
3. **Audio2Face Provider** - Generates avatar videos from audio
4. **Video Composer** - Composes final multi-persona video

## Performance

- **Generation Speed:** Fast (GPU-accelerated)
- **Quality:** Excellent (professional-grade)
- **Resource Usage:** High (requires 8GB+ VRAM, 32GB+ RAM)
- **Output Format:** USD animation (can be exported to video)

## Next Steps

1. ✅ **Setup Complete** - Audio2Face is configured and active
2. ⏭️ **Configure Characters** - Set up character USD files for each persona
3. ⏭️ **Test Generation** - Run a test generation to verify setup
4. ⏭️ **Optimize Settings** - Adjust fps, quality settings as needed

## References

- **Audio2Face Documentation:** https://docs.omniverse.nvidia.com/audio2face/
- **Omniverse Installation:** https://docs.omniverse.nvidia.com/install-guide/
- **Omniverse Python API:** https://docs.omniverse.nvidia.com/py/
- **Character Setup Guide:** `docs/AUDIO2FACE_3D_ASSETS_GUIDE.md`

