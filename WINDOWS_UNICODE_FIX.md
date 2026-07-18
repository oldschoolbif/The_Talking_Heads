# Windows Unicode Encoding Fix

## The Problem

On Windows, the console uses `cp1252` (Windows-1252) encoding by default, which doesn't support many Unicode characters like:
- ✓ (checkmark)
- ✗ (cross mark)
- ⚠ (warning sign)
- • (bullet)
- → (arrow)

When Python tries to print these characters, you get:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2717' in position 2
```

## The Solution

We've implemented several fixes:

### 1. Automatic UTF-8 Configuration

The `src/utils/console_output.py` module automatically:
- Configures stdout/stderr to use UTF-8 encoding on Windows
- Provides ASCII-safe alternatives if Unicode fails
- Exports constants like `CHECKMARK`, `CROSS`, `WARNING` that work on all platforms

### 2. Script-Level Fixes

All scripts now:
- Set UTF-8 encoding at startup
- Use ASCII-safe alternatives (`[OK]`, `[X]`, `[!]`) when Unicode fails
- Handle encoding errors gracefully

### 3. Rich Console (CLI)

The CLI uses `rich.Console` which handles Unicode properly, but we still use ASCII-safe alternatives in error messages.

## Usage

### In Scripts

```python
from src.utils.console_output import CHECKMARK, CROSS, WARNING, safe_print

# Use constants
print(f"{CHECKMARK} Success!")
print(f"{CROSS} Failed!")
print(f"{WARNING} Warning!")

# Or use safe_print for automatic fallback
safe_print("✓ Success!")  # Automatically converts to [OK] on Windows if needed
```

### Manual Fix (One-Time)

If you want to permanently fix your Windows console:

**PowerShell:**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

**CMD:**
```cmd
chcp 65001
```

Or set in your PowerShell profile:
```powershell
# Add to $PROFILE
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## Files Fixed

- ✅ `scripts/setup_api_keys.py` - Uses ASCII-safe symbols
- ✅ `scripts/generate_real_output.py` - Uses ASCII-safe symbols
- ✅ `scripts/verify_api_keys.py` - Uses ASCII-safe symbols
- ✅ `src/utils/console_output.py` - New utility module
- ✅ `src/cli/main.py` - Uses Rich console (handles Unicode)

## Testing

To verify the fix works:

```bash
python scripts/verify_api_keys.py
```

This should run without Unicode errors on Windows.

## Why This Happens

Windows console encoding is a legacy issue:
- Default encoding is `cp1252` (limited character set)
- Python 3.7+ allows reconfiguring stdout/stderr to UTF-8
- But not all terminals support it
- Best practice: Use ASCII-safe alternatives or handle errors gracefully

## Best Practices

1. **Always use the utility module** for console output with symbols
2. **Test on Windows** before committing Unicode characters
3. **Use Rich console** for CLI applications (handles Unicode better)
4. **Provide fallbacks** - ASCII-safe alternatives when Unicode fails

