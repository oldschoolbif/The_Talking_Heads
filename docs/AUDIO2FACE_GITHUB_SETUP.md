# Audio2Face GitHub Setup Guide

**Status:** ✅ Complete - Audio2Face from GitHub  
**Date:** November 2025

## Overview

Audio2Face is now available from GitHub and integrated into The Talking Heads. This guide covers the complete setup process.

## Installation Steps

### 1. Install py-audio2face Package ✅

The `py-audio2face` package provides the Python client for Audio2Face:

```bash
pip install py-audio2face
```

**Status:** ✅ Installed (version 0.1.3)

### 2. Get Audio2Face from GitHub ✅

Two repositories are available:

#### Audio2Face-3D (Main Repository)
```bash
cd d:\dev
git clone https://github.com/NVIDIA/Audio2Face-3D.git
```

**Status:** ✅ Cloned to `d:\dev\Audio2Face-3D`

#### Audio2Face-3D-SDK (SDK for Building)
```bash
cd d:\dev
git clone https://github.com/NVIDIA/Audio2Face-3D-SDK.git
```

**Status:** ✅ Cloned to `d:\dev\Audio2Face-3D-SDK`

### 3. Audio2Face Installation Path

Audio2Face needs to know where it's installed. The provider will auto-detect, but you can also set it manually:

#### Option A: Via Omniverse (Recommended if Omniverse is installed)

If you have NVIDIA Omniverse installed:
1. **Install Audio2Face Extension:**
   - Open Omniverse Launcher
   - Go to "Exchange" tab
   - Search for "Audio2Face"
   - Click "Install"

2. **Auto-detection:**
   - The provider will automatically find Audio2Face in Omniverse
   - Location: `C:\Users\<user>\AppData\Local\ov\pkg\<audio2face-package>`

3. **Audio2Face will start automatically** when you use `py-audio2face`
   - The `init_a2f()` method will start the headless server if needed
   - Default API URL: `http://localhost:8011`

#### Option B: Use Audio2Face-3D-SDK (Fallback)

If Omniverse Audio2Face extension is not installed:
1. **Set SDK path in config:**
   ```yaml
   audio2face:
     a2f_install_path: d:/dev/Audio2Face-3D-SDK
   ```

2. **Note:** SDK needs to be built for full functionality
   - See "Build Audio2Face-3D-SDK" section below

#### Option C: Build Audio2Face-3D-SDK (Advanced)

If you want to build from source:

**Prerequisites:**
- CUDA 12.8-12.9
- TensorRT >=10.13, <11.0
- Visual Studio 2022+ (Windows) or g++ (Linux)
- CMake
- Python 3.8-3.10

**Build Steps:**
```powershell
cd d:\dev\Audio2Face-3D-SDK
git lfs pull  # Pull large files
.\fetch_deps.bat release
$env:TENSORRT_ROOT_DIR="C:\path\to\tensorrt"
.\build.bat all release
```

**Note:** Building the SDK is optional - `py-audio2face` can work with Omniverse installation.

## Configuration

### config/config.yaml

```yaml
audio2face:
  # API URL (Audio2Face uses port 8011 by default, not 8000)
  server_url: http://localhost:8011
  
  # Audio2Face installation path (auto-detected if null)
  # Will search:
  # 1. Omniverse packages (C:\Users\<user>\AppData\Local\ov\pkg)
  # 2. Audio2Face-3D-SDK (d:/dev/Audio2Face-3D-SDK)
  a2f_install_path: null
  
  # Omniverse installation path (for fallback methods, auto-detected if null)
  omniverse_path: null  # Windows: C:\Users\<user>\AppData\Local\ov\pkg
  
  # Default character USD file path (required for generation)
  default_character_usd: null
  
  # Output directory
  output_dir: .cache/audio2face_outputs
  
  # Settings
  fps: 60.0
  quality: high
  use_api: true  # Use py-audio2face API
```

## Usage

### Basic Usage

The Audio2Face provider is automatically used when `avatar.engine` is set to `audio2face`:

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

### Direct py-audio2face Usage

