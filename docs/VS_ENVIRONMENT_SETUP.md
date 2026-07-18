# Visual Studio Environment Setup

**Date:** November 2025  
**Purpose:** Make C++ compiler available in regular PowerShell sessions

---

## Problem

Visual Studio Build Tools installs the C++ compiler (`cl.exe`), but it's **not automatically added to PATH**. The compiler is only available in:
- Developer Command Prompt for VS 2022
- PowerShell sessions that manually initialize the VS environment

---

## Solution

We've created a PowerShell script that initializes the Visual Studio environment in any PowerShell session.

---

## Quick Start

### Option 1: Manual Initialization (Per Session)

**Before building 3DDFA or DECA, run:**
```powershell
cd d:\dev\The_Talking_Heads
.\scripts\init_vs_env_best.ps1
```

**Verify:**
```powershell
cl
# Should show Microsoft C/C++ compiler version info
```

---

### Option 2: Automatic Initialization (PowerShell Profile)

**Add to your PowerShell profile to auto-initialize VS environment:**

1. **Find your profile:**
   ```powershell
   $PROFILE
   ```

2. **Edit profile:**
   ```powershell
   notepad $PROFILE
   ```

3. **Add this line:**
   ```powershell
   # Initialize Visual Studio environment
   & "d:\dev\The_Talking_Heads\scripts\init_vs_env_best.ps1" -Quiet | Out-Null
   ```

4. **Reload profile:**
   ```powershell
   . $PROFILE
   ```

**Now VS environment initializes automatically in every PowerShell session!**

---

### Option 3: Use Build Scripts (Recommended)

**The build scripts automatically initialize VS environment:**

```powershell
# Build 3DDFA (auto-initializes VS environment)
.\scripts\build_3ddfa.ps1

# Build DECA (auto-initializes VS environment)
.\scripts\build_deca.ps1
```

---

## Scripts Available

### `scripts/init_vs_env_best.ps1` ⭐ **RECOMMENDED**

**Best method** - Initializes VS environment and sets all required environment variables.

**Usage:**
```powershell
.\scripts\init_vs_env_best.ps1
```

**Quiet mode (for scripts):**
```powershell
.\scripts\init_vs_env_best.ps1 -Quiet
```

**What it does:**
1. Finds Visual Studio installation
2. Runs `vcvars64.bat` via cmd.exe
3. Captures all environment variables
4. Sets them in current PowerShell session
5. Verifies compiler is available

---

### `scripts/build_3ddfa.ps1`

**Builds 3DDFA Cython extensions** - Automatically initializes VS environment.

**Usage:**
```powershell
.\scripts\build_3ddfa.ps1
```

**What it does:**
1. Initializes VS environment
2. Builds FaceBoxes NMS extension
3. Builds Sim3DR extension

---

### `scripts/build_deca.ps1`

**Sets up DECA** - Verifies CUDA and installs requirements.

**Usage:**
```powershell
.\scripts\build_deca.ps1
```

**What it does:**
1. Initializes VS environment (if needed)
2. Verifies CUDA installation
3. Installs DECA requirements
4. Notes that DECA uses JIT compilation

---

## Verification

**Check if VS environment is initialized:**
```powershell
.\scripts\check_build_tools.ps1
```

**Expected output:**
```
[OK] Visual Studio found
[OK] C++ compiler found in PATH  ← This should be OK now!
[OK] CUDA Toolkit found
[OK] All build tools are ready!
```

---

## How It Works

1. **Finds Visual Studio** using `vswhere.exe` or common paths
2. **Locates `vcvars64.bat`** in `VC\Auxiliary\Build\`
3. **Runs batch file** via `cmd.exe` to set environment variables
4. **Captures output** and parses environment variables
5. **Sets variables** in current PowerShell session using `Set-Item env:`

**Key environment variables set:**
- `PATH` - Adds compiler, linker, and other tools
- `INCLUDE` - C++ header file paths
- `LIB` - Library file paths
- `VCINSTALLDIR` - Visual Studio installation directory
- And 100+ other VS-specific variables

---

## Troubleshooting

### "cl is not recognized" after running script

**Solution:**
1. Open a **new PowerShell window**
2. Run `.\scripts\init_vs_env_best.ps1` again
3. Verify with `cl`

### Script fails to find Visual Studio

**Solution:**
1. Check VS is installed: `Test-Path "C:\Program Files\Microsoft Visual Studio\18\Community"`
2. Or find manually: `Get-ChildItem "C:\Program Files\Microsoft Visual Studio\" -Directory`
3. Update script with correct path if needed

### Environment variables not persisting

**This is expected!** The script sets variables for the **current PowerShell session only**.

**To persist:**
- Add to PowerShell profile (Option 2 above)
- Or run script at start of each session
- Or use build scripts (they auto-initialize)

---

## Alternative: Developer Command Prompt

**If you prefer, you can use Developer Command Prompt:**

1. **Open:** Start Menu → Visual Studio 2022 → Developer Command Prompt for VS 2022
2. **Navigate:** `cd d:\dev\The_Talking_Heads`
3. **Run:** `pwsh` (to start PowerShell with VS environment already set)

---

## Next Steps

1. ✅ Initialize VS environment (using one of the options above)
2. ✅ Verify compiler: `cl`
3. ✅ Build 3DDFA: `.\scripts\build_3ddfa.ps1`
4. ✅ Build DECA: `.\scripts\build_deca.ps1`
5. ✅ Test 3D reconstruction

---

## Summary

**Problem:** C++ compiler only available in Developer Command Prompt  
**Solution:** Run `.\scripts\init_vs_env_best.ps1` before building  
**Best Practice:** Add to PowerShell profile or use build scripts

**You're ready to build 3DDFA and DECA!** 🚀

