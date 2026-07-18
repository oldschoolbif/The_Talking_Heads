# UX Principles for The Talking Heads

## Core Principle: Progress Indicators

**ALWAYS create progress indicators when the user has ZERO clue what is happening inside of the process.**

### When to Add Progress Indicators

1. **API Calls** - Any external API request that may take > 1 second
2. **File Operations** - Large file reads/writes, downloads, uploads
3. **Processing** - Audio/video processing, encoding, mixing
4. **Polling** - Waiting for async operations to complete
5. **Any operation > 3 seconds** - If it takes longer than 3 seconds, show progress

### Progress Indicator Requirements

1. **Message**: Clear description of what's happening
2. **Progress Value**: Percentage (0.0-1.0) or step count (X/Y)
3. **Frequency**: Update at least every 5-10 seconds during long operations
4. **Visibility**: Must be visible in console output, not just internal callbacks

### Implementation Pattern

```python
# Always use the progress callback if available
if self.progress_callback:
    self.progress_callback("Clear message about what's happening", progress_value)
else:
    # Fallback to print if no callback
    print(f"[INFO] Clear message about what's happening ({progress_value*100:.0f}%)")
```

### Areas That Must Have Progress Indicators

- ✅ TTS generation (API calls can be slow)
- ✅ Avatar generation (API calls + polling + downloads)
- ✅ Audio mixing (file processing)
- ✅ Video composition (FFmpeg operations)
- ✅ File downloads (show MB downloaded)
- ✅ Polling operations (show elapsed time)

### User Experience Goal

**Never leave the user wondering "Is it still working?"**

