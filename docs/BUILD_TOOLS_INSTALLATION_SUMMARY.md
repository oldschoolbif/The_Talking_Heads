# Build Tools Installation Summary

**Date:** November 2025  
**Status:** Ready to install

---

## What You Need

### ✅ Already Have:
- Python 3.12 ✅
- PyTorch with CUDA 12.1 ✅
- Cython 3.2.1 ✅

### ❌ Need to Install:
1. **Visual Studio Build Tools** (for C++ compilation)
2. **CUDA Toolkit 12.x** (for CUDA compilation)

---

## Installation Steps

### 1. Visual Studio Build Tools

**Download:** https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

**Install:**
- Run installer
- Select "C++ build tools" workload
- Ensure these are checked:
  - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
  - ✅ Windows 10/11 SDK
  - ✅ C++ CMake tools for Windows
- Install (15-30 minutes)

**Size:** ~3-4 GB

---

### 2. CUDA Toolkit 12.x

**Download:** https://developer.nvidia.com/cuda-downloads

**Select:**
- Windows
- x86_64
- Windows 10/11
- exe (local)

**Install:**
- Run installer
- Choose "Express Installation"
- Takes 10-15 minutes

**Size:** ~2-3 GB

**Note:** Your PyTorch uses CUDA 12.1, so install CUDA Toolkit 12.1 or 12.4 (both compatible)

---

## After Installation

1. **Close PowerShell** (important!)
2. **Open new PowerShell window**
3. **Verify installation:**
   ```powershell
   cd d:\dev\The_Talking_Heads
   .\scripts\check_build_tools.ps1
   ```

**Expected output:**
```
[OK] Visual Studio found
[OK] C++ compiler found in PATH
[OK] CUDA Toolkit found
[OK] All build tools are ready!
```

---

## Next Steps After Installation

1. Build 3DDFA extensions
2. Build DECA extensions
3. Test 3D reconstruction with your headshot images

---

## Troubleshooting

### "cl is not recognized"
- **Solution:** Open new PowerShell window
- **Or:** Use "Developer Command Prompt for VS 2022"

### "nvcc is not recognized"
- **Solution:** Restart PowerShell
- **Or:** Add CUDA to PATH manually

### Build fails
- Check Python version (3.8-3.11 recommended for 3DDFA)
- Ensure all dependencies installed
- Check error messages for specific issues

---

## Time Estimate

- **Visual Studio Build Tools:** 15-30 minutes
- **CUDA Toolkit:** 10-15 minutes
- **Total:** ~30-45 minutes

---

## Ready to Install?

Run the installation guide script:
```powershell
.\scripts\install_build_tools_guide.ps1
```

Or follow the manual steps above!

