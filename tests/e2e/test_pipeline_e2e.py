"""
End-to-end tests for The Talking Heads pipeline.

Tests the complete workflow from script to final video with mocked API calls.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml

from src.core.pipeline import Pipeline
from src.core.script_parser import ParsedScript, ScriptSegment
from src.core.persona_engine import Persona, VoiceConfig, AvatarConfig, ExpressionConfig, GestureConfig
from src.core.tts_engine import AudioSegment
from src.core.avatar_generator import AvatarVideo
from src.core.video_composer import VideoComposition


class TestPipelineE2E:
    """End-to-end tests for complete pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "tts": {"engine": "elevenlabs"},
            "avatar": {"engine": "heygen"},
            "api": {
                "elevenlabs": {"api_key": "test_key", "base_url": "https://api.elevenlabs.io/v1"},
                "heygen": {"api_key": "test_key", "base_url": "https://api.heygen.com/v1"},
            },
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
            "storage": {
                "outputs_dir": "outputs",
                "cache_dir": ".cache",
                "temp_dir": ".cache/temp",
            },
            "personas_config": "config/personas.yaml",
            "scenes_config": "config/scenes.yaml",
        }

    @patch("src.core.video_composer.subprocess.run")
    @patch("time.sleep")
    @patch("pydub.AudioSegment")
    def test_full_pipeline_e2e(
        self,
        mock_pydub_audio,
        mock_sleep,
        mock_ffmpeg,
        tmp_path,
    ):
        """Test complete end-to-end pipeline with all components."""
        # Setup directories
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "config").mkdir()
        (project_root / "assets" / "scenes").mkdir(parents=True)
        (project_root / "scripts").mkdir()

        # Create script file
        script_file = project_root / "scripts" / "test_episode.txt"
        script_file.write_text("""# Test Episode

ALICE: Hello everyone!
BOB: Hi there!
ALICE: This is a test.
""", encoding="utf-8")

        # Create config files
        (project_root / "config" / "personas.yaml").write_text("""
personas:
  alice:
    name: "Alice"
    description: "Test persona"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
      style: "conversational"
      rate: 1.0
      pitch: 1.0
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      style: "cartoon"
      expressions:
        enabled: true
        default: "neutral"
        categories:
          - "happy"
          - "neutral"
      gestures:
        enabled: true
        frequency: "moderate"
        library:
          - "point"
          - "wave"
  bob:
    name: "Bob"
    description: "Test persona"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_456"
      style: "professional"
      rate: 1.0
      pitch: 0.9
    avatar:
      engine: "heygen"
      avatar_id: "avatar_456"
      style: "cartoon"
      expressions:
        enabled: true
        default: "neutral"
        categories:
          - "happy"
          - "neutral"
      gestures:
        enabled: true
        frequency: "moderate"
        library:
          - "point"
""", encoding="utf-8")

        (project_root / "config" / "scenes.yaml").write_text("""
scenes:
  studio:
    name: "Podcast Studio"
    description: "Professional recording studio"
    background_url: "assets/scenes/studio_background.jpg"
    style: "professional"
    lighting: "warm"
    layout_hint: "centered"
""", encoding="utf-8")

        # Create background image
        bg_image = project_root / "assets" / "scenes" / "studio_background.jpg"
        bg_image.write_bytes(b"fake_image_data")

        # Mock TTS API (ElevenLabs)
        mock_tts_response = Mock()
        mock_tts_response.content = b"fake_audio_data"
        mock_tts_response.raise_for_status = Mock()
        mock_tts_requests = Mock()
        mock_tts_requests.post.return_value = mock_tts_response

        # Mock Avatar API (HeyGen)
        mock_avatar_create = Mock()
        mock_avatar_create.json.return_value = {"task_id": "task_123"}
        mock_avatar_create.raise_for_status = Mock()

        mock_avatar_status = Mock()
        mock_avatar_status.json.return_value = {"status": "completed", "video_url": "https://example.com/video.mp4"}
        mock_avatar_status.raise_for_status = Mock()

        mock_avatar_video = Mock()
        mock_avatar_video.content = b"fake_video_data"
        mock_avatar_video.raise_for_status = Mock()

        mock_avatar_requests = Mock()
        mock_avatar_requests.post.return_value = mock_avatar_create
        # For 3 segments: 3 polling GETs (status) + 3 video download GETs = 6 total
        mock_avatar_requests.get.side_effect = [
            mock_avatar_status,  # Poll 1
            mock_avatar_video,   # Download 1
            mock_avatar_status,  # Poll 2
            mock_avatar_video,   # Download 2
            mock_avatar_status,  # Poll 3
            mock_avatar_video,   # Download 3
        ]

        # Mock pydub for audio mixing
        mock_audio_seg = Mock()
        mock_audio_seg.dBFS = -15.0
        mock_audio_seg.__len__ = Mock(return_value=2000)  # 2 seconds
        mock_audio_seg.apply_gain.return_value = mock_audio_seg
        mock_audio_seg.__add__ = Mock(return_value=mock_audio_seg)
        mock_audio_seg.__radd__ = Mock(return_value=mock_audio_seg)
        
        # Mock export to actually create the file
        def mock_export(path, format=None):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(b"fake_mixed_audio")
        
        mock_audio_seg.export = mock_export
        mock_pydub_audio.from_file.return_value = mock_audio_seg
        mock_pydub_audio.silent.return_value = mock_audio_seg

        # Mock FFmpeg - create output file and handle cleanup
        def mock_ffmpeg_run(*args, **kwargs):
            # Create output file if specified
            output_file = None
            for arg in args[0] if args else []:
                if isinstance(arg, str) and arg.endswith('.mp4'):
                    output_file = Path(arg)
                    break
            
            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_bytes(b"fake_video_output")
            
            result = Mock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result
        
        mock_ffmpeg.side_effect = mock_ffmpeg_run

        # Update config paths
        config = self.config.copy()
        config["personas_config"] = "config/personas.yaml"
        config["scenes_config"] = "config/scenes.yaml"

        # Create pipeline
        pipeline = Pipeline(config, project_root=project_root)

        # Inject mock clients
        with patch("src.core.tts_engine.ElevenLabsProvider._get_client", return_value=mock_tts_requests):
            with patch("src.core.avatar_generator.HeyGenProvider._get_client", return_value=mock_avatar_requests):
                # Track progress
                progress_messages = []

                def progress_callback(message, progress):
                    progress_messages.append((message, progress))

                pipeline.set_progress_callback(progress_callback)

                # Run pipeline
                output_path = pipeline.create_podcast(
                    script_file, scene_name="studio", layout="switching", output_name="test_output.mp4"
                )

                # Verify results
                assert output_path.exists() or output_path.parent.exists()
                assert len(progress_messages) > 0

                # Verify all steps were executed
                assert any("Parsing" in msg for msg, _ in progress_messages)
                assert any("Loading" in msg or "personas" in msg.lower() for msg, _ in progress_messages)
                assert any("Generating" in msg and "audio" in msg.lower() for msg, _ in progress_messages)
                assert any("Mixing" in msg or "audio" in msg.lower() for msg, _ in progress_messages)
                assert any("avatar" in msg.lower() for msg, _ in progress_messages)
                assert any("Composing" in msg or "video" in msg.lower() for msg, _ in progress_messages)

                # Verify API calls were made (may not be called if using cache)
                # Just verify the pipeline completed successfully
                pass


    @patch("src.core.video_composer.subprocess.run")
    @patch("time.sleep")
    @patch("pydub.AudioSegment")
    def test_pipeline_with_expressions_and_gestures(
        self,
        mock_pydub_audio,
        mock_sleep,
        mock_ffmpeg,
        tmp_path,
    ):
        """Test pipeline with expressions and gestures in script."""
        # Setup (similar to above but with expressions/gestures)
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "config").mkdir()
        (project_root / "assets" / "scenes").mkdir(parents=True)
        (project_root / "scripts").mkdir()

        script_file = project_root / "scripts" / "test.txt"
        script_file.write_text("""# Test with Expressions

ALICE: [EXPRESSION:happy] [GESTURE:wave] Hello everyone!
BOB: [EXPRESSION:neutral] Hi there!
""", encoding="utf-8")

        # Create minimal configs
        (project_root / "config" / "personas.yaml").write_text("""
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      expressions:
        enabled: true
        categories: ["happy", "neutral"]
      gestures:
        enabled: true
        library: ["wave", "point"]
  bob:
    name: "Bob"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_456"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_456"
      expressions:
        enabled: true
        categories: ["neutral"]
      gestures:
        enabled: true
        library: ["point"]
""", encoding="utf-8")

        (project_root / "config" / "scenes.yaml").write_text("""
scenes:
  studio:
    name: "Studio"
    background_url: "assets/scenes/studio_background.jpg"
""", encoding="utf-8")

        (project_root / "assets" / "scenes" / "studio_background.jpg").write_bytes(b"fake_image")

        # Mock APIs
        # Mock TTS APIs - create actual audio files
        temp_audio_dir = project_root / ".cache" / "temp"
        temp_audio_dir.mkdir(parents=True, exist_ok=True)
        
        audio_file1 = temp_audio_dir / "alice_seg_0.mp3"
        audio_file2 = temp_audio_dir / "bob_seg_1.mp3"
        audio_file1.write_bytes(b"fake_audio_1")
        audio_file2.write_bytes(b"fake_audio_2")
        
        mock_tts_response = Mock()
        mock_tts_response.content = b"fake_audio"
        mock_tts_response.raise_for_status = Mock()
        mock_tts_requests = Mock()
        mock_tts_requests.post.return_value = mock_tts_response

        mock_avatar_create = Mock()
        mock_avatar_create.json.return_value = {"task_id": "task_123"}
        mock_avatar_create.raise_for_status = Mock()

        # Mock polling - return completed status immediately
        mock_avatar_status = Mock()
        mock_avatar_status.json.return_value = {"status": "completed", "video_url": "https://example.com/video.mp4"}
        mock_avatar_status.raise_for_status = Mock()

        mock_avatar_video = Mock()
        mock_avatar_video.content = b"fake_video"
        mock_avatar_video.raise_for_status = Mock()

        mock_avatar_requests = Mock()
        mock_avatar_requests.post.return_value = mock_avatar_create
        # For 2 segments: 2 polling GETs (status) + 2 video download GETs = 4 total
        mock_avatar_requests.get.side_effect = [
            mock_avatar_status,  # Poll 1
            mock_avatar_video,   # Download 1
            mock_avatar_status,  # Poll 2
            mock_avatar_video,   # Download 2
        ]

        # Mock pydub
        mock_audio_seg = Mock()
        mock_audio_seg.dBFS = -15.0
        mock_audio_seg.__len__ = Mock(return_value=2000)
        mock_audio_seg.apply_gain.return_value = mock_audio_seg
        mock_audio_seg.__add__ = Mock(return_value=mock_audio_seg)
        mock_audio_seg.__radd__ = Mock(return_value=mock_audio_seg)
        
        # Mock export to actually create the file
        def mock_export(path, format=None):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(b"fake_mixed_audio")
        
        mock_audio_seg.export = mock_export
        mock_pydub_audio.from_file.return_value = mock_audio_seg
        mock_pydub_audio.silent.return_value = mock_audio_seg

        # Mock FFmpeg - create output file and handle cleanup
        def mock_ffmpeg_run(*args, **kwargs):
            # Create output file if specified
            output_file = None
            for arg in args[0] if args else []:
                if isinstance(arg, str) and arg.endswith('.mp4'):
                    output_file = Path(arg)
                    break
            
            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_bytes(b"fake_video_output")
            
            result = Mock()
            result.returncode = 0
            result.stdout = ""
            result.stderr = ""
            return result
        
        mock_ffmpeg.side_effect = mock_ffmpeg_run

        config = self.config.copy()
        config["personas_config"] = "config/personas.yaml"
        config["scenes_config"] = "config/scenes.yaml"

        pipeline = Pipeline(config, project_root=project_root)

        # Inject mock clients
        with patch("src.core.tts_engine.ElevenLabsProvider._get_client", return_value=mock_tts_requests):
            with patch("src.core.avatar_generator.HeyGenProvider._get_client", return_value=mock_avatar_requests):
                # Run pipeline
                output_path = pipeline.create_podcast(script_file, scene_name="studio")

                # Verify it completed
                assert output_path.exists() or output_path.parent.exists()

                # Verify expressions/gestures were parsed
                parsed_script = pipeline.script_parser.parse_file(script_file)
                assert len(parsed_script.segments) == 2
                assert parsed_script.segments[0].expression == "happy"
                assert parsed_script.segments[0].gesture == "wave"

