# Bug Report: KeyError 'streams' in av_utils_ffmpeg.get_audio_duration

## Description

HeyGem's compiled FFmpeg wrapper (`av_utils_ffmpeg.so`) fails with `KeyError: 'streams'` when attempting to get audio duration, even though the audio files are correctly formatted and FFprobe can read them successfully.

**Error Message:**
```
KeyError: 'streams'
Exception: 三次获取音频时长失败
```

## Environment

- **OS:** Windows 10 (via Docker Desktop)
- **HeyGem Version:** Latest (from docker-compose)
- **Docker Container:** `heygem-gen-video`
- **Audio Format:** PCM 16-bit WAV, 22050 Hz, mono

## Steps to Reproduce

1. Submit a video generation task via API with a valid audio file
2. Audio file is correctly converted to PCM 16-bit WAV format
3. HeyGem attempts to get audio duration using `av_utils_ffmpeg.get_audio_duration()`
4. Error occurs: `KeyError: 'streams'`

## Expected Behavior

HeyGem should successfully read the audio duration from valid WAV files.

## Actual Behavior

HeyGem's FFmpeg wrapper fails to parse FFprobe output, even though:
- Audio files are correctly formatted (16-bit PCM WAV)
- FFprobe can read the files successfully when called directly
- FFprobe JSON output contains the `streams` key

## Error Logs

```
Traceback (most recent call last):
  File "av_utils_ffmpeg.py", line 59, in av_utils_ffmpeg.get_audio_duration
KeyError: 'streams'
Traceback (most recent call last):
  File "av_utils_ffmpeg.py", line 59, in av_utils_ffmpeg.get_audio_duration
KeyError: 'streams'
Traceback (most recent call last):
  File "av_utils_ffmpeg.py", line 59, in av_utils_ffmpeg.get_audio_duration
KeyError: 'streams'
Traceback (most recent call last):
  File "trans_dh_service.py", line 398, in trans_dh_service.TransDhTask.work
  File "av_utils_ffmpeg.py", line 66, in av_utils_ffmpeg.get_audio_duration
Exception: 三次获取音频时长失败
2025-11-23 12:46:20,646-[service.self_logger]-threading.py[line:870]-ERROR: 672f2757-7747-47ed-a5df-096cc63da562 -> 任务执行失败，异常信息:[三次获取音频时长失败]
```

## FFprobe Verification

When calling FFprobe directly on the same audio file, it works correctly:

```bash
docker exec heygem-gen-video ffprobe -v error -show_format -show_streams -of json /code/data/temp/audio_file.wav
```

**Output (successful):**
```json
{
    "streams": [
        {
            "index": 0,
            "codec_name": "pcm_s16le",
            "codec_long_name": "PCM signed 16-bit little-endian",
            "codec_type": "audio",
            "sample_rate": "22050",
            "channels": 1,
            "bits_per_sample": 16,
            "duration": "9.733333"
        }
    ],
    "format": {
        "format_name": "wav",
        "format_long_name": "WAV / WAVE (Waveform Audio)",
        "duration": "9.733333",
        "size": "429284",
        "bit_rate": "352836"
    }
}
```

The JSON output clearly contains the `streams` key, but HeyGem's wrapper fails to access it.

## Audio File Details

- **Format:** WAV (PCM)
- **Codec:** pcm_s16le (16-bit PCM little-endian)
- **Sample Rate:** 22050 Hz
- **Channels:** 1 (mono)
- **Bits per Sample:** 16
- **Duration:** ~9.7 seconds
- **File Size:** ~429 KB

## Investigation

The issue appears to be in HeyGem's compiled Python module (`av_utils_ffmpeg.cpython-38-x86_64-linux-gnu.so`). The module uses this FFprobe command:

```
ffprobe -v quiet -print_format json -show_format -show_streams %s
```

When this command is executed manually, it returns valid JSON with a `streams` key. However, the compiled wrapper fails to parse it correctly.

## Workaround Attempts

1. ✅ Verified audio files are correct format (16-bit PCM WAV)
2. ✅ Confirmed FFprobe works when called directly
3. ✅ Verified JSON output contains `streams` key
4. ✅ Tried different audio file naming conventions
5. ✅ Added file sync delays to ensure files are fully written
6. ❌ Issue persists - appears to be a bug in the compiled wrapper

## Additional Context

This issue prevents video generation via the API when using external audio files. The audio files are correctly formatted and accessible, but HeyGem's internal FFmpeg wrapper cannot process them.

## Related Files

- Error logs: `heygem_error_log.txt`
- FFprobe verification: `ffprobe_verification.json`

