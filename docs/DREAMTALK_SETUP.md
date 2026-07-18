# DreamTalk Setup Guide for The Talking Heads

## Overview

DreamTalk is now integrated as the **default avatar generation engine** in The Talking Heads project. It provides high-quality local GPU-based talking head generation without API costs or content restrictions.

## Prerequisites

- Windows 11 with WSL2
- NVIDIA GPU (RTX 4090 recommended, 8GB+ VRAM minimum)
- CUDA 11.1+ installed
- Python 3.7-3.11
- ~10GB free disk space

## Step 1: Install CUDA in WSL2

```bash
# In WSL2 terminal
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-3

# Verify installation
nvcc --version
nvidia-smi
```

## Step 2: Clone DreamTalk Repository

```bash
cd ~
git clone https://github.com/ali-vilab/dreamtalk.git
cd dreamtalk
```

## Step 3: Set Up Python Environment

```bash
# Create conda environment (recommended)
conda create -n dreamtalk python=3.7.0
conda activate dreamtalk

# Or use venv
python3.7 -m venv venv
source venv/bin/activate
```

## Step 4: Install Dependencies

```bash
# Install PyTorch with CUDA support
conda install pytorch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0 cudatoolkit=11.1 -c pytorch -c conda-forge

# Or with pip (if using venv)
pip install torch==1.8.0 torchvision==0.9.0 torchaudio==0.8.0 --index-url https://download.pytorch.org/whl/cu111

# Install other dependencies
pip install -r requirements.txt
pip install urllib3==1.26.6 transformers==4.28.1 dlib

# Update ffmpeg
conda update ffmpeg
```

## Step 5: Obtain DreamTalk Checkpoints

**Important:** DreamTalk checkpoints are not publicly available due to social impact considerations.

To obtain checkpoints:

1. Send an email to: **mayf18@mails.tsinghua.edu.cn**
2. Request access to DreamTalk checkpoints
3. Agree to use checkpoints solely for academic research purposes
4. Wait for approval and download instructions

Once you have the checkpoints:

```bash
# Create checkpoints directory
mkdir -p checkpoints

# Place downloaded checkpoint files in checkpoints/
# Typical files:
# - checkpoint.pth
# - other model files as provided
```

## Step 6: Configure The Talking Heads

Update `config/config.yaml`:

```yaml
dreamtalk:
  # Path to DreamTalk installation
  dreamtalk_path: ~/dreamtalk  # Or absolute path: /home/username/dreamtalk
  
  # Python executable (auto-detected from venv if available)
  python_exec: python
  
  # Output directory for DreamTalk results
  result_dir: .cache/dreamtalk_outputs
  
  # Default enhancer (gfpgan, None)
  enhancer: gfpgan

avatar:
  engine: dreamtalk  # Set as default
```

## Step 7: Prepare Persona Images

DreamTalk requires source images for each persona. Update `config/personas.yaml`:

```yaml
ALICE:
  name: "Alice"
  avatar:
    engine: dreamtalk
    avatar_id: "alice"  # Used as identifier
    # Add image_path for DreamTalk
    image_path: "examples/personas/alice.jpg"  # Path to persona image
```

Or ensure `avatar_id` points to an existing image file:

```yaml
ALICE:
  avatar:
    avatar_id: "examples/personas/alice.jpg"  # Direct path to image
```

## Step 8: Test Installation

```bash
# Test DreamTalk directly
cd ~/dreamtalk
python inference.py \
    --driven_audio examples/driven_audio/test.wav \
    --source_image examples/source_image/person.jpg \
    --result_dir results \
    --enhancer gfpgan
```

## Step 9: Test Integration

Run a test with The Talking Heads:

```bash
# From project root
python scripts/test_e2e_2personas.py
```

The system should:
1. Detect DreamTalk as the default engine
2. Use DreamTalk for avatar generation
3. Generate videos locally on your GPU

## Troubleshooting

### DreamTalk Not Found

**Error:** `DreamTalk Python executable not found`

**Solution:**
- Verify `dreamtalk_path` in `config.yaml` is correct
- Ensure DreamTalk is cloned and installed
- Check that `inference.py` exists in DreamTalk directory

### CUDA Out of Memory

**Error:** `CUDA out of memory`

**Solution:**
- Reduce batch size (process videos sequentially)
- Use lower resolution
- Close other GPU-intensive applications
- Check GPU memory: `nvidia-smi`

### Checkpoints Not Found

**Error:** `Checkpoint file not found`

**Solution:**
- Ensure checkpoints are downloaded and placed correctly
- Verify checkpoint paths in DreamTalk configuration
- Contact DreamTalk maintainers if checkpoints are missing

### Import Errors

**Error:** `ModuleNotFoundError` or `ImportError`

**Solution:**
```bash
# Reinstall dependencies
cd ~/dreamtalk
pip install -r requirements.txt --force-reinstall

# Verify PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Slow Performance

**Check:**
- GPU is being used: `nvidia-smi` should show Python process
- CUDA is available: `python -c "import torch; print(torch.cuda.is_available())"`
- GPU drivers are up to date

## Performance Optimization

### For RTX 4090 (24GB VRAM):

1. **Parallel Generation:**
   - DreamTalk can process multiple videos in parallel
   - Use `max_workers=3-5` in `generate_multiple()`

2. **Quality Settings:**
   - Use `enhancer: gfpgan` for best quality
   - Higher resolution = better quality but slower

3. **Memory Management:**
   - Process videos in batches
   - Clear GPU cache between generations if needed

## Integration Details

### How It Works

1. **Provider Selection:**
   - DreamTalk is set as default in `config.yaml`
   - Can be overridden per-persona or globally

2. **Image Path Resolution:**
   - Checks `persona.avatar.image_path` first
   - Falls back to `avatar_id` if it's a file path
   - Raises error if no image found

3. **Video Generation:**
   - Calls DreamTalk `inference.py` via subprocess
   - Streams output for progress updates
   - Locates generated video file
   - Returns video path and duration

4. **Fallback:**
   - If DreamTalk unavailable, falls back to HeyGen or D-ID
   - Automatic provider switching based on availability

## Next Steps

1. ✅ Complete DreamTalk installation
2. ✅ Obtain checkpoints
3. ✅ Configure `config.yaml`
4. ✅ Add persona images
5. ✅ Test generation
6. ✅ Benchmark performance vs HeyGen/D-ID

## Resources

- **DreamTalk GitHub:** https://github.com/ali-vilab/dreamtalk
- **DreamTalk Project Page:** https://dreamtalk-project.github.io/
- **Checkpoint Request:** mayf18@mails.tsinghua.edu.cn
- **CUDA Installation:** https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
- **WSL2 GPU Support:** https://docs.nvidia.com/cuda/wsl-user-guide/index.html

## Notes

- DreamTalk requires checkpoints (not publicly available)
- Contact maintainers for checkpoint access
- Local generation is faster than API calls (no network latency)
- Your RTX 4090 can handle multiple parallel generations
- DreamTalk provides highest quality output

