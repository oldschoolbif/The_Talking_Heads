# API Issues and Solutions

## HeyGen API

### Status: ⚠️ Needs Update to v2

**Problem:**
- HeyGen API v1 has been decommissioned (all endpoints return 404)
- We've updated config to use v2 (`https://api.heygen.com/v2`)
- However, v2 API may have different endpoint structure and request format

**Solution:**
1. ✅ Updated `config/config.yaml` to use v2 base URL
2. ⏳ Need to verify v2 API endpoint format and request structure
3. ⏳ May need to update `HeyGenProvider.generate()` method

**Next Steps:**
- Check HeyGen v2 API documentation: https://docs.heygen.com
- Verify correct endpoint: `/v2/video/generate` or `/v2/talks` or other?
- Update request format if needed

## D-ID API

### Status: ⚠️ Request Format Issue

**Problem:**
- D-ID API returns 500/403 errors
- D-ID may not support direct audio file uploads
- D-ID typically expects:
  - `script` parameter (text-to-speech) OR
  - `audio_url` parameter (publicly accessible URL)

**Current Implementation:**
- We're trying to upload audio files directly via `files={"audio": ...}`
- This may not be supported by D-ID API

**Solution Options:**

### Option 1: Use D-ID's Text-to-Speech (Not Recommended)
- Skip ElevenLabs, use D-ID's built-in TTS
- Pros: Simpler integration
- Cons: Lose ElevenLabs voice quality and control

### Option 2: Upload Audio to Public URL (Recommended)
- Upload audio files to temporary hosting (S3, Cloudinary, etc.)
- Use the public URL in D-ID API request
- Pros: Keep ElevenLabs TTS quality
- Cons: Requires additional service/infrastructure

### Option 3: Use HeyGen v2 (When Fixed)
- Once HeyGen v2 is properly configured, use it instead
- HeyGen supports direct audio file uploads

**Next Steps:**
1. Check D-ID API documentation for correct format: https://docs.d-id.com
2. Implement audio URL hosting (temporary S3 bucket or similar)
3. Update `DIDProvider.generate()` to use `audio_url` instead of file upload

## Current Workaround

**Using D-ID with Image URLs:**
- ✅ D-ID supports using image URLs as avatars (already configured)
- ✅ Personas.yaml uses image URLs: `avatar_id: "https://d-id-public-bucket.s3.amazonaws.com/alice.jpg"`
- ⚠️ Still need to fix audio upload issue

## API Version Policy

**Remember:** Always check for and use the newest stable version of APIs.

- ✅ **ElevenLabs**: v1 (latest stable)
- ⚠️ **HeyGen**: v2 (needs verification)
- ⚠️ **D-ID**: Latest (needs format fix)

