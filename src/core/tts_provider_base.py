"""
Base TTS Provider class.

Separated to avoid circular imports.
"""

from typing import Dict, Any, Optional, Callable


class TTSProvider:
    """Base class for TTS providers."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize TTS provider with configuration."""
        self.config = config
        self.progress_callback: Optional[Callable[[str, float], None]] = None

    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """
        Set progress callback function.
        
        Args:
            callback: Function that takes (message: str, progress: float) where progress is 0.0-1.0
        """
        self.progress_callback = callback

    def _report_progress(self, message: str, progress: float = None):
        """Report progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(message, progress)

    def generate(self, text: str, voice_id: str, **kwargs) -> tuple[bytes, float]:
        """
        Generate audio from text.

        Args:
            text: Text to convert to speech
            voice_id: Voice identifier
            **kwargs: Additional provider-specific parameters

        Returns:
            Tuple of (audio_bytes, duration_seconds)

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        raise NotImplementedError("Subclass must implement generate()")

    def is_available(self) -> bool:
        """
        Check if provider is available (dependencies installed, API keys configured).

        Returns:
            True if provider can be used
        """
        return False

