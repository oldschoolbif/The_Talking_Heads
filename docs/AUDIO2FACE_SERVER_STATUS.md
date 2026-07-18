# Audio2Face Server Status

**Date:** November 2025

## Current Status

### ✅ Completed
1. **py-audio2face installed** - Version 0.1.3
2. **Audio2Face-3D cloned** - `d:\dev\Audio2Face-3D`
3. **Audio2Face-3D-SDK cloned** - `d:\dev\Audio2Face-3D-SDK`
4. **Provider updated** - Uses correct `Audio2Face` API
5. **Auto-detection** - Finds SDK path automatically

### ⚠️ Server Status

**Audio2Face server is NOT currently running.**

The test shows:
- ✅ `py-audio2face` package is installed
- ✅ Audio2Face instance can be created with SDK path
- ❌ Server initialization fails (server not started)

**Error:** `audio2face_headless.bat not found in d:\dev\Audio2Face-3D-SDK/. Is audio2face installed?`

## What This Means

Audio2Face needs to be installed via one of these methods:

### Option 1: Install Audio2Face Extension via Omniverse (Recommended)

1. Open **Omniverse Launcher**
2. Go to **"Exchange"** tab
3. Search for **"Audio2Face"**
4. Click **"Install"**

After installation, Audio2Face will be available at:
- `C:\Users\<user>\AppData\Local\ov\pkg\<audio2face-package>`

The provider will auto-detect it and the server will start automatically.

### Option 2: Build Audio2Face-3D-SDK

If you want to use the SDK directly:

**Prerequisites:**
- CUDA 12.8-12.9
- TensorRT >=10.13, <11.0
- Visual Studio 2022+ (Windows)
- CMake
- Python 3.8-3.10

**Build Steps:**
```powershell
cd d:\dev\Audio2Face-3D-SDK
git lfs pull
.\fetch_deps.bat release
$env:TENSORRT_ROOT_DIR="C:\path\to\tensorrt"
.\build.bat all release
```

After building, the SDK will have the headless server executable.

## Testing

### Test Server Connection

```bash
python scripts/test_audio2face_server.py
```

**Current Output:**
- ✅ Package installed
- ✅ Instance created (with SDK path)
- ⚠️ Server initialization fails (needs Audio2Face installation)

### Test Full Workflow

```bash
python scripts/test_tddfa_a2f_full_workflow.py
```

**Note:** This test will proceed through 3DDFA reconstruction and USD conversion, but Audio2Face animation will fail until the server is available.

## Next Steps

1. **Install Audio2Face Extension** via Omniverse Launcher (easiest)
2. **Or build Audio2Face-3D-SDK** if you need SDK functionality
3. **Then test again** with `python scripts/test_audio2face_server.py`

## Configuration

Once Audio2Face is installed, the provider will auto-detect it. You can also set it manually:

```yaml
audio2face:
  # Set if auto-detection doesn't work
  a2f_install_path: C:\Users\<user>\AppData\Local\ov\pkg\<audio2face-package>
  # Or for SDK:
  # a2f_install_path: d:/dev/Audio2Face-3D-SDK
```

## References

- **Audio2Face GitHub:** https://github.com/NVIDIA/Audio2Face-3D
- **Setup Guide:** [AUDIO2FACE_GITHUB_SETUP.md](AUDIO2FACE_GITHUB_SETUP.md)
- **Omniverse Launcher:** https://www.nvidia.com/en-us/omniverse/

