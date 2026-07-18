# Coqui TTS Terms of Service Acceptance

## Overview

Coqui TTS models (XTTS-v2, XTTS-v3) require accepting their Terms of Service before downloading models. This is a one-time process.

## How to Accept ToS

### Method 1: Interactive Script (Recommended)

Run the provided script in an interactive terminal:

```bash
python scripts/accept_coqui_tos.py
```

This will:
1. Prompt you to accept the Terms of Service
2. Download the XTTS-v2 model
3. Store the acceptance so you won't be prompted again

**When prompted:**
- Type `y` and press Enter to accept the non-commercial CPML license
- Type `n` to decline (model won't download)

### Method 2: Manual Acceptance

When you first use XTTS-v2 in your code, you'll be prompted:

```python
from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
```

The prompt will appear:
```
> You must confirm the following:
> "I have purchased a commercial license from Coqui: licensing@coqui.ai"
> "Otherwise, I agree to the terms of the non-commercial CPML: https://coqui.ai/cpml" - [y/n]
```

Type `y` and press Enter.

### Method 3: Environment Variable (Non-Interactive)

For automated/CI environments, you can set:

```bash
export COQUI_TOS_AGREED=1
```

Or on Windows PowerShell:
```powershell
$env:COQUI_TOS_AGREED = "1"
```

**Note:** This bypasses the interactive prompt but you still need to accept the ToS.

## License Information

- **Non-Commercial Use**: CPML (Coqui Public Model License)
- **Commercial Use**: Requires purchasing a license from licensing@coqui.ai
- **License URL**: https://coqui.ai/cpml

## Verification

After accepting ToS, verify the model is downloaded:

```python
from TTS.api import TTS
import torch

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=torch.cuda.is_available())
print("Model loaded successfully!")
```

If successful, the model is ready to use.

## Troubleshooting

### "EOFError: EOF when reading a line"

This means the ToS prompt requires interactive input. Solutions:
1. Run in an interactive terminal (not piped/redirected)
2. Use the `accept_coqui_tos.py` script
3. Set `COQUI_TOS_AGREED=1` environment variable

### Model Not Found

If you see "KeyError: 'xtts_v3'":
- XTTS-v3 may not be available in your TTS version
- Use XTTS-v2 instead: `tts_models/multilingual/multi-dataset/xtts_v2`

### ToS Prompt Keeps Appearing

The acceptance is stored in the model cache directory. If it keeps appearing:
1. Check write permissions on the cache directory
2. Clear cache and re-accept: `rm -rf ~/.local/share/tts/`
3. Re-run the acceptance script

## Notes

- ToS acceptance is stored per-user in the TTS cache directory
- Once accepted, you won't be prompted again for that model
- Different models may require separate acceptance
- The acceptance is stored locally and not transmitted anywhere

