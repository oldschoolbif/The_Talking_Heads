"""
The Talking Heads - CLI Interface
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich import print as rprint

from src.utils.config_loader import load_config
from src.core.pipeline import Pipeline

app = typer.Typer(
    name="talking-heads",
    help="The Talking Heads - AI-Generated Multi-Persona Podcast Creator",
    add_completion=False,
)

console = Console()


def _find_project_root() -> Path:
    """Find project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "config" / "config.yaml").exists():
            return current
        current = current.parent
    return Path.cwd()


@app.command()
def create(
    script_path: Path = typer.Argument(..., help="Path to the script file"),
    output_name: Optional[str] = typer.Option(None, "--output", "-o", help="Output video name"),
    scene: Optional[str] = typer.Option("studio", "--scene", "-s", help="Background scene name"),
    layout: Optional[str] = typer.Option(None, "--layout", "-l", help="Avatar layout: switching, side_by_side, picture_in_picture, grid"),
    quality: Optional[str] = typer.Option(None, "--quality", "-q", help="Video quality: fastest, fast, medium, high"),
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config.yaml file"),
):
    """
    Create a multi-persona podcast video from a script.
    
    Example:
        talking-heads create examples/scripts/episode.txt --scene studio --layout switching
    """
    try:
        # Find project root
        project_root = _find_project_root()

        # Load configuration
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = project_root / "config" / "config.yaml"

        if not config_file.exists():
            console.print(f"[red]Error:[/red] Config file not found: {config_file}")
            raise typer.Exit(1)

        config = load_config(config_file, project_root=project_root)

        # Override quality if provided
        if quality:
            config["video"]["quality"] = quality

        # Display header
        console.print(Panel.fit(
            f"[bold blue]The Talking Heads[/bold blue]\n"
            f"Creating podcast from: [cyan]{script_path}[/cyan]",
            border_style="blue"
        ))

        # Initialize pipeline
        pipeline = Pipeline(config, project_root=project_root)

        # Validate setup
        setup_errors = pipeline.validate_setup()
        if setup_errors:
            console.print("[yellow]Warning:[/yellow] Setup validation found issues:")
            for error in setup_errors:
                console.print(f"  * {error}")
            console.print("\n[yellow]Continuing anyway...[/yellow]\n")

        # Setup progress reporting
        progress_messages = []

        def progress_callback(message: str, progress: float):
            progress_messages.append((message, progress))

        pipeline.set_progress_callback(progress_callback)

        # Run pipeline with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Processing...", total=100)

            def update_progress(message: str, progress_value: float):
                # Use ASCII-safe characters for Windows console
                safe_message = message.replace("[OK]", "[OK]").replace("[X]", "[X]")
                progress.update(task, completed=int(progress_value * 100))
                if safe_message:
                    progress.update(task, description=f"[cyan]{safe_message}")

            pipeline.set_progress_callback(update_progress)

            try:
                output_path = pipeline.create_podcast(
                    script_path, scene_name=scene, layout=layout, output_name=output_name
                )

                progress.update(task, completed=100, description="[green]Complete!")

                # Display success message
                console.print("\n[bold green][OK] Podcast created successfully![/bold green]")
                console.print(f"[green]Output:[/green] {output_path.absolute()}")
                console.print(f"[green]Duration:[/green] {output_path.stat().st_size / 1024 / 1024:.2f} MB")

            except FileNotFoundError as e:
                console.print(f"[red]Error:[/red] File not found: {e}")
                raise typer.Exit(1)
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)
            except RuntimeError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)
            except Exception as e:
                console.print(f"[red]Unexpected error:[/red] {e}")
                raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def list_personas(
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config.yaml file"),
):
    """List all configured personas."""
    try:
        project_root = _find_project_root()

        if config_path:
            config_file = Path(config_path)
        else:
            config_file = project_root / "config" / "config.yaml"

        if not config_file.exists():
            console.print(f"[red]Error:[/red] Config file not found: {config_file}")
            raise typer.Exit(1)

        config = load_config(config_file, project_root=project_root)

        from src.core.persona_engine import PersonaEngine

        persona_engine = PersonaEngine()
        personas_config_path = project_root / config.get("personas_config", "config/personas.yaml")
        persona_engine.load_personas(personas_config_path)

        personas = persona_engine.get_all_personas()

        console.print("[bold] Configured Personas:[/bold]")
        for persona in personas:
            console.print(f"  * [cyan]{persona.name.upper()}[/cyan]: {persona.description or 'No description'}")
        console.print(f"\n[dim]See {personas_config_path} for full configuration.[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def list_scenes(
    config_path: Optional[Path] = typer.Option(None, "--config", "-c", help="Path to config.yaml file"),
):
    """List all available scenes."""
    try:
        project_root = _find_project_root()

        if config_path:
            config_file = Path(config_path)
        else:
            config_file = project_root / "config" / "config.yaml"

        if not config_file.exists():
            console.print(f"[red]Error:[/red] Config file not found: {config_file}")
            raise typer.Exit(1)

        config = load_config(config_file, project_root=project_root)

        from src.core.scene_manager import SceneManager

        scene_manager = SceneManager(project_root=project_root)
        scenes_config_path = project_root / config.get("scenes_config", "config/scenes.yaml")
        scene_manager.load_scenes(scenes_config_path)

        scenes = scene_manager.get_all_scenes()

        console.print("[bold] Available Scenes:[/bold]")
        for scene in scenes:
            console.print(f"  * [cyan]{scene.key}[/cyan]: {scene.name} - {scene.description or 'No description'}")
        console.print(f"\n[dim]See {scenes_config_path} for full configuration.[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    from src import __version__
    typer.echo(f"The Talking Heads v{__version__}")


if __name__ == "__main__":
    app()

