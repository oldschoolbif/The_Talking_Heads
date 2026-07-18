"""
Unit tests for audio mixer.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.core.audio_mixer import AudioMixer
from src.core.tts_engine import AudioSegment
from src.core.script_parser import ScriptSegment


class TestAudioMixer:
    """Test cases for AudioMixer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mixer = AudioMixer()

    def test_init_with_output_dir(self, tmp_path):
        """Test initialization with custom output directory."""
        output_dir = tmp_path / "audio_output"
        mixer = AudioMixer(output_dir=output_dir)

        assert mixer.output_dir == output_dir
        assert output_dir.exists()

    def test_init_without_output_dir(self):
        """Test initialization with default output directory."""
        mixer = AudioMixer()
        assert mixer.output_dir.exists()

    def test_mix_persona_tracks_empty_segments(self):
        """Test mixing with empty segments raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            self.mixer.mix_persona_tracks([])

    def test_mix_persona_tracks_missing_file(self, tmp_path):
        """Test mixing with missing audio file raises ValueError."""
        segment = AudioSegment(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            audio_path=tmp_path / "nonexistent.mp3",
            duration=1.0,
            provider="elevenlabs",
        )

        with pytest.raises(ValueError, match="Audio file not found"):
            self.mixer.mix_persona_tracks([segment])

    @patch("pydub.AudioSegment")
    def test_mix_persona_tracks_single_segment(self, mock_pydub_class, tmp_path):
        """Test mixing a single audio segment."""
        # Create mock audio file
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segment = AudioSegment(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            audio_path=audio_file,
            duration=1.0,
            provider="elevenlabs",
        )

        # Mock pydub
        mock_audio_seg = Mock()
        mock_audio_seg.dBFS = -15.0
        mock_audio_seg.apply_gain.return_value = mock_audio_seg
        mock_pydub_class.from_file.return_value = mock_audio_seg

        mixer = AudioMixer(output_dir=tmp_path)
        output_path = mixer.mix_persona_tracks(
            [segment], output_filename="output.mp3", output_dir=tmp_path
        )

        assert output_path.parent.exists()

    @patch("pydub.AudioSegment")
    def test_mix_persona_tracks_multiple_segments(self, mock_pydub_class, tmp_path):
        """Test mixing multiple audio segments."""
        # Create mock audio files
        audio1 = tmp_path / "audio1.mp3"
        audio2 = tmp_path / "audio2.mp3"
        audio1.write_bytes(b"fake_audio_data_1")
        audio2.write_bytes(b"fake_audio_data_2")

        segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello"),
                audio_path=audio1,
                duration=1.0,
                provider="elevenlabs",
            ),
            AudioSegment(
                segment=ScriptSegment(persona="BOB", text="Hi there"),
                audio_path=audio2,
                duration=1.5,
                provider="elevenlabs",
            ),
        ]

        # Mock pydub - need to support sum() operation
        mock_audio_seg = Mock()
        mock_audio_seg.dBFS = -15.0
        mock_audio_seg.apply_gain.return_value = mock_audio_seg
        # Make sum() work by making the mock return itself when added
        mock_audio_seg.__add__ = Mock(return_value=mock_audio_seg)
        mock_audio_seg.__radd__ = Mock(return_value=mock_audio_seg)  # Support 0 + mock
        mock_pydub_class.from_file.return_value = mock_audio_seg
        mock_pydub_class.silent.return_value = Mock()

        mixer = AudioMixer(output_dir=tmp_path)
        output_path = mixer.mix_persona_tracks(segments, output_filename="output.mp3")

        assert output_path.parent.exists()

    @patch("pydub.AudioSegment")
    def test_mix_persona_tracks_with_padding(self, mock_pydub_class, tmp_path):
        """Test mixing with padding between segments."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello"),
                audio_path=audio_file,
                duration=1.0,
                provider="elevenlabs",
            ),
            AudioSegment(
                segment=ScriptSegment(persona="BOB", text="Hi"),
                audio_path=audio_file,
                duration=1.0,
                provider="elevenlabs",
            ),
        ]

        # Mock pydub - need to support sum() operation
        mock_audio_seg = Mock()
        mock_audio_seg.dBFS = -15.0
        mock_audio_seg.apply_gain.return_value = mock_audio_seg
        mock_audio_seg.__add__ = Mock(return_value=mock_audio_seg)
        mock_audio_seg.__radd__ = Mock(return_value=mock_audio_seg)  # Support 0 + mock
        mock_silence = Mock()
        mock_silence.__add__ = Mock(return_value=mock_audio_seg)
        mock_silence.__radd__ = Mock(return_value=mock_audio_seg)
        mock_pydub_class.from_file.return_value = mock_audio_seg
        mock_pydub_class.silent.return_value = mock_silence

        mixer = AudioMixer(output_dir=tmp_path)
        output_path = mixer.mix_persona_tracks(
            segments, output_filename="output.mp3", padding_seconds=0.5
        )

        # Verify silence was created
        mock_pydub_class.silent.assert_called()
        assert output_path.parent.exists()

    @patch("pydub.AudioSegment")
    def test_mix_persona_tracks_without_normalization(self, mock_pydub_class, tmp_path):
        """Test mixing without volume normalization."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segment = AudioSegment(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            audio_path=audio_file,
            duration=1.0,
            provider="elevenlabs",
        )

        # Mock pydub
        mock_audio_seg = Mock()
        mock_pydub_class.from_file.return_value = mock_audio_seg

        mixer = AudioMixer(output_dir=tmp_path)
        output_path = mixer.mix_persona_tracks(
            [segment], output_filename="output.mp3", normalize_volume=False
        )

        # Verify apply_gain was not called
        mock_audio_seg.apply_gain.assert_not_called()
        assert output_path.parent.exists()

    @patch("builtins.__import__")
    def test_mix_persona_tracks_pydub_not_installed(self, mock_import, tmp_path):
        """Test that missing pydub raises RuntimeError."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segment = AudioSegment(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            audio_path=audio_file,
            duration=1.0,
            provider="elevenlabs",
        )

        def import_side_effect(name, *args, **kwargs):
            if name == "pydub":
                raise ImportError("No module named 'pydub'")
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_side_effect

        with pytest.raises(RuntimeError, match="pydub is required"):
            self.mixer.mix_persona_tracks([segment])

    @patch("pydub.AudioSegment")
    def test_mix_with_timing(self, mock_pydub_class, tmp_path):
        """Test mixing with timing preservation."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello", start_time=0.0, end_time=1.0),
                audio_path=audio_file,
                duration=1.0,
                provider="elevenlabs",
            ),
            AudioSegment(
                segment=ScriptSegment(persona="BOB", text="Hi", start_time=2.0, end_time=3.5),
                audio_path=audio_file,
                duration=1.5,
                provider="elevenlabs",
            ),
        ]

        # Mock pydub - need to support sum() operation
        mock_audio_seg = Mock()
        mock_audio_seg.dBFS = -15.0
        mock_audio_seg.__len__ = Mock(return_value=1000)  # 1 second in ms
        mock_audio_seg.apply_gain.return_value = mock_audio_seg
        mock_audio_seg.__add__ = Mock(return_value=mock_audio_seg)
        mock_audio_seg.__radd__ = Mock(return_value=mock_audio_seg)  # Support 0 + mock
        mock_silence = Mock()
        mock_silence.__add__ = Mock(return_value=mock_audio_seg)
        mock_silence.__radd__ = Mock(return_value=mock_audio_seg)
        mock_pydub_class.from_file.return_value = mock_audio_seg
        mock_pydub_class.silent.return_value = mock_silence

        mixer = AudioMixer(output_dir=tmp_path)
        output_path, timing_info = mixer.mix_with_timing(
            segments, output_filename="output.mp3", preserve_timing=True
        )

        assert output_path.parent.exists()
        assert len(timing_info) == 2
        assert timing_info[0]["persona"] == "ALICE"
        assert timing_info[1]["persona"] == "BOB"
        assert timing_info[0]["start_time"] == 0.0
        # Should have silence between segments
        assert timing_info[1]["start_time"] >= 1.0

    @patch("pydub.AudioSegment")
    def test_mix_with_timing_no_preserve(self, mock_pydub_class, tmp_path):
        """Test mixing with timing preservation disabled."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello", start_time=0.0, end_time=1.0),
                audio_path=audio_file,
                duration=1.0,
                provider="elevenlabs",
            ),
        ]

        # Mock pydub
        mock_audio_seg = Mock()
        mock_audio_seg.dBFS = -15.0
        mock_audio_seg.__len__ = Mock(return_value=1000)
        mock_audio_seg.apply_gain.return_value = mock_audio_seg
        mock_pydub_class.from_file.return_value = mock_audio_seg

        mixer = AudioMixer(output_dir=tmp_path)
        output_path, timing_info = mixer.mix_with_timing(
            segments, output_filename="output.mp3", preserve_timing=False
        )

        assert output_path.parent.exists()
        assert len(timing_info) == 1

    def test_get_total_duration_empty(self):
        """Test getting total duration of empty segments."""
        duration = self.mixer.get_total_duration([])
        assert duration == 0.0

    @patch("pydub.AudioSegment")
    def test_get_total_duration_with_files(self, mock_pydub_class, tmp_path):
        """Test getting total duration from actual files."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello"),
                audio_path=audio_file,
                duration=1.0,
                provider="elevenlabs",
            ),
            AudioSegment(
                segment=ScriptSegment(persona="BOB", text="Hi"),
                audio_path=audio_file,
                duration=1.5,
                provider="elevenlabs",
            ),
        ]

        # Mock pydub
        mock_audio_seg = Mock()
        mock_audio_seg.__len__ = Mock(return_value=2000)  # 2 seconds in ms
        mock_pydub_class.from_file.return_value = mock_audio_seg

        duration = self.mixer.get_total_duration(segments)
        assert duration == 4.0  # 2 segments * 2 seconds each

    @patch("builtins.__import__")
    def test_get_total_duration_fallback(self, mock_import, tmp_path):
        """Test getting total duration with fallback when pydub unavailable."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello"),
                audio_path=audio_file,
                duration=1.0,
                provider="elevenlabs",
            ),
            AudioSegment(
                segment=ScriptSegment(persona="BOB", text="Hi"),
                audio_path=audio_file,
                duration=1.5,
                provider="elevenlabs",
            ),
        ]

        # Mock ImportError for pydub
        def import_side_effect(name, *args, **kwargs):
            if name == "pydub":
                raise ImportError("No module named 'pydub'")
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_side_effect

        duration = self.mixer.get_total_duration(segments)
        # Should fallback to sum of segment durations
        assert duration == 2.5

    def test_get_total_duration_missing_files(self, tmp_path):
        """Test getting total duration when files don't exist."""
        segments = [
            AudioSegment(
                segment=ScriptSegment(persona="ALICE", text="Hello"),
                audio_path=tmp_path / "nonexistent.mp3",
                duration=1.0,
                provider="elevenlabs",
            ),
        ]

        # Should fallback to stored duration
        duration = self.mixer.get_total_duration(segments)
        assert duration == 1.0

    @patch("pydub.AudioSegment")
    def test_mix_persona_tracks_export_error(self, mock_pydub_class, tmp_path):
        """Test handling of export errors."""
        audio_file = tmp_path / "test_audio.mp3"
        audio_file.write_bytes(b"fake_audio_data")

        segment = AudioSegment(
            segment=ScriptSegment(persona="ALICE", text="Hello"),
            audio_path=audio_file,
            duration=1.0,
            provider="elevenlabs",
        )

        # Mock pydub with export error
        mock_audio_seg = Mock()
        mock_audio_seg.dBFS = -15.0
        mock_audio_seg.apply_gain.return_value = mock_audio_seg
        mock_audio_seg.export.side_effect = Exception("Export failed")
        mock_pydub_class.from_file.return_value = mock_audio_seg

        with pytest.raises(RuntimeError, match="Audio mixing failed"):
            self.mixer.mix_persona_tracks([segment], output_dir=tmp_path)

