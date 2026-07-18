# Quick Start: 3D Face Reconstruction from 2D Images

**Date:** November 2025  
**Purpose:** Quick guide to test 3D face reconstruction

---

## Fastest Option: Test 3DDFA

### Installation (5 minutes)

```bash
# Clone repository
git clone https://github.com/cleardusk/3DDFA_V2.git
cd 3DDFA_V2

# Install dependencies
pip install torch torchvision
pip install -r requirements.txt

# Download models (automatic on first run)
python setup.py build_ext --inplace
```

### Test with Your Headshot (1 minute)

```bash
# Basic test
python demo.py -i path/to/headshot.jpg -o output.obj

# With visualization
python demo.py -i path/to/headshot.jpg -o output.obj --show_flag True
```

### Output

- **3D face mesh** (OBJ format)
- **Texture map** (if available)
- **Facial landmarks**

---

## Check Omniverse Create (Since You Have It!)

### Steps:

1. **Open Omniverse Create**
2. **Look for:**
   - "Face Reconstruction" tool
   - "Image to USD" converter
   - "Photogrammetry" tools
   - "Mesh Import" with face detection

3. **If available:**
   - Import your headshot image
   - Use face reconstruction tool
   - Export as USD
   - **Direct compatibility with Audio2Face!**

---

## Test DECA (Higher Quality)

### Installation (10 minutes)

```bash
git clone https://github.com/YadiraF/DECA.git
cd DECA
pip install -r requirements.txt
# Download models from releases
```

### Test

```bash
python demos/demo_reconstruct.py -i path/to/headshot.jpg
```

---

## Convert OBJ → USD

If you get OBJ/PLY from reconstruction, convert to USD:

### Option 1: Python USD Library

```python
from pxr import Usd, UsdGeom, Gf

# Create USD stage
stage = Usd.Stage.CreateNew("output.usd")

# Import OBJ mesh (simplified)
# You'll need to parse OBJ and create USD mesh
# This is complex - may need Blender/Maya instead
```

### Option 2: Blender (Easier)

```bash
# 1. Import OBJ in Blender
# 2. Export as USD
# 3. Use USD in Audio2Face
```

### Option 3: Omniverse Create

```bash
# 1. Import OBJ in Omniverse Create
# 2. Export as USD
# 3. Use in Audio2Face
```

---

## Quick Comparison Test

**Test all three and compare:**

1. **SadTalker** - 2D → Video (simplest)
2. **3DDFA** - 2D → 3D → USD → Audio2Face (complex)
3. **Omniverse Create** - 2D → USD (if available, easiest for Audio2Face)

**See which gives best results for your use case!**

