# Downloading FLAME Model for DECA

**Date:** November 2025  
**Purpose:** Get FLAME 2020 model data needed for DECA

---

## Quick Steps

1. **Register at FLAME website** (if you haven't already)
2. **Download FLAME 2020 model**
3. **Extract and place in DECA data folder**

---

## Detailed Instructions

### Step 1: Register at FLAME Website

1. Go to: **https://flame.is.tue.mpg.de/**
2. Click **"Register"** or **"Sign Up"**
3. Create an account (free)
4. **Agree to the FLAME license terms** (required)

**Note:** You must agree to the license terms to download the model.

---

### Step 2: Download FLAME 2020 Model

1. **Go to download page:**
   - **Direct link:** https://flame.is.tue.mpg.de/download.php
   - Or navigate from the main FLAME website

2. **Select the correct version:**
   - **Choose: "FLAME 2020 (fixed mouth, improved expressions, more data)"**
   - ⚠️ **NOT** FLAME 2023 (too new, DECA was built for 2020)
   - ⚠️ **NOT** FLAME Blender Add-on (that's just a Blender plugin)
   - ⚠️ **NOT** FLAME texture space (that's separate texture data)

3. **Download:**
   - Click download link for "FLAME 2020"
   - You'll be prompted to log in if not already logged in
   - Download `FLAME2020.zip` (~200-300 MB)

---

### Step 3: Extract and Place Model

1. **Extract the ZIP file:**
   ```powershell
   # Extract FLAME2020.zip
   Expand-Archive -Path "FLAME2020.zip" -DestinationPath "temp_flame"
   ```

2. **Find the model file:**
   - Look for `generic_model.pkl` in the extracted folder
   - It should be in the root of the FLAME2020 folder

3. **Copy to DECA data folder:**
   ```powershell
   # Copy generic_model.pkl to DECA data folder
   Copy-Item "temp_flame\FLAME2020\generic_model.pkl" -Destination "d:\dev\DECA\data\generic_model.pkl"
   ```

4. **Verify:**
   ```powershell
   Test-Path "d:\dev\DECA\data\generic_model.pkl"
   # Should return True
   ```

---

## Alternative: Manual Download Script

If you prefer, here's a PowerShell script to help:

```powershell
# Download FLAME Model Helper Script
# Note: You still need to manually download from the website
# This script helps with extraction and placement

$flameZip = Read-Host "Enter path to FLAME2020.zip"
$decaDataPath = "d:\dev\DECA\data"

if (Test-Path $flameZip) {
    Write-Host "Extracting FLAME2020.zip..." -ForegroundColor Yellow
    
    # Extract to temp folder
    $tempDir = [System.IO.Path]::GetTempPath() + "flame_extract"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    Expand-Archive -Path $flameZip -DestinationPath $tempDir -Force
    
    # Find generic_model.pkl
    $modelFile = Get-ChildItem -Path $tempDir -Recurse -Filter "generic_model.pkl" | Select-Object -First 1
    
    if ($modelFile) {
        Write-Host "Found generic_model.pkl at: $($modelFile.FullName)" -ForegroundColor Green
        Copy-Item $modelFile.FullName -Destination "$decaDataPath\generic_model.pkl" -Force
        Write-Host "Copied to: $decaDataPath\generic_model.pkl" -ForegroundColor Green
        
        # Cleanup
        Remove-Item $tempDir -Recurse -Force
        Write-Host "Done!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] generic_model.pkl not found in ZIP file" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] ZIP file not found: $flameZip" -ForegroundColor Red
}
```

---

## What You Need

**File:** `generic_model.pkl`  
**Size:** ~200-300 MB (compressed)  
**Location:** `d:\dev\DECA\data\generic_model.pkl`  
**Source:** https://flame.is.tue.mpg.de/download.php  
**Specific Option:** "FLAME 2020 (fixed mouth, improved expressions, more data)"

**Important:** DECA was built and tested with FLAME 2020. While FLAME 2023 exists, use FLAME 2020 for compatibility.

---

## Verification

After placing the file, verify it's there:

```powershell
cd d:\dev\DECA
Test-Path "data\generic_model.pkl"
# Should return True
```

Then test DECA:

```powershell
python demos/demo_reconstruct.py -i TestSamples/examples/IMG_0392_inputs.jpg
```

---

## Troubleshooting

### "File not found" error
- **Check:** File is at `d:\dev\DECA\data\generic_model.pkl`
- **Verify:** File name is exactly `generic_model.pkl` (not `generic_model.pkl.pkl`)

### Download link doesn't work
- **Solution:** Make sure you're logged in and have agreed to license terms
- **Alternative:** Check FLAME website for updated download links

### File is corrupted
- **Solution:** Re-download the ZIP file
- **Check:** File size should be ~200-300 MB compressed

---

## Additional DECA Model Data (Optional)

DECA also needs its trained model. The `fetch_data.sh` script mentions downloading `deca_model.tar` from Google Drive. This is optional for basic reconstruction but needed for full features.

**To get DECA model:**
- File ID: `1rp8kdyLPvErw2dTmqtjISRVvQLj6Yzje`
- Download from: https://drive.google.com/file/d/1rp8kdyLPvErw2dTmqtjISRVvQLj6Yzje/view
- Extract to `d:\dev\DECA\data\`

---

## Summary

1. ✅ Register at https://flame.is.tue.mpg.de/
2. ✅ Download FLAME2020.zip from https://flame.is.tue.mpg.de/download.php
3. ✅ Extract and copy `generic_model.pkl` to `d:\dev\DECA\data\`
4. ✅ Test DECA

**That's it!** Once you have `generic_model.pkl` in place, DECA will work.

