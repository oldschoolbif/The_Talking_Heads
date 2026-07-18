# Why VALL-E X and DreamTalk Require Manual Installation

## Overview

Both **VALL-E X** and **DreamTalk** are reported as requiring "manual installation" because they are **NOT available as pip packages**. Unlike Bark (`pip install bark`) or Coqui TTS (`pip install coqui-tts`), these tools must be cloned from GitHub and set up manually.

## VALL-E X

### Why Manual Installation?

1. **No pip package**: There is no `pip install valle` command
2. **GitHub repository**: Must be cloned from: https://github.com/Plachtaa/VALL-E-X
3. **Custom setup**: Requires specific dependencies and model checkpoints
4. **Multiple implementations**: Various community ports exist, each with different setup

### What the Test Checks For

The test script looks for:
- Directory: `~/valle` or `./valle` or `/opt/valle`
- File: `inference.py` in that directory

**Current Status**: Neither directory nor inference script found → Reports "manual installation required"

### To Install VALL-E X

```bash
# Clone repository
cd ~
git clone https://github.com/Plachtaa/VALL-E-X.git valle
cd valle

# Install dependencies
pip install -r requirements.txt

# Download model checkpoints (follow repo instructions)

# Update config.yaml
# valle_path: ~/valle
```

**See**: `docs/VALLE_SETUP.md` for complete instructions

---

## DreamTalk

### Why Manual Installation?

1. **No pip package**: There is no `pip install dreamtalk` command
2. **GitHub repository**: Must be cloned from: https://github.com/ali-vilab/dreamtalk
3. **Checkpoints required**: Model checkpoints must be obtained separately (email request)
4. **Custom environment**: Requires specific Python version and dependencies

### What the Test Checks For

The test script checks:
- Directory: `~/dreamtalk` (or path in `config.yaml`)
- File: `inference.py` in that directory
- Python executable: Available and working

**Current Status**: Directory `~/dreamtalk` not found → Reports "needs to be installed and configured"

### To Install DreamTalk

```bash
# Clone repository
cd ~
git clone https://github.com/ali-vilab/dreamtalk.git
cd dreamtalk

# Set up Python environment (Python 3.7-3.11)
conda create -n dreamtalk python=3.7.0
conda activate dreamtalk

# Install dependencies
pip install -r requirements.txt

# Request checkpoints via email (see docs/DREAMTALK_SETUP.md)
# Place checkpoints in dreamtalk/checkpoints/

# Update config.yaml
# dreamtalk_path: ~/dreamtalk
```

**See**: `docs/DREAMTALK_SETUP.md` for complete instructions

---

## Are They Required?

**NO** - Both are **OPTIONAL** providers:

### For TTS:
- ✅ **Bark** - Already installed and working
- ✅ **XTTS-v2** - Installed (accept ToS to use)
- ⚠️ **VALL-E X** - Optional, advanced alternative

### For Avatars:
- ✅ **HeyGen** - Working (cloud API)
- ✅ **D-ID** - Working (cloud API)
- ⚠️ **DreamTalk** - Optional, local GPU alternative

---

## Summary

| Provider | Installation Method | Status | Required? |
|----------|---------------------|--------|-----------|
| **Bark** | `pip install bark` | ✅ Installed | ✅ Working |
| **XTTS-v2** | `pip install coqui-tts` | ✅ Installed | ⏳ Needs ToS |
| **VALL-E X** | Manual (GitHub clone) | ❌ Not installed | ❌ Optional |
| **DreamTalk** | Manual (GitHub clone) | ❌ Not installed | ❌ Optional |
| **HeyGen** | API (configured) | ✅ Working | ✅ Available |
| **D-ID** | API (configured) | ✅ Working | ✅ Available |

**Bottom Line**: You have working TTS (Bark) and working Avatars (HeyGen/D-ID). VALL-E X and DreamTalk are advanced local alternatives that require manual setup if you want to use them.

