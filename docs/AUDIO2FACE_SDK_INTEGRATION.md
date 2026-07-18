# Audio2Face SDK Integration (GitHub Version)

**Status:** ⚠️ In Progress  
**Date:** November 2025

## Overview

This document describes the integration of NVIDIA's Audio2Face SDK from GitHub (`Audio2Face-3D-SDK`) into The Talking Heads project. This integration does **not** require Omniverse, as the Omniverse Launcher was deprecated on October 1, 2025.

## Current Status

### ✅ Completed

1. **SDK Built Successfully**
   - Location: `d:\dev\Audio2Face-3D-SDK\_build\release\`
   - All libraries and executables compiled
   - CUDA 13.0 + TensorRT 10.14.1.48 + Visual Studio 2025

2. **3DDFA → USD Conversion**
   - PLY mesh conversion to USD working
   - Uses `usd-core` (pxr Python API)

3. **Provider Structure**
   - `Audio2FaceSDKProvider` class created
   - Integration points defined

### ⚠️ In Progress

1. **Wrapper Executable**
   - Created `a2f-wrapper` source code
   - Needs to be added to SDK build and compiled
   - Location: `d:\dev\Audio2Face-3D-SDK\audio2face-sdk\source\samples\a2f-wrapper\`

2. **USD Export**
   - SDK generates geometry (vertex positions)
   - Need to export geometry to USD format
   - Currently placeholder in wrapper

3. **Video Rendering**
   - USD animation needs to be rendered to video
   - Options: USD renderer, Blender, or custom renderer

## Architecture

### Workflow

```
2D Image (blonde.png)
    ↓
3DDFA (3D reconstruction)
    ↓
PLY Mesh
    ↓
USD Conversion (usd-core)
    ↓
Character USD File
    ↓
Audio2Face SDK (animation generation)
    ↓
Animated USD File
    ↓
Video Rendering (TODO)
    ↓
Final Video
```

### Components

1. **Audio2FaceSDKProvider** (`src/core/audio2face_sdk_provider.py`)
   - Python provider that interfaces with the SDK
   - Uses wrapper executable (when built) or direct DLL access (future)

2. **Wrapper Executable** (`a2f-wrapper.exe`)
   - C++ executable that accepts command-line arguments
   - Uses SDK API to generate animation
   - Exports results to USD

3. **TDDFA_A2FProvider** (`src/core/tddfa_a2f_provider.py`)
   - Combined provider that orchestrates the full workflow
   - Calls 3DDFA → USD → Audio2Face → Video

## Setup Instructions

### 1. Build Wrapper Executable

The wrapper executable needs to be added to the SDK build:

```powershell
# Navigate to SDK directory
cd d:\dev\Audio2Face-3D-SDK

# Add wrapper to CMakeLists.txt in audio2face-sdk/source/samples/
# (Add: add_subdirectory(a2f-wrapper))

# Rebuild SDK
$env:TENSORRT_ROOT_DIR = "D:\dev\TensorRT-10.14.1.48"
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0"
.\build.bat all release
```

### 2. Download Models

The SDK requires model files to be downloaded:

```powershell
cd d:\dev\Audio2Face-3D-SDK

# Create venv
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r deps\requirements.txt

# Authenticate with Hugging Face (one-time)
hf auth login

# Download models
.\download_models.bat

# Generate test data
.\gen_testdata.bat
```

### 3. Configure Provider

Update `config/config.yaml`:

```yaml
audio2face_sdk:
  sdk_build_path: d:\dev\Audio2Face-3D-SDK\_build\release
  sdk_base_path: d:\dev\Audio2Face-3D-SDK
  model_path: null  # Auto-detected if null
  output_dir: .cache/audio2face_sdk_outputs
  fps: 60.0
```

## Usage

### Direct Provider Usage

```python
from src.core.audio2face_sdk_provider import Audio2FaceSDKProvider

config = {
    "audio2face_sdk": {
        "sdk_build_path": "d:/dev/Audio2Face-3D-SDK/_build/release",
        "fps": 60.0
    }
}

provider = Audio2FaceSDKProvider(config)

if provider.is_available():
    video_path, duration = provider.generate(
        audio_path=Path("audio.wav"),
        avatar_id="character.usd",  # Character USD file
        text="Hello world"
    )
```

### Via TDDFA_A2F Provider

```python
from src.core.tddfa_a2f_provider import TDDFA_A2FProvider

config = {
    "tddfa_a2f": {
        "usd_cache_dir": ".cache/usd_models",
        "default_source_image": "blonde.png"
    },
    "audio2face_sdk": {
        "sdk_build_path": "d:/dev/Audio2Face-3D-SDK/_build/release"
    }
}

provider = TDDFA_A2FProvider(config)

video_path, duration = provider.generate(
    audio_path=Path("audio.wav"),
    avatar_id="blonde.png",  # 2D image
    text="Hello world"
)
```

## Known Limitations

1. **USD Export Not Implemented**
   - Wrapper generates geometry but doesn't export to USD yet
   - Need to implement USD writing using pxr API

2. **Video Rendering Not Implemented**
   - Animated USD needs to be rendered to video
   - Options: USD renderer, Blender, or custom solution

3. **Wrapper Needs Building**
   - Wrapper source exists but needs to be added to build
   - Or implement direct DLL access via ctypes

## Next Steps

1. **Complete Wrapper Implementation**
   - Add USD export functionality
   - Test with sample audio and character

2. **Implement Video Rendering**
   - Choose rendering solution (USD renderer vs Blender)
   - Integrate into pipeline

3. **End-to-End Testing**
   - Test full workflow: 2D image → 3DDFA → USD → Audio2Face → Video
   - Verify quality and performance

## Troubleshooting

### SDK Not Available

**Error:** `Audio2Face SDK is not available`

**Solutions:**
- Verify SDK build path is correct
- Check that `audio2x.dll` exists in `_build/release/audio2x-sdk/bin/`
- Ensure models are downloaded (`download_models.bat`)

### Wrapper Not Found

**Error:** `Audio2Face SDK wrapper executable not found`

**Solutions:**
- Build the wrapper executable (see Setup Instructions)
- Or implement direct DLL access (future work)

### Model Files Missing

**Error:** `Failed to load model.json`

**Solutions:**
- Run `download_models.bat` to download required models
- Verify model path in config
- Check Hugging Face authentication (`hf auth login`)

## References

- **Audio2Face-3D-SDK GitHub:** https://github.com/NVIDIA/Audio2Face-3D-SDK
- **SDK Documentation:** `d:\dev\Audio2Face-3D-SDK\docs\README.md`
- **Omniverse Deprecation:** Omniverse Launcher deprecated Oct 1, 2025

