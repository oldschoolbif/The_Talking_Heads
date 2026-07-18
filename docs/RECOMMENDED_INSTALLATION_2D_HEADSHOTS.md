# Recommended Installation for 2D Headshot Animation

**Date:** November 2025  
**Use Case:** Animate 2D headshot images on background stage image

---

## Summary

**Your Requirements:**
- ✅ 2D headshot images (photos of personas)
- ✅ Animate headshots with audio
- ✅ Background image (stage photo)
- ✅ Composite animated headshots on background

**Audio2Face is NOT the right tool** - it's for 3D character animation, not 2D images.

**Use SadTalker or LivePortrait instead** - designed specifically for 2D headshot animation.

---

## Recommended Tool: SadTalker ⭐

### Why SadTalker?

- ✅ **Designed for 2D images** - Works with photos directly
- ✅ **Simple installation** - Python package, no SDK building
- ✅ **Full animation** - Head movements, expressions, lip sync
- ✅ **Perfect workflow** - Image + Audio → Video
- ✅ **Easy integration** - Can be wrapped in provider class

### Installation Steps

```bash
# 1. Navigate to project
cd d:\dev\The_Talking_Heads

# 2. Clone SadTalker
cd ..
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker

# 3. Create virtual environment (if needed)
python -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux

# 4. Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

# 5. Download models (will download automatically on first use)
# Or download manually from: https://github.com/OpenTalker/SadTalker#checkpoints

# 6. Test installation
python inference.py \
    --driven_audio path/to/audio.wav \
    --source_image path/to/headshot.jpg \
    --result_dir ./output
```

### Integration into Your Project

**Create SadTalker Provider:**

```python
# src/core/sadtalker_provider.py
class SadTalkerProvider(AvatarProvider):
    def __init__(self, config):
        self.sadtalker_path = Path(config.get("sadtalker_path", "../SadTalker"))
        # ... initialization
    
    def generate(self, audio_path, avatar_id, **kwargs):
        # avatar_id is path to headshot image
        # Generate animated video from image + audio
        # Return video path and duration
        pass
```

**Update config.yaml:**

```yaml
sadtalker:
  sadtalker_path: ../SadTalker  # Path to SadTalker installation
  checkpoint_path: null  # Auto-detect
  output_dir: .cache/sadtalker_outputs
  # Settings
  still: true  # Use still mode (better for headshots)
  preprocess: crop  # Crop face from image
  expression_scale: 1.0  # Expression strength
  input_yaw: null  # Auto-detect head pose
  input_pitch: null  # Auto-detect head pose
  input_roll: null  # Auto-detect head pose
  ref_eyeblink: null  # Reference video for eye blinking
  ref_pose: null  # Reference video for head pose
  checkpoint_dir: null  # Auto-detect
  result_dir: .cache/sadtalker_outputs

avatar:
  engine: sadtalker  # Use SadTalker for 2D headshots
```

---

## Alternative: LivePortrait (Higher Quality)

### Why LivePortrait?

- ✅ **Better quality** than SadTalker
- ✅ **Same simplicity** - 2D image input
- ✅ **Latest technology** (2024)
- ⚠️ **Newer project** - Less community support

### Installation Steps

```bash
# 1. Clone LivePortrait
git clone https://github.com/KwaiVGI/LivePortrait.git
cd LivePortrait

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download models
# Follow instructions in README

# 4. Test
python app.py  # Or use API
```

---

## Your Workflow

### Step-by-Step Process:

```
1. Prepare Assets:
   - Headshot images (one per persona): alice.jpg, bob.jpg, charlie.jpg
   - Background image: stage_background.jpg

2. Generate Audio:
   - TTS generates audio per persona: alice_audio.wav, bob_audio.wav, etc.

3. Animate Headshots:
   - SadTalker processes each headshot:
     * alice.jpg + alice_audio.wav → alice_animated.mp4
     * bob.jpg + bob_audio.wav → bob_animated.mp4
     * charlie.jpg + charlie_audio.wav → charlie_animated.mp4

4. Composite Video:
   - Video Composer combines:
     * Background: stage_background.jpg
     * Avatars: [alice_animated.mp4, bob_animated.mp4, charlie_animated.mp4]
     * Layout: Side-by-side, grid, or switching
   * Output: final_podcast.mp4
```

---

## Comparison: Audio2Face vs SadTalker

| Aspect | Audio2Face | SadTalker |
|--------|-----------|-----------|
| **Input** | 3D USD models | 2D images ✅ |
| **Setup Time** | 3-5 hours | 30 minutes ✅ |
| **Complexity** | High (SDK build) | Low (Python install) ✅ |
| **Your Use Case** | ❌ Wrong tool | ✅ Perfect fit |
| **Background** | 3D scene | 2D image ✅ |
| **Integration** | Complex | Simple ✅ |

---

## Updated Installation Plan

### Skip Audio2Face - Use SadTalker Instead

**Reasons:**
1. ✅ **Right tool for the job** - Designed for 2D images
2. ✅ **Simpler setup** - No SDK building required
3. ✅ **Faster to integrate** - Python API, easy to wrap
4. ✅ **Perfect workflow** - Image + Audio → Video
5. ✅ **Better fit** - Matches your requirements exactly

**Installation Time:**
- Audio2Face SDK: 3-5 hours
- SadTalker: 30 minutes

**Integration Time:**
- Audio2Face: 4-8 hours (complex SDK integration)
- SadTalker: 2-4 hours (simple Python wrapper)

---

## Next Steps

1. **Install SadTalker** (30 minutes)
2. **Test with sample headshot** (10 minutes)
3. **Create SadTalkerProvider** (2-4 hours)
4. **Update config** (10 minutes)
5. **Test multi-persona workflow** (1 hour)
6. **Integrate with video composer** (existing code)

**Total Time:** ~4-6 hours vs 8-13 hours for Audio2Face

**Result:** Working 2D headshot animation pipeline ✅

---

## Questions?

**Q: Can I still use Audio2Face later?**  
A: Yes, but you'd need to convert 2D headshots to 3D models first, which adds complexity.

**Q: Is SadTalker quality good enough?**  
A: Yes, for podcast use cases. LivePortrait is higher quality if needed.

**Q: Can I use both?**  
A: Yes, you can have multiple providers and choose per persona.

**Q: What about background images?**  
A: Your existing video composer handles this - just composite animated headshots on background image.

---

## Conclusion

**For 2D headshot animation:**
- ✅ **Use SadTalker** (or LivePortrait)
- ❌ **Skip Audio2Face** (wrong tool for 2D images)

**Much simpler, faster, and perfect for your use case!**

