# VALL-E X Setup Guide

## Overview

VALL-E X is a high-quality zero-shot voice cloning TTS model from Microsoft. It requires manual installation as it's not available as a standard pip package.

## Why Manual Installation?

VALL-E X is a research-grade model that:
- Requires specific repository setup
- May have custom dependencies
- Needs model checkpoints downloaded separately
- Has multiple community implementations

## Installation Options

### Option 1: VALL-E X (Plachtaa Implementation) - Recommended

**Repository**: https://github.com/Plachtaa/VALL-E-X

**Steps**:
1. Clone the repository:
   ```bash
   cd ~
   git clone https://github.com/Plachtaa/VALL-E-X.git valle
   cd valle
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download model checkpoints (follow repository instructions)

4. Update `config/config.yaml`:
   ```yaml
   valle:
     valle_path: ~/valle  # or absolute path: C:/Users/YourName/valle
     python_exec: python
     output_dir: .cache/valle_outputs
   ```

### Option 2: Other VALL-E Implementations

There are several VALL-E implementations available:
- **VALL-E X (Plachtaa)**: https://github.com/Plachtaa/VALL-E-X
- **VALL-E (Microsoft)**: Original research code (may require special access)
- **VALL-E X (Community)**: Various community ports

Choose the one that best fits your needs.

## Configuration

After installation, update `config/config.yaml`:

```yaml
valle:
  # Path to VALL-E installation (absolute or relative to project root)
  valle_path: ~/valle
  
  # Python executable (auto-detected from venv if available)
  python_exec: python
  
  # Output directory for VALL-E results
  output_dir: .cache/valle_outputs
```

## Verification

Run the test script:
```bash
python scripts/test_local_providers.py
```

Or test directly:
```python
from src.core.valle_provider import VALLEProvider
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

provider = VALLEProvider(config['valle'])
print("Available:", provider.is_available())
```

## Notes

- VALL-E X requires significant GPU memory (8GB+ recommended)
- Model checkpoints are large (several GB)
- Installation complexity varies by implementation
- Some implementations may require specific CUDA/PyTorch versions

## Alternative

If VALL-E X setup is too complex, consider:
- **XTTS-v2**: Easier setup, similar voice cloning capabilities
- **Bark**: Already installed and working, good for expressive TTS

