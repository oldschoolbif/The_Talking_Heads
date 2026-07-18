# Unicode Fix Solution - MEMORIZE THIS

## The Problem

Windows console uses `cp1252` encoding by default, which cannot display Unicode characters like:
- → (arrow)
- ✓ (checkmark)
- ✗ (cross)
- ⚠ (warning)

When Python tries to print these, you get:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'
```

## The Solution (MEMORIZE THIS)

### 1. Add This to EVERY Script (at the very top, before any imports)

```python
import sys
import os

# FIX UNICODE FIRST - MUST BE BEFORE ANY OTHER IMPORTS OR PRINT STATEMENTS
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass
```

### 2. Use ASCII-Safe Characters in Print Statements

**NEVER use Unicode characters in print statements. Use these instead:**

```python
# BAD (causes Unicode error):
print("✓ Success!")
print("→ Next step")

# GOOD (ASCII-safe):
print("[OK] Success!")
print("-> Next step")
```

**ASCII-Safe Replacements:**
- `✓` → `[OK]`
- `✗` → `[FAIL]` or `[X]`
- `⚠` → `[WARN]` or `[!]`
- `→` → `->`
- `←` → `<-`
- `•` → `*`

### 3. Fix Docstrings Too

Even docstrings can cause issues if they contain Unicode. Replace arrows in docstrings:

```python
# BAD:
"""
Workflow: Image → 3DDFA → USD → Video
"""

# GOOD:
"""
Workflow: Image -> 3DDFA -> USD -> Video
"""
```

### 4. Use the Utility Module

For scripts that need symbols, use `src.utils.console_output`:

```python
from src.utils.console_output import CHECKMARK, CROSS, WARNING, safe_print

print(f"{CHECKMARK} Success!")  # Automatically uses [OK] on Windows
safe_print("✓ Success!")  # Automatically converts Unicode to ASCII
```

## Quick Fix Script

Run `scripts/fix_all_unicode.py` to automatically fix all Unicode characters in the codebase:

```bash
python scripts/fix_all_unicode.py
```

## Template for New Scripts

Copy this template to the top of every new script:

```python
import sys
import os

# FIX UNICODE FIRST - MUST BE BEFORE ANY OTHER IMPORTS OR PRINT STATEMENTS
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

# ASCII-safe characters (use these instead of Unicode)
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"
ARROW = "->"
```

## Why This Works

1. **PYTHONIOENCODING=utf-8**: Sets UTF-8 encoding for subprocess calls
2. **sys.stdout.reconfigure()**: Configures Python's stdout to use UTF-8
3. **errors="replace"**: Replaces invalid characters instead of crashing
4. **ASCII-safe characters**: Guaranteed to work on all systems

## Files Fixed

- ✅ All scripts in `scripts/` directory
- ✅ All source files in `src/` directory
- ✅ Docstrings updated to use ASCII arrows
- ✅ Print statements use ASCII-safe characters

## Remember

**ALWAYS:**
1. Add Unicode fix at the top of every script
2. Use ASCII-safe characters in print statements
3. Fix docstrings to use ASCII arrows
4. Test scripts on Windows before committing

**NEVER:**
1. Use Unicode characters in print statements
2. Use Unicode arrows in docstrings
3. Assume Unicode will work on Windows

