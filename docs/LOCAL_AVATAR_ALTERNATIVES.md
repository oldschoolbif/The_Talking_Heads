# Local Talking Head Generation Alternatives

## Overview

This document compares open-source alternatives to HeyGen and D-ID that can run **locally on your GPU**, providing:
- ✅ No API costs
- ✅ No content restrictions/censorship
- ✅ Full control over data
- ✅ Faster processing (no network latency)
- ✅ Works offline

## Top Recommendations

### 1. **SadTalker** ⭐ **RECOMMENDED**

**Best for:** High-quality talking head generation with good lip-sync

**Features:**
- Generates realistic talking head videos from a single image + audio
- Excellent lip-sync quality
- Supports head pose and expression control
- Active development and community

**GPU Requirements:**
- Minimum: 6GB VRAM (RTX 3060 or better)
- Recommended: 8GB+ VRAM (RTX 3070/4070 or better)
- Your RTX 4090: ✅ Perfect (24GB VRAM)

**Speed:**
- ~30-60 seconds per minute of video on RTX 4090
- Much faster than HeyGen/D-ID API calls

**Setup Complexity:** Medium
- Requires PyTorch, CUDA, and model downloads (~2-3GB)
- Well-documented installation process

**GitHub:** https://github.com/OpenTalker/SadTalker

**Pros:**
- ✅ Best quality-to-speed ratio
- ✅ Active community support
- ✅ Good documentation
- ✅ Supports batch processing
- ✅ Can generate multiple videos in parallel

**Cons:**
- ⚠️ Requires CUDA setup
- ⚠️ Model download needed (~2-3GB)

---

### 2. **DreamTalk** ⭐ **HIGH QUALITY**

**Best for:** State-of-the-art quality with natural expressions

**Features:**
- Recent (2024) high-quality model
- Excellent expression and head movement
- Better than SadTalker for natural motion
- Supports emotion control

**GPU Requirements:**
- Minimum: 8GB VRAM
- Recommended: 12GB+ VRAM
- Your RTX 4090: ✅ Excellent

**Speed:**
- ~60-90 seconds per minute of video
- Slower than SadTalker but higher quality

**Setup Complexity:** Medium-High
- More complex setup than SadTalker
- Requires careful CUDA configuration

**GitHub:** https://github.com/ali-vilab/dreamtalk

**Pros:**
- ✅ Highest quality output
- ✅ Natural expressions and movements
- ✅ Emotion control
- ✅ Recent model (2024)

**Cons:**
- ⚠️ Slower than SadTalker
- ⚠️ More complex setup
- ⚠️ Larger model size

---

### 3. **Wav2Lip** ⭐ **CLASSIC & RELIABLE**

**Best for:** Simple lip-sync when you already have a video

**Features:**
- Classic lip-sync solution
- Very fast processing
- Lower GPU requirements
- Good for batch processing

**GPU Requirements:**
- Minimum: 4GB VRAM
- Recommended: 6GB+ VRAM
- Your RTX 4090: ✅ Overkill (but fast!)

**Speed:**
- ~10-20 seconds per minute of video
- Fastest option

**Setup Complexity:** Low-Medium
- Simpler than SadTalker
- Well-established codebase

**GitHub:** https://github.com/Rudrabha/Wav2Lip

**Pros:**
- ✅ Very fast
- ✅ Simple to use
- ✅ Low GPU requirements
- ✅ Reliable results

**Cons:**
- ⚠️ Only does lip-sync (not full head generation)
- ⚠️ Requires existing video/image
- ⚠️ Less natural than SadTalker/DreamTalk

---

### 4. **HeyGem** ⭐ **HEYGEN ALTERNATIVE**

**Best for:** Direct HeyGen replacement, Windows-friendly

**Features:**
- Specifically designed as HeyGen alternative
- Fully offline operation
- Windows + WSL2 support
- Docker-based deployment

**GPU Requirements:**
- Minimum: RTX 4070 (12GB VRAM)
- Recommended: RTX 4080/4090
- Your RTX 4090: ✅ Perfect

**Speed:**
- Similar to HeyGen API speeds
- ~1-2 minutes per video

**Setup Complexity:** Medium
- Docker-based (easier for Windows)
- ~70GB download for models
- ~30 minutes initial setup

