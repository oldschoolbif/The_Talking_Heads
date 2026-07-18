"""
Windows-safe console output utilities.

Handles Unicode encoding issues on Windows by providing ASCII-safe alternatives
and proper encoding configuration.
"""

import sys
import os
from typing import Optional

# Try to set UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        # Set console to UTF-8 if possible
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        # Fallback: use ASCII-safe characters
        pass

# Check if console supports Unicode
def _supports_unicode() -> bool:
    """Check if console supports Unicode output."""
    if sys.platform != "win32":
        return True
    
    try:
        # Try to print a Unicode character
        test_char = "[OK]"
        sys.stdout.write(test_char)
        sys.stdout.flush()
        # If we get here, it worked
        return True
    except UnicodeEncodeError:
        return False
    except Exception:
        return False

_UNICODE_SUPPORT = _supports_unicode()

# ASCII-safe alternatives
CHECKMARK = "[OK]" if _UNICODE_SUPPORT else "[OK]"
CROSS = "[X]" if _UNICODE_SUPPORT else "[X]"
WARNING = "[!]" if _UNICODE_SUPPORT else "[!]"
ARROW_RIGHT = "->" if _UNICODE_SUPPORT else "->"
ARROW_LEFT = "<-" if _UNICODE_SUPPORT else "<-"
BULLET = "*" if _UNICODE_SUPPORT else "*"

def safe_print(*args, **kwargs):
    """
    Safe print function that handles Unicode encoding errors.
    
    Falls back to ASCII-safe alternatives on Windows if Unicode fails.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Replace Unicode characters with ASCII alternatives
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_arg = (
                    arg.replace("[OK]", "[OK]")
                    .replace("[X]", "[X]")
                    .replace("[!]", "[!]")
                    .replace("->", "->")
                    .replace("<-", "<-")
                    .replace("*", "*")
                )
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)

