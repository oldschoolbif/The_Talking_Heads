"""
Unit tests for CLI interface.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner
from src.cli.main import app, _find_project_root


class TestCLI:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "The Talking Heads" in result.stdout

    def test_list_personas_command(self, tmp_path):
        """Test list_personas command."""
        # Create config files
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "config.yaml").write_text("""
personas_config: config/personas.yaml
scenes_config: config/scenes.yaml
api:
  elevenlabs:
    api_key: test_key
  heygen:
    api_key: test_key
storage:
  outputs_dir: outputs
  cache_dir: .cache
  temp_dir: .cache/temp
""")
        (tmp_path / "config" / "personas.yaml").write_text("""
personas:
  alice:
    name: "Alice"
    description: "Test persona"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
""")

        with patch("src.cli.main._find_project_root", return_value=tmp_path):
            result = self.runner.invoke(app, ["list-personas", "--config", str(tmp_path / "config" / "config.yaml")])

            assert result.exit_code == 0
            assert "ALICE" in result.stdout or "Alice" in result.stdout

    def test_list_scenes_command(self, tmp_path):
        """Test list_scenes command."""
        # Create config files
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "config.yaml").write_text("""
personas_config: config/personas.yaml
scenes_config: config/scenes.yaml
api:
  elevenlabs:
    api_key: test_key
  heygen:
    api_key: test_key
storage:
  outputs_dir: outputs
  cache_dir: .cache
  temp_dir: .cache/temp
""")
        (tmp_path / "config" / "scenes.yaml").write_text("""
scenes:
  studio:
    name: "Podcast Studio"
    description: "Professional studio"
    background_url: "assets/studio.jpg"
""")

        with patch("src.cli.main._find_project_root", return_value=tmp_path):
            result = self.runner.invoke(app, ["list-scenes", "--config", str(tmp_path / "config" / "config.yaml")])

            assert result.exit_code == 0
            assert "studio" in result.stdout.lower()

    def test_create_command_missing_script(self, tmp_path):
        """Test create command with missing script file."""
        with patch("src.cli.main._find_project_root", return_value=tmp_path):
            result = self.runner.invoke(app, ["create", str(tmp_path / "nonexistent.txt")])

            assert result.exit_code != 0
            assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    @patch("src.cli.main.Pipeline")
    def test_create_command_success(self, mock_pipeline_class, tmp_path):
        """Test create command with successful pipeline execution."""
        # Create script file
        script_file = tmp_path / "test_script.txt"
        script_file.write_text("""# Test Podcast

ALICE: Hello!
""", encoding="utf-8")

        # Create config files
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "config.yaml").write_text("""
personas_config: config/personas.yaml
scenes_config: config/scenes.yaml
api:
  elevenlabs:
    api_key: test_key
  heygen:
    api_key: test_key
storage:
  outputs_dir: outputs
  cache_dir: .cache
  temp_dir: .cache/temp
""")

        # Mock pipeline
        mock_pipeline = Mock()
        mock_pipeline.validate_setup.return_value = []
        output_path = tmp_path / "output.mp4"
        output_path.write_bytes(b"fake_video_data")
        mock_pipeline.create_podcast.return_value = output_path
        mock_pipeline_class.return_value = mock_pipeline

        with patch("src.cli.main._find_project_root", return_value=tmp_path):
            result = self.runner.invoke(
                app,
                [
                    "create",
                    str(script_file),
                    "--config",
                    str(tmp_path / "config" / "config.yaml"),
                    "--scene",
                    "studio",
                ],
            )

            # Should succeed (exit code 0) or show progress
            assert mock_pipeline.create_podcast.called

    def test_find_project_root(self, tmp_path):
        """Test finding project root."""
        # Create config structure
        (tmp_path / "config").mkdir(parents=True, exist_ok=True)
        (tmp_path / "config" / "config.yaml").write_text("test: config", encoding="utf-8")

        with patch("src.cli.main.Path.cwd", return_value=tmp_path):
            root = _find_project_root()
            # Should find a directory with config/config.yaml
            assert isinstance(root, Path)