**GitHub:** https://github.com/brandon-rezko/HeyGem

**Pros:**
- ✅ Designed as HeyGen replacement
- ✅ Docker-based (Windows-friendly)
- ✅ Fully offline
- ✅ Good documentation

**Cons:**
- ⚠️ Large download (~70GB)
- ⚠️ Docker overhead
- ⚠️ Less flexible than SadTalker

---

### 5. **Video-Retalking**

**Best for:** Retalking existing videos with new audio

**Features:**
- Retalk videos with new audio
- Good for editing existing content
- Supports expression control

**GPU Requirements:**
- Minimum: 6GB VRAM
- Recommended: 8GB+ VRAM
- Your RTX 4090: ✅ Great

**Speed:**
- ~30-60 seconds per minute

**Setup Complexity:** Medium

**GitHub:** https://github.com/OpenTalker/video-retalking

**Pros:**
- ✅ Good for video editing
- ✅ Expression control
- ✅ Active development

**Cons:**
- ⚠️ Requires existing video
- ⚠️ Less popular than SadTalker

---

## Comparison Table

| Solution | Quality | Speed | GPU Req | Setup | Best For |
|----------|---------|-------|---------|-------|----------|
| **SadTalker** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 6GB+ | Medium | **General use** |
| **DreamTalk** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 8GB+ | Medium-High | **Highest quality** |
| **Wav2Lip** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4GB+ | Low | **Fast lip-sync** |
| **HeyGem** | ⭐⭐⭐⭐ | ⭐⭐⭐ | 12GB+ | Medium | **HeyGen replacement** |
| **Video-Retalking** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 6GB+ | Medium | **Video editing** |

## Recommendation for Your Setup

**Given your RTX 4090 (24GB VRAM) and Windows 11 + WSL2:**

### Primary Choice: **SadTalker**
- ✅ Best balance of quality and speed
- ✅ Well-documented and maintained
- ✅ Your GPU can handle multiple parallel generations
- ✅ Easy to integrate into existing pipeline

### Secondary Choice: **DreamTalk**
- ✅ If you need highest quality
- ✅ Better for natural expressions
- ✅ Worth the extra setup time for premium results

### Quick Start: **Wav2Lip**
- ✅ Fastest to set up and test
- ✅ Good for prototyping
- ✅ Can use alongside SadTalker for different use cases

## Integration Strategy

### Option 1: Replace HeyGen/D-ID Entirely
- Use SadTalker as primary avatar generator
- Integrate into `src/core/avatar_generator.py`
- Add `SadTalkerProvider` class

### Option 2: Hybrid Approach
- Keep HeyGen/D-ID for quick tests
- Use SadTalker for production/local generation
- Switch via config: `avatar.engine: "sadtalker"`

### Option 3: Multi-Provider
- Support all providers (HeyGen, D-ID, SadTalker, DreamTalk)
- Let user choose per persona or globally
- Fallback chain: Local → Cloud APIs

## Next Steps

1. **Test SadTalker locally:**
   ```bash
   # In WSL2
   git clone https://github.com/OpenTalker/SadTalker.git
   cd SadTalker
   # Follow installation instructions
   ```

2. **Create integration wrapper:**
   - Add `SadTalkerProvider` to `src/core/avatar_generator.py`
   - Match existing `HeyGenProvider` interface
   - Add to config system

3. **Benchmark performance:**
   - Compare quality vs HeyGen/D-ID
   - Measure generation speed
   - Test parallel generation

4. **Update UI:**
   - Add "Local (SadTalker)" option to avatar engine dropdown
   - Show GPU status/memory usage
   - Add progress indicators

## Resources

- **SadTalker:** https://github.com/OpenTalker/SadTalker
- **DreamTalk:** https://github.com/ali-vilab/dreamtalk
- **Wav2Lip:** https://github.com/Rudrabha/Wav2Lip
- **HeyGem:** https://github.com/brandon-rezko/HeyGem
- **Video-Retalking:** https://github.com/OpenTalker/video-retalking

## Notes

- All solutions require CUDA and PyTorch
- WSL2 GPU passthrough works well with NVIDIA drivers
- Consider Docker for easier dependency management
- Your RTX 4090 can handle multiple parallel generations
- Local generation is typically faster than API calls (no network latency)

