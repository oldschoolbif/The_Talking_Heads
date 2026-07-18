# Audio2Face SDK Build Prerequisites

**Date:** November 2025

## Current Status

### ✅ Available
- **CUDA:** 13.0 installed (SDK wants 12.8-12.9, but 13.0 may work)
- **CUDA_PATH:** Set to `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0`
- **Git LFS:** Available
- **Python:** Available

### ❌ Missing (Required)
- **TensorRT:** Not found (REQUIRED)
- **Visual Studio 2022:** Not found in standard locations

## Required Prerequisites

### 1. TensorRT (REQUIRED)

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

**Note:** TensorRT is a separate download from CUDA. You need both.

### 2. Visual Studio 2022 (REQUIRED)

**Download:** https://visualstudio.microsoft.com/downloads/

**Required Components:**
- Visual Studio 2022 Community/Professional/Enterprise
- **Desktop development with C++** workload
- **Windows 10/11 SDK**

**Or:** Visual Studio Build Tools 2022 (lighter weight option)

**Verify Installation:**
```powershell
# Should find vcvarsall.bat
Get-ChildItem "C:\Program Files*" -Recurse -Filter "vcvarsall.bat" -ErrorAction SilentlyContinue
```

### 3. CUDA Version Note

**Current:** CUDA 13.0  
**SDK Wants:** CUDA 12.8-12.9

**Status:** CUDA 13.0 may work, but 12.9 is recommended. If build fails, consider installing CUDA 12.9.

## Build Steps (Once Prerequisites Are Met)

### Step 1: Install Prerequisites

1. **Install TensorRT:**
   - Download from NVIDIA Developer site
   - Extract to `C:\TensorRT` (or your preferred location)
   - Set `TENSORRT_ROOT_DIR` environment variable

2. **Install Visual Studio 2022:**
   - Download from Microsoft
   - Install "Desktop development with C++" workload
   - Or install Build Tools 2022

### Step 2: Pull Git LFS Files

```powershell
cd d:\dev\Audio2Face-3D-SDK
git lfs pull
```

### Step 3: Fetch Dependencies

```powershell
cd d:\dev\Audio2Face-3D-SDK
.\fetch_deps.bat release
```

This downloads CMake, Ninja, and other build dependencies.

### Step 4: Set Environment Variables

```powershell
$env:TENSORRT_ROOT_DIR = "C:\TensorRT"  # Your TensorRT path
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0"  # Already set
```

### Step 5: Build SDK

```powershell
cd d:\dev\Audio2Face-3D-SDK
.\build.bat clean release  # Optional: clean previous build
.\build.bat all release    # Build everything
```

**Or use the helper script:**
```powershell
cd d:\dev\The_Talking_Heads
.\scripts\build_audio2face_sdk.ps1 -TensorRTPath "C:\TensorRT"
```

## Quick Start Script

A helper script is available at `scripts/build_audio2face_sdk.ps1`:

```powershell
cd d:\dev\The_Talking_Heads
.\scripts\build_audio2face_sdk.ps1 -TensorRTPath "C:\TensorRT"
```

## Troubleshooting

### TensorRT Not Found

**Error:** `TENSORRT_ROOT_DIR is not defined`

**Solution:**
1. Download TensorRT from NVIDIA Developer site
2. Extract to a location
3. Set environment variable:
   ```powershell
   $env:TENSORRT_ROOT_DIR = "C:\path\to\tensorrt"
   ```

### Visual Studio Not Found

**Error:** `Visual Studio installation not found`

**Solution:**
1. Install Visual Studio 2022 with C++ tools
2. Or install Visual Studio Build Tools 2022
3. Verify installation:
   ```powershell
   Get-ChildItem "C:\Program Files*" -Recurse -Filter "vcvarsall.bat"
   ```

### CUDA Version Mismatch

**Warning:** CUDA 13.0 vs required 12.8-12.9

**Solution:**
- Try building with CUDA 13.0 first (may work)
- If build fails, install CUDA 12.9 alongside 13.0
- Set `CUDA_PATH` to point to 12.9

## Next Steps

1. **Install TensorRT** (required)
2. **Install Visual Studio 2022** (required)
3. **Run build script** once prerequisites are met

## References

- **TensorRT Download:** https://developer.nvidia.com/tensorrt
- **Visual Studio Download:** https://visualstudio.microsoft.com/downloads/
- **CUDA Toolkit:** https://developer.nvidia.com/cuda-toolkit
- **Audio2Face SDK GitHub:** https://github.com/NVIDIA/Audio2Face-3D-SDK

