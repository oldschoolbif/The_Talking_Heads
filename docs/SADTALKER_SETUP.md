# SadTalker Setup Guide for The Talking Heads

## Prerequisites

- Windows 11 with WSL2
- NVIDIA RTX 4090 (24GB VRAM) ✅
- CUDA 11.8+ installed
- Python 3.8-3.11
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

## Step 2: Clone SadTalker Repository

```bash
cd ~
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker
```

## Step 3: Create Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

## Step 4: Install Dependencies

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install -r requirements.txt

# Additional dependencies (if needed)
pip install face-alignment
pip install imageio-ffmpeg
pip install mediapipe
```

## Step 5: Download Pre-trained Models

```bash
# Create checkpoints directory
mkdir -p checkpoints

# Download models (you'll need to get URLs from SadTalker repo)
# Option 1: Use their download script (if available)
python scripts/download_models.py

# Option 2: Manual download
# Check SadTalker GitHub releases or HuggingFace for model files
# Place in checkpoints/ directory
```

## Step 6: Test Installation

```bash
# Test with a simple example
python inference.py \
    --driven_audio examples/driven_audio/bus_chinese.wav \
    --source_image examples/source_image/full_body_1.png \
    --result_dir results \
    --still \
    --preprocess full \
    --enhancer gfpgan
```

## Step 7: Integration with The Talking Heads

### Create SadTalker Provider Class

Create `src/core/sadtalker_provider.py`:

```python
"""
SadTalker local avatar generation provider.
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import shutil

class SadTalkerProvider:
    """Local SadTalker avatar generation provider."""
    
    def __init__(self, config: Dict[str, Any], project_root: Path):
        self.config = config
        self.project_root = project_root
        self.sadtalker_path = Path(config.get("sadtalker_path", "~/SadTalker"))
        self.checkpoints_path = self.sadtalker_path / "checkpoints"
        self.venv_python = self.sadtalker_path / "venv" / "bin" / "python"
        
    def generate(
        self,
        audio_path: Path,
        image_path: Path,
        output_path: Path,
        **kwargs
    ) -> Path:
        """
        Generate talking head video using SadTalker.
        
        Args:
            audio_path: Path to audio file
            image_path: Path to source image
            output_path: Path to save output video
            **kwargs: Additional options (enhancer, preprocess, etc.)
        
        Returns:
            Path to generated video
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = [
            str(self.venv_python),
            str(self.sadtalker_path / "inference.py"),
            "--driven_audio", str(audio_path),
            "--source_image", str(image_path),
            "--result_dir", str(output_path.parent),
            "--enhancer", kwargs.get("enhancer", "gfpgan"),
            "--preprocess", kwargs.get("preprocess", "full"),
        ]
        
        if kwargs.get("still", False):
            cmd.append("--still")
        
        # Run SadTalker
        result = subprocess.run(
            cmd,
            cwd=str(self.sadtalker_path),
            capture_output=True,
            text=True,
            check=True
        )
        
        # Find output video (SadTalker creates timestamped directories)
        output_dir = output_path.parent
        video_files = list(output_dir.glob("*.mp4"))
        
        if not video_files:
            raise RuntimeError("SadTalker did not generate output video")
        
        # Copy to desired output path
        generated_video = video_files[-1]  # Get most recent
        shutil.copy2(generated_video, output_path)
        
        return output_path
```

### Update Avatar Generator

Add to `src/core/avatar_generator.py`:

```python
from src.core.sadtalker_provider import SadTalkerProvider

class AvatarProvider(ABC):
    # ... existing code ...

class SadTalkerProviderWrapper(AvatarProvider):
    """Wrapper for SadTalker local provider."""
    
    def __init__(self, config: Dict[str, Any], project_root: Path):
        self.provider = SadTalkerProvider(config, project_root)
        self.progress_callback = None
    
    def generate(self, audio_path: Path, **kwargs) -> Path:
        # Get image path from persona config
        image_path = kwargs.get("image_path")
        if not image_path:
            raise ValueError("SadTalker requires image_path")
        
        # Generate video
        output_path = kwargs.get("output_path")
        if not output_path:
            output_path = Path(tempfile.mkdtemp()) / "sadtalker_output.mp4"
        
        return self.provider.generate(
            audio_path=audio_path,
            image_path=image_path,
            output_path=output_path,
            **kwargs
        )
```

### Update Config

Add to `config/config.yaml`:

```yaml
avatar:
  engine: sadtalker  # or "heygen", "did", "sadtalker"
  
sadtalker:
  path: ~/SadTalker  # Path to SadTalker installation
  enhancer: gfpgan  # or "None"
  preprocess: full  # or "crop", "extract", "full", "resize"
  still: false  # Keep head still or allow movement
```

## Step 8: Test Integration

```python
# Test script
from pathlib import Path
from src.core.avatar_generator import AvatarProviderFactory
from src.utils.config_loader import load_config

config = load_config(Path("config/config.yaml"))
provider = AvatarProviderFactory.create("sadtalker", config, Path("."))

# Generate test video
audio_path = Path("test_audio.wav")
image_path = Path("test_image.jpg")
output_path = Path("output.mp4")

result = provider.generate(
    audio_path=audio_path,
    image_path=image_path,
    output_path=output_path
)

print(f"Generated: {result}")
```

## Performance Optimization

### For RTX 4090 (24GB VRAM):

1. **Batch Processing:**
   - Generate multiple videos in parallel
   - Use `ThreadPoolExecutor` for concurrent generation

2. **Memory Management:**
   - Process videos in batches
   - Clear GPU cache between generations

3. **Quality Settings:**
   - Use `enhancer: gfpgan` for best quality
   - Use `preprocess: full` for best results
   - Consider `still: true` for faster processing

## Troubleshooting

### CUDA Out of Memory
```bash
# Reduce batch size or process sequentially
# Check GPU memory: nvidia-smi
```

### Model Not Found
```bash
# Ensure checkpoints are downloaded
ls checkpoints/
# Should see: mapping_*.pth, gfpgan_*.pth, etc.
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Slow Performance
```bash
# Check CUDA is being used
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

## Next Steps

1. ✅ Complete SadTalker installation
2. ✅ Test with sample audio/image
3. ✅ Create integration wrapper
4. ✅ Add to avatar generator factory
5. ✅ Update UI to show "Local (SadTalker)" option
6. ✅ Benchmark vs HeyGen/D-ID
7. ✅ Add progress callbacks
8. ✅ Support parallel generation

## Resources

- **SadTalker GitHub:** https://github.com/OpenTalker/SadTalker
- **SadTalker Paper:** https://arxiv.org/abs/2211.12194
- **CUDA Installation:** https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
- **WSL2 GPU Support:** https://docs.nvidia.com/cuda/wsl-user-guide/index.html

