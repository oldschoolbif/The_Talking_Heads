# Unicode Encoding Fix for Windows

## Problem

Windows console (PowerShell, CMD) uses `cp1252` encoding by default, which cannot handle Unicode characters like:
- ✓ (checkmark)
- ✗ (cross)
- ⚠ (warning)
- → (arrow)
- Other Unicode symbols

This causes `UnicodeEncodeError: 'charmap' codec can't encode character` errors.

## Solution

### 1. Use `src/utils/console_setup.py` (Recommended)

**Always import and call this at the start of your scripts:**

```python
import sys
from pathlib import Path

# Setup console encoding FIRST (before any other imports that might print)
try:
    from src.utils.console_setup import setup_console_encoding
    setup_console_encoding()
except ImportError:
    # Fallback for scripts outside project structure
    if sys.platform == "win32":
        import os
        os.environ["PYTHONIOENCODING"] = "utf-8"
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Now continue with rest of imports
from src.core import ...
```

### 2. Use ASCII-Safe Characters (Alternative)

If you can't use UTF-8 setup, use ASCII-safe replacements:

```python
# Instead of:
print("✓ Success")
print("✗ Failed")
print("⚠ Warning")

# Use:
print("[OK] Success")
print("[FAIL] Failed")
print("[WARN] Warning")
```

### 3. Use `safe_print()` Function

The `console_setup.py` module provides a `safe_print()` function that automatically handles Unicode:

```python
from src.utils.console_setup import safe_print

safe_print("✓ This will work even if UTF-8 fails")
```

## Implementation Checklist

When creating new Python scripts:

- [ ] Import `setup_console_encoding` at the very top (before other imports)
- [ ] Call `setup_console_encoding()` immediately after import
- [ ] Use ASCII-safe characters (`[OK]`, `[FAIL]`, `[WARN]`) instead of Unicode symbols
- [ ] Or use `safe_print()` for automatic fallback

## Files That Need This Fix

Any Python script that:
- Prints to console
- Uses Unicode characters
- May run on Windows
- Is called from PowerShell/CMD

## Testing

To verify the fix works:

```python
# This should work without errors:
print("✓ Test checkmark")
print("✗ Test cross")
print("⚠ Test warning")
```

If you see `UnicodeEncodeError`, the fix isn't applied correctly.

## Environment Variables

You can disable auto-setup by setting:
```bash
$env:DISABLE_CONSOLE_SETUP = "1"
```

## Notes

- The fix sets `PYTHONIOENCODING=utf-8` environment variable
- It reconfigures `sys.stdout` and `sys.stderr` to use UTF-8
- On Windows, it also sets console code page to UTF-8 (CP 65001)
- If reconfiguration fails, scripts should use ASCII-safe characters as fallback

## Remember

**MEMORIZE THIS:** Always add console encoding setup at the start of Python scripts that may run on Windows. Use `src/utils/console_setup.py` or the fallback code shown above.

