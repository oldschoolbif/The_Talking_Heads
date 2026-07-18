#!/usr/bin/env python3
"""Test Audio2Face server connection and initialization."""

import sys
from pathlib import Path

# Configure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console

console = Console(force_terminal=True, width=None, legacy_windows=False)

def main():
    """Test Audio2Face server."""
    console.print("\n[bold cyan]=== Audio2Face Server Test ===[/bold cyan]\n", highlight=False)
    
    # Test 1: Check if py-audio2face is installed
    console.print("[yellow]1. Checking py-audio2face package...[/yellow]", highlight=False)
    try:
        from py_audio2face import Audio2Face
        console.print("[green][OK][/green] py-audio2face is installed", highlight=False)
        console.print(f"  Package: {Audio2Face}", highlight=False)
    except ImportError as e:
        console.print(f"[red][ERROR][/red] py-audio2face not installed: {e}", highlight=False)
        console.print("[yellow]Install with: pip install py-audio2face[/yellow]", highlight=False)
        return False
    
    # Test 2: Try to create Audio2Face instance
    console.print("\n[yellow]2. Creating Audio2Face instance...[/yellow]", highlight=False)
    
    # Try to find Audio2Face installation
    import os
    from pathlib import Path
    
    a2f_install_path = None
    
    # Check Omniverse location
    if os.name == 'nt':  # Windows
        appdata = os.getenv('LOCALAPPDATA', '')
        if appdata:
            ov_path = Path(appdata) / "ov" / "pkg"
            if ov_path.exists():
                for pkg_dir in ov_path.iterdir():
                    if pkg_dir.is_dir() and "audio2face" in pkg_dir.name.lower():
                        a2f_install_path = str(pkg_dir)
                        break
    
    # Check SDK location
    if not a2f_install_path:
        sdk_paths = [
            Path("d:/dev/Audio2Face-3D-SDK"),
            Path.home() / "dev" / "Audio2Face-3D-SDK",
        ]
        for sdk_path in sdk_paths:
            if sdk_path.exists():
                a2f_install_path = str(sdk_path)
                break
    
    try:
        if a2f_install_path:
            a2f = Audio2Face(api_url="http://localhost:8011", a2f_install_path=a2f_install_path)
            console.print("[green][OK][/green] Audio2Face instance created", highlight=False)
            console.print(f"  API URL: http://localhost:8011", highlight=False)
            console.print(f"  Install Path: {a2f_install_path}", highlight=False)
        else:
            # Try without install path (may work if Audio2Face is in registry)
            a2f = Audio2Face(api_url="http://localhost:8011")
            console.print("[green][OK][/green] Audio2Face instance created (auto-detected)", highlight=False)
            console.print(f"  API URL: http://localhost:8011", highlight=False)
    except Exception as e:
        console.print(f"[yellow][WARN][/yellow] Failed to create instance: {e}", highlight=False)
        console.print("[yellow]Solution:[/yellow]", highlight=False)
        console.print("  1. Install Audio2Face via Omniverse Launcher (Exchange -> Audio2Face)", highlight=False)
        console.print("  2. Or set a2f_install_path in config/config.yaml:", highlight=False)
        console.print("     audio2face:", highlight=False)
        console.print("       a2f_install_path: d:/dev/Audio2Face-3D-SDK", highlight=False)
        console.print("\n[yellow]Note:[/yellow] Audio2Face SDK needs to be built for full functionality.", highlight=False)
        return False
    
    # Test 3: Try to initialize Audio2Face (starts server if needed)
    console.print("\n[yellow]3. Initializing Audio2Face (this may start the server)...[/yellow]", highlight=False)
    try:
        a2f.init_a2f(streaming=False)
        console.print("[green][OK][/green] Audio2Face initialized successfully!", highlight=False)
        console.print("[green]Server is ready to use![/green]", highlight=False)
        return True
    except Exception as e:
        console.print(f"[yellow][WARN][/yellow] Initialization failed: {e}", highlight=False)
        console.print("[yellow]This may mean:[/yellow]", highlight=False)
        console.print("  1. Audio2Face server needs to be started manually", highlight=False)
        console.print("  2. Omniverse Audio2Face extension needs to be installed", highlight=False)
        console.print("  3. Audio2Face-3D-SDK needs to be built", highlight=False)
        console.print("\n[yellow]Check the documentation for setup instructions.[/yellow]", highlight=False)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

