# Script Standard for The Talking Heads Project

## Standard: Python for All Scripts

**Decision:** Use **Python** for all scripts in this project.

**Rationale:**
- Cross-platform compatibility (Windows 11, WSL2, Linux, macOS)
- Better error handling and exception management
- Robust libraries for API calls, JSON parsing, file I/O
- Consistent with the main codebase (Python-based)
- Better for complex logic and data processing
- Works seamlessly in both Windows PowerShell and WSL2 environments

## When to Use What

### ✅ Use Python For:
- **All diagnostic/troubleshooting scripts**
- **All test scripts**
- **All monitoring scripts**
- **All utility scripts**
- **All automation scripts**

### ❌ Do NOT Use PowerShell For:
- Scripts that need complex logic
- Scripts that make API calls
- Scripts that parse JSON/XML
- Scripts that need cross-platform compatibility
- Scripts that need robust error handling

### ⚠️ PowerShell Only For:
- Simple one-liner commands
- Windows-specific system administration (if absolutely necessary)
- Quick terminal commands

## Python Script Standards

### 1. Shebang (for Linux/WSL2 compatibility)
```python
#!/usr/bin/env python3
```

### 2. Encoding (for Windows compatibility)
```python
# -*- coding: utf-8 -*-
import sys
import os

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

### 3. Error Handling
```python
import sys
from pathlib import Path

def main():
    try:
        # Your code here
        pass
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 4. Output Formatting
- Use ASCII-safe characters (avoid Unicode symbols like ✓, ✗)
- Use `[OK]`, `[FAIL]`, `[INFO]`, `[ERROR]` prefixes
- Use `->` instead of `→` for arrows
- Use `*` instead of `•` for bullets

### 5. File Paths
```python
from pathlib import Path

# Always use Path objects for cross-platform compatibility
project_root = Path(__file__).parent.parent
config_path = project_root / "config" / "config.yaml"
```

### 6. Logging
```python
import logging
from datetime import datetime

# Use Python's logging module for consistency
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## Running Python Scripts

### In PowerShell (Windows):
```powershell
python scripts/script_name.py
```

### In WSL2:
```bash
python3 scripts/script_name.py
```

### With Arguments:
```powershell
python scripts/script_name.py --arg1 value1 --arg2 value2
```

## Migration Plan

If you find PowerShell scripts that should be Python:
1. Identify the script's purpose
2. Rewrite in Python following the standards above
3. Test in both Windows PowerShell and WSL2
4. Update documentation
5. Remove the PowerShell version

## Examples

### ✅ Good: Python Script
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent
    print(f"[INFO] Project root: {project_root}")
    # ... rest of code

if __name__ == "__main__":
    main()
```

### ❌ Bad: PowerShell Script (for complex tasks)
```powershell
# Don't use PowerShell for complex API calls, JSON parsing, etc.
```

## Summary

**MEMORIZE:** Use Python for all scripts. It's more robust, cross-platform, and consistent with the project's main codebase.

