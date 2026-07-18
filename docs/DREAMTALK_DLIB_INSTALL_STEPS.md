# Step-by-Step: Installing dlib for DreamTalk (Windows, No Conda)

Since Conda is not available, you need to install Visual Studio Build Tools to compile dlib from source.

## Quick Steps

### Step 1: Install Visual Studio Build Tools

1. **Download:** https://visualstudio.microsoft.com/downloads/
   - Scroll down to "Tools for Visual Studio"
   - Click "Build Tools for Visual Studio 2022" (or latest version)

2. **Run the installer:**
   - When prompted, select **"Desktop development with C++"** workload
   - This includes the C++ compiler, Windows SDK, and CMake
   - Click "Install" (this will take 10-20 minutes)

3. **Wait for installation to complete**

### Step 2: Install CMake (if not included)

1. **Download:** https://cmake.org/download/
   - Choose "Windows x64 Installer"

2. **Run installer:**
   - ✅ **IMPORTANT:** Check "Add CMake to system PATH" during installation
   - Click "Install"

### Step 3: Install dlib

1. **Open a NEW PowerShell window** (important - to pick up Visual Studio environment)

2. **Navigate to project:**
   ```powershell
   cd D:\dev\The_Talking_Heads
   ```

3. **Install dlib:**
   ```powershell
   python -m pip install dlib
   ```
   
   **Note:** This will compile dlib from source and may take 10-30 minutes.

4. **Verify installation:**
   ```powershell
   python -c "import dlib; print(f'dlib version {dlib.__version__}')"
   ```

### Step 4: Test DreamTalk

Once dlib is installed:

```powershell
python scripts/smoke_test_avatar_providers.py
```

## Troubleshooting

### "cmake not found"
- **Solution:** Restart PowerShell after installing CMake, or manually add CMake to PATH

### "cl.exe not found" or "C++ compiler not found"
- **Solution:** Make sure Visual Studio Build Tools are installed with "Desktop development with C++" workload
- Open a NEW PowerShell window after installation

### Installation takes a long time
- **Normal:** Compiling dlib from source takes 10-30 minutes depending on your CPU
- Be patient and let it complete

### "Failed building wheel"
- **Solution:** Make sure Visual Studio Build Tools are installed and you opened a NEW PowerShell window

## Alternative: Install Miniconda

If you prefer to avoid Visual Studio Build Tools:

1. **Download Miniconda:** https://docs.conda.io/en/latest/miniconda.html
2. **Install** (add to PATH during installation)
3. **Open NEW PowerShell window**
4. **Run:**
   ```powershell
   conda create -n dreamtalk python=3.11 -y
   conda activate dreamtalk
   conda install -c conda-forge dlib -y
   python -c "import dlib; print('SUCCESS')"
   ```

## Current Status

- ❌ Conda: Not installed
- ❌ dlib-binary: Failed (no pre-built wheel for Python 3.12)
- ✅ Next step: Install Visual Studio Build Tools + CMake, then compile dlib

