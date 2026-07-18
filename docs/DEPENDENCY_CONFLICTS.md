# Dependency Version Conflicts and Solutions

## Current Status

### Installed Versions
- **torch**: 2.5.1+cu121 (CUDA-enabled) ✓
- **numpy**: 2.3.5 (NumPy 2.x)
- **scipy**: 1.15.3
- **librosa**: 0.10.2.post1
- **soundfile**: 0.12.1
- **pydub**: 0.25.1
- **bark**: 0.1.5 ✓
- **TTS (Coqui)**: NOT INSTALLED ✗

## Identified Conflicts

### 1. TTS (Coqui TTS) Installation Issue

**Problem**: Package `TTS` cannot be found via pip

**Current Status**: NOT INSTALLED

**Solutions** (choose one):

#### Option A: Install from GitHub (Recommended)
```bash
pip install git+https://github.com/coqui-ai/TTS.git
```
- **Pros**: Latest version, most features
- **Cons**: Requires git, may take longer to install

#### Option B: Install coqui-tts package
```bash
pip install coqui-tts
```
- **Pros**: Official package name, faster install
- **Cons**: May be older version

#### Option C: Manual installation
1. Clone repository: `git clone https://github.com/coqui-ai/TTS.git`
2. Install: `cd TTS && pip install -e .`
- **Pros**: Full control, can modify code
- **Cons**: Most complex, requires git

#### Option D: Skip XTTS-v3, use Bark only
- **Pros**: No installation needed (Bark already works)
- **Cons**: Missing XTTS-v3 features (better voice cloning)

**Recommendation**: Try Option A first, fall back to Option B if it fails.

---

### 2. NumPy 2.x Compatibility

**Problem**: NumPy 2.3.5 installed, but some packages may expect NumPy <2.0

**Current Status**: numpy 2.3.5, scipy 1.15.3

**Impact**: 
- SciPy 1.15.3 should be compatible with NumPy 2.x
- Some older packages may have issues
- Current tests show imports work fine

**Solutions** (choose one):

#### Option A: Keep NumPy 2.x (Current)
```bash
# Do nothing - already installed
```
- **Pros**: Latest features, performance improvements
- **Cons**: May break some older packages
- **Status**: Currently working ✓

#### Option B: Downgrade to NumPy 1.x
```bash
pip install 'numpy<2.0'
```
- **Pros**: Maximum compatibility with older packages
- **Cons**: Missing NumPy 2.x improvements, may conflict with newer packages
- **Impact**: May require reinstalling packages that depend on NumPy

#### Option C: Upgrade SciPy
```bash
pip install --upgrade scipy
```
- **Pros**: Better NumPy 2.x compatibility
- **Cons**: May break other dependencies
- **Status**: SciPy 1.15.3 already supports NumPy 2.x

**Recommendation**: Keep Option A (current setup) unless you encounter specific errors.

---

### 3. PyTorch CUDA Availability

**Problem**: PyTorch CUDA version installed, but GPU may not be detected

**Current Status**: torch 2.5.1+cu121 installed

**Solutions** (choose one):

#### Option A: Verify GPU is detected
```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```
- If `False`: GPU drivers may need update or CUDA version mismatch
- If `True`: GPU acceleration is available ✓

#### Option B: Install CPU-only PyTorch (if GPU not available)
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio
```
- **Pros**: Smaller package, faster install
- **Cons**: No GPU acceleration (much slower)

#### Option C: Match CUDA version
- Check CUDA version: `nvidia-smi`
- Install matching PyTorch: `pip install torch --index-url https://download.pytorch.org/whl/cu118` (for CUDA 11.8)
- **Pros**: Proper GPU support
- **Cons**: Need to match exact CUDA version

**Recommendation**: Verify GPU first (Option A), then proceed accordingly.

---

## Summary of Recommendations

1. **TTS Installation**: Try `pip install git+https://github.com/coqui-ai/TTS.git` first
2. **NumPy**: Keep current version (2.3.5) unless issues arise
3. **PyTorch**: Verify GPU detection, keep CUDA version if GPU is available

## Testing After Changes

Run these commands to verify:
```bash
# Check all dependencies
python scripts/check_dependency_conflicts.py

# Test TTS providers
python scripts/test_local_providers.py

# Test basic functionality
python scripts/test_tts_basic.py
```

## Notes

- `pip check` shows no broken requirements ✓
- All current imports work correctly ✓
- Bark TTS is functional ✓
- Main issue is TTS (Coqui) installation

