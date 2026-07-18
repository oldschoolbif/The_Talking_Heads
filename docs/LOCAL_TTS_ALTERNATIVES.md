# Local GPU-Based TTS Alternatives

## Overview

This document compares open-source Text-to-Speech (TTS) solutions that can run **locally on your GPU**, providing:
- ✅ No API costs
- ✅ No content restrictions
- ✅ Full control over data
- ✅ Works offline
- ✅ Fast processing (GPU acceleration)
- ✅ Voice cloning capabilities

## Top Recommendations

### 1. **Coqui TTS (XTTS-v2)** ⭐ **RECOMMENDED**

**Best for:** High-quality TTS with voice cloning capabilities

**Features:**
- State-of-the-art voice cloning (clone voices from short samples)
- Multi-language support (17+ languages)
- Natural prosody and emotion
- Fast GPU inference
- Active development and community

**GPU Requirements:**
- Minimum: 6GB VRAM (RTX 3060 or better)
- Recommended: 8GB+ VRAM (RTX 3070/4070 or better)
- Your RTX 4090: ✅ Perfect (24GB VRAM)

**Speed:**
- ~1-3 seconds per sentence on RTX 4090
- Real-time factor: ~0.1-0.3x (faster than real-time)

**Setup Complexity:** Medium
- Requires PyTorch, CUDA, and model downloads (~2-3GB)
- Well-documented installation process

**GitHub:** https://github.com/coqui-ai/TTS

**Voice Cloning:**
- Clone voices from 3-10 second audio samples
- High-quality results
- Supports emotional control

**Pros:**
- ✅ Best quality-to-speed ratio
- ✅ Voice cloning from short samples
- ✅ Multi-language support
- ✅ Active community
- ✅ Good documentation
- ✅ Supports batch processing

**Cons:**
- ⚠️ Requires CUDA setup
- ⚠️ Model download needed (~2-3GB)
- ⚠️ Voice cloning requires reference audio

---

### 2. **XTTS-v3** ⭐ **LATEST & BEST QUALITY**

**Best for:** Highest quality voice cloning and TTS

**Features:**
- Latest model from Coqui (2024)
- Improved voice cloning quality
- Better multilingual support
- Enhanced prosody and emotion
- Faster inference than XTTS-v2

**GPU Requirements:**
- Minimum: 8GB VRAM
- Recommended: 12GB+ VRAM
- Your RTX 4090: ✅ Excellent

**Speed:**
- ~0.5-2 seconds per sentence
- Real-time factor: ~0.05-0.2x (very fast)

**Setup Complexity:** Medium-High
- Similar to XTTS-v2 but newer
- May require more recent PyTorch/CUDA versions

**GitHub:** https://github.com/coqui-ai/TTS (check for XTTS-v3)

**Pros:**
- ✅ Highest quality output
- ✅ Best voice cloning
- ✅ Latest technology
- ✅ Improved multilingual support

**Cons:**
- ⚠️ Newer (less tested)
- ⚠️ May require more setup
- ⚠️ Larger model size

---

### 3. **Piper TTS** ⭐ **FAST & SIMPLE**

**Best for:** Fast, lightweight TTS without voice cloning

**Features:**
- Very fast inference
- Low GPU requirements
- Multiple voice options
- Good quality for non-cloned voices
- Simple setup

**GPU Requirements:**
- Minimum: 2GB VRAM
- Recommended: 4GB+ VRAM
- Your RTX 4090: ✅ Overkill (but very fast!)

**Speed:**
- ~0.1-0.5 seconds per sentence
- Real-time factor: ~0.01-0.1x (extremely fast)

**Setup Complexity:** Low-Medium
- Simpler than Coqui TTS
- Smaller model downloads

**GitHub:** https://github.com/rhasspy/piper

**Pros:**
- ✅ Very fast
- ✅ Low GPU requirements
- ✅ Simple to use
- ✅ Good quality (for non-cloned voices)
- ✅ Multiple pre-trained voices

**Cons:**
- ⚠️ No voice cloning
- ⚠️ Limited to pre-trained voices
- ⚠️ Less natural than XTTS

---

### 4. **Bark (Suno AI)** ⭐ **EXPRESSIVE & CREATIVE**

**Best for:** Expressive TTS with music and sound effects

**Features:**
- Very expressive and natural
- Can generate music, sound effects, and non-speech sounds
- Good for creative content
- Voice cloning support (experimental)

**GPU Requirements:**
- Minimum: 8GB VRAM
- Recommended: 12GB+ VRAM
- Your RTX 4090: ✅ Great

