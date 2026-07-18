# FLAME 2023 Extraction Guide

**Date:** November 2025  
**Purpose:** Where to extract FLAME 2023 ZIP and how to set it up

---

## Quick Answer

**Extract anywhere temporarily** (Downloads, Desktop, temp folder)  
**Then copy `generic_model.pkl` to:** `d:\dev\DECA\data\`

---

## Step-by-Step

### Option 1: Extract to Downloads (Easiest)

1. **Download FLAME 2023 Open ZIP** to your Downloads folder
2. **Extract ZIP** to Downloads (or anywhere convenient)
   ```powershell
   # Example: Extract to Downloads
   Expand-Archive -Path "$env:USERPROFILE\Downloads\FLAME2023.zip" -DestinationPath "$env:USERPROFILE\Downloads\FLAME2023"
   ```
3. **Find `generic_model.pkl`** inside the extracted folder
4. **Use test script** - It will ask for the path:
   ```powershell
   cd d:\dev\The_Talking_Heads
   .\scripts\test_flame2023_with_deca.ps1
   # When prompted, enter path to generic_model.pkl
   ```

---

### Option 2: Extract Directly to Temp Folder

```powershell
# Extract to temp folder
$tempPath = "$env:TEMP\FLAME2023"
Expand-Archive -Path "path\to\FLAME2023.zip" -DestinationPath $tempPath

# Find generic_model.pkl
$modelFile = Get-ChildItem -Path $tempPath -Recurse -Filter "generic_model.pkl" | Select-Object -First 1

# Copy to DECA data folder
Copy-Item $modelFile.FullName -Destination "d:\dev\DECA\data\generic_model.pkl" -Force
```

---

### Option 3: Use the Setup Script

I can create a script that handles extraction automatically. For now, extract manually and use the test script.

---

## What You're Looking For

**File:** `generic_model.pkl`  
**Size:** ~50-100 MB (uncompressed)  
**Location in ZIP:** Usually in root or in a subfolder

**Structure might be:**
```
FLAME2023.zip
└── FLAME2023/
    └── generic_model.pkl
```

Or:
```
FLAME2023.zip
└── generic_model.pkl  (in root)
```

---

## Final Destination

**Copy `generic_model.pkl` to:**
```
d:\dev\DECA\data\generic_model.pkl
```

**The test script will do this automatically** - just point it to where you extracted the ZIP!

---

## Recommended Workflow

1. **Download FLAME 2023 Open ZIP** to Downloads
2. **Extract to Downloads** (or Desktop - anywhere convenient)
3. **Run test script:**
   ```powershell
   cd d:\dev\The_Talking_Heads
   .\scripts\test_flame2023_with_deca.ps1
   ```
4. **When prompted**, enter the full path to `generic_model.pkl`
   - Example: `C:\Users\YourName\Downloads\FLAME2023\generic_model.pkl`
5. **Script handles the rest** - copies to DECA, tests, backs up old model

---

## Quick PowerShell Commands

**Find generic_model.pkl after extraction:**
```powershell
# If extracted to Downloads
Get-ChildItem "$env:USERPROFILE\Downloads" -Recurse -Filter "generic_model.pkl"
```

**Copy manually (if you prefer):**
```powershell
# Find the file
$modelFile = Get-ChildItem "$env:USERPROFILE\Downloads" -Recurse -Filter "generic_model.pkl" | Select-Object -First 1

# Copy to DECA
Copy-Item $modelFile.FullName -Destination "d:\dev\DECA\data\generic_model.pkl" -Force
```

---

## Summary

**Extract anywhere** → **Find `generic_model.pkl`** → **Use test script** (it handles copying)

Or manually copy `generic_model.pkl` to `d:\dev\DECA\data\`

The test script makes it easy - just extract the ZIP anywhere and point the script to the `generic_model.pkl` file!

