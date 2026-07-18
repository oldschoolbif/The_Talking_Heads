# Audio2Face SDK Build Status

**Date:** November 2025

## Current Status

### ✅ Completed
1. **Git LFS files pulled** - Large files downloaded
2. **Dependencies fetched** - CMake, Ninja, and all build dependencies installed
   - CMake 3.24.1
   - Ninja 1.10.0
   - Python 3.10.18
   - Test data and libraries

### ✅ Available
- **Visual Studio 2025** (version 18) - Found and working
- **CUDA 13.0** - Installed (SDK wants 12.8-12.9, but 13.0 may work)
- **CUDA_PATH** - Set correctly

### ❌ Required Before Building
- **TensorRT** - Not installed (REQUIRED for build)

## Next Steps

### 1. Install TensorRT

**Download:** https://developer.nvidia.com/tensorrt

**Requirements:**
- TensorRT >=10.13, <11.0
- Compatible with CUDA 12.x or 13.x

**Installation:**
1. Download TensorRT from NVIDIA Developer site
2. Extract to a location (e.g., `C:\TensorRT`)
3. Set environment variable:
   ```powershell
   $env:TENSORRT_ROOT_DIR = "C:\TensorRT"
   ```

### 2. Build SDK

Once TensorRT is installed, run:

```powershell
cd d:\dev\Audio2Face-3D-SDK

# Set TensorRT path
$env:TENSORRT_ROOT_DIR = "C:\TensorRT"  # Your TensorRT path

# Clean previous build (optional)
.\build.bat clean release

# Build SDK
.\build.bat all release
```

**Or use the helper script:**
```powershell
cd d:\dev\The_Talking_Heads
.\scripts\build_audio2face_sdk.ps1 -TensorRTPath "C:\TensorRT"
```

## Build Output Location

After successful build, output will be at:
```
d:\dev\Audio2Face-3D-SDK\_build\release\
```

## Estimated Build Time

- **Dependencies:** ✅ Already fetched (~2 minutes)
- **Build:** ~10-30 minutes (depending on system)

## Troubleshooting

### TensorRT Not Found

**Error:** `TENSORRT_ROOT_DIR is not defined`

**Solution:** Download and install TensorRT, then set the environment variable.

### CUDA Version Warning

**Note:** CUDA 13.0 vs required 12.8-12.9

**Status:** May work, but if build fails, consider installing CUDA 12.9.

### Visual Studio Version

**Found:** Visual Studio 2025 (version 18)  
**SDK Wants:** Visual Studio 2022 (version 17)

**Status:** Should work fine - newer version is compatible.

## References

- **TensorRT Download:** https://developer.nvidia.com/tensorrt
- **Build Script:** `scripts/build_audio2face_sdk.ps1`
- **Prerequisites Guide:** `docs/AUDIO2FACE_SDK_BUILD_PREREQUISITES.md`

