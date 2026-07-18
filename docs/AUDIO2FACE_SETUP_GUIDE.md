# Audio2Face Setup and Integration Guide

**Date:** November 2025  
**Status:** Setup Guide - Step-by-Step Instructions

## Overview

This guide will help you:
1. Install Audio2Face (if not already installed)
2. Set up Audio2Face for programmatic use
3. Choose the best integration method
4. Integrate with The Talking Heads project

---

## Step 1: Understanding Audio2Face

**What is Audio2Face?**
- NVIDIA's proprietary tool for generating facial animations from audio
- Part of NVIDIA Omniverse ecosystem
- Generates realistic facial expressions, lip sync, head movements
- Requires 3D character models in USD format

**Important Note:** As of October 2025, NVIDIA deprecated the Omniverse Launcher. Audio2Face is now available as a standalone download.

---

## Step 2: Check What You Have

### Check 1: Do you have Omniverse installed?

```powershell
# Check if Omniverse is installed (Windows)
Test-Path "$env:LOCALAPPDATA\ov\pkg"

# Or check common installation paths
Test-Path "C:\Users\$env:USERNAME\AppData\Local\ov"
```

### Check 2: Do you have Audio2Face?

Audio2Face might be:
- Installed as part of Omniverse (if you installed it before Oct 2025)
- Available as standalone (if downloaded recently)
- Not installed yet

**Where to check:**
- Windows: `%LOCALAPPDATA%\ov\pkg\omni.audio2face`
- Or standalone: Check Reallusion website download

---

## Step 3: Installation Options

### Option A: Standalone Audio2Face (Recommended - Current Method)

**As of October 2025, NVIDIA recommends:**

1. **Download from Reallusion:**
   - Visit: https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html
   - Download the standalone ZIP package (includes Nucleus)
   - Latest version: A2F 2023.2.0 with Nucleus 2023.2.3

2. **Installation:**
   - Extract ZIP file
   - Follow installation instructions in the package
   - Includes Nucleus (required for Audio2Face)

3. **Verify Installation:**
   - Launch Audio2Face application
   - Should open GUI interface
   - Test with sample audio/character

### Option B: Via Omniverse (If Already Installed)

If you have Omniverse Launcher (pre-Oct 2025):
1. Open Omniverse Launcher
2. Go to "Exchange" tab
3. Search for "Audio2Face"
4. Install Audio2Face extension

---

## Step 4: Choose Integration Method

Based on your needs, here are the options:

### Method 1: py_audio2face (Python API - EASIEST) ⭐ **RECOMMENDED**

**Best for:** Python-based projects, easy integration

**Requirements:**
- Audio2Face installed
- Audio2Face headless server running
- Python package: `pip install py-audio2face`

**Pros:**
- ✅ Pure Python
- ✅ Easy to integrate
- ✅ Well-documented API
- ✅ Works with headless server

**Cons:**
- ⚠️ Requires headless server setup
- ⚠️ Community-maintained (not official)

**Setup Steps:**
1. Install Audio2Face (see Step 3)
2. Start Audio2Face headless server
3. Install Python package: `pip install py-audio2face`
4. Update provider to use this library

### Method 2: Audio2Face-3D-SDK (Official SDK - MORE COMPLEX)

**Best for:** High performance, C++/CUDA integration

**Requirements:**
- C++/CUDA development environment
- Building SDK from source
- More complex integration

**Pros:**
- ✅ Official NVIDIA SDK
- ✅ High performance
- ✅ Direct control

**Cons:**
- ❌ C++/CUDA (not Python-native)
- ❌ Complex setup
- ❌ Requires compilation

**Setup Steps:**
1. Clone SDK: `git clone https://github.com/NVIDIA/Audio2Face-3D-SDK`
2. Build SDK (follow their instructions)
3. Create Python bindings or use C++ directly
4. Integrate with provider

### Method 3: Application Scripting (GUI Automation)

**Best for:** Quick testing, if other methods don't work

**Requirements:**
- Audio2Face GUI application
- UI automation (like PyAutoGUI)
- Less reliable for production

**Pros:**
- ✅ Uses installed application
- ✅ No additional setup

