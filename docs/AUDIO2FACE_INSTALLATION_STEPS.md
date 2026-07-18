# Audio2Face Installation Steps

**Date:** November 2025

## Quick Answer

**You're currently in the Omniverse Editor.** To install Audio2Face, you need to use the **Omniverse Launcher** (a separate application).

## Step-by-Step Installation

### 1. Open Omniverse Launcher

The Omniverse Launcher is a separate application from the Editor. Look for:
- **Desktop shortcut:** "Omniverse Launcher"
- **Start Menu:** Search for "Omniverse Launcher"
- **Or:** Close the Editor and look for the Launcher icon

### 2. Install Audio2Face Extension

Once in the Launcher:

1. **Click the "Exchange" tab** (at the top)
2. **Search for "Audio2Face"** in the search bar
3. **Find "Audio2Face"** in the results
4. **Click "Install"** button

The installation will download and install the Audio2Face extension.

### 3. Verify Installation

After installation, you can verify it's installed:

```powershell
# Check if Audio2Face package exists
$appdata = [Environment]::GetFolderPath('LocalApplicationData')
$ovPath = Join-Path $appdata "ov\pkg"
Get-ChildItem $ovPath -Directory | Where-Object { $_.Name -match "audio2face" }
```

Or test with Python:

```bash
python scripts/test_audio2face_server.py
```

### 4. Use Audio2Face

Once installed, Audio2Face can be used:

#### Option A: Via Python API (Our Integration)
```python
from py_audio2face import Audio2Face

a2f = Audio2Face()
a2f.init_a2f()  # Starts server automatically
# Use Audio2Face...
```

#### Option B: Via Omniverse Editor
- Open Omniverse Editor (the one you're currently in)
- Audio2Face will be available as an extension/plugin
- You can load character USD files and animate them

## What You're Currently Looking At

The screenshot shows:
- ✅ **Omniverse Editor** - This is the 3D editing environment
- ✅ **RTX 4060 Laptop GPU** - Good GPU for Audio2Face
- ✅ **Omniverse is running** - Confirmed by the interface

**What's Missing:**
- ❌ **Audio2Face Extension** - Needs to be installed via Launcher

## After Installation

Once Audio2Face is installed:

1. **The provider will auto-detect it** - No config changes needed
2. **Server starts automatically** - When you use `py-audio2face`
3. **Ready to use** - Can generate animations from audio

## Troubleshooting

### Can't Find Omniverse Launcher?

- Check Start Menu for "Omniverse"
- Look for "Omniverse Launcher" vs "Omniverse Create" (Editor)
- Launcher is usually a separate icon

### Audio2Face Not in Exchange?

- Make sure you're logged into Omniverse account
- Check internet connection
- Try refreshing the Exchange tab

### Still Having Issues?

Run the test script to see what's detected:

```bash
python scripts/test_audio2face_server.py
```

## Summary

**Current Location:** Omniverse Editor ✅  
**Need to Go:** Omniverse Launcher → Exchange → Install Audio2Face  
**After Installation:** Audio2Face will work automatically with our integration

