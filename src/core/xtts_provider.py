"""
Coqui XTTS-v3 local TTS provider.

XTTS-v3 is a high-quality local TTS model with voice cloning capabilities.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import time

from src.core.tts_provider_base import TTSProvider


class XTTSProvider(TTSProvider):
    """Coqui XTTS-v3 local GPU-based TTS provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize XTTS provider."""
        super().__init__(config)
        
        # XTTS installation path (can be absolute or relative to project root)
        self.xtts_path = Path(config.get("xtts_path", "~/xtts")).expanduser()
        
        # Check if path is relative and resolve it
        if not self.xtts_path.is_absolute():
            # Try to find project root (go up from src/core)
            project_root = Path(__file__).parent.parent.parent
            self.xtts_path = project_root / self.xtts_path
        
        # Python executable (use venv if available, otherwise system Python)
        self.python_exec = config.get("python_exec", "python")
        if (self.xtts_path / "venv" / "bin" / "python").exists():
            self.python_exec = str(self.xtts_path / "venv" / "bin" / "python")
        elif (self.xtts_path / "venv" / "Scripts" / "python.exe").exists():
            self.python_exec = str(self.xtts_path / "venv" / "Scripts" / "python.exe")
        
        # Model name (default to XTTS-v2, more stable than v3)
        self.model_name = config.get("model_name", "tts_models/multilingual/multi-dataset/xtts_v2")
        
        # Output directory for TTS results
        self.output_dir = Path(config.get("output_dir", tempfile.mkdtemp(prefix="xtts_")))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache TTS instance to avoid reloading model (PERFORMANCE CRITICAL)
        self._tts_instance = None
        self._tts_model_name = None

    def is_available(self) -> bool:
        """Check if XTTS is available."""
        # Check if TTS library is available
        try:
            # Try importing TTS directly
            import sys
            import importlib.util
            
            # Check if TTS can be imported
            spec = importlib.util.find_spec("TTS")
            if spec is None:
                return False
            
            # Try importing
            try:
                import TTS
                # Check if API is available
                from TTS.api import TTS as TTSAPI
                return True
            except ImportError:
                return False
                
        except Exception:
            return False

    def generate(self, text: str, voice_id: str, **kwargs) -> tuple[bytes, float]:
        """
        Generate audio using XTTS-v3.

        Args:
            text: Text to convert to speech
            voice_id: Voice identifier (can be reference audio path or speaker name)
            **kwargs: Additional parameters:
                - reference_audio: Path to reference audio for voice cloning
                - language: Language code (default: "en")
                - output_path: Output audio path

        Returns:
            Tuple of (audio_bytes, duration_seconds)

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Get reference audio for voice cloning
        reference_audio = kwargs.get("reference_audio")
        if not reference_audio:
            # Try to resolve voice_id as audio path
            if Path(voice_id).exists():
                reference_audio = Path(voice_id)
            else:
                raise ValueError(
                    f"XTTS requires 'reference_audio' parameter for voice cloning. "
                    f"voice_id '{voice_id}' is not a valid file path. "
                    f"Please provide reference_audio in kwargs."
                )
        
        if not Path(reference_audio).exists():
            raise ValueError(f"Reference audio not found: {reference_audio}")
        
        # Get language
        language = kwargs.get("language", "en")
        
        # Generate output path
        output_path = kwargs.get("output_path")
        if not output_path:
            # Generate output filename
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_filename = f"xtts_{text_hash}.wav"
            output_path = self.output_dir / output_filename
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use TTS library directly (no subprocess - more reliable)
        try:
            from TTS.api import TTS
            import torch
            
            # CRITICAL: Reuse TTS instance if model hasn't changed (avoids slow reload)
            if self._tts_instance is None or self._tts_model_name != self.model_name:
                print(f"[INFO] Loading XTTS-v2 model: {self.model_name} (this may take a moment)")
                use_gpu = torch.cuda.is_available()
                print(f"[INFO] Using device: {'CUDA (GPU)' if use_gpu else 'CPU'}")
                
                # Initialize on CPU first (faster), then move to GPU
                self._tts_instance = TTS(self.model_name, gpu=False)
                
                if use_gpu:
                    print("[INFO] Moving XTTS model to GPU for fast generation...")
                    self._tts_instance.to("cuda")
                    print("[INFO] XTTS model loaded on GPU - ready for generation")
                else:
                    print("[WARN] GPU not available - XTTS will be slow on CPU")
                
                self._tts_model_name = self.model_name
            else:
                print("[INFO] Reusing cached XTTS model instance (fast)")
            
            tts = self._tts_instance
            
            # Generate speech directly
            print(f"[INFO] Generating audio (text length: {len(text)} chars)...")
            tts.tts_to_file(
                text=text,
                speaker_wav=str(Path(reference_audio).absolute()),
                language=language,
                file_path=str(output_path.absolute())
            )
            
            # Verify output file exists
            if not output_path.exists():
                raise RuntimeError(f"XTTS did not generate output file: {output_path}")
            
            # Read audio file
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            # Get duration
            try:
                from pydub import AudioSegment
                audio_file = AudioSegment.from_file(str(output_path))
                duration = len(audio_file) / 1000.0
            except Exception:
                # Estimate duration (rough: ~150 words per minute)
                words = len(text.split())
                duration = (words / 150.0) * 60.0
            
            return audio_bytes, duration
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("XTTS generation timed out (5 minutes)")
        except FileNotFoundError:
            raise RuntimeError(
                f"XTTS Python executable not found: {self.python_exec}. "
                f"Please ensure Coqui TTS is installed: pip install TTS"
            )
        except Exception as e:
            raise RuntimeError(f"XTTS generation failed: {e}")