**Cons:**
- ❌ Requires GUI running
- ❌ Less reliable
- ❌ Slower

---

## Step 5: Recommended Path Forward

**For The Talking Heads project, I recommend:**

### Phase 1: Try py_audio2face First

1. **Install Audio2Face** (if not already)
   - Download standalone from Reallusion
   - Install and verify it works

2. **Set up Headless Server**
   - Audio2Face can run in headless mode
   - Check documentation for headless server setup
   - Start server on localhost

3. **Install Python Package**
   ```bash
   pip install py-audio2face
   ```

4. **Test Integration**
   - Create simple test script
   - Verify it can connect to Audio2Face server
   - Test animation generation

5. **Update Provider**
   - Replace skeleton code with py_audio2face calls
   - Test with real audio/character

### Phase 2: Fallback Options

If py_audio2face doesn't work:
- Try SDK integration (more complex)
- Or use application scripting (less ideal)

---

## Step 6: What You Need to Do Now

### Immediate Actions:

1. **Check if Audio2Face is installed:**
   ```powershell
   # Check for Audio2Face
   Get-ChildItem "$env:LOCALAPPDATA\ov\pkg" -Filter "*audio2face*" -Recurse -ErrorAction SilentlyContinue
   ```

2. **If NOT installed, download it:**
   - Visit: https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html
   - Download standalone package
   - Install following their instructions

3. **Test Audio2Face:**
   - Launch Audio2Face application
   - Try loading a sample character
   - Try generating animation from sample audio
   - Verify it works

4. **Check for Headless Server:**
   - Look for Audio2Face server/headless mode
   - Check documentation for server setup
   - Try starting server if available

5. **Report Back:**
   - Is Audio2Face installed? ✅/❌
   - Can you launch the GUI? ✅/❌
   - Is headless server available? ✅/❌/?
   - What version did you install?

---

## Step 7: Integration Implementation Plan

Once you confirm Audio2Face is working, I will:

1. **Update Provider Implementation:**
   - Implement using py_audio2face (if server available)
   - Or implement SDK integration (if needed)
   - Or implement application scripting (fallback)

2. **Test Integration:**
   - Create test script
   - Verify audio → animation works
   - Test with your characters

3. **Update Configuration:**
   - Add Audio2Face-specific settings
   - Configure character paths
   - Set up output directories

4. **Documentation:**
   - Update setup guide with your specific setup
   - Add troubleshooting section
   - Document character requirements

---

## Questions to Answer

Please check and report back:

1. **Audio2Face Installation:**
   - [ ] Is Audio2Face installed?
   - [ ] Where is it installed? (path)
   - [ ] Can you launch the GUI?
   - [ ] What version?

2. **Headless Server:**
   - [ ] Is headless server available?
   - [ ] Can you start it?
   - [ ] What port does it use?

3. **Characters:**
   - [ ] Do you have character USD files?
   - [ ] Where are they located?
   - [ ] Are they Audio2Face-compatible?

4. **Preferences:**
   - [ ] Prefer Python API (py_audio2face)?
   - [ ] Prefer SDK (more complex)?
   - [ ] Prefer application scripting (simpler but less reliable)?

---

## Next Steps

1. **You:** Check Audio2Face installation status
2. **You:** Install Audio2Face if needed
3. **You:** Test Audio2Face GUI
4. **You:** Report back with status
5. **Me:** Update provider implementation based on your setup
6. **Together:** Test and verify integration works

---

## Resources

- **Audio2Face Download:** https://www.reallusion.com/iclone/nvidia-omniverse/Audio2Face.html
- **py_audio2face:** https://github.com/SocAIty/py_audio2face
- **Audio2Face-3D-SDK:** https://github.com/NVIDIA/Audio2Face-3D-SDK
- **Audio2Face Docs:** https://docs.omniverse.nvidia.com/audio2face/
- **Audio2Face-3D-Samples:** https://github.com/NVIDIA/Audio2Face-3D-Samples

---

## Current Status

- ✅ Provider skeleton created
- ⏳ Waiting for Audio2Face installation confirmation
- ⏳ Waiting for integration method decision
- ⏳ Ready to implement once setup confirmed

Let me know what you find, and I'll help you get Audio2Face integrated properly!

