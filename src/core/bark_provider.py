"""
Bark local TTS provider.

Bark is an expressive TTS model that can generate music, sound effects, and natural speech.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import time

from src.core.tts_provider_base import TTSProvider


class BarkProvider(TTSProvider):
    """Bark local GPU-based TTS provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Bark provider."""
        super().__init__(config)
        
        # Bark installation path
        self.bark_path = Path(config.get("bark_path", "~/bark")).expanduser()
        
        # Check if path is relative and resolve it
        if not self.bark_path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            self.bark_path = project_root / self.bark_path
        
        # Python executable
        self.python_exec = config.get("python_exec", "python")
        if (self.bark_path / "venv" / "bin" / "python").exists():
            self.python_exec = str(self.bark_path / "venv" / "bin" / "python")
        elif (self.bark_path / "venv" / "Scripts" / "python.exe").exists():
            self.python_exec = str(self.bark_path / "venv" / "Scripts" / "python.exe")
        
        # Output directory
        self.output_dir = Path(config.get("output_dir", tempfile.mkdtemp(prefix="bark_")))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        """Check if Bark is available."""
        try:
            result = subprocess.run(
                [self.python_exec, "-c", "import bark; print('OK')"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        
        # Check GPU availability
        try:
            result = subprocess.run(
                [self.python_exec, "-c", "import torch; print(torch.cuda.is_available())"],
                capture_output=True,
                timeout=10
            )
        except Exception:
            pass
        
        return True

    def generate(self, text: str, voice_id: Optional[str] = None, **kwargs) -> tuple[bytes, float]:
        """
        Generate audio using Bark.

        Args:
            text: Text to convert to speech
            voice_id: Voice preset name (e.g., "v2/en_speaker_0") - can be in kwargs instead
            **kwargs: Additional parameters:
                - output_path: Output audio path
                - history_prompt: Voice history prompt for cloning
                - voice_id: Voice preset name (alternative to positional arg)

        Returns:
            Tuple of (audio_bytes, duration_seconds)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Get voice_id from kwargs if not provided positionally
        if voice_id is None:
            voice_id = kwargs.pop("voice_id", None)
        
        # Get output path
        output_path = kwargs.get("output_path")
        if not output_path:
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_filename = f"bark_{text_hash}.wav"
            output_path = self.output_dir / output_filename
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use Bark library directly (no subprocess - more reliable)
        try:
            from bark import SAMPLE_RATE, generate_audio, preload_models
            from scipy.io.wavfile import write as write_wav
            
            self._report_progress("Bark: Initializing generation...", 0.0)
            
            # Preload models (first time only, cached)
            if not hasattr(self, '_models_loaded'):
                self._report_progress("Bark: Loading models (first time, may take a moment)...", 0.1)
                preload_models()
                self._models_loaded = True
                self._report_progress("Bark: Models loaded", 0.2)
            else:
                self._report_progress("Bark: Using cached models", 0.1)
            
            # Generate audio directly
            # Bark needs None or a valid history prompt, not a string
            history_prompt = kwargs.get("history_prompt", None)
            
            self._report_progress(f"Bark: Generating audio (text length: {len(text)} chars)...", 0.3)
            
            # If no history_prompt provided, use None (Bark will use default voice)
            # Bark shows progress bars internally, but we can't easily capture them
            # So we'll report progress at key stages
            audio_array = generate_audio(
                text,
                history_prompt=history_prompt,  # None is valid, will use default
            )
            
            self._report_progress("Bark: Audio generated, saving file...", 0.9)
            
            # Save audio
            write_wav(str(output_path), SAMPLE_RATE, audio_array)
            
            if not output_path.exists():
                self._report_progress("Bark: Output file not found", 1.0)
                raise RuntimeError(f"Bark did not generate output file: {output_path}")
            
            # Read audio file
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            # Get duration
            try:
                from pydub import AudioSegment
                audio_file = AudioSegment.from_file(str(output_path))
                duration = len(audio_file) / 1000.0
            except Exception:
                # Estimate duration
                words = len(text.split())
                duration = (words / 150.0) * 60.0
            
            self._report_progress(f"Bark: Generation complete ({duration:.2f}s)", 1.0)
            
            return audio_bytes, duration
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Bark generation timed out (10 minutes)")
        except FileNotFoundError:
            raise RuntimeError(
                f"Bark Python executable not found: {self.python_exec}. "
                f"Please ensure Bark is installed: pip install bark"
            )
        except Exception as e:
            raise RuntimeError(f"Bark generation failed: {e}")

