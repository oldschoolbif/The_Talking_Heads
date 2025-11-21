"""
The Talking Heads - CLI Interface
"""

import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="talking-heads",
    help="The Talking Heads - AI-Generated Multi-Persona Podcast Creator",
    add_completion=False,
)


@app.command()
def create(
    script_path: Path = typer.Argument(..., help="Path to the script file"),
    output_name: Optional[str] = typer.Option(None, "--output", "-o", help="Output video name"),
    scene: Optional[str] = typer.Option("studio", "--scene", "-s", help="Background scene name"),
    layout: Optional[str] = typer.Option("switching", "--layout", "-l", help="Avatar layout: switching, side_by_side, picture_in_picture, grid"),
    quality: Optional[str] = typer.Option("high", "--quality", "-q", help="Video quality: fastest, fast, medium, high"),
):
    """
    Create a multi-persona podcast video from a script.
    
    Example:
        talking-heads create examples/scripts/episode.txt --scene studio --layout switching
    """
    typer.echo(f"🎙️  The Talking Heads - Creating podcast from: {script_path}")
    typer.echo(f"📝 Script: {script_path}")
    typer.echo(f"🎬 Scene: {scene}")
    typer.echo(f"📐 Layout: {layout}")
    typer.echo(f"🎨 Quality: {quality}")
    typer.echo("\n[INFO] Feature implementation in progress...")
    typer.echo("This command will be implemented in Phase 1 of the project.")
    typer.echo("\nFor now, please see PROJECT_SETUP.md for implementation details.")


@app.command()
def list_personas():
    """List all configured personas."""
    typer.echo("📋 Configured Personas:")
    typer.echo("  - ALICE: Main host, friendly and engaging")
    typer.echo("  - BOB: Co-host, professional and knowledgeable")
    typer.echo("  - CHARLIE: Guest, enthusiastic and expressive")
    typer.echo("\nSee config/personas.yaml for full configuration.")


@app.command()
def list_scenes():
    """List all available scenes."""
    typer.echo("🎬 Available Scenes:")
    typer.echo("  - studio: Professional recording studio")
    typer.echo("  - classroom: Educational setting")
    typer.echo("  - living_room: Casual setting")
    typer.echo("  - office: Professional office")
    typer.echo("  - outdoors: Natural outdoor setting")
    typer.echo("\nSee config/scenes.yaml for full configuration.")


@app.command()
def version():
    """Show version information."""
    from src import __version__
    typer.echo(f"The Talking Heads v{__version__}")


if __name__ == "__main__":
    app()