```python
from py_audio2face import Audio2Face

# Create Audio2Face instance
a2f = Audio2Face(
    api_url="http://localhost:8011",
    a2f_install_path=None,  # Auto-detect Omniverse
    output_dir="outputs"
)

# Initialize (starts server if needed)
a2f.init_a2f(streaming=False)

# Generate animation
output_path = a2f.audio2face_single(
    audio_file_path="audio.wav",
    output_path="animation.usd",
    fps=60,
    emotion_auto_detect=True
)
```

## Testing

### Test Server Connection

```bash
python scripts/test_audio2face_server.py
```

This will:
1. Check if `py-audio2face` is installed ✅
2. Try to find Audio2Face installation (Omniverse or SDK)
3. Create Audio2Face instance
4. Initialize Audio2Face (starts server if needed)
5. Report status

**Expected Output:**
- ✅ If Audio2Face extension is installed: Will auto-detect and initialize
- ⚠️ If not installed: Will show instructions to install via Omniverse Launcher or set SDK path

### Test Full Workflow

```bash
python scripts/test_tddfa_a2f_full_workflow.py
```

This tests the complete pipeline:
1. 3DDFA reconstructs 3D face from 2D image
2. Converts PLY mesh to USD format
3. Audio2Face animates USD model with audio
4. Creates final video

## Troubleshooting

### Audio2Face Server Not Starting

**Error:** `Failed to initialize Audio2Face`

**Solutions:**
1. **Check Omniverse Installation:**
   - Ensure Omniverse is installed
   - Verify Audio2Face extension is installed via Omniverse Launcher
   - Check `omniverse_path` in config

2. **Manual Server Start:**
   - If using Audio2Face-3D-SDK, you may need to start the server manually
   - Check SDK documentation for server startup commands

3. **Check Port 8011:**
   - Ensure port 8011 is not blocked by firewall
   - Check if another process is using port 8011

### py-audio2face Import Error

**Error:** `ImportError: cannot import name 'Audio2Face'`

**Solution:**
```bash
pip install py-audio2face
```

### Character USD Not Found

**Error:** `Character USD file not found`

**Solutions:**
1. Set `default_character_usd` in `config/config.yaml`
2. Or set `avatar_id` in persona configuration to USD file path
3. Ensure USD file exists and path is correct

### API Connection Failed

**Error:** `Connection refused` or `Cannot connect to server`

**Solutions:**
1. Check if Audio2Face server is running:
   ```bash
   netstat -an | findstr "8011"
   ```

2. Try starting Audio2Face manually:
   - Via Omniverse Launcher → Audio2Face application
   - Or via SDK if built

3. Check API URL in config (default: `http://localhost:8011`)

## Integration Status

✅ **py-audio2face installed** - Version 0.1.3  
✅ **Audio2Face-3D cloned** - `d:\dev\Audio2Face-3D`  
✅ **Audio2Face-3D-SDK cloned** - `d:\dev\Audio2Face-3D-SDK`  
✅ **Provider integrated** - `src/core/audio2face_provider.py`  
✅ **API updated** - Uses `Audio2Face` class (not `Audio2FaceClient`)  
✅ **Configuration ready** - `config/config.yaml`  
✅ **Auto-detection** - Finds SDK path automatically  
⚠️ **Server Status** - Audio2Face extension needs to be installed via Omniverse Launcher  

## Next Steps

1. ✅ **Installation Complete** - Audio2Face from GitHub is set up
2. ⏭️ **Install Audio2Face Extension** - Via Omniverse Launcher (Exchange → Audio2Face)
3. ⏭️ **Test Server** - Run `python scripts/test_audio2face_server.py`
4. ⏭️ **Configure Characters** - Set up character USD files
5. ⏭️ **Test Generation** - Run full workflow test

**See [AUDIO2FACE_SERVER_STATUS.md](AUDIO2FACE_SERVER_STATUS.md) for current server status.**

## References

- **Audio2Face-3D GitHub:** https://github.com/NVIDIA/Audio2Face-3D
- **Audio2Face-3D-SDK GitHub:** https://github.com/NVIDIA/Audio2Face-3D-SDK
- **py-audio2face PyPI:** https://pypi.org/project/py-audio2face/
- **Audio2Face Documentation:** https://docs.omniverse.nvidia.com/audio2face/
- **Omniverse Installation:** https://docs.omniverse.nvidia.com/install-guide/

