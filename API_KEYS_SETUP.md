# 🔑 API Keys Setup Guide

This guide will help you set up API keys for The Talking Heads.

## ✅ API Keys Configured

Your API keys have been set up in the `.env` file:
- ✅ HeyGen API Key - Configured
- ✅ D-ID API Key - Configured  
- ✅ ElevenLabs API Key - Configured
- ✅ Azure Speech Key - Configured
- ✅ Azure Speech Region - Configured (eastus)

The `.env` file is in `.gitignore` to keep your keys secure.

## Quick Start

If you need to update keys, run the interactive setup script:

```bash
python scripts/setup_api_keys.py
```

This will guide you through:
1. Getting API keys from providers
2. Setting them up in `.env` file (recommended) or `config/config.yaml`
3. Verifying your configuration

## Required API Keys

You need at least **one avatar key** and **one TTS key**:

### Avatar Generation (Choose One)

#### HeyGen (Recommended)
1. Sign up at https://www.heygen.com
2. Go to **Settings** → **API Keys**
3. Create a new API key
4. Copy the key

**Environment Variable:** `HEYGEN_API_KEY`

#### D-ID (Alternative)
1. Sign up at https://www.d-id.com
2. Go to **API** section
3. Generate API key
4. Copy the key

**Environment Variable:** `DID_API_KEY`

### Text-to-Speech (Choose One)

#### ElevenLabs (Recommended)
1. Sign up at https://elevenlabs.io
2. Go to **Profile** → **API Keys**
3. Copy your API key

**Environment Variable:** `ELEVENLABS_API_KEY`

#### Azure Speech Service (Alternative)
1. Go to https://portal.azure.com
2. Create a **Speech Service** resource
3. Go to **Keys and Endpoint**
4. Copy **Key 1** and **Location/Region**

**Environment Variables:** 
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`

#### gTTS (Free - No Key Needed!)
- Google Text-to-Speech is automatically used as fallback
- No API key required
- Lower quality but works for testing

## Setup Methods

### Method 1: Environment Variables (.env file) - Recommended

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your keys:
   ```env
   HEYGEN_API_KEY=your_key_here
   ELEVENLABS_API_KEY=your_key_here
   ```

3. **Important:** Add `.env` to `.gitignore` (already done) to keep keys secure!

### Method 2: Direct Configuration (config.yaml)

Edit `config/config.yaml` and add keys directly:

```yaml
api:
  heygen:
    api_key: your_key_here
  elevenlabs:
    api_key: your_key_here
```

**Note:** This method is less secure as keys are in version control.

## Verification

After setting up keys, verify your configuration:

```bash
python scripts/setup_api_keys.py
# Choose option 3: "Just verify existing keys"
```

Or test with a real generation:

```bash
python scripts/generate_real_output.py
```

## Priority Order

Configuration is loaded in this priority (highest to lowest):

1. **Environment variables** (`.env` file)
2. **config/config.yaml** (direct values)
3. **Default values** (in code)

## Free Options

If you don't have API keys yet, you can still test:

- **gTTS** (Google Text-to-Speech) - No key needed, automatically used as fallback
- **Limited functionality** - Avatar generation requires a key

## Troubleshooting

### "API key not found" error
- Check that `.env` file exists and has correct variable names
- Verify keys are set: `python scripts/setup_api_keys.py` (option 3)
- Make sure there are no extra spaces in `.env` file

### "Provider not available" error
- Verify API key is correct
- Check if you have credits/quota remaining
- For HeyGen/D-ID: Check if account is active

### Environment variables not loading
- Make sure `.env` file is in project root
- Restart your terminal/IDE after creating `.env`
- On Windows: Use PowerShell or CMD (not Git Bash for env vars)

## Security Best Practices

1. ✅ **Never commit `.env` file** to git (already in `.gitignore`)
2. ✅ **Use environment variables** instead of hardcoding in config.yaml
3. ✅ **Rotate keys regularly** if exposed
4. ✅ **Use separate keys** for development and production

## Getting Help

- Run `python scripts/setup_api_keys.py` for interactive help
- Check provider documentation:
  - HeyGen: https://docs.heygen.com
  - ElevenLabs: https://elevenlabs.io/docs
  - D-ID: https://docs.d-id.com

## Next Steps

Once keys are configured:

1. **Test the setup:**
   ```bash
   python scripts/generate_real_output.py
   ```

2. **Generate your first podcast:**
   ```bash
   python -m src.cli.main create scripts/test_episode.txt
   ```

3. **Check the output:**
   - Video will be in `outputs/` directory
   - You can play it with any video player

