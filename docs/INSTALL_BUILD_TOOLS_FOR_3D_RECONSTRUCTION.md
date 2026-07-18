# Installing Build Tools for 3D Reconstruction (3DDFA & DECA)

**Date:** November 2025  
**Purpose:** Install C++ and CUDA build tools needed for 3DDFA and DECA

---

## Required Tools

### 1. Visual Studio Build Tools (C++ Compiler) ⭐ **REQUIRED**

**Why:** 3DDFA needs Cython extensions compiled to `.pyd` files (Windows Python extensions)

**What to Install:**
- Visual Studio Build Tools 2022 (or Visual Studio 2022 Community)
- C++ build tools workload
- Windows 10/11 SDK

### 2. CUDA Toolkit ⭐ **REQUIRED for DECA**

**Why:** DECA needs CUDA extensions compiled

**What to Install:**
- CUDA Toolkit 11.8 or 12.x (match your PyTorch CUDA version)
- cuDNN (optional but recommended)

---

## Installation Steps

### Step 1: Install Visual Studio Build Tools

#### Option A: Visual Studio Build Tools (Recommended - Smaller Download)

1. **Download:**
   - Go to: https://visualstudio.microsoft.com/downloads/
   - Scroll down to "Tools for Visual Studio"
   - Click "Build Tools for Visual Studio 2022"
   - Download (~3-4 GB)

2. **Install:**
   - Run the installer
   - Select "C++ build tools" workload
   - Under "Installation details", ensure:
     - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
     - ✅ Windows 10/11 SDK (latest version)
     - ✅ C++ CMake tools for Windows
   - Click "Install" (takes 15-30 minutes)

3. **Verify:**
   ```powershell
   # Open new PowerShell window (important!)
   cl
   # Should show Microsoft C/C++ compiler version info
   ```

#### Option B: Visual Studio 2022 Community (Full IDE)

1. **Download:**
   - Go to: https://visualstudio.microsoft.com/vs/community/
   - Download Visual Studio 2022 Community (free)

2. **Install:**
   - Run installer
   - Select "Desktop development with C++" workload
   - Install (takes 30-60 minutes, ~6-8 GB)

---

### Step 2: Verify CUDA Installation

**Check if CUDA is already installed:**
```powershell
nvcc --version
nvidia-smi
```

**If CUDA is not installed:**

1. **Check PyTorch CUDA version:**
   ```powershell
   python -c "import torch; print('PyTorch CUDA:', torch.version.cuda)"
   ```
   - You have: PyTorch 2.5.1+cu121 (CUDA 12.1)

2. **Download CUDA Toolkit 12.x:**
   - Go to: https://developer.nvidia.com/cuda-downloads
   - Select: Windows → x86_64 → 10/11 → exe (local)
   - Download CUDA Toolkit 12.1 or 12.4 (match PyTorch)

3. **Install:**
   - Run installer
   - Choose "Express Installation"
   - Takes 10-15 minutes

4. **Verify:**
   ```powershell
   nvcc --version
   # Should show CUDA compiler version
   ```

---

### Step 3: Set Up Environment Variables

**After installing Visual Studio Build Tools:**

1. **Open new PowerShell window** (important - to get new PATH)

2. **Verify compiler is in PATH:**
   ```powershell
   where cl
   # Should show path like: C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\...
   ```

3. **If not found, manually set:**
   ```powershell
   # Find Visual Studio installation
   $vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath
   
   # Set environment variables (for current session)
   $env:PATH = "$vsPath\VC\Tools\MSVC\14.xx.xxxxx\bin\Hostx64\x64;$env:PATH"
   ```

**For CUDA:**
- CUDA installer should add to PATH automatically
- Verify: `nvcc --version` works

---

### Step 4: Build 3DDFA Extensions

**After Visual Studio Build Tools are installed:**

```powershell
cd d:\dev\3DDFA_V2

# Build FaceBoxes NMS (Cython)
cd FaceBoxes
python setup.py build_ext --inplace
cd ..

# Build Sim3DR (Cython)
cd Sim3DR
python setup.py build_ext --inplace
cd ..

# Build render extension (C)
cd utils/asset
# On Windows, need to compile render.c
# May need to use Visual Studio or MinGW
cd ../..
```

**Or use the build script (if adapted for Windows):**
- May need to adapt `build.sh` for Windows
- Or build manually as above

---

### Step 5: Build DECA Extensions

**DECA uses PyTorch JIT compilation, which should work automatically:**

```powershell
cd d:\dev\DECA

# Install requirements
pip install -r requirements.txt

# DECA will compile CUDA extensions on first run
# Or use pytorch3d if compilation fails
```

**If DECA CUDA compilation fails:**
- Install pytorch3d: `pip install pytorch3d`
- Use `--rasterizer_type=pytorch3d` flag

---

## Quick Installation Script

I'll create a PowerShell script to help automate this:

```powershell
# Check for Visual Studio Build Tools
$vsPath = & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null

if ($vsPath) {
    Write-Host "[OK] Visual Studio found: $vsPath" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Visual Studio Build Tools not found" -ForegroundColor Red
    Write-Host "Download from: https://visualstudio.microsoft.com/downloads/" -ForegroundColor Yellow
}

# Check for CUDA
$cudaVersion = nvcc --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] CUDA found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] CUDA not found" -ForegroundColor Red
    Write-Host "Download from: https://developer.nvidia.com/cuda-downloads" -ForegroundColor Yellow
}
```

---

## Installation Time Estimates

| Tool | Download Size | Install Time | Total |
|------|--------------|--------------|-------|
| Visual Studio Build Tools | 3-4 GB | 15-30 min | ~45 min |
| Visual Studio Community | 6-8 GB | 30-60 min | ~90 min |
| CUDA Toolkit | 2-3 GB | 10-15 min | ~25 min |
| **Total** | **5-7 GB** | **25-45 min** | **~70-90 min** |

---

## After Installation

1. **Restart PowerShell** (to get new PATH)
2. **Verify tools:**
   ```powershell
   cl              # C++ compiler
   nvcc --version  # CUDA compiler
   ```
3. **Build 3DDFA:**
   ```powershell
   cd d:\dev\3DDFA_V2
   # Follow build steps above
   ```
4. **Test DECA:**
   ```powershell
   cd d:\dev\DECA
   # Install requirements and test
   ```

---

## Troubleshooting

### "cl is not recognized"
- **Solution:** Open new PowerShell window
- **Or:** Manually add Visual Studio to PATH

### "nvcc is not recognized"
- **Solution:** Restart PowerShell
- **Or:** Add CUDA bin to PATH manually

### Cython build fails
- **Solution:** Ensure Cython is installed: `pip install cython`
- **Check:** Python version compatibility (3.8-3.11 recommended)

### CUDA compilation fails
- **Solution:** Use pytorch3d instead
- **Or:** Check CUDA version matches PyTorch

---

## Next Steps After Installation

1. ✅ Install Visual Studio Build Tools
2. ✅ Verify CUDA (or install if needed)
3. ✅ Build 3DDFA extensions
4. ✅ Build DECA extensions (or use pytorch3d)
5. ✅ Test 3DDFA with headshot image
6. ✅ Test DECA with headshot image

Let's start with Visual Studio Build Tools!

