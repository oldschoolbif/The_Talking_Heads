# TensorRT Setup Complete

**Date:** November 2025

## Installation Location

**TensorRT Path:** `D:\dev\TensorRT-10.14.1.48`

## Environment Variables Set

### Session Variables (Current PowerShell)
- `TENSORRT_ROOT_DIR` = `D:\dev\TensorRT-10.14.1.48`
- `CUDA_PATH` = `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0`
- `PATH` = Updated to include TensorRT `bin` and `lib` directories

## Setup Script

A helper script is available to set up the environment:

```powershell
cd d:\dev\The_Talking_Heads
.\scripts\setup_tensorrt_env.ps1
```

This script:
- Verifies TensorRT installation
- Sets `TENSORRT_ROOT_DIR` environment variable
- Adds TensorRT `bin` and `lib` to PATH
- Displays current environment status

## Building Audio2Face SDK

Now that TensorRT is set up, you can build the SDK:

### Option 1: Manual Build

```powershell
# Set environment (or run setup script)
$env:TENSORRT_ROOT_DIR = "D:\dev\TensorRT-10.14.1.48"

# Navigate to SDK
cd d:\dev\Audio2Face-3D-SDK

# Build
.\build.bat all release
```

### Option 2: Using Helper Script

```powershell
cd d:\dev\The_Talking_Heads
.\scripts\build_audio2face_sdk.ps1
```

The script will automatically use `D:\dev\TensorRT-10.14.1.48` as the default TensorRT path.

## Persistent Environment Variables (Optional)

To make these settings persistent across sessions, you can set them system-wide:

### Via PowerShell (Admin)
```powershell
[System.Environment]::SetEnvironmentVariable("TENSORRT_ROOT_DIR", "D:\dev\TensorRT-10.14.1.48", "Machine")
```

### Via System Properties
1. Right-click "This PC" → Properties
2. Advanced system settings → Environment Variables
3. Add `TENSORRT_ROOT_DIR` = `D:\dev\TensorRT-10.14.1.48`

**Note:** For this build session, the environment variables are already set. You can proceed with building.

## Verification

To verify TensorRT is set up correctly:

```powershell
# Check environment variable
Write-Host $env:TENSORRT_ROOT_DIR

# Check if TensorRT files exist
Test-Path "$env:TENSORRT_ROOT_DIR\lib"
Test-Path "$env:TENSORRT_ROOT_DIR\include"
Test-Path "$env:TENSORRT_ROOT_DIR\bin"
```

## Next Steps

1. ✅ **TensorRT installed** - `D:\dev\TensorRT-10.14.1.48`
2. ✅ **Environment variables set** - Ready for build
3. ⏭️ **Build SDK** - Run `.\build.bat all release` in SDK directory
4. ⏭️ **Test Audio2Face** - After build completes

## References

- **Build Script:** `scripts/build_audio2face_sdk.ps1`
- **Setup Script:** `scripts/setup_tensorrt_env.ps1`
- **Build Status:** `docs/AUDIO2FACE_SDK_BUILD_STATUS.md`

