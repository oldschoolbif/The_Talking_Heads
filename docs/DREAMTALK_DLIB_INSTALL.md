# Installing dlib for DreamTalk on Windows

## ✅ EASIEST METHOD: Use dlib-bin (Pre-built, No Compilation!)

**This is the recommended method - no Visual Studio Build Tools needed!**

```powershell
python -m pip install dlib-bin
```

That's it! This installs a pre-built binary wheel for Python 3.12 on Windows.

### Verify Installation

```powershell
python -c "import dlib; print(f'dlib version {dlib.__version__}')"
```

### Test DreamTalk

```powershell
cd D:\dev\The_Talking_Heads
python scripts/smoke_test_avatar_providers.py
```

---

## Alternative Methods (if dlib-bin doesn't work)

### Option 1: dlib-installer

```powershell
python -m pip install dlib-installer
python -c "from dlib_installer import install_dlib; install_dlib()"
```

**Note:** May not have wheels for Python 3.12.

### Option 2: Conda (if available)

```powershell
conda create -n dreamtalk python=3.11 -y
conda activate dreamtalk
conda install -c conda-forge dlib -y
```

### Option 3: Build from Source (Last Resort)

Requires Visual Studio Build Tools:

1. Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
   - Select "Desktop development with C++" workload
2. Install CMake: https://cmake.org/download/ (add to PATH)
3. Open NEW PowerShell window
4. Run: `python -m pip install dlib`

---

## Current Status

- ✅ **dlib-bin:** Works perfectly for Python 3.12 on Windows!
- ✅ **No compilation needed:** Pre-built binary wheel
- ✅ **Easy updates:** Just run `pip install --upgrade dlib-bin`

## Why dlib-bin?

- **No Visual Studio Build Tools required**
- **No compilation** (saves 10-30 minutes)
- **Pre-built for Python 3.12** on Windows
- **Easy to update:** Standard pip upgrade process
- **Works immediately** after installation

## Troubleshooting

### "dlib-bin not found"
- **Solution:** Make sure pip is up to date: `python -m pip install --upgrade pip`

### "ModuleNotFoundError: No module named 'dlib'"
- **Solution:** Verify installation: `python -c "import dlib; print('OK')"`
- If it fails, try: `python -m pip install --force-reinstall dlib-bin`

### DreamTalk still can't import dlib
- **Solution:** Make sure you're using the same Python environment that DreamTalk uses
- Check: `python -c "import sys; print(sys.executable)"`

## Quick Reference

```powershell
# Install dlib (pre-built, no compilation)
python -m pip install dlib-bin

# Verify
python -c "import dlib; print(f'dlib {dlib.__version__}')"

# Test DreamTalk
cd D:\dev\The_Talking_Heads
python scripts/smoke_test_avatar_providers.py

# Update dlib later
python -m pip install --upgrade dlib-bin
```
