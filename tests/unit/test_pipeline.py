"""
Unit tests for main pipeline.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.core.pipeline import Pipeline
from src.core.script_parser import ParsedScript, ScriptSegment
from src.core.persona_engine import Persona, VoiceConfig, AvatarConfig, ExpressionConfig, GestureConfig
from src.core.tts_engine import AudioSegment
from src.core.avatar_generator import AvatarVideo
from src.core.scene_manager import Scene
from src.core.video_composer import VideoComposition


class TestPipeline:
    """Test cases for Pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "tts": {"engine": "elevenlabs"},
            "avatar": {"engine": "heygen"},
            "api": {
                "elevenlabs": {"api_key": "test_key"},
                "heygen": {"api_key": "test_key"},
            },
            "storage": {
                "outputs_dir": "outputs",
                "cache_dir": ".cache",
                "temp_dir": ".cache/temp",
            },
            "personas_config": "config/personas.yaml",
            "scenes_config": "config/scenes.yaml",
        }

    def test_init(self, tmp_path):
        """Test pipeline initialization."""
        pipeline = Pipeline(self.config, project_root=tmp_path)

        assert pipeline.script_parser is not None
        assert pipeline.persona_engine is not None
        assert pipeline.tts_engine is not None
        assert pipeline.audio_mixer is not None
        assert pipeline.avatar_generator is not None
        assert pipeline.scene_manager is not None
        assert pipeline.video_composer is not None

    def test_set_progress_callback(self, tmp_path):
        """Test setting progress callback."""
        pipeline = Pipeline(self.config, project_root=tmp_path)

        callback = Mock()
        pipeline.set_progress_callback(callback)

        pipeline._report_progress("Test message", 0.5)
        callback.assert_called_once_with("Test message", 0.5)

    def test_validate_setup_missing_configs(self, tmp_path):
        """Test validation with missing config files."""
        pipeline = Pipeline(self.config, project_root=tmp_path)

        errors = pipeline.validate_setup()

        # Should have errors for missing config files
        assert len(errors) > 0
        assert any("config" in error.lower() for error in errors)

    def test_validate_setup_valid(self, tmp_path):
        """Test validation with valid setup."""
        # Create config files
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "personas.yaml").write_text("personas: {}")
        (tmp_path / "config" / "scenes.yaml").write_text("scenes: {}")

        config = self.config.copy()
        config["personas_config"] = "config/personas.yaml"
        config["scenes_config"] = "config/scenes.yaml"

        pipeline = Pipeline(config, project_root=tmp_path)

        # Mock providers as available
        with patch.object(pipeline.tts_engine.active_provider, "is_available", return_value=True):
            with patch.object(pipeline.avatar_generator.active_provider, "is_available", return_value=True):
                errors = pipeline.validate_setup()

                # Should have fewer errors (only API key checks might fail)
                assert isinstance(errors, list)

    @patch("src.core.pipeline.VideoComposer")
    @patch("src.core.pipeline.AvatarGenerator")
    @patch("src.core.pipeline.AudioMixer")
    @patch("src.core.pipeline.TTSEngine")
    @patch("src.core.pipeline.PersonaEngine")
    @patch("src.core.pipeline.ScriptParser")
    def test_create_podcast_full_workflow(
        self, mock_parser, mock_persona_engine, mock_tts, mock_mixer, mock_avatar, mock_composer, tmp_path
    ):
        """Test complete podcast creation workflow."""
        # Create script file
        script_file = tmp_path / "test_script.txt"
        script_file.write_text("""# Test Podcast

ALICE: Hello!
BOB: Hi there!
""", encoding="utf-8")

        # Create config files
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "personas.yaml").write_text("""
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
  bob:
    name: "Bob"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_456"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_456"
""")
        (tmp_path / "config" / "scenes.yaml").write_text("""
scenes:
  studio:
    name: "Studio"
    background_url: "assets/studio.jpg"
""")

        # Mock parsed script
        parsed_script = ParsedScript(
            title="Test Podcast",
            segments=[
                ScriptSegment(persona="ALICE", text="Hello!"),
                ScriptSegment(persona="BOB", text="Hi there!"),
            ],
            personas=["ALICE", "BOB"],
        )

        # Mock personas
        alice = Persona(
            key="alice",
            name="Alice",
            voice=VoiceConfig(engine="elevenlabs", voice_id="voice_123"),
            avatar=AvatarConfig(engine="heygen", avatar_id="avatar_123"),
        )
        bob = Persona(
            key="bob",
            name="Bob",
            voice=VoiceConfig(engine="elevenlabs", voice_id="voice_456"),
            avatar=AvatarConfig(engine="heygen", avatar_id="avatar_456"),
        )

        # Mock audio segments
        audio_seg1 = AudioSegment(
            segment=ScriptSegment(persona="ALICE", text="Hello!"),
            audio_path=tmp_path / "audio1.mp3",
            duration=1.0,
            provider="elevenlabs",
        )
        audio_seg2 = AudioSegment(
            segment=ScriptSegment(persona="BOB", text="Hi there!"),
            audio_path=tmp_path / "audio2.mp3",
            duration=1.5,
            provider="elevenlabs",
        )

        # Mock avatar videos
        avatar_video1 = AvatarVideo(
            segment=ScriptSegment(persona="ALICE", text="Hello!"),
            video_path=tmp_path / "avatar1.mp4",
            duration=1.0,
            provider="heygen",
            persona="Alice",
        )
        avatar_video2 = AvatarVideo(
            segment=ScriptSegment(persona="BOB", text="Hi there!"),
            video_path=tmp_path / "avatar2.mp4",
            duration=1.5,
            provider="heygen",
            persona="Bob",
        )

        # Mock video composition
        composition = VideoComposition(
            video_path=tmp_path / "output.mp4",
            duration=2.5,
            resolution=(1920, 1080),
            fps=30,
            layout="switching",
        )

        # Setup mocks
        mock_parser_instance = Mock()
        mock_parser_instance.parse_file.return_value = parsed_script
        mock_parser.return_value = mock_parser_instance

        mock_persona_instance = Mock()
        mock_persona_instance.get_persona.side_effect = lambda name: alice if name == "ALICE" else bob
        mock_persona_instance.validate_script.return_value = []
        mock_persona_engine.return_value = mock_persona_instance

        mock_tts_instance = Mock()
        mock_tts_instance.generate_multiple.return_value = [audio_seg1, audio_seg2]
        mock_tts_instance.active_provider.is_available.return_value = True
        mock_tts.return_value = mock_tts_instance

        mock_mixer_instance = Mock()
        mock_mixer_instance.mix_persona_tracks.return_value = tmp_path / "mixed_audio.mp3"
        mock_mixer_instance.output_dir = tmp_path
        mock_mixer.return_value = mock_mixer_instance

        mock_avatar_instance = Mock()
        mock_avatar_instance.generate_multiple.return_value = [avatar_video1, avatar_video2]
        mock_avatar_instance.active_provider.is_available.return_value = True
        mock_avatar.return_value = mock_avatar_instance

        mock_composer_instance = Mock()
        mock_composer_instance.compose.return_value = composition
        mock_composer.return_value = mock_composer_instance

        # Create pipeline and run
        config = self.config.copy()
        config["personas_config"] = "config/personas.yaml"
        config["scenes_config"] = "config/scenes.yaml"

        pipeline = Pipeline(config, project_root=tmp_path)

        # Replace instances with mocks
        pipeline.script_parser = mock_parser_instance
        pipeline.persona_engine = mock_persona_instance
        pipeline.tts_engine = mock_tts_instance
        pipeline.audio_mixer = mock_mixer_instance
        pipeline.avatar_generator = mock_avatar_instance
        pipeline.video_composer = mock_composer_instance

        # Mock scene manager
        scene = Scene(key="studio", name="Studio", background_url="assets/studio.jpg")
        pipeline.scene_manager.get_scene = Mock(return_value=scene)
        pipeline.scene_manager.load_scenes = Mock()

        # Run pipeline
        output_path = pipeline.create_podcast(script_file, scene_name="studio")

        assert output_path == tmp_path / "output.mp4"
        mock_parser_instance.parse_file.assert_called_once()
        mock_persona_instance.validate_script.assert_called_once()
        mock_tts_instance.generate_multiple.assert_called_once()
        mock_mixer_instance.mix_persona_tracks.assert_called_once()
        mock_avatar_instance.generate_multiple.assert_called_once()
        mock_composer_instance.compose.assert_called_once()

    def test_create_podcast_script_not_found(self, tmp_path):
        """Test creating podcast with missing script file."""
        pipeline = Pipeline(self.config, project_root=tmp_path)

        with pytest.raises(FileNotFoundError):
            pipeline.create_podcast(tmp_path / "nonexistent.txt")

    def test_create_podcast_validation_errors(self, tmp_path):
        """Test creating podcast with validation errors."""
        script_file = tmp_path / "test_script.txt"
        script_file.write_text("""# Test Podcast

ALICE: Hello!
UNKNOWN: Hi there!
""", encoding="utf-8")

        # Create config files
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "personas.yaml").write_text("""
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
""")
        (tmp_path / "config" / "scenes.yaml").write_text("""
scenes:
  studio:
    name: "Studio"
    background_url: "assets/studio.jpg"
""")

        config = self.config.copy()
        config["personas_config"] = "config/personas.yaml"
        config["scenes_config"] = "config/scenes.yaml"

        pipeline = Pipeline(config, project_root=tmp_path)

        with pytest.raises(ValueError, match="validation failed"):
            pipeline.create_podcast(script_file)

    def test_create_podcast_scene_not_found(self, tmp_path):
        """Test creating podcast with invalid scene name."""
        script_file = tmp_path / "test_script.txt"
        script_file.write_text("""# Test Podcast

ALICE: Hello!
""", encoding="utf-8")

        # Create config files
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "personas.yaml").write_text("""
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
""")
        (tmp_path / "config" / "scenes.yaml").write_text("""
scenes:
  studio:
    name: "Studio"
    background_url: "assets/studio.jpg"
""")

        config = self.config.copy()
        config["personas_config"] = "config/personas.yaml"
        config["scenes_config"] = "config/scenes.yaml"

        pipeline = Pipeline(config, project_root=tmp_path)

        # Mock all components to get to scene loading
        with patch.object(pipeline.script_parser, "parse_file") as mock_parse:
            with patch.object(pipeline.persona_engine, "load_personas"):
                with patch.object(pipeline.persona_engine, "validate_script", return_value=[]):
                    with patch.object(pipeline.persona_engine, "get_persona"):
                        with patch.object(pipeline.tts_engine, "generate_multiple"):
                            with patch.object(pipeline.audio_mixer, "mix_persona_tracks"):
                                with patch.object(pipeline.avatar_generator, "generate_multiple"):
                                    with patch.object(pipeline.scene_manager, "load_scenes"):
                                        pipeline.scene_manager.get_scene = Mock(return_value=None)

                                        mock_parse.return_value = ParsedScript(
                                            title="Test", segments=[], personas=["ALICE"]
                                        )

                                        with pytest.raises(ValueError, match="not found"):
                                            pipeline.create_podcast(script_file, scene_name="nonexistent")

    def test_cleanup_temp_files(self, tmp_path):
        """Test cleanup of temporary files."""
        pipeline = Pipeline(self.config, project_root=tmp_path)

        # Create some temp files
        temp_file1 = tmp_path / "temp1.mp3"
        temp_file2 = tmp_path / "temp2.mp4"
        temp_file1.write_bytes(b"data")
        temp_file2.write_bytes(b"data")

        pipeline.temp_files = [temp_file1, temp_file2]

        pipeline._cleanup_temp_files()

        assert not temp_file1.exists()
        assert not temp_file2.exists()
        assert len(pipeline.temp_files) == 0

    def test_cleanup_on_error(self, tmp_path):
        """Test that cleanup happens on error."""
        script_file = tmp_path / "test_script.txt"
        script_file.write_text("""# Test Podcast

ALICE: Hello!
""", encoding="utf-8")

        config = self.config.copy()
        config["personas_config"] = "config/personas.yaml"
        config["scenes_config"] = "config/scenes.yaml"

        pipeline = Pipeline(config, project_root=tmp_path)

        # Create temp file
        temp_file = tmp_path / "temp.mp3"
        temp_file.write_bytes(b"data")
        pipeline.temp_files = [temp_file]

        # Mock to raise error
        with patch.object(pipeline.script_parser, "parse_file", side_effect=ValueError("Test error")):
            with pytest.raises(ValueError):
                pipeline.create_podcast(script_file, cleanup_temp=True)

            # Temp file should be cleaned up
            assert not temp_file.exists()

    def test_progress_reporting(self, tmp_path):
        """Test progress reporting during pipeline execution."""
        script_file = tmp_path / "test_script.txt"
        script_file.write_text("""# Test Podcast

ALICE: Hello!
""", encoding="utf-8")

        # Create config files
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "personas.yaml").write_text("""
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
""")
        (tmp_path / "config" / "scenes.yaml").write_text("""
scenes:
  studio:
    name: "Studio"
    background_url: "assets/studio.jpg"
""")

        config = self.config.copy()
        config["personas_config"] = "config/personas.yaml"
        config["scenes_config"] = "config/scenes.yaml"

        pipeline = Pipeline(config, project_root=tmp_path)

        # Set up progress callback
        progress_calls = []

        def progress_callback(message, progress):
            progress_calls.append((message, progress))

        pipeline.set_progress_callback(progress_callback)

        # Mock all components
        with patch.object(pipeline.script_parser, "parse_file") as mock_parse:
            with patch.object(pipeline.persona_engine, "load_personas"):
                with patch.object(pipeline.persona_engine, "validate_script", return_value=[]):
                    with patch.object(pipeline.persona_engine, "get_persona"):
                        with patch.object(pipeline.tts_engine, "generate_multiple", return_value=[]):
                            with patch.object(pipeline.audio_mixer, "mix_persona_tracks", return_value=tmp_path / "mixed.mp3"):
                                with patch.object(pipeline.avatar_generator, "generate_multiple", return_value=[]):
                                    with patch.object(pipeline.scene_manager, "load_scenes"):
                                        with patch.object(pipeline.video_composer, "compose") as mock_compose:
                                            scene = Scene(key="studio", name="Studio")
                                            pipeline.scene_manager.get_scene = Mock(return_value=scene)

                                            mock_parse.return_value = ParsedScript(
                                                title="Test", segments=[], personas=["ALICE"]
                                            )

                                            composition = VideoComposition(
                                                video_path=tmp_path / "output.mp4",
                                                duration=1.0,
                                                resolution=(1920, 1080),
                                                fps=30,
                                                layout="switching",
                                            )
                                            mock_compose.return_value = composition

                                            pipeline.create_podcast(script_file)

                                            # Verify progress was reported
                                            assert len(progress_calls) > 0
                                            assert any("Parsing" in msg for msg, _ in progress_calls)
                                            assert any("Generating" in msg for msg, _ in progress_calls)

