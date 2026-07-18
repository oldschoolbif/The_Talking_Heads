# Audio2Face Installation Guide (2025)

**Important Update:** As of October 2025, NVIDIA has **deprecated the Omniverse Launcher**. This changes how Audio2Face is installed.

## Current Situation

- ❌ **Omniverse Launcher** - No longer available (deprecated October 2025)
- ✅ **Omniverse Editor** - You have this running (My Editor 0.1.0)
- ✅ **Audio2Face-3D-SDK** - Already cloned from GitHub
- ✅ **py-audio2face** - Already installed

## Installation Options

### Option 1: Use Audio2Face-3D-SDK (Recommended)

Since the Launcher is deprecated, we should use the SDK directly:

**Prerequisites:**
- CUDA 12.8-12.9
- TensorRT >=10.13, <11.0
- Visual Studio 2022+ (Windows)
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

After building, Audio2Face will be available as a standalone SDK.

### Option 2: Install via Omniverse Editor Extension Manager

If the Editor has an extension manager:

1. **In Omniverse Editor** (the one you're currently in)
2. **Look for:** "Extensions" or "Plugins" menu
3. **Search for:** "Audio2Face"
4. **Install** if available

### Option 3: Direct Download from GitHub/NGC

Audio2Face components may be available directly:
- **GitHub:** https://github.com/NVIDIA/Audio2Face-3D
- **NGC Catalog:** https://catalog.ngc.nvidia.com/ (search for Audio2Face)

### Option 4: Use py-audio2face with Built SDK

Once the SDK is built, `py-audio2face` can use it:

```python
from py_audio2face import Audio2Face

# Point to built SDK
a2f = Audio2Face(
    a2f_install_path="d:/dev/Audio2Face-3D-SDK/_build/release"
)
```

## Recommended Path Forward

Since you have:
- ✅ Omniverse Editor running
- ✅ Audio2Face-3D-SDK cloned
- ✅ py-audio2face installed

**Best approach:**
1. **Check if Editor has Extension Manager** - Look in the Editor menus
2. **If not, build the SDK** - Use Option 1 above
3. **Configure provider** - Point to SDK location

## Checking Your Editor

In the Omniverse Editor you're currently in:

1. **Check Menu Bar:**
   - Look for "Extensions", "Plugins", or "Add-ons"
   - Check "Window" menu for extension manager

2. **Check Content Panel:**
   - The bottom panel might have extension options
   - Look for "Install" or "Add Extension" buttons

3. **Check Help Menu:**
   - May have "Install Extensions" option

## Next Steps

1. **Check Editor for Extension Manager** (easiest)
2. **If not available, build SDK** (more work but guaranteed to work)
3. **Update config** to point to installation location

## References

- **Audio2Face-3D GitHub:** https://github.com/NVIDIA/Audio2Face-3D
- **Audio2Face-3D-SDK GitHub:** https://github.com/NVIDIA/Audio2Face-3D-SDK
- **NVIDIA Legacy Tools:** https://developer.nvidia.com/omniverse/legacy-tools
- **NGC Catalog:** https://catalog.ngc.nvidia.com/

