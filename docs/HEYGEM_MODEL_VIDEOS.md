# HeyGem Model Videos Setup Guide

HeyGem requires video model files (videos of people speaking) to generate avatars. This guide explains how to get and set up model videos.

## Requirements

- **Video Duration**: ~10 seconds minimum (up to 10 minutes recommended)
- **Content**: Person speaking, face clearly visible
- **Quality**: Good lighting, clear audio, stable camera
- **Format**: MP4, AVI, or other common video formats

## Option 1: Record Your Own Videos (Recommended)

1. **Record a video** of yourself or someone else speaking
2. **Ensure good quality**:
   - Face is clearly visible
   - Good lighting
   - Person is speaking (for lip-sync training)
   - Stable camera (no shaking)
3. **Save the video** to: `D:\heygem_data\face2face\`

## Option 2: Use Free Stock Videos

### Free Stock Video Sites:
- **Pexels Videos**: https://www.pexels.com/videos/
  - Search for "person speaking", "talking head", "interview"
  - Free to use, no attribution required
- **Pixabay Videos**: https://pixabay.com/videos/
  - Similar search terms
  - Free for commercial use
- **Videvo**: https://www.videvo.net/
  - Free stock videos with various licenses

### Steps:
1. Search for videos of people speaking
2. Download a video (preferably 10-30 seconds)
3. Save it to: `D:\heygem_data\face2face\`
4. Rename it to something like `alice.mp4` or `bob.mp4`

## Option 3: Use HeyGem Client Application

HeyGem provides a desktop client that can help you:
1. Download the client from: https://github.com/GuijiAI/HeyGem.ai/releases
2. Install and run `HeyGem-x.x.x-setup.exe`
3. Use the client to create and manage model videos
4. The client will handle video processing and storage

## Setting Up Model Videos

1. **Place videos in the data directory**:
   ```
   D:\heygem_data\face2face\
   ├── alice.mp4
   ├── bob.mp4
   └── charlie.mp4
   ```

2. **Update personas.yaml**:
   ```yaml
   personas:
     alice:
       avatar:
         engine: "heygem"
         avatar_id: "alice.mp4"  # Must match filename in face2face directory
   ```

3. **Verify the path**:
   - Videos should be directly in `D:\heygem_data\face2face\`
   - Or use relative paths from that directory

## Testing

After adding model videos, run the test:
```bash
python scripts/test_bark_heygem.py
```

## Troubleshooting

**Error: "Avatar video model not found"**
- Check that the video file exists in `D:\heygem_data\face2face\`
- Verify the filename matches `avatar_id` in `personas.yaml`
- Ensure the file is a valid video format (MP4, AVI, etc.)

**Video quality issues**
- Use videos with clear facial features
- Ensure good lighting in the source video
- Avoid videos with heavy motion blur

## Quick Test Setup

For immediate testing, you can:
1. Record a quick 10-second video on your phone
2. Transfer it to `D:\heygem_data\face2face\test_model.mp4`
3. Update `personas.yaml` to use `test_model.mp4` as the avatar_id

## Notes

- Model videos are used to train the avatar's appearance and lip-sync
- Better quality source videos = better avatar results
- You can use the same model video for multiple personas if desired
- Videos are stored locally and never uploaded to cloud services

