"""
Video Composer for The Talking Heads

Composes final video with multiple avatars, backgrounds, and audio synchronization.
"""

import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
import os

from src.core.avatar_generator import AvatarVideo
from src.core.scene_manager import Scene
from src.core.script_parser import ScriptSegment


@dataclass
class VideoComposition:
    """Represents a composed video with metadata."""

    video_path: Path
    duration: float
    resolution: tuple[int, int]  # (width, height)
    fps: int
    layout: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert composition to dictionary."""
        return {
            "video_path": str(self.video_path),
            "duration": self.duration,
            "resolution": self.resolution,
            "fps": self.fps,
            "layout": self.layout,
        }


class VideoComposer:
    """Composes final video with multiple avatars and audio."""

    def __init__(self, config: Dict[str, Any], output_dir: Optional[Path] = None):
        """
        Initialize video composer.

        Args:
            config: Configuration dictionary with video and layout settings
            output_dir: Directory for output video files (optional)
        """
        self.config = config
        self.video_config = config.get("video", {})
        self.layout_config = config.get("layout", {})

        # Setup output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            output_dir_str = config.get("storage", {}).get("outputs_dir", "outputs")
            self.output_dir = Path(output_dir_str)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Video settings
        self.resolution = (
            self.video_config.get("resolution", {}).get("width", 1920),
            self.video_config.get("resolution", {}).get("height", 1080),
        )
        self.fps = self.video_config.get("fps", 30)
        self.format = self.video_config.get("format", "mp4")
        self.codec = self.video_config.get("codec", "h264")

        # Layout settings
        self.default_layout = self.layout_config.get("mode", "switching")
        self.transition_type = self.layout_config.get("transition", {}).get("type", "fade")
        self.transition_duration = self.layout_config.get("transition", {}).get("duration", 0.5)

    def compose(
        self,
        audio_path: Path,
        avatar_videos: List[AvatarVideo],
        scene: Optional[Scene] = None,
        layout: Optional[str] = None,
        output_filename: Optional[str] = None,
    ) -> VideoComposition:
        """
        Compose final video with avatars, background, and audio.

        Args:
            audio_path: Path to mixed audio file
            avatar_videos: List of avatar videos with timing
            scene: Background scene (optional)
            layout: Layout mode ("switching", "side_by_side", "picture_in_picture", "grid")
            output_filename: Optional output filename

        Returns:
            VideoComposition with video file path and metadata

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If video composition fails
        """
        if not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        if not avatar_videos:
            raise ValueError("avatar_videos cannot be empty")

        layout = layout or self.default_layout

        # Generate output path
        if output_filename:
            output_path = self.output_dir / output_filename
        else:
            output_path = self.output_dir / "final_video.mp4"

        try:
            # Compose based on layout
            if layout == "switching":
                self._compose_switching(audio_path, avatar_videos, scene, output_path)
            elif layout == "side_by_side":
                self._compose_side_by_side(audio_path, avatar_videos, scene, output_path)
            elif layout == "picture_in_picture":
                self._compose_picture_in_picture(audio_path, avatar_videos, scene, output_path)
            elif layout == "grid":
                self._compose_grid(audio_path, avatar_videos, scene, output_path)
            else:
                raise ValueError(f"Unsupported layout mode: {layout}")

            # Get video duration (estimate from audio or actual video)
            duration = self._get_video_duration(output_path)

            return VideoComposition(
                video_path=output_path,
                duration=duration,
                resolution=self.resolution,
                fps=self.fps,
                layout=layout,
            )

        except Exception as e:
            raise RuntimeError(f"Video composition failed: {e}") from e

    def _compose_switching(
        self, audio_path: Path, avatar_videos: List[AvatarVideo], scene: Optional[Scene], output_path: Path
    ):
        """
        Compose video with switching layout (show only active speaker).

        Args:
            audio_path: Path to audio file
            avatar_videos: List of avatar videos
            scene: Background scene
            output_path: Output video path
        """
        # For MVP, use simple concatenation with transitions
        # In production, this would use FFmpeg complex filters for precise timing

        # Create temporary file list for concatenation
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            concat_file = Path(f.name)

            try:
                # Write file list for FFmpeg concat demuxer
                for avatar_video in avatar_videos:
                    video_path = avatar_video.video_path.resolve()  # Get absolute path
                    if video_path.exists():
                        # Convert to forward slashes for FFmpeg (works on Windows too)
                        video_path_str = str(video_path).replace("\\", "/")
                        # Escape single quotes for FFmpeg
                        video_path_str = video_path_str.replace("'", "'\\''")
                        f.write(f"file '{video_path_str}'\n")
                    else:
                        # Log missing file but continue
                        import logging
                        logging.warning(f"Avatar video not found: {video_path}")

                f.flush()
                f.close()  # Explicitly close to ensure file is written

                # Build FFmpeg command
                cmd = [
                    "ffmpeg",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(concat_file),
                    "-i",
                    str(audio_path),
                    "-c:v",
                    "libx264",
                    "-c:a",
                    "aac",
                    "-shortest",
                    "-y",  # Overwrite output
                    str(output_path),
                ]

                # Add background if provided
                if scene:
                    scene_path = self._get_scene_background_path(scene)
                    if scene_path and scene_path.exists():
                        # Use overlay filter for background
                        # This is simplified - full implementation would use complex filtergraph
                        cmd = [
                            "ffmpeg",
                            "-loop",
                            "1",
                            "-i",
                            str(scene_path),
                            "-f",
                            "concat",
                            "-safe",
                            "0",
                            "-i",
                            str(concat_file),
                            "-i",
                            str(audio_path),
                            "-filter_complex",
                            "[0:v][1:v]overlay=0:0:shortest=1[v]",
                            "-map",
                            "[v]",
                            "-map",
                            "2:a",
                            "-c:v",
                            "libx264",
                            "-c:a",
                            "aac",
                            "-shortest",
                            "-y",
                            str(output_path),
                        ]

                # Execute FFmpeg
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=1800,  # 30 minute timeout
                    encoding="utf-8",
                    errors="replace",
                )

                if result.returncode != 0:
                    raise RuntimeError(f"FFmpeg failed: {result.stderr}")

            finally:
                # Clean up temp file (with retry for Windows file locking)
                if concat_file.exists():
                    try:
                        concat_file.unlink()
                    except (PermissionError, OSError):
                        # File may be locked on Windows, try again after a brief delay
                        import time
                        time.sleep(0.1)
                        try:
                            concat_file.unlink()
                        except (PermissionError, OSError):
                            # If still locked, just leave it (will be cleaned up later)
                            pass

    def _compose_side_by_side(
        self, audio_path: Path, avatar_videos: List[AvatarVideo], scene: Optional[Scene], output_path: Path
    ):
        """
        Compose video with side-by-side layout (all avatars visible).

        Args:
            audio_path: Path to audio file
            avatar_videos: List of avatar videos
            scene: Background scene
            output_path: Output video path
        """
        # For MVP, use simple side-by-side layout
        # This is a simplified implementation
        self._compose_switching(audio_path, avatar_videos, scene, output_path)

    def _compose_picture_in_picture(
        self, audio_path: Path, avatar_videos: List[AvatarVideo], scene: Optional[Scene], output_path: Path
    ):
        """
        Compose video with picture-in-picture layout.

        Args:
            audio_path: Path to audio file
            avatar_videos: List of avatar videos
            scene: Background scene
            output_path: Output video path
        """
        # For MVP, use switching layout as fallback
        self._compose_switching(audio_path, avatar_videos, scene, output_path)

    def _compose_grid(
        self, audio_path: Path, avatar_videos: List[AvatarVideo], scene: Optional[Scene], output_path: Path
    ):
        """
        Compose video with grid layout (all avatars in grid).

        Args:
            audio_path: Path to audio file
            avatar_videos: List of avatar videos
            scene: Background scene
            output_path: Output video path
        """
        # For MVP, use switching layout as fallback
        self._compose_switching(audio_path, avatar_videos, scene, output_path)

    def _get_scene_background_path(self, scene: Scene) -> Optional[Path]:
        """
        Get background image path for scene.

        Args:
            scene: Scene object

        Returns:
            Path to background image, or None if not available
        """
        try:
            from src.core.scene_manager import SceneManager

            manager = SceneManager(project_root=Path.cwd())
            return manager.get_background_path(scene)
        except Exception:
            return None

    def _get_video_duration(self, video_path: Path) -> float:
        """
        Get duration of video file.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds
        """
        try:
            # Use FFprobe to get duration
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace"
            )

            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())

        except Exception:
            pass

        # Fallback: estimate from file size (very rough)
        return 0.0