**Speed:**
- ~5-15 seconds per sentence
- Slower than other options

**Setup Complexity:** Medium

**GitHub:** https://github.com/suno-ai/bark

**Pros:**
- ✅ Most expressive output
- ✅ Can generate music/sounds
- ✅ Very natural prosody
- ✅ Creative capabilities

**Cons:**
- ⚠️ Slower than other options
- ⚠️ Higher GPU requirements
- ⚠️ May be overkill for simple TTS

---

### 5. **AllTalk TTS** ⭐ **USER-FRIENDLY**

**Best for:** Easy setup with web UI and voice cloning

**Features:**
- User-friendly web interface
- Voice cloning from short samples
- Multiple TTS engine support
- API endpoints for integration
- Complete data privacy

**GPU Requirements:**
- Minimum: 4GB VRAM
- Recommended: 8GB+ VRAM
- Your RTX 4090: ✅ Excellent

**Speed:**
- ~1-3 seconds per sentence

**Setup Complexity:** Low-Medium
- Web UI makes it easy to use
- Good documentation

**GitHub:** https://github.com/erew123/alltalk_tts

**Pros:**
- ✅ Web UI for easy use
- ✅ Voice cloning support
- ✅ Multiple engine options
- ✅ API for integration
- ✅ Good documentation

**Cons:**
- ⚠️ May be slower than pure Coqui
- ⚠️ Web UI overhead

---

### 6. **RealtimeTTS** ⭐ **REAL-TIME**

**Best for:** Real-time TTS with multiple engine support

**Features:**
- Real-time speech synthesis
- Supports multiple TTS engines (Coqui, Piper, etc.)
- Low latency
- Good for interactive applications

**GPU Requirements:**
- Minimum: 4GB VRAM
- Recommended: 8GB+ VRAM
- Your RTX 4090: ✅ Great

**Speed:**
- Real-time or faster
- Low latency

**Setup Complexity:** Medium

**GitHub:** https://github.com/KoljaB/RealtimeTTS

**Pros:**
- ✅ Real-time synthesis
- ✅ Low latency
- ✅ Multiple engine support
- ✅ Good for interactive apps

**Cons:**
- ⚠️ May sacrifice quality for speed
- ⚠️ More complex setup

---

### 7. **VALL-E X** ⭐ **RESEARCH-GRADE**

**Best for:** Research and highest quality (if available)

**Features:**
- Microsoft's VALL-E model
- High-quality voice cloning
- Zero-shot voice cloning
- Research-grade quality

**GPU Requirements:**
- Minimum: 12GB VRAM
- Recommended: 16GB+ VRAM
- Your RTX 4090: ✅ Perfect

**Speed:**
- ~2-5 seconds per sentence

**Setup Complexity:** High
- May require more setup
- Check availability (may be research-only)

**GitHub:** Various implementations (check availability)

**Pros:**
- ✅ Research-grade quality
- ✅ Zero-shot cloning
- ✅ Microsoft technology

**Cons:**
- ⚠️ May not be publicly available
- ⚠️ Complex setup
- ⚠️ Higher requirements

---

## Comparison Table

| Solution | Quality | Speed | GPU Req | Voice Cloning | Setup | Best For |
|----------|---------|-------|---------|---------------|-------|----------|
| **Coqui XTTS-v2** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 6GB+ | ✅ Yes | Medium | **General use** |
| **XTTS-v3** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 8GB+ | ✅ Yes | Medium-High | **Best quality** |
| **Piper TTS** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 2GB+ | ❌ No | Low | **Fast & simple** |
| **Bark** | ⭐⭐⭐⭐⭐ | ⭐⭐ | 8GB+ | ⚠️ Experimental | Medium | **Expressive** |
| **AllTalk TTS** | ⭐⭐⭐⭐ | ⭐⭐⭐ | 4GB+ | ✅ Yes | Low-Medium | **Easy setup** |
| **RealtimeTTS** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 4GB+ | ⚠️ Depends | Medium | **Real-time** |
| **VALL-E X** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 12GB+ | ✅ Yes | High | **Research** |

## Recommendation for Your Setup

**Given your RTX 4090 (24GB VRAM) and Windows 11 + WSL2:**

### Primary Choice: **Coqui TTS (XTTS-v2 or v3)**
- ✅ Best balance of quality and speed
- ✅ Voice cloning from short samples
- ✅ Well-documented and maintained
- ✅ Your GPU can handle multiple parallel generations
- ✅ Easy to integrate into existing pipeline

