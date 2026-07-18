# Local GPU-Only Defaults Policy

## ⚠️ CRITICAL: Default Provider Policy

**ONLY local GPU-based providers are used as defaults.**

Cloud-based providers (HeyGen, D-ID, ElevenLabs, Azure) are **NOT** defaults and should only be used as alternatives when explicitly selected.

## Default Providers

### Avatar Generation
- **Default:** `dreamtalk` (local GPU)
- **Alternatives:** `heygen`, `did` (cloud APIs - NOT defaults)

### Text-to-Speech
- **Default:** `xtts` (local GPU - Coqui XTTS-v2)
- **Alternatives:** `bark`, `valle` (local GPU)
- **External (NOT defaults):** `elevenlabs`, `azure` (cloud APIs)

## Configuration

In `config/config.yaml`:

```yaml
avatar:
  engine: dreamtalk  # Local GPU - default
  # Cloud alternatives: heygen, did

tts:
  engine: xtts  # Local GPU - default
  # Local alternatives: bark, valle
  # External (NOT default): elevenlabs, azure
```

## Why This Policy?

1. **No API costs** - Local providers don't charge per request
2. **No rate limits** - Process as many videos as needed
3. **Privacy** - Audio/video stays on your machine
4. **GPU utilization** - Makes use of local hardware
5. **Consistency** - Predictable performance and quality

## Current Limitations

### DreamTalk (Avatar)
- ✅ Local GPU-based
- ❌ Requires checkpoints (must request via email)
- ⚠️ Currently unavailable until checkpoints obtained

**When DreamTalk is unavailable:**
- System will error if DreamTalk is selected but checkpoints missing
- User must explicitly select a cloud provider if needed
- **Do NOT automatically fall back to cloud providers**

### XTTS-v2 (TTS)
- ✅ Local GPU-based
- ✅ Available and working
- ✅ Default TTS provider

## Implementation Notes

- **Never** set cloud providers as defaults in code
- **Always** check for local provider availability first
- **Error** if local provider unavailable rather than silently falling back to cloud
- **Document** when local providers require additional setup (like DreamTalk checkpoints)

## Memorization

**CRITICAL RULE:** 
- Defaults = Local GPU providers ONLY
- Cloud providers = Alternatives/explicit selection ONLY
- Never auto-fallback to cloud providers

