# Audio2Face Installation Guide

**Date:** November 2025  
**Status:** Installation Instructions

## Overview

Audio2Face can be installed in multiple ways. Since you have Omniverse installed, we'll use the simplest method first.

---

## Installation Methods

### Method 1: Via Omniverse Launcher (Recommended - Simplest) ⭐

**Best for:** Users with Omniverse already installed

**Steps:**

1. **Launch Omniverse Launcher**
   - Open Omniverse Launcher from Start Menu
   - Or run: `.\scripts\install_audio2face_omniverse.ps1`

2. **Install Audio2Face Extension**
   - Go to **"Exchange"** tab
   - Search for **"Audio2Face"**
   - Click **"Install"**
   - Wait for installation to complete

3. **Verify Installation**
   ```bash
   python scripts/test_audio2face_integration.py
   ```

**Pros:**
- ✅ Simplest method
- ✅ Integrates with existing Omniverse
- ✅ No building required
- ✅ Official NVIDIA distribution

**Cons:**
- ⚠️ Requires Omniverse Launcher (which you have)

---

### Method 2: Audio2Face-3D-SDK (GitHub - More Complex)

**Best for:** Advanced users, custom integration, high performance

**Repository:** https://github.com/NVIDIA/Audio2Face-3D-SDK

**Status:** ✅ Cloned to `d:\dev\Audio2Face-3D-SDK`

**Requirements:**
- CUDA 12.8+
- TensorRT 10.13+
- Visual Studio 2022+ (Windows)
- CMake, Ninja
- Python 3.8-3.10

**Build Steps:**

1. **Install Prerequisites**
   ```powershell
   # Check CUDA
   nvidia-smi
   
   # Check TensorRT (need to install if not available)
   # Download from: https://developer.nvidia.com/tensorrt
   ```

2. **Fetch Dependencies**
   ```powershell
   cd d:\dev\Audio2Face-3D-SDK
   .\fetch_deps.bat release
   ```

3. **Set Environment Variables**
   ```powershell
   $env:TENSORRT_ROOT_DIR = "C:\path\to\tensorrt"
   $env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9"
   ```

4. **Build SDK**
   ```powershell
   .\build.bat all release
   ```

5. **Download Models**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r deps\requirements.txt
   hf auth login  # Hugging Face authentication
   .\download_models.bat
   .\gen_testdata.bat
   ```

**Pros:**
- ✅ Official NVIDIA SDK
- ✅ High performance (C++/CUDA)
- ✅ Full control
- ✅ Latest features

**Cons:**
- ❌ Complex setup
- ❌ Requires building
- ❌ Needs CUDA/TensorRT
- ❌ More time-consuming

---

### Method 3: Standalone Audio2Face (Alternative)

**Best for:** Users without Omniverse or wanting standalone version

**Download:** https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html

**Steps:**
1. Download standalone ZIP package
2. Extract and install
3. Follow installation instructions

---

## Recommended Installation Path

**For You (with Omniverse installed):**

1. **Try Method 1 First** (Omniverse Launcher)
   - Simplest and fastest
   - Uses your existing Omniverse installation
   - Run: `.\scripts\install_audio2face_omniverse.ps1`

2. **If Method 1 Doesn't Work:**
   - Try Method 3 (Standalone)
   - Or proceed with Method 2 (SDK) if you need advanced features

---

## After Installation

### Verify Installation

```bash
# Run diagnostic
.\scripts\check_audio2face_setup.ps1

# Run integration test
python scripts/test_audio2face_integration.py
```

### Configure Integration

Once Audio2Face is installed, update `config/config.yaml`:

```yaml
audio2face:
  # If using py_audio2face (headless server)
  server_url: http://localhost:8000
  
  # If using Omniverse API
  omniverse_path: null  # Auto-detect
  
  # Character USD file (required)
  default_character_usd: path/to/character.usd
```

---

## Next Steps

1. **Install Audio2Face** (choose method above)
2. **Verify installation** (run test scripts)
3. **Configure characters** (get USD files)
4. **Test integration** (generate sample animation)

---

## Current Status

- ✅ Audio2Face-3D-SDK cloned to `d:\dev\Audio2Face-3D-SDK`
- ✅ Provider implementation ready
- ⏳ Waiting for Audio2Face installation
- ⏳ Ready to test once installed

---

## Help

If you encounter issues:

1. Check system requirements (CUDA, GPU, etc.)
2. Verify Omniverse installation
3. Check Audio2Face documentation
4. Run diagnostic scripts
5. Review error messages

Let me know which installation method you want to use, and I'll help you through it!

