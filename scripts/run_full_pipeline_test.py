#!/usr/bin/env python3
"""
Full Pipeline Test: TTS + Avatar Generation
Tests the complete pipeline with TTS and avatar movements
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any

# Configure UTF-8 encoding for Windows console BEFORE any imports
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
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Configure Rich console for Windows Unicode support
console = Console(force_terminal=True, width=None, legacy_windows=False)

def update_config_for_test(config_path: Path, tts_engine: str = "bark", avatar_engine: str = "mock"):
    """Update config for testing."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Update TTS engine
    config['tts']['engine'] = tts_engine
    
    # Update avatar engine
    config['avatar']['engine'] = avatar_engine
    
    # Save config
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
        console.print(f"[green][OK][/green] Config updated: TTS={tts_engine}, Avatar={avatar_engine}", highlight=False)

def update_personas_for_test(personas_path: Path, avatar_engine: str = "mock"):
    """Update personas to use specified avatar engine."""
    with open(personas_path, 'r', encoding='utf-8') as f:
        personas = yaml.safe_load(f)
    
    # Update all personas to use the specified avatar engine
    for persona_key, persona_data in personas.get('personas', {}).items():
        if 'avatar' in persona_data:
            persona_data['avatar']['engine'] = avatar_engine
    
    # Save personas
    with open(personas_path, 'w', encoding='utf-8') as f:
        yaml.dump(personas, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    console.print(f"[green][OK][/green] Personas updated to use avatar engine: {avatar_engine}", highlight=False)

def create_test_script(script_path: Path):
    """Create a test script if it doesn't exist."""
    if script_path.exists():
        return
    
    test_content = """# Simple Single-Persona Test Script

ALICE: Hello! This is a simple test of the podcast generation system.
ALICE: We're testing with just one persona to keep things simple.
ALICE: The system should generate audio and avatar movements correctly.
"""
    
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(test_content, encoding='utf-8')
    console.print(f"[green][OK][/green] Created test script: {script_path}", highlight=False)

def main():
    """Run full pipeline test."""
    project_root = Path(__file__).parent.parent
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test full pipeline: TTS + Avatar Generation')
    parser.add_argument('--script', type=str, default='examples/scripts/test_single_persona.txt',
                       help='Path to script file')
    parser.add_argument('--tts-engine', type=str, default='bark',
                       choices=['bark', 'valle', 'elevenlabs', 'azure', 'gtts'],
                       help='TTS engine to use')
    parser.add_argument('--avatar-engine', type=str, default='mock',
                       choices=['mock', 'heygen', 'did', 'audio2face', 'dreamtalk'],
                       help='Avatar engine to use')
    parser.add_argument('--scene', type=str, default='studio',
                       help='Scene name')
    parser.add_argument('--layout', type=str, default='switching',
                       help='Layout mode')
    parser.add_argument('--no-update-config', action='store_true',
                       help='Skip updating config files')
    
    args = parser.parse_args()
    
    console.print("\n[bold cyan]=== Full Pipeline Test: TTS + Avatar Generation ===[/bold cyan]\n", highlight=False)
    
    # Paths
    config_path = project_root / "config" / "config.yaml"
    personas_path = project_root / "config" / "personas.yaml"
    script_path = project_root / args.script
    
    # Create test script if needed
    create_test_script(script_path)
    
    if not script_path.exists():
        console.print(f"[red][ERROR][/red] Script file not found: {script_path}", highlight=False)
        sys.exit(1)
    
    # Update configs if requested
    if not args.no_update_config:
        console.print("[yellow]Updating configuration...[/yellow]", highlight=False)
        update_config_for_test(config_path, args.tts_engine, args.avatar_engine)
        update_personas_for_test(personas_path, args.avatar_engine)
        console.print("")
    
    # Load config
        console.print("[yellow]Loading configuration...[/yellow]", highlight=False)
    config = load_config(config_path, project_root=project_root)
    
    # Override from args
    config['tts']['engine'] = args.tts_engine
    config['avatar']['engine'] = args.avatar_engine
    
    console.print(f"[green][OK][/green] TTS Engine: [cyan]{args.tts_engine}[/cyan]", highlight=False)
    console.print(f"[green][OK][/green] Avatar Engine: [cyan]{args.avatar_engine}[/cyan]", highlight=False)
    console.print(f"[green][OK][/green] Script: [cyan]{script_path}[/cyan]", highlight=False)
    console.print("")
    
    # Initialize pipeline
    console.print("[yellow]Initializing pipeline...[/yellow]", highlight=False)
    pipeline = Pipeline(config, project_root=project_root)
    
    # Validate setup
    setup_errors = pipeline.validate_setup()
    if setup_errors:
        console.print("[yellow][WARN][/yellow] Setup validation found issues:", highlight=False)
        for error in setup_errors:
            console.print(f"  * {error}", highlight=False)
        console.print("[yellow]Continuing anyway...[/yellow]\n", highlight=False)
    
    # Setup progress reporting
    progress_messages = []
    
    def progress_callback(message: str, progress: float):
        progress_messages.append((message, progress))
        # Print progress updates
        progress_pct = int(progress * 100)
        console.print(f"[cyan][{progress_pct:3d}%][/cyan] {message}", highlight=False)
    
    pipeline.set_progress_callback(progress_callback)
    
    # Run pipeline
    console.print("\n[bold green]Starting pipeline...[/bold green]\n", highlight=False)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Generating podcast...", total=100)
            
            def progress_with_bar(message: str, prog: float):
                progress_callback(message, prog)
                progress.update(task, completed=int(prog * 100))
            
            pipeline.set_progress_callback(progress_with_bar)
            
            output_path = pipeline.create_podcast(
                script_file=script_path,
                scene_name=args.scene,
                layout=args.layout,
                cleanup_temp=False  # Keep temp files for inspection
            )
        
        console.print(f"\n[bold green][OK] Pipeline Complete![/bold green]", highlight=False)
        console.print(f"[green]Output video:[/green] [cyan]{output_path}[/cyan]", highlight=False)
        console.print(f"\n[green]Check outputs in:[/green] [cyan]{output_path.parent}[/cyan]", highlight=False)
        
    except Exception as e:
        console.print(f"\n[bold red][ERROR] Pipeline Failed[/bold red]", highlight=False)
        console.print(f"[red]Error:[/red] {e}", highlight=False)
        import traceback
        console.print(f"\n[red]Traceback:[/red]", highlight=False)
        console.print(traceback.format_exc(), highlight=False)
        sys.exit(1)

if __name__ == "__main__":
    main()

