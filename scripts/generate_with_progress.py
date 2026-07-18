"""
Generate podcast with full progress tracking and webhook support.

This script demonstrates the complete pipeline with step-by-step progress.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.core.pipeline import Pipeline
from src.utils.config_loader import load_config
from src.utils.console_output import safe_print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel

console = Console()


def main():
    """Generate podcast with progress tracking."""
    safe_print("="*60)
    safe_print("The Talking Heads - Podcast Generator")
    safe_print("="*60)
    safe_print("")
    
    # Load configuration
    config_path = project_root / "config" / "config.yaml"
    config = load_config(config_path)
    
    # Initialize pipeline
    pipeline = Pipeline(config, project_root=project_root)
    
    # Set up progress callback with Rich
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        expand=True
    ) as progress:
        
        def progress_callback(message: str, progress_value: float):
            """Update progress bar."""
            task_id = progress.add_task(message, total=100)
            progress.update(task_id, completed=int(progress_value * 100))
            if progress_value >= 1.0:
                progress.remove_task(task_id)
        
        pipeline.set_progress_callback(progress_callback)
        
        # Get script path
        script_path = project_root / "examples" / "scripts" / "multi_persona_episode.txt"
        if not script_path.exists():
            safe_print(f"[X] Script not found: {script_path}")
            sys.exit(1)
        
        safe_print(f"[INFO] Using script: {script_path}")
        safe_print("")
        
        # Validate setup
        errors = pipeline.validate_setup()
        if errors:
            safe_print("[X] Setup validation failed:")
            for error in errors:
                safe_print(f"  - {error}")
            sys.exit(1)
        
        # Check webhook server
        if pipeline.webhook_server:
            base_url = pipeline.webhook_server.get_base_url()
            safe_print(f"[OK] Webhook server running at: {base_url}")
            safe_print("[INFO] For external access, use ngrok: ngrok http 5000")
        else:
            safe_print("[WARN] Webhook server not available, using polling fallback")
        safe_print("")
        
        # Generate podcast
        try:
            console.print(Panel.fit("[bold green]Starting Podcast Generation[/bold green]", border_style="green"))
            safe_print("")
            
            output_path = pipeline.create_podcast(
                script_path=script_path,
                scene_name="studio",
                cleanup_temp=False  # Keep temp files for inspection
            )
            
            console.print(Panel.fit(
                f"[bold green]Success![/bold green]\n\n"
                f"Output: [cyan]{output_path}[/cyan]",
                border_style="green"
            ))
            
            safe_print("")
            safe_print(f"[OK] Podcast generated successfully!")
            safe_print(f"[OK] Output file: {output_path}")
            
        except Exception as e:
            console.print(Panel.fit(
                f"[bold red]Error[/bold red]\n\n{str(e)}",
                border_style="red"
            ))
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()

