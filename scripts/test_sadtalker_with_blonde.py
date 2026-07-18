#!/usr/bin/env python3
"""
Test SadTalker with blonde.png from Downloads folder.
Creates a talking avatar from the 2D headshot image.
"""

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

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config_loader import load_config
from src.core.pipeline import Pipeline
from rich.console import Console

console = Console(force_terminal=True, width=None, legacy_windows=False)

def main():
    """Test SadTalker with blonde.png."""
    console.print("\n[bold cyan]=== 3DDFA Test: 3D Face Reconstruction ===[/bold cyan]\n", highlight=False)
    
    # Find blonde.png
    downloads = Path.home() / "Downloads"
    blonde_image = downloads / "blonde.png"
    
    if not blonde_image.exists():
        console.print(f"[red][ERROR][/red] blonde.png not found at: {blonde_image}", highlight=False)
        console.print(f"[yellow]Please ensure blonde.png is in your Downloads folder.[/yellow]", highlight=False)
        sys.exit(1)
    
    console.print(f"[green][OK][/green] Found source image: {blonde_image}", highlight=False)
    
    # Load config
    config_path = project_root / "config" / "config.yaml"
    config = load_config(config_path, project_root=project_root)
    
    # Update config to use 3DDFA
    config['avatar']['engine'] = 'tddfa'
    
    # Add 3DDFA config if not present
    if 'tddfa' not in config:
        config['tddfa'] = {
            'tddfa_path': 'd:/dev/3DDFA_V2',
            'result_dir': str(project_root / '.cache' / 'temp' / 'tddfa_results'),
            'default_source_image': str(blonde_image),
            'output_dir': str(project_root / '.cache' / 'temp' / 'avatars')
        }
    
    console.print(f"[green][OK][/green] Avatar Engine: [cyan]tddfa[/cyan]", highlight=False)
    console.print(f"[green][OK][/green] Source Image: [cyan]{blonde_image}[/cyan]", highlight=False)
    console.print("")
    
    # Create a simple test script
    test_script = project_root / "examples" / "scripts" / "test_sadtalker_blonde.txt"
    test_script.parent.mkdir(parents=True, exist_ok=True)
    
    script_content = """# 3DDFA Test - Blonde Avatar

ALICE: Hello! This is a test of 3DDFA avatar generation.
ALICE: We're using 3DDFA to reconstruct a 3D face from the 2D headshot image.
ALICE: The system will process the image and create an enhanced version.
"""
    
    test_script.write_text(script_content, encoding='utf-8')
    console.print(f"[green][OK][/green] Created test script: {test_script}", highlight=False)
    console.print("")
    
    # Initialize pipeline
    console.print("[yellow]Initializing pipeline...[/yellow]", highlight=False)
    pipeline = Pipeline(config, project_root=project_root)
    
    # Setup progress callback
    def progress_callback(message: str, progress: float):
        progress_pct = int(progress * 100)
        console.print(f"[cyan][{progress_pct:3d}%][/cyan] {message}", highlight=False)
    
    pipeline.set_progress_callback(progress_callback)
    
    # Update persona to use SadTalker and blonde.png
    personas_path = project_root / "config" / "personas.yaml"
    import yaml
    with open(personas_path, 'r', encoding='utf-8') as f:
        personas = yaml.safe_load(f)
    
    if 'alice' in personas.get('personas', {}):
        personas['personas']['alice']['avatar']['engine'] = 'tddfa'
        personas['personas']['alice']['avatar']['avatar_id'] = str(blonde_image)
    
    with open(personas_path, 'w', encoding='utf-8') as f:
        yaml.dump(personas, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    console.print("[yellow]Starting pipeline...[/yellow]\n", highlight=False)
    
    # Run pipeline
    try:
        output_path = pipeline.create_podcast(
            script_file=test_script,
            scene_name="studio",
            layout="switching",
            cleanup_temp=False
        )
        
        console.print(f"\n[bold green][OK] Pipeline Complete![/bold green]", highlight=False)
        console.print(f"[green]Output video:[/green] [cyan]{output_path}[/cyan]", highlight=False)
        console.print(f"\n[green]The video should show the blonde avatar talking![/green]", highlight=False)
        
    except Exception as e:
        console.print(f"\n[bold red][ERROR] Pipeline Failed[/bold red]", highlight=False)
        console.print(f"[red]Error:[/red] {e}", highlight=False)
        import traceback
        console.print(f"\n[red]Traceback:[/red]", highlight=False)
        console.print(traceback.format_exc(), highlight=False)
        sys.exit(1)

if __name__ == "__main__":
    main()

