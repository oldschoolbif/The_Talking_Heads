"""
TEMPLATE: Add this to the TOP of every script file (before any other imports)

This fixes Unicode encoding issues on Windows.
"""

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

# ASCII-safe character constants (use these instead of Unicode)
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"
ARROW = "->"

