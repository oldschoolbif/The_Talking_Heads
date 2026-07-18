"""
Audio Mixer for The Talking Heads

Concatenates and mixes audio segments from multiple personas.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import os

from src.core.tts_engine import AudioSegment


class AudioMixer:
    """Mixes and concatenates audio segments from multiple personas."""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize audio mixer.

        Args:
            output_dir: Directory for output files (default: current directory)
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def mix_persona_tracks(
        self,
        audio_segments: List[AudioSegment],
        output_filename: str = "mixed_audio.mp3",
        padding_seconds: float = 0.0,
        normalize_volume: bool = True,
        target_dBFS: float = -20.0,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """
        Concatenate persona audio tracks into a single mixed audio file.

        Args:
            audio_segments: List of audio segments to mix
            output_filename: Name for the output audio file
            padding_seconds: Seconds of silence to add between segments (default: 0.0)
            normalize_volume: Whether to normalize volume across segments (default: True)
            target_dBFS: Target volume in dBFS for normalization (default: -20.0)

        Returns:
            Path to the generated mixed audio file

        Raises:
            ValueError: If audio_segments is empty or files don't exist
            RuntimeError: If audio processing fails
        """
        if not audio_segments:
            raise ValueError("audio_segments cannot be empty")

        # Verify all audio files exist
        for seg in audio_segments:
            if not seg.audio_path.exists():
                raise ValueError(f"Audio file not found: {seg.audio_path}")

        try:
            from pydub import AudioSegment as PydubAudioSegment
        except ImportError:
            raise RuntimeError(
                "pydub is required for audio mixing. Install it with: pip install pydub"
            ) from None

        try:
            # Load all audio segments
            pydub_segments = []
            for seg in audio_segments:
                audio_file = PydubAudioSegment.from_file(str(seg.audio_path))
                
                # Normalize volume if requested
                if normalize_volume:
                    change_in_dBFS = target_dBFS - audio_file.dBFS
                    audio_file = audio_file.apply_gain(change_in_dBFS)
                
                pydub_segments.append(audio_file)

                # Add padding between segments (except after last one)
                if padding_seconds > 0 and seg != audio_segments[-1]:
                    silence = PydubAudioSegment.silent(duration=int(padding_seconds * 1000))
                    pydub_segments.append(silence)

            # Concatenate all segments
            if len(pydub_segments) == 1:
                final_audio = pydub_segments[0]
            else:
                final_audio = sum(pydub_segments)

            # Export to file
            output_dir = output_dir or self.output_dir
            output_path = output_dir / output_filename
            
            # Determine format from extension
            format_type = output_filename.split(".")[-1] if "." in output_filename else "mp3"
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            final_audio.export(str(output_path), format=format_type)

            return output_path

        except Exception as e:
            raise RuntimeError(f"Audio mixing failed: {e}") from e

    def mix_with_timing(
        self,
        audio_segments: List[AudioSegment],
        output_filename: str = "mixed_audio.mp3",
        preserve_timing: bool = True,
        normalize_volume: bool = True,
    ) -> tuple[Path, List[Dict[str, Any]]]:
        """
        Mix audio segments while preserving timing information for video sync.

        Args:
            audio_segments: List of audio segments to mix
            output_filename: Name for the output audio file
            preserve_timing: Whether to preserve original timing (add silence to match)
            normalize_volume: Whether to normalize volume across segments

        Returns:
            Tuple of (output_path, timing_info) where timing_info is a list of dicts
            with start_time, end_time, and persona for each segment

        Raises:
            ValueError: If audio_segments is empty or files don't exist
            RuntimeError: If audio processing fails
        """
        if not audio_segments:
            raise ValueError("audio_segments cannot be empty")

        try:
            from pydub import AudioSegment as PydubAudioSegment
        except ImportError:
            raise RuntimeError(
                "pydub is required for audio mixing. Install it with: pip install pydub"
            ) from None

        # Build timing information
        timing_info = []
        current_time = 0.0

        try:
            pydub_segments = []
            
            for seg in audio_segments:
                if not seg.audio_path.exists():
                    raise ValueError(f"Audio file not found: {seg.audio_path}")

                # Load audio
                audio_file = PydubAudioSegment.from_file(str(seg.audio_path))
                
                # Normalize volume if requested
                if normalize_volume:
                    target_dBFS = -20.0
                    change_in_dBFS = target_dBFS - audio_file.dBFS
                    audio_file = audio_file.apply_gain(change_in_dBFS)

                # If preserving timing, add silence before segment if needed
                if preserve_timing and seg.segment.start_time > current_time:
                    silence_duration = (seg.segment.start_time - current_time) * 1000  # Convert to ms
                    silence = PydubAudioSegment.silent(duration=int(silence_duration))
                    pydub_segments.append(silence)
                    current_time = seg.segment.start_time

                # Add the audio segment
                pydub_segments.append(audio_file)

                # Record timing
                segment_duration = len(audio_file) / 1000.0  # Convert ms to seconds
                timing_info.append({
                    "start_time": current_time,
                    "end_time": current_time + segment_duration,
                    "persona": seg.segment.persona,
                    "segment_index": len(timing_info),
                })

                current_time += segment_duration

            # Concatenate all segments
            if len(pydub_segments) == 1:
                final_audio = pydub_segments[0]
            else:
                final_audio = sum(pydub_segments)

            # Export to file
            output_path = self.output_dir / output_filename
            format_type = output_filename.split(".")[-1] if "." in output_filename else "mp3"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            final_audio.export(str(output_path), format=format_type)

            return output_path, timing_info

        except Exception as e:
            raise RuntimeError(f"Audio mixing with timing failed: {e}") from e

    def get_total_duration(self, audio_segments: List[AudioSegment]) -> float:
        """
        Calculate total duration of all audio segments.

        Args:
            audio_segments: List of audio segments

        Returns:
            Total duration in seconds
        """
        if not audio_segments:
            return 0.0

        try:
            from pydub import AudioSegment as PydubAudioSegment
        except ImportError:
            # Fallback: sum segment durations
            return sum(seg.duration for seg in audio_segments)

        total_duration = 0.0
        for seg in audio_segments:
            if seg.audio_path.exists():
                try:
                    audio_file = PydubAudioSegment.from_file(str(seg.audio_path))
                    total_duration += len(audio_file) / 1000.0  # Convert ms to seconds
                except Exception:
                    # Fallback to stored duration
                    total_duration += seg.duration
            else:
                total_duration += seg.duration

        return total_duration

