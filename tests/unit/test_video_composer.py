"""
Unit tests for video composer.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.core.video_composer import VideoComposer, VideoComposition
from src.core.avatar_generator import AvatarVideo
from src.core.scene_manager import Scene
from src.core.script_parser import ScriptSegment


class TestVideoComposer:
    """Test cases for VideoComposer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "video": {
                "resolution": {"width": 1920, "height": 1080},
                "fps": 30,
                "format": "mp4",
                "codec": "h264",
            },
            "layout": {
                "mode": "switching",
                "transition": {"type": "fade", "duration": 0.5},
            },
            "storage": {"outputs_dir": "outputs"},
        }

    def test_init_with_output_dir(self, tmp_path):
        """Test initialization with custom output directory."""
        output_dir = tmp_path / "video_output"
        composer = VideoComposer(self.config, output_dir=output_dir)

        assert composer.output_dir == output_dir
        assert output_dir.exists()

    def test_init_without_output_dir(self, tmp_path):
        """Test initialization with default output directory."""
        composer = VideoComposer(self.config)
        assert composer.output_dir.exists()

    def test_compose_missing_audio(self, tmp_path):
        """Test composing with missing audio file."""
        composer = VideoComposer(self.config, output_dir=tmp_path)
        avatar_videos = []

        with pytest.raises(ValueError, match="Audio file not found"):
            composer.compose(tmp_path / "nonexistent.mp3", avatar_videos)

    def test_compose_empty_avatar_videos(self, tmp_path):
        """Test composing with empty avatar videos."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        composer = VideoComposer(self.config, output_dir=tmp_path)

        with pytest.raises(ValueError, match="cannot be empty"):
            composer.compose(audio_file, [])

    def test_compose_unsupported_layout(self, tmp_path):
        """Test composing with unsupported layout."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        avatar_video = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            video_path=tmp_path / "avatar.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        (tmp_path / "avatar.mp4").write_bytes(b"fake_video_data")

        composer = VideoComposer(self.config, output_dir=tmp_path)

        with pytest.raises(RuntimeError, match="Unsupported layout mode"):
            composer.compose(audio_file, [avatar_video], layout="unsupported")

    @patch("src.core.video_composer.subprocess.run")
    @patch("src.core.video_composer.tempfile.NamedTemporaryFile")
    def test_compose_switching_layout(self, mock_tempfile, mock_subprocess, tmp_path):
        """Test composing with switching layout."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        avatar_video = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            video_path=tmp_path / "avatar.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        (tmp_path / "avatar.mp4").write_bytes(b"fake_video_data")

        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = str(tmp_path / "concat.txt")
        mock_tempfile.return_value.__enter__.return_value = mock_file

        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        composer = VideoComposer(self.config, output_dir=tmp_path)
        composition = composer.compose(audio_file, [avatar_video], layout="switching")

        assert composition.video_path.parent.exists()
        assert composition.layout == "switching"
        assert composition.resolution == (1920, 1080)
        assert composition.fps == 30
        mock_subprocess.assert_called()

    @patch("src.core.video_composer.subprocess.run")
    @patch("src.core.video_composer.tempfile.NamedTemporaryFile")
    def test_compose_with_scene(self, mock_tempfile, mock_subprocess, tmp_path):
        """Test composing with background scene."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        scene_bg = tmp_path / "background.jpg"
        scene_bg.write_bytes(b"fake_image_data")

        scene = Scene(
            key="studio",
            name="Studio",
            background_url=str(scene_bg),
        )

        avatar_video = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            video_path=tmp_path / "avatar.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        (tmp_path / "avatar.mp4").write_bytes(b"fake_video_data")

        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = str(tmp_path / "concat.txt")
        mock_tempfile.return_value.__enter__.return_value = mock_file

        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        composer = VideoComposer(self.config, output_dir=tmp_path)
        composition = composer.compose(audio_file, [avatar_video], scene=scene, layout="switching")

        assert composition.video_path.parent.exists()
        # Should have called FFmpeg with background
        assert mock_subprocess.called

    @patch("src.core.video_composer.subprocess.run")
    @patch("src.core.video_composer.tempfile.NamedTemporaryFile")
    def test_compose_ffmpeg_failure(self, mock_tempfile, mock_subprocess, tmp_path):
        """Test handling of FFmpeg failure."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        avatar_video = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            video_path=tmp_path / "avatar.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        (tmp_path / "avatar.mp4").write_bytes(b"fake_video_data")

        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = str(tmp_path / "concat.txt")
        mock_tempfile.return_value.__enter__.return_value = mock_file

        # Mock subprocess failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "FFmpeg error"
        mock_subprocess.return_value = mock_result

        composer = VideoComposer(self.config, output_dir=tmp_path)

        with pytest.raises(RuntimeError, match="FFmpeg failed"):
            composer.compose(audio_file, [avatar_video])

    def test_get_video_duration_success(self, tmp_path):
        """Test getting video duration from FFprobe."""
        video_file = tmp_path / "test_video.mp4"
        video_file.write_bytes(b"fake_video_data")

        composer = VideoComposer(self.config, output_dir=tmp_path)

        with patch("src.core.video_composer.subprocess.run") as mock_subprocess:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "10.5\n"
            mock_subprocess.return_value = mock_result

            duration = composer._get_video_duration(video_file)
            assert duration == 10.5

    def test_get_video_duration_failure(self, tmp_path):
        """Test getting video duration when FFprobe fails."""
        video_file = tmp_path / "test_video.mp4"
        video_file.write_bytes(b"fake_video_data")

        composer = VideoComposer(self.config, output_dir=tmp_path)

        with patch("src.core.video_composer.subprocess.run") as mock_subprocess:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_subprocess.return_value = mock_result

            duration = composer._get_video_duration(video_file)
            assert duration == 0.0

    def test_video_composition_to_dict(self):
        """Test VideoComposition to_dict conversion."""
        composition = VideoComposition(
            video_path=Path("test.mp4"),
            duration=10.5,
            resolution=(1920, 1080),
            fps=30,
            layout="switching",
        )

        result = composition.to_dict()

        assert result["duration"] == 10.5
        assert result["resolution"] == (1920, 1080)
        assert result["fps"] == 30
        assert result["layout"] == "switching"
        assert "video_path" in result

    @patch("src.core.video_composer.subprocess.run")
    @patch("src.core.video_composer.tempfile.NamedTemporaryFile")
    def test_compose_side_by_side_layout(self, mock_tempfile, mock_subprocess, tmp_path):
        """Test composing with side-by-side layout."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        avatar_video = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            video_path=tmp_path / "avatar.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        (tmp_path / "avatar.mp4").write_bytes(b"fake_video_data")

        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = str(tmp_path / "concat.txt")
        mock_tempfile.return_value.__enter__.return_value = mock_file

        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        composer = VideoComposer(self.config, output_dir=tmp_path)
        composition = composer.compose(audio_file, [avatar_video], layout="side_by_side")

        assert composition.layout == "side_by_side"

    @patch("src.core.video_composer.subprocess.run")
    @patch("src.core.video_composer.tempfile.NamedTemporaryFile")
    def test_compose_picture_in_picture_layout(self, mock_tempfile, mock_subprocess, tmp_path):
        """Test composing with picture-in-picture layout."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        avatar_video = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            video_path=tmp_path / "avatar.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        (tmp_path / "avatar.mp4").write_bytes(b"fake_video_data")

        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = str(tmp_path / "concat.txt")
        mock_tempfile.return_value.__enter__.return_value = mock_file

        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        composer = VideoComposer(self.config, output_dir=tmp_path)
        composition = composer.compose(audio_file, [avatar_video], layout="picture_in_picture")

        assert composition.layout == "picture_in_picture"

    @patch("src.core.video_composer.subprocess.run")
    @patch("src.core.video_composer.tempfile.NamedTemporaryFile")
    def test_compose_grid_layout(self, mock_tempfile, mock_subprocess, tmp_path):
        """Test composing with grid layout."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        avatar_video = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            video_path=tmp_path / "avatar.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        (tmp_path / "avatar.mp4").write_bytes(b"fake_video_data")

        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = str(tmp_path / "concat.txt")
        mock_tempfile.return_value.__enter__.return_value = mock_file

        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        composer = VideoComposer(self.config, output_dir=tmp_path)
        composition = composer.compose(audio_file, [avatar_video], layout="grid")

        assert composition.layout == "grid"

    @patch("src.core.video_composer.subprocess.run")
    @patch("src.core.video_composer.tempfile.NamedTemporaryFile")
    def test_compose_custom_output_filename(self, mock_tempfile, mock_subprocess, tmp_path):
        """Test composing with custom output filename."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        avatar_video = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            video_path=tmp_path / "avatar.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        (tmp_path / "avatar.mp4").write_bytes(b"fake_video_data")

        # Mock temp file
        mock_file = MagicMock()
        mock_file.name = str(tmp_path / "concat.txt")
        mock_tempfile.return_value.__enter__.return_value = mock_file

        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        composer = VideoComposer(self.config, output_dir=tmp_path)
        composition = composer.compose(
            audio_file, [avatar_video], layout="switching", output_filename="custom_output.mp4"
        )

        assert composition.video_path.name == "custom_output.mp4"

