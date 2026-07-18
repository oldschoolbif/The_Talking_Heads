# FLAME Model Selection Guide

**Date:** November 2025  
**Purpose:** Choose the correct FLAME model version for DECA

---

## ✅ Correct Choice: FLAME 2020

**Select this option:**
- **"FLAME 2020 (fixed mouth, improved expressions, more data)"**

**Why:**
- DECA was built and tested with FLAME 2020
- The `fetch_data.sh` script downloads FLAME2020.zip
- DECA's code expects the FLAME 2020 model format

---

## ❌ Don't Choose These

### FLAME 2023 Options
- **"FLAME 2023 Open"** - Too new, may have compatibility issues
- **"FLAME 2023 (revised eye region...)"** - Too new, may have compatibility issues

**Why not:** DECA was developed before FLAME 2023 existed. While it might work, FLAME 2020 is guaranteed compatible.

### Other Options
- **"FLAME Blender Add-on"** - This is just a Blender plugin, not the model
- **"FLAME texture space"** - This is texture data, not the base model
- **"Morphable Albedo texture space"** - This is texture data, not the base model
- **"FLAME Vertex Masks"** - Just masks, not the model
- **"FLAME Mediapipe Landmark Embedding"** - Just landmark data, not the model
- **"FLAME 2019"** or **"FLAME 2017"** - Older versions, may not work

---

## Download Options Summary

| Option | Use For DECA? | Notes |
|--------|---------------|-------|
| FLAME 2020 | ✅ **YES** | This is the one! |
| FLAME 2023 | ❌ No | Too new, compatibility unknown |
| FLAME Blender Add-on | ❌ No | Just a Blender plugin |
| FLAME texture space | ❌ No | Texture data only |
| FLAME 2019/2017 | ❌ No | Too old |

---

## What You'll Get

After downloading "FLAME 2020", you'll get:
- `FLAME2020.zip` file (~200-300 MB)
- Inside: `generic_model.pkl` (this is what DECA needs)
- Also includes other FLAME 2020 files (not needed for basic DECA)

---

## Quick Reference

**Download Page:** https://flame.is.tue.mpg.de/download.php  
**Select:** "FLAME 2020 (fixed mouth, improved expressions, more data)"  
**Extract:** `generic_model.pkl` from the ZIP  
**Place:** `d:\dev\DECA\data\generic_model.pkl`

---

## Verification

After downloading, verify you have the right file:

```powershell
# Check file exists
Test-Path "d:\dev\DECA\data\generic_model.pkl"

# Check file size (should be ~50-100 MB uncompressed)
(Get-Item "d:\dev\DECA\data\generic_model.pkl").Length / 1MB
```

If the file is there and ~50-100 MB, you're good to go!

