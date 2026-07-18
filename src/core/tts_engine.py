"""
TTS Engine for The Talking Heads

Generates text-to-speech audio for persona segments using multiple providers.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import os

from src.core.script_parser import ScriptSegment
from src.core.persona_engine import Persona
from src.core.tts_provider_base import TTSProvider


@dataclass
class AudioSegment:
    """Represents a generated audio segment with metadata."""

    segment: ScriptSegment
    audio_path: Path
    duration: float  # Duration in seconds
    provider: str  # TTS provider used
    cached: bool = False  # Whether this was loaded from cache

    def to_dict(self) -> Dict[str, Any]:
        """Convert audio segment to dictionary."""
        return {
            "segment": self.segment.to_dict(),
            "audio_path": str(self.audio_path),
            "duration": self.duration,
            "provider": self.provider,
            "cached": self.cached,
        }


# Import TTSProvider from base module (defined in tts_provider_base.py)
# Import provider implementations
from src.core.xtts_provider import XTTSProvider
from src.core.bark_provider import BarkProvider
from src.core.valle_provider import VALLEProvider


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize ElevenLabs provider."""
        super().__init__(config)
        self.api_key = config.get("api_key") or os.getenv("ELEVENLABS_API_KEY")
        self.base_url = config.get("base_url", "https://api.elevenlabs.io/v1")
        self._client = None

    def is_available(self) -> bool:
        """Check if ElevenLabs is available."""
        if not self.api_key:
            return False
        try:
            import requests
            return True
        except ImportError:
            return False

    def _get_client(self):
        """Get or create HTTP client."""
        if self._client is None:
            import requests
            self._client = requests
        return self._client

    def generate(self, text: str, voice_id: str, **kwargs) -> tuple[bytes, float]:
        """
        Generate audio using ElevenLabs API.

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            **kwargs: Additional parameters (model_id, stability, similarity_boost, etc.)

        Returns:
            Tuple of (audio_bytes, duration_seconds)

        Raises:
            ValueError: If API key is missing
            RuntimeError: If API request fails
        """
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required")

        if not self.is_available():
            raise RuntimeError("ElevenLabs provider is not available (requests not installed)")

        requests = self._get_client()

        url = f"{self.base_url}/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }

        # Default parameters
        data = {
            "text": text,
            "model_id": kwargs.get("model_id", "eleven_monolingual_v1"),
            "voice_settings": {
                "stability": kwargs.get("stability", 0.5),
                "similarity_boost": kwargs.get("similarity_boost", 0.75),
                "style": kwargs.get("style", 0.0),
                "use_speaker_boost": kwargs.get("use_speaker_boost", True),
            },
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()

            audio_bytes = response.content
            # Estimate duration (rough: ~150 words per minute, ~2.5 chars per word)
            # Better: use actual audio duration if available
            estimated_duration = len(text) / (150 * 2.5) * 60  # Rough estimate

            return audio_bytes, estimated_duration

        except Exception as e:
            # Handle both real requests exceptions and any other errors
            raise RuntimeError(f"ElevenLabs API request failed: {e}") from e


class AzureSpeechProvider(TTSProvider):
    """Azure Speech Service TTS provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Azure Speech provider."""
        super().__init__(config)
        self.speech_key = config.get("speech_key") or os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = config.get("speech_region") or os.getenv("AZURE_SPEECH_REGION")

    def is_available(self) -> bool:
        """Check if Azure Speech is available."""
        if not self.speech_key or not self.speech_region:
            return False
        try:
            import azure.cognitiveservices.speech as speechsdk
            return True
        except ImportError:
            return False

    def generate(self, text: str, voice_id: str, **kwargs) -> tuple[bytes, float]:
        """
        Generate audio using Azure Speech Service.

        Args:
            text: Text to convert to speech
            voice_id: Azure voice name (e.g., "en-US-AriaNeural")
            **kwargs: Additional parameters

        Returns:
            Tuple of (audio_bytes, duration_seconds)

        Raises:
            ValueError: If credentials are missing
            RuntimeError: If API request fails
        """
        if not self.speech_key or not self.speech_region:
            raise ValueError("Azure Speech key and region are required")

        if not self.is_available():
            raise RuntimeError("Azure Speech provider is not available (azure-cognitiveservices-speech not installed)")

        try:
            import azure.cognitiveservices.speech as speechsdk

            speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
            speech_config.speech_synthesis_voice_name = voice_id

            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_bytes = result.audio_data
                # Estimate duration (rough)
                estimated_duration = len(text) / (150 * 2.5) * 60
                return audio_bytes, estimated_duration
            else:
                cancellation = speechsdk.CancellationDetails(result)
                raise RuntimeError(f"Azure Speech synthesis failed: {cancellation.reason} - {cancellation.error_details}")

        except ImportError:
            raise RuntimeError("Azure Speech SDK not installed") from None
        except Exception as e:
            raise RuntimeError(f"Azure Speech API request failed: {e}") from e


class GTTSProvider(TTSProvider):
    """Google Text-to-Speech (gTTS) fallback provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize gTTS provider."""
        super().__init__(config)
        self.lang = config.get("lang", "en")
        self.slow = config.get("slow", False)

    def is_available(self) -> bool:
        """Check if gTTS is available."""
        try:
            from gtts import gTTS
            return True
        except ImportError:
            return False

    def generate(self, text: str, voice_id: str = None, **kwargs) -> tuple[bytes, float]:
        """
        Generate audio using gTTS.

        Args:
            text: Text to convert to speech
            voice_id: Not used for gTTS (uses lang parameter)
            **kwargs: Additional parameters (lang, slow)

        Returns:
            Tuple of (audio_bytes, duration_seconds)

        Raises:
            RuntimeError: If gTTS is not available or request fails
        """
        if not self.is_available():
            raise RuntimeError("gTTS provider is not available (gtts not installed)")

        try:
            from gtts import gTTS
            from io import BytesIO

            lang = kwargs.get("lang", self.lang)
            slow = kwargs.get("slow", self.slow)

            tts = gTTS(text=text, lang=lang, slow=slow)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_bytes = audio_buffer.getvalue()

            # Estimate duration
            estimated_duration = len(text) / (150 * 2.5) * 60

            return audio_bytes, estimated_duration

        except ImportError:
            raise RuntimeError("gTTS not installed") from None
        except Exception as e:
            raise RuntimeError(f"gTTS request failed: {e}") from e


class TTSEngine:
    """Main TTS engine with multi-provider support."""

    def __init__(self, config: Dict[str, Any], cache_dir: Optional[Path] = None):
        """
        Initialize TTS engine.

        Args:
            config: Configuration dictionary with TTS and API settings
            cache_dir: Directory for caching audio files (optional)
        """
        self.config = config
        self.tts_config = config.get("tts", {})
        self.api_config = config.get("api", {})

        # Setup cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            cache_dir_str = config.get("storage", {}).get("cache_dir", ".cache")
            self.cache_dir = Path(cache_dir_str) / "tts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize providers
        self.providers: Dict[str, TTSProvider] = {}
        self._init_providers()

        # Set default engine (default to Bark)
        self.engine = self.tts_config.get("engine", "bark")
        self.progress_callback: Optional[Callable[[str, float], None]] = None
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """
        Set progress callback function.
        
        Args:
            callback: Function that takes (message: str, progress: float) where progress is 0.0-1.0
        """
        self.progress_callback = callback

    def _init_providers(self):
        """Initialize available TTS providers."""
        # Local GPU-based providers (priority)
        # XTTS-v3 (default)
        xtts_config = self.config.get("xtts", {})
        self.providers["xtts"] = XTTSProvider(xtts_config)
        
        # Bark
        bark_config = self.config.get("bark", {})
        self.providers["bark"] = BarkProvider(bark_config)
        
        # VALL-E X
        valle_config = self.config.get("valle", {})
        self.providers["valle"] = VALLEProvider(valle_config)
        
        # External API providers (marked as external)
        # ElevenLabs
        elevenlabs_config = self.api_config.get("elevenlabs", {})
        self.providers["elevenlabs"] = ElevenLabsProvider(elevenlabs_config)

        # Azure Speech
        azure_config = self.api_config.get("azure", {})
        self.providers["azure"] = AzureSpeechProvider(azure_config)

        # gTTS (free but low quality)
        gtts_config = self.tts_config.get("gtts", {})
        self.providers["gtts"] = GTTSProvider(gtts_config)

    def _get_provider(self, engine: str) -> TTSProvider:
        """
        Get TTS provider by engine name.

        Args:
            engine: Engine name ("xtts", "bark", "valle", "elevenlabs", "azure", "gtts")

        Returns:
            TTSProvider instance

        Raises:
            ValueError: If engine is not supported
            RuntimeError: If provider is not available
        """
        if engine not in self.providers:
            raise ValueError(
                f"Unsupported TTS engine: {engine}. "
                f"Supported engines: {', '.join(self.providers.keys())}"
            )

        provider = self.providers[engine]
        if not provider.is_available():
            raise RuntimeError(
                f"TTS engine '{engine}' is not available. "
                f"Please check configuration and ensure all dependencies are installed. "
                f"For local providers (xtts/bark/valle): ensure models are installed and CUDA is configured. "
                f"For external providers (elevenlabs/azure): ensure API keys are configured."
            )

        return provider

    def _get_cache_key(self, text: str, voice_id: str, provider: str) -> str:
        """Generate cache key for text + voice combination."""
        key_data = f"{provider}:{voice_id}:{text}"
        return hashlib.md5(key_data.encode("utf-8")).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for cache key."""
        return self.cache_dir / f"{cache_key}.mp3"

    def _load_from_cache(self, cache_key: str) -> Optional[tuple[bytes, float]]:
        """
        Load audio from cache if available.

        Args:
            cache_key: Cache key for the audio

        Returns:
            Tuple of (audio_bytes, duration) if found, None otherwise
        """
        cache_path = self._get_cache_path(cache_key)
        metadata_path = cache_path.with_suffix(".json")

        if cache_path.exists() and metadata_path.exists():
            try:
                audio_bytes = cache_path.read_bytes()
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                duration = metadata.get("duration", 0.0)
                return audio_bytes, duration
            except Exception:
                # Cache corrupted, ignore
                return None

        return None

    def _save_to_cache(self, cache_key: str, audio_bytes: bytes, duration: float):
        """
        Save audio to cache.

        Args:
            cache_key: Cache key for the audio
            audio_bytes: Audio data to cache
            duration: Duration in seconds
        """
        cache_path = self._get_cache_path(cache_key)
        metadata_path = cache_path.with_suffix(".json")

        try:
            cache_path.write_bytes(audio_bytes)
            # Get provider name for metadata
            provider_name = self.engine
            try:
                provider = self._get_provider(provider_name)
                provider_class_name = provider.__class__.__name__
            except Exception:
                provider_class_name = "Unknown"
            metadata = {"duration": duration, "provider": provider_class_name}
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        except Exception:
            # Cache write failed, ignore
            pass

    def generate_persona_audio(
        self, persona: Persona, text: str, use_cache: bool = True, output_dir: Optional[Path] = None
    ) -> AudioSegment:
        """
        Generate audio for a persona's text.

        Args:
            persona: Persona configuration
            text: Text to convert to speech
            use_cache: Whether to use cache if available
            output_dir: Directory to save audio file (default: cache_dir)

        Returns:
            AudioSegment with audio file path and metadata

        Raises:
            RuntimeError: If audio generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        voice_id = persona.voice.voice_id
        provider_name = persona.voice.engine or self.engine

        # Get provider (no fallback - use selected provider or error)
        provider = self._get_provider(provider_name)
        
        # Set progress callback on provider if available
        if hasattr(provider, 'set_progress_callback') and self.progress_callback:
            provider.set_progress_callback(self.progress_callback)

        # Check cache
        cache_key = self._get_cache_key(text, voice_id, provider_name)
        cached = False

        if use_cache:
            cached_audio = self._load_from_cache(cache_key)
            if cached_audio:
                audio_bytes, duration = cached_audio
                cached = True
            else:
                # Generate new audio
                # For local providers (xtts, bark, valle), we need reference_audio
                generate_kwargs = {
                    "rate": persona.voice.rate,
                    "pitch": persona.voice.pitch,
                }
                
                # Add reference_audio for local providers that need voice cloning
                if provider_name in ["xtts", "bark", "valle"]:
                    # Try to find reference audio for this persona
                    reference_audio = None
                    # Check if voice_id is a file path
                    if Path(voice_id).exists():
                        reference_audio = Path(voice_id)
                    else:
                        # Try to find in common locations
                        project_root = Path(__file__).parent.parent.parent
                        possible_paths = [
                            project_root / "examples" / "personas" / "voices" / f"{persona.key.lower()}.wav",
                            project_root / "examples" / "personas" / "voices" / f"{persona.key.lower()}.mp3",
                            project_root / "examples" / "personas" / f"{persona.key.lower()}_voice.wav",
                            project_root / "examples" / "personas" / f"{persona.key.lower()}_voice.mp3",
                        ]
                        for path in possible_paths:
                            if path.exists():
                                reference_audio = path
                                break
                    
                    if reference_audio:
                        generate_kwargs["reference_audio"] = reference_audio
                    elif provider_name == "bark":
                        # Bark can use voice presets if no reference audio
                        # Set voice_id in kwargs, but don't pass it as positional arg
                        generate_kwargs["voice_id"] = voice_id or "v2/en_speaker_0"
                        voice_id = None  # Clear positional arg to avoid duplicate
                    else:
                        raise ValueError(
                            f"{provider_name.upper()} requires reference_audio for voice cloning. "
                            f"Please provide a reference audio file for persona '{persona.key}'. "
                            f"Expected location: examples/personas/voices/{persona.key.lower()}.wav"
                        )
                
                # For Bark, if voice_id is in kwargs, extract it and don't pass as positional
                if provider_name == "bark" and "voice_id" in generate_kwargs:
                    bark_voice_id = generate_kwargs.pop("voice_id")
                    audio_bytes, duration = provider.generate(text, bark_voice_id, **generate_kwargs)
                else:
                    audio_bytes, duration = provider.generate(text, voice_id, **generate_kwargs)
                # Save to cache
                self._save_to_cache(cache_key, audio_bytes, duration)
        else:
            # Generate new audio (same logic as above)
            generate_kwargs = {
                "rate": persona.voice.rate,
                "pitch": persona.voice.pitch,
            }
            
            if provider_name in ["xtts", "bark", "valle"]:
                reference_audio = None
                if Path(voice_id).exists():
                    reference_audio = Path(voice_id)
                else:
                    project_root = Path(__file__).parent.parent.parent
                    possible_paths = [
                        project_root / "examples" / "personas" / "voices" / f"{persona.key.lower()}.wav",
                        project_root / "examples" / "personas" / "voices" / f"{persona.key.lower()}.mp3",
                    ]
                    for path in possible_paths:
                        if path.exists():
                            reference_audio = path
                            break
                
                if reference_audio:
                    generate_kwargs["reference_audio"] = reference_audio
                elif provider_name == "bark":
                    generate_kwargs["voice_id"] = voice_id or "v2/en_speaker_0"
                else:
                    raise ValueError(
                        f"{provider_name.upper()} requires reference_audio. "
                        f"Expected: examples/personas/voices/{persona.key.lower()}.wav"
                    )
            
            # For Bark, if voice_id is in kwargs, extract it and don't pass as positional
            if provider_name == "bark" and "voice_id" in generate_kwargs:
                bark_voice_id = generate_kwargs.pop("voice_id")
                audio_bytes, duration = provider.generate(text, bark_voice_id, **generate_kwargs)
            else:
                audio_bytes, duration = provider.generate(text, voice_id, **generate_kwargs)

        # Save audio file
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = self.cache_dir

        audio_filename = f"{cache_key}.mp3"
        audio_path = output_path / audio_filename
        audio_path.write_bytes(audio_bytes)

        # Create a minimal segment for the audio segment
        # This will be replaced with the actual segment in generate_multiple
        from src.core.script_parser import ScriptSegment

        segment = ScriptSegment(persona=persona.key.upper(), text=text)

        return AudioSegment(
            segment=segment, audio_path=audio_path, duration=duration, provider=provider_name, cached=cached
        )

    def generate_multiple(
        self,
        segments: List[ScriptSegment],
        personas: Dict[str, Persona],
        use_cache: bool = True,
        output_dir: Optional[Path] = None,
    ) -> List[AudioSegment]:
        """
        Generate audio for multiple script segments.

        Args:
            segments: List of script segments to generate audio for
            personas: Dictionary mapping persona names to Persona objects
            use_cache: Whether to use cache if available
            output_dir: Directory to save audio files

        Returns:
            List of AudioSegment objects with audio files and timing
        """
        audio_segments = []

        for segment in segments:
            persona_name = segment.persona.upper()
            persona = personas.get(persona_name)

            if not persona:
                raise ValueError(f"Persona '{persona_name}' not found in personas dictionary")

            audio_segment = self.generate_persona_audio(persona, segment.text, use_cache=use_cache, output_dir=output_dir)
            # Update segment reference
            audio_segment.segment = segment
            audio_segments.append(audio_segment)

        return audio_segments

