"""
Core modules for The Talking Heads
"""

from src.core.script_parser import ScriptParser, ScriptSegment, ParsedScript
from src.core.persona_engine import (
    PersonaEngine,
    Persona,
    VoiceConfig,
    AvatarConfig,
    ExpressionConfig,
    GestureConfig,
)
from src.core.tts_engine import TTSEngine, AudioSegment
from src.core.tts_provider_base import TTSProvider
from src.core.audio_mixer import AudioMixer
from src.core.avatar_generator import AvatarGenerator, AvatarVideo
from src.core.avatar_provider_base import AvatarProvider
from src.core.heygen_webhook import HeyGenWebhookHandler, HeyGenWebhookEvent
from src.core.scene_manager import SceneManager, Scene
from src.core.video_composer import VideoComposer, VideoComposition
from src.core.pipeline import Pipeline

__all__ = [
    "ScriptParser",
    "ScriptSegment",
    "ParsedScript",
    "PersonaEngine",
    "Persona",
    "VoiceConfig",
    "AvatarConfig",
    "ExpressionConfig",
    "GestureConfig",
    "TTSEngine",
    "AudioSegment",
    "TTSProvider",
    "AudioMixer",
    "AvatarGenerator",
    "AvatarVideo",
    "AvatarProvider",
    "HeyGenWebhookHandler",
    "HeyGenWebhookEvent",
    "SceneManager",
    "Scene",
    "VideoComposer",
    "VideoComposition",
    "Pipeline",
]

