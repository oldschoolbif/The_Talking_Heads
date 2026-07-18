# Testing FLAME 2023 with DECA

**Date:** November 2025  
**Purpose:** Test if DECA works with FLAME 2023 model

---

## Quick Test

**Run the test script:**
```powershell
cd d:\dev\The_Talking_Heads
.\scripts\test_flame2023_with_deca.ps1
```

The script will:
1. ✅ Backup your current FLAME 2020 model
2. ✅ Replace with FLAME 2023 model
3. ✅ Test DECA reconstruction
4. ✅ Restore FLAME 2020 if test fails

---

## Manual Steps

### Step 1: Download FLAME 2023

1. Go to: https://flame.is.tue.mpg.de/download.php
2. Select: **"FLAME 2023 Open"** (CC-BY-4.0, commercial use allowed)
   - Or **"FLAME 2023"** (revised eye region, improved expressions)
3. Download and extract
4. Find `generic_model.pkl` in the extracted files

---

### Step 2: Backup Current Model

```powershell
cd d:\dev\DECA\data
Copy-Item generic_model.pkl generic_model.pkl.backup
```

---

### Step 3: Replace with FLAME 2023

```powershell
# Copy FLAME 2023 model to DECA data folder
Copy-Item "path\to\FLAME2023\generic_model.pkl" -Destination "d:\dev\DECA\data\generic_model.pkl" -Force
```

---

### Step 4: Test DECA

```powershell
cd d:\dev\DECA
python demos/demo_reconstruct.py -i TestSamples/examples/IMG_0392_inputs.jpg
```

**What to look for:**
- ✅ **Success:** Reconstruction completes without errors
- ❌ **Failure:** Errors about model format, missing keys, or attribute errors

---

### Step 5: Restore FLAME 2020 (if needed)

If FLAME 2023 doesn't work:

```powershell
cd d:\dev\DECA\data
Copy-Item generic_model.pkl.backup generic_model.pkl -Force
```

---

## Expected Results

### ✅ Success Indicators

- DECA runs without errors
- 3D reconstruction completes
- Output files are generated
- Quality looks good (or better than FLAME 2020)

### ❌ Failure Indicators

- `KeyError` or `AttributeError` when loading model
- `FileNotFoundError` for model components
- Shape mismatch errors
- Reconstruction fails or produces bad results

---

## Troubleshooting

### "KeyError" or "AttributeError"

**Problem:** FLAME 2023 has different structure than FLAME 2020

**Solution:**
- FLAME 2023 may not be compatible with DECA
- Try PIXIE or EMOCA instead (they support FLAME 2023)

---

### "Shape mismatch" errors

**Problem:** Model dimensions don't match what DECA expects

**Solution:**
- FLAME 2023 may have different vertex counts
- DECA code may need modifications
- Consider switching to PIXIE

---

### Model loads but quality is bad

**Problem:** FLAME 2023 works but produces poor results

**Solution:**
- Check if DECA needs code updates for FLAME 2023
- Compare results with FLAME 2020
- May need to stick with FLAME 2020

---

## Comparison: FLAME 2020 vs 2023

| Feature | FLAME 2020 | FLAME 2023 |
|---------|------------|------------|
| **Compatibility** | ✅ Works with DECA | ⚠️ May not work |
| **Eye Region** | Good | ✅ Better (revised) |
| **Expressions** | Good | ✅ Better (improved) |
| **Training Data** | Good | ✅ More data |
| **License** | Research use | ✅ CC-BY-4.0 (Open) |
| **Commercial Use** | Limited | ✅ Allowed (Open) |

---

## If FLAME 2023 Doesn't Work

**Option 1: Stick with FLAME 2020**
- ✅ Works perfectly with DECA
- ✅ Good quality
- ✅ Stable and tested

**Option 2: Switch to PIXIE**
- ✅ Official FLAME 2023 support
- ✅ More recent tool
- ✅ Better quality

**Option 3: Modify DECA**
- ⚠️ Requires code changes
- ⚠️ May be complex
- ⚠️ Not recommended unless you need FLAME 2023 features

---

## Next Steps

1. **Run the test script** to check compatibility
2. **If it works:** Great! You have FLAME 2023 benefits
3. **If it doesn't:** Consider PIXIE or stick with FLAME 2020

**Want help?** Let me know the test results and I can help troubleshoot!