### Secondary Choice: **XTTS-v3**
- ✅ If you want the absolute best quality
- ✅ Latest improvements
- ✅ Worth the extra setup time

### Quick Start: **Piper TTS**
- ✅ Fastest to set up and test
- ✅ Good for prototyping
- ✅ Can use alongside Coqui for different use cases

## Integration Strategy

### Option 1: Replace ElevenLabs Entirely
- Use Coqui TTS as primary TTS provider
- Integrate into `src/core/tts_engine.py`
- Add `CoquiTTSProvider` class

### Option 2: Hybrid Approach
- Keep ElevenLabs for quick tests
- Use Coqui TTS for production/local generation
- Switch via config: `tts.engine: "coqui"`

### Option 3: Multi-Provider
- Support all providers (ElevenLabs, Azure, Coqui, Piper)
- Let user choose per persona or globally
- No fallback (errors if unavailable)

## Voice Cloning Workflow

### With Coqui XTTS:

1. **Prepare Reference Audio:**
   - 3-10 seconds of clean speech
   - Single speaker
   - Good quality (no background noise)

2. **Clone Voice:**
   ```python
   from TTS.api import TTS
   
   tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
   tts.tts_to_file(
       text="Hello, this is a test",
       speaker_wav="reference_audio.wav",
       language="en",
       file_path="output.wav"
   )
   ```

3. **Use Cloned Voice:**
   - Save reference audio per persona
   - Use same reference for all persona segments
   - Maintains consistent voice

## Performance Optimization

### For RTX 4090 (24GB VRAM):

1. **Batch Processing:**
   - Generate multiple audio segments in parallel
   - Use batch inference for faster processing

2. **Model Optimization:**
   - Use quantized models for faster inference
   - Use half-precision (FP16) for speed

3. **Caching:**
   - Cache generated audio by text + voice
   - Reuse cached audio for repeated text

## Cost Comparison

### Current Setup (ElevenLabs):
- **Cost:** ~$0.18 per 1000 characters
- **Example:** 5-minute podcast (~2500 chars) = ~$0.45

### Local TTS (Coqui XTTS):
- **Cost:** $0 (one-time GPU electricity)
- **Example:** Unlimited generations
- **Break-even:** After ~2-3 videos

## Next Steps

1. **Test Coqui TTS locally:**
   ```bash
   # In WSL2
   pip install TTS
   python -c "from TTS.api import TTS; tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2'); print('Ready!')"
   ```

2. **Create integration wrapper:**
   - Add `CoquiTTSProvider` to `src/core/tts_engine.py`
   - Match existing `ElevenLabsProvider` interface
   - Add to config system

3. **Benchmark performance:**
   - Compare quality vs ElevenLabs
   - Measure generation speed
   - Test voice cloning

4. **Update UI:**
   - Add "Local (Coqui TTS)" option to TTS engine dropdown
   - Show GPU status/memory usage
   - Add voice cloning interface

## Resources

- **Coqui TTS:** https://github.com/coqui-ai/TTS
- **Coqui Docs:** https://tts.readthedocs.io/
- **XTTS-v2 Model:** https://huggingface.co/coqui/XTTS-v2
- **Piper TTS:** https://github.com/rhasspy/piper
- **Bark:** https://github.com/suno-ai/bark
- **AllTalk TTS:** https://github.com/erew123/alltalk_tts
- **RealtimeTTS:** https://github.com/KoljaB/RealtimeTTS
- **CUDA Installation:** https://docs.nvidia.com/cuda/cuda-installation-guide-linux/
- **WSL2 GPU Support:** https://docs.nvidia.com/cuda/wsl-user-guide/index.html

## Notes

- All solutions require CUDA and PyTorch
- WSL2 GPU passthrough works well with NVIDIA drivers
- Your RTX 4090 can handle multiple parallel generations
- Local TTS is typically faster than API calls (no network latency)
- Voice cloning requires reference audio samples
- Consider keeping ElevenLabs as option for high-quality pre-trained voices

## Voice Cloning Considerations

### Advantages:
- ✅ Clone any voice from short sample
- ✅ Consistent voice across all generations
- ✅ No per-voice API costs
- ✅ Full control over voice characteristics

### Requirements:
- ⚠️ Need reference audio for each persona
- ⚠️ Quality depends on reference audio quality
- ⚠️ May need fine-tuning for best results
- ⚠️ Storage for reference audio files

### Workflow:
1. Record or obtain 3-10 second audio sample per persona
2. Store in `examples/personas/voices/` directory
3. Reference in persona config
4. Use for all TTS generations for that persona

