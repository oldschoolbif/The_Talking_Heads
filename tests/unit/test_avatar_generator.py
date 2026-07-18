"""
Unit tests for avatar generator.
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.core.avatar_generator import (
    AvatarGenerator,
    AvatarVideo,
    AvatarProvider,
    HeyGenProvider,
    DIDProvider,
)
from src.core.script_parser import ScriptSegment
from src.core.persona_engine import Persona, VoiceConfig, AvatarConfig, ExpressionConfig, GestureConfig
from src.core.tts_engine import AudioSegment


class TestAvatarProvider:
    """Test cases for base AvatarProvider."""

    def test_provider_not_implemented(self):
        """Test that base provider raises NotImplementedError."""
        provider = AvatarProvider({})
        with pytest.raises(NotImplementedError):
            provider.generate(Path("test.mp3"), "avatar_123")


class TestHeyGenProvider:
    """Test cases for HeyGenProvider."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {"api_key": "test_key", "base_url": "https://api.heygen.com/v1"}

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        provider = HeyGenProvider(self.config)
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        provider = HeyGenProvider({})
        assert provider.is_available() is False

    def test_generate_missing_key(self):
        """Test generation without API key."""
        provider = HeyGenProvider({})
        with pytest.raises(ValueError, match="API key is required"):
            provider.generate(Path("test.mp3"), "avatar_123")

    def test_generate_missing_audio_file(self, tmp_path):
        """Test generation with missing audio file."""
        provider = HeyGenProvider(self.config)
        with pytest.raises(ValueError, match="Audio file not found"):
            provider.generate(tmp_path / "nonexistent.mp3", "avatar_123")

    def test_generate_success(self, tmp_path):
        """Test successful avatar generation."""
        # Create test audio file
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        # Mock API responses
        mock_requests = Mock()
        mock_response_create = Mock()
        mock_response_create.json.return_value = {"task_id": "task_123"}
        mock_response_create.raise_for_status = Mock()

        mock_response_status = Mock()
        mock_response_status.json.return_value = {"status": "completed", "video_url": "https://example.com/video.mp4"}
        mock_response_status.raise_for_status = Mock()

        mock_response_video = Mock()
        mock_response_video.content = b"fake_video_data"
        mock_response_video.raise_for_status = Mock()

        mock_requests.post.return_value = mock_response_create
        mock_requests.get.side_effect = [mock_response_status, mock_response_video]

        provider = HeyGenProvider(self.config)
        provider._client = mock_requests

        output_path = tmp_path / "output.mp4"
        video_path, duration = provider.generate(audio_file, "avatar_123", output_path=output_path)

        assert video_path == output_path
        assert duration >= 0.0
        mock_requests.post.assert_called_once()

    @patch("src.core.avatar_generator.time.sleep")
    def test_poll_task_status_timeout(self, mock_sleep, tmp_path):
        """Test polling timeout handling."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        mock_requests = Mock()
        mock_response_create = Mock()
        mock_response_create.json.return_value = {"task_id": "task_123"}
        mock_response_create.raise_for_status = Mock()

        mock_response_status = Mock()
        mock_response_status.json.return_value = {"status": "processing"}
        mock_response_status.raise_for_status = Mock()

        mock_requests.post.return_value = mock_response_create
        mock_requests.get.return_value = mock_response_status

        provider = HeyGenProvider(self.config)
        provider._client = mock_requests

        with pytest.raises(RuntimeError, match="timed out"):
            provider.generate(audio_file, "avatar_123", output_path=tmp_path / "output.mp4")


class TestDIDProvider:
    """Test cases for DIDProvider."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {"api_key": "test_key", "base_url": "https://api.d-id.com"}

    def test_is_available_with_key(self):
        """Test availability check with API key."""
        provider = DIDProvider(self.config)
        with patch.dict("sys.modules", {"requests": MagicMock()}):
            assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test availability check without API key."""
        provider = DIDProvider({})
        assert provider.is_available() is False

    def test_generate_missing_key(self):
        """Test generation without API key."""
        provider = DIDProvider({})
        with pytest.raises(ValueError, match="API key is required"):
            provider.generate(Path("test.mp3"), "avatar_123")


class TestAvatarGenerator:
    """Test cases for AvatarGenerator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "avatar": {"engine": "heygen", "style": "cartoon"},
            "api": {
                "heygen": {"api_key": "test_key", "base_url": "https://api.heygen.com/v1"},
                "did": {"api_key": "test_key", "base_url": "https://api.d-id.com"},
            },
            "storage": {"outputs_dir": "outputs"},
        }

    def test_init_with_output_dir(self, tmp_path):
        """Test initialization with custom output directory."""
        output_dir = tmp_path / "avatar_output"
        generator = AvatarGenerator(self.config, output_dir=output_dir)

        assert generator.output_dir == output_dir
        assert output_dir.exists()

    def test_init_without_output_dir(self, tmp_path):
        """Test initialization with default output directory."""
        generator = AvatarGenerator(self.config)
        assert generator.output_dir.exists()

    def test_get_provider_unsupported(self):
        """Test getting unsupported provider."""
        generator = AvatarGenerator(self.config)

        with pytest.raises(ValueError, match="Unsupported avatar engine"):
            generator._get_provider("unsupported")

    def test_generate_persona_avatar_missing_audio(self, tmp_path):
        """Test generating avatar with missing audio file."""
        persona = Persona(
            key="alice",
            name="Alice",
            voice=VoiceConfig(engine="elevenlabs", voice_id="voice_123"),
            avatar=AvatarConfig(engine="heygen", avatar_id="avatar_123"),
        )

        generator = AvatarGenerator(self.config, output_dir=tmp_path)

        with pytest.raises(ValueError, match="Audio file not found"):
            generator.generate_persona_avatar(persona, tmp_path / "nonexistent.mp3")

    def test_generate_persona_avatar_success(self, tmp_path):
        """Test successful avatar generation for persona."""
        # Create test audio file
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        persona = Persona(
            key="alice",
            name="Alice",
            voice=VoiceConfig(engine="elevenlabs", voice_id="voice_123"),
            avatar=AvatarConfig(
                engine="heygen",
                avatar_id="avatar_123",
                expressions=ExpressionConfig(enabled=True, default="happy"),
            ),
        )

        # Mock API responses
        mock_requests = Mock()
        mock_response_create = Mock()
        mock_response_create.json.return_value = {"task_id": "task_123"}
        mock_response_create.raise_for_status = Mock()

        mock_response_status = Mock()
        mock_response_status.json.return_value = {"status": "completed", "video_url": "https://example.com/video.mp4"}
        mock_response_status.raise_for_status = Mock()

        mock_response_video = Mock()
        mock_response_video.content = b"fake_video_data"
        mock_response_video.raise_for_status = Mock()

        mock_requests.post.return_value = mock_response_create
        mock_requests.get.side_effect = [mock_response_status, mock_response_video]

        generator = AvatarGenerator(self.config, output_dir=tmp_path)
        generator.providers["heygen"]._client = mock_requests

        avatar_video = generator.generate_persona_avatar(persona, audio_file)

        assert avatar_video.video_path.exists()
        assert avatar_video.persona == "Alice"
        assert avatar_video.provider == "heygen"
        assert avatar_video.expression == "happy"

    def test_generate_multiple_mismatched_lengths(self, tmp_path):
        """Test generating multiple avatars with mismatched segment lengths."""
        segments = [ScriptSegment(persona="ALICE", text="Hello")]
        audio_segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello"),
                audio_path=tmp_path / "audio1.mp3",
                duration=1.0,
                provider="elevenlabs",
            ),
            AudioSegment(
                segment=ScriptSegment(persona="BOB", text="Hi"),
                audio_path=tmp_path / "audio2.mp3",
                duration=1.0,
                provider="elevenlabs",
            ),
        ]
        personas = {}

        generator = AvatarGenerator(self.config, output_dir=tmp_path)

        with pytest.raises(ValueError, match="must have the same length"):
            generator.generate_multiple(segments, audio_segments, personas)

    def test_generate_multiple_missing_persona(self, tmp_path):
        """Test generating multiple avatars with missing persona."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segments = [ScriptSegment(persona="ALICE", text="Hello")]
        audio_segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello"),
                audio_path=audio_file,
                duration=1.0,
                provider="elevenlabs",
            ),
        ]
        personas = {}  # Empty personas dict

        generator = AvatarGenerator(self.config, output_dir=tmp_path)

        with pytest.raises(ValueError, match="not found in personas dictionary"):
            generator.generate_multiple(segments, audio_segments, personas)

    def test_avatar_video_to_dict(self):
        """Test AvatarVideo to_dict conversion."""
        segment = ScriptSegment(persona="ALICE", text="Hello!")
        avatar_video = AvatarVideo(
            segment=segment,
            video_path=Path("test.mp4"),
            duration=2.5,
            provider="heygen",
            persona="Alice",
            expression="happy",
            gesture="wave",
        )

        result = avatar_video.to_dict()

        assert result["duration"] == 2.5
        assert result["provider"] == "heygen"
        assert result["persona"] == "Alice"
        assert result["expression"] == "happy"
        assert result["gesture"] == "wave"
        assert "segment" in result
        assert "video_path" in result

