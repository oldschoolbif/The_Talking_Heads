"""
Console setup utilities for Windows compatibility.

This module ensures proper UTF-8 encoding for console output on Windows,
preventing UnicodeEncodeError issues with special characters.
"""

import sys
import os
from typing import Optional


def setup_console_encoding(encoding: str = "utf-8", force: bool = True) -> bool:
    """
    Configure console encoding for UTF-8 output on Windows.
    
    Args:
        encoding: Encoding to use (default: "utf-8")
        force: If True, force encoding even if already set
    
    Returns:
        True if encoding was set successfully, False otherwise
    """
    if sys.platform == "win32":
        try:
            # Set environment variable for subprocesses
            os.environ["PYTHONIOENCODING"] = encoding
            
            # Reconfigure stdout and stderr to use UTF-8
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding=encoding, errors="replace")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding=encoding, errors="replace")
            
            # Also try to set console code page on Windows
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # CP_UTF8 = 65001
                kernel32.SetConsoleOutputCP(65001)
            except Exception:
                pass  # Not critical if this fails
            
            return True
        except Exception as e:
            # If reconfiguration fails, continue anyway
            # The script will use ASCII-safe characters as fallback
            return False
    return True


def get_safe_chars() -> dict:
    """
    Return a dictionary of ASCII-safe character replacements for common Unicode symbols.
    
    Returns:
        Dictionary mapping Unicode symbols to ASCII-safe alternatives
    """
    return {
        "[OK]": "[OK]",
        "[X]": "[FAIL]",
        "[!]": "[WARN]",
        "->": "->",
        "<-": "<-",
        "^": "^",
        "v": "v",
        "*": "*",
        "—": "-",
        "–": "-",
        "…": "...",
        "°": "deg",
        "±": "+/-",
        "×": "x",
        "÷": "/",
        "∞": "inf",
        "≠": "!=",
        "≤": "<=",
        "≥": ">=",
        "≈": "~=",
        "∑": "sum",
        "∏": "prod",
        "√": "sqrt",
        "α": "alpha",
        "β": "beta",
        "γ": "gamma",
        "π": "pi",
        "λ": "lambda",
        "μ": "mu",
        "σ": "sigma",
        "Δ": "Delta",
        "Ω": "Omega",
    }


def safe_print(*args, **kwargs):
    """
    Print function that handles Unicode encoding issues gracefully.
    
    Automatically uses ASCII-safe replacements if UTF-8 encoding fails.
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Replace Unicode characters with ASCII-safe alternatives
        safe_chars = get_safe_chars()
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_str = arg
                for unicode_char, ascii_replacement in safe_chars.items():
                    safe_str = safe_str.replace(unicode_char, ascii_replacement)
                safe_args.append(safe_str)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)


# Auto-setup on import (can be disabled by setting environment variable)
if os.getenv("DISABLE_CONSOLE_SETUP") != "1":
    setup_console_encoding()

