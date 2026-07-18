"""
Base Avatar Provider class.

Separated to avoid circular imports.
"""

from typing import Dict, Optional, Any
from pathlib import Path


class AvatarProvider:
    """Base class for avatar providers."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize avatar provider with configuration."""
        self.config = config
        self.progress_callback: Optional[callable] = None

    def set_progress_callback(self, callback: callable):
        """Set progress callback function.
        
        Args:
            callback: Function that takes (message: str, progress: float) where progress is 0.0-1.0
        """
        self.progress_callback = callback

    def _report_progress(self, message: str, progress: float = None):
        """Report progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(message, progress)

    def generate(
        self, audio_path: Path, avatar_id: str, expression: Optional[str] = None, gesture: Optional[str] = None, **kwargs
    ) -> tuple[Path, float]:
        """
        Generate avatar video from audio.

        Args:
            audio_path: Path to audio file
            avatar_id: Avatar identifier
            expression: Expression to apply (optional)
            gesture: Gesture to apply (optional)
            **kwargs: Additional provider-specific parameters

        Returns:
            Tuple of (video_path, duration_seconds)

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

