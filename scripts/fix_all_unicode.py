"""
Fix all Unicode characters in Python scripts.

This script replaces Unicode characters with ASCII-safe alternatives in all Python files.
"""

import re
from pathlib import Path

# Unicode to ASCII replacements
REPLACEMENTS = {
    "->": "->",
    "<-": "<-",
    "^": "^",
    "v": "v",
    "[OK]": "[OK]",
    "[X]": "[X]",
    "[!]": "[!]",
    "[!]️": "[!]",
    "*": "*",
    "": "",
    "": "",
    "": "",
    "": "",
    "": "",
    "": "",
    "[OK]": "[OK]",
    "[FAIL]": "[FAIL]",
    "": "",
    "": "",
    "": "",
}

def fix_file(file_path: Path):
    """Fix Unicode characters in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Replace Unicode characters
        for unicode_char, ascii_replacement in REPLACEMENTS.items():
            content = content.replace(unicode_char, ascii_replacement)
        
        # Only write if changed
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"[OK] Fixed: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"[FAIL] Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in scripts and src directories."""
    project_root = Path(__file__).parent.parent
    
    # Find all Python files
    python_files = []
    for directory in ["scripts", "src"]:
        dir_path = project_root / directory
        if dir_path.exists():
            python_files.extend(dir_path.rglob("*.py"))
    
    print(f"Found {len(python_files)} Python files")
    print("Fixing Unicode characters...\n")
    
    fixed_count = 0
    for py_file in python_files:
        if fix_file(py_file):
            fixed_count += 1
    
    print(f"\n[OK] Fixed {fixed_count} files")
    print("[OK] All Unicode characters replaced with ASCII-safe alternatives")

if __name__ == "__main__":
    main()

