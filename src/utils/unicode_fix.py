"""
Universal Unicode fix for Windows console.

This module MUST be imported at the very start of any script that prints output.
It configures UTF-8 encoding and provides ASCII-safe character replacements.

Usage:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.utils.unicode_fix import fix_unicode, ASCII_CHARS  # MUST be first import
    
    fix_unicode()  # Call at script start
    
    # Use ASCII-safe characters
    print(f"{ASCII_CHARS.OK} Success!")
"""

import sys
import os

# ASCII-safe character replacements
class ASCII_CHARS:
    """ASCII-safe alternatives to Unicode characters."""
    OK = "[OK]"
    FAIL = "[FAIL]"
    WARN = "[WARN]"
    ARROW_RIGHT = "->"
    ARROW_LEFT = "<-"
    ARROW_UP = "^"
    ARROW_DOWN = "v"
    BULLET = "*"
    CHECKMARK = "[OK]"
    CROSS = "[X]"
    WARNING = "[!]"

def fix_unicode():
    """
    Configure UTF-8 encoding for Windows console.
    
    This MUST be called at the start of any script that prints output.
    """
    if sys.platform == "win32":
        # Set environment variable for subprocess calls
        os.environ["PYTHONIOENCODING"] = "utf-8"
        
        # Reconfigure stdout/stderr to UTF-8
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            # Fallback: encoding not supported, will use ASCII-safe chars
            pass

# Auto-fix on import
fix_unicode()

