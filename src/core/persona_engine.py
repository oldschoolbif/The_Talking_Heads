"""
Persona Engine for The Talking Heads

Loads and manages persona configurations, validates personas in scripts.
"""

import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.core.script_parser import ScriptSegment, ParsedScript


@dataclass
class VoiceConfig:
    """Voice configuration for a persona."""

    engine: str
    voice_id: str
    style: str = "conversational"
    rate: float = 1.0
    pitch: float = 1.0


@dataclass
class ExpressionConfig:
    """Expression configuration for a persona."""

    enabled: bool = True
    default: str = "neutral"
    categories: List[str] = field(default_factory=list)


@dataclass
class GestureConfig:
    """Gesture configuration for a persona."""

    enabled: bool = True
    frequency: str = "moderate"  # "low", "moderate", "high"
    library: List[str] = field(default_factory=list)


@dataclass
class AvatarConfig:
    """Avatar configuration for a persona."""

    engine: str
    avatar_id: str
    style: str = "cartoon"
    expressions: ExpressionConfig = field(default_factory=lambda: ExpressionConfig())
    gestures: GestureConfig = field(default_factory=lambda: GestureConfig())


@dataclass
class Persona:
    """Represents a persona configuration."""

    key: str  # The key in the YAML (e.g., "alice")
    name: str  # Display name (e.g., "Alice")
    description: str = ""
    voice: VoiceConfig = field(default_factory=lambda: VoiceConfig(engine="elevenlabs", voice_id=""))
    avatar: AvatarConfig = field(default_factory=lambda: AvatarConfig(engine="heygen", avatar_id=""))

    def to_dict(self) -> Dict[str, Any]:
        """Convert persona to dictionary."""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "voice": {
                "engine": self.voice.engine,
                "voice_id": self.voice.voice_id,
                "style": self.voice.style,
                "rate": self.voice.rate,
                "pitch": self.voice.pitch,
            },
            "avatar": {
                "engine": self.avatar.engine,
                "avatar_id": self.avatar.avatar_id,
                "style": self.avatar.style,
                "expressions": {
                    "enabled": self.avatar.expressions.enabled,
                    "default": self.avatar.expressions.default,
                    "categories": self.avatar.expressions.categories,
                },
                "gestures": {
                    "enabled": self.avatar.gestures.enabled,
                    "frequency": self.avatar.gestures.frequency,
                    "library": self.avatar.gestures.library,
                },
            },
        }


class PersonaEngine:
    """Manages persona configurations and validation."""

    def __init__(self):
        """Initialize the persona engine."""
        self._personas: Dict[str, Persona] = {}
        self._loaded: bool = False

    def load_personas(self, config_path: Path) -> None:
        """
        Load persona configurations from YAML file.

        Args:
            config_path: Path to personas.yaml configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid or missing required fields
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Persona config file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in persona config: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading persona config: {e}") from e

        if not config or "personas" not in config:
            raise ValueError("Persona config must contain 'personas' key")

        personas_dict = config["personas"]
        if not isinstance(personas_dict, dict):
            raise ValueError("'personas' must be a dictionary")

        self._personas = {}
        for key, persona_data in personas_dict.items():
            try:
                persona = self._parse_persona(key, persona_data)
                self._personas[key.upper()] = persona
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(f"Invalid persona configuration for '{key}': {e}") from e

        self._loaded = True

    def _parse_persona(self, key: str, data: Dict[str, Any]) -> Persona:
        """Parse a single persona from configuration data."""
        if "name" not in data:
            raise ValueError("Persona must have 'name' field")

        # Parse voice config
        voice_data = data.get("voice", {})
        if not voice_data or "engine" not in voice_data or "voice_id" not in voice_data:
            raise ValueError("Persona must have 'voice' with 'engine' and 'voice_id'")

        voice = VoiceConfig(
            engine=voice_data["engine"],
            voice_id=voice_data["voice_id"],
            style=voice_data.get("style", "conversational"),
            rate=float(voice_data.get("rate", 1.0)),
            pitch=float(voice_data.get("pitch", 1.0)),
        )

        # Parse avatar config
        avatar_data = data.get("avatar", {})
        if not avatar_data or "engine" not in avatar_data or "avatar_id" not in avatar_data:
            raise ValueError("Persona must have 'avatar' with 'engine' and 'avatar_id'")

        # Parse expressions
        expressions_data = avatar_data.get("expressions", {})
        expressions = ExpressionConfig(
            enabled=expressions_data.get("enabled", True),
            default=expressions_data.get("default", "neutral"),
            categories=expressions_data.get("categories", []),
        )

        # Parse gestures
        gestures_data = avatar_data.get("gestures", {})
        gestures = GestureConfig(
            enabled=gestures_data.get("enabled", True),
            frequency=gestures_data.get("frequency", "moderate"),
            library=gestures_data.get("library", []),
        )

        avatar = AvatarConfig(
            engine=avatar_data["engine"],
            avatar_id=avatar_data["avatar_id"],
            style=avatar_data.get("style", "cartoon"),
            expressions=expressions,
            gestures=gestures,
        )

        return Persona(
            key=key.lower(),
            name=data["name"],
            description=data.get("description", ""),
            voice=voice,
            avatar=avatar,
        )

    def get_persona(self, name: str) -> Optional[Persona]:
        """
        Get persona by name (case-insensitive).

        Args:
            name: Persona name (e.g., "ALICE", "alice", "Alice")

        Returns:
            Persona object if found, None otherwise
        """
        if not self._loaded:
            raise RuntimeError("Personas must be loaded before use. Call load_personas() first.")

        return self._personas.get(name.upper())

    def get_all_personas(self) -> List[Persona]:
        """
        Get all loaded personas.

        Returns:
            List of all Persona objects
        """
        if not self._loaded:
            raise RuntimeError("Personas must be loaded before use. Call load_personas() first.")

        return list(self._personas.values())

    def validate_personas(self, script_segments: List[ScriptSegment]) -> List[str]:
        """
        Validate that all personas in script segments are configured.

        Args:
            script_segments: List of script segments to validate

        Returns:
            List of error messages for missing personas (empty if all valid)

        Raises:
            RuntimeError: If personas haven't been loaded
        """
        if not self._loaded:
            raise RuntimeError("Personas must be loaded before validation. Call load_personas() first.")

        errors = []
        script_personas = set(seg.persona.upper() for seg in script_segments)

        for persona_name in script_personas:
            if persona_name not in self._personas:
                errors.append(f"Persona '{persona_name}' is used in script but not configured in personas.yaml")

        return errors

    def validate_expressions(self, script_segments: List[ScriptSegment]) -> List[str]:
        """
        Validate that expressions used in script are supported by personas.

        Args:
            script_segments: List of script segments to validate

        Returns:
            List of error messages for invalid expressions (empty if all valid)

        Raises:
            RuntimeError: If personas haven't been loaded
        """
        if not self._loaded:
            raise RuntimeError("Personas must be loaded before validation. Call load_personas() first.")

        errors = []
        for segment in script_segments:
            if not segment.expression:
                continue

            persona = self.get_persona(segment.persona)
            if not persona:
                continue  # Already handled by validate_personas

            if not persona.avatar.expressions.enabled:
                errors.append(
                    f"Persona '{persona.name}' has expressions disabled but script uses expression '{segment.expression}'"
                )
                continue

            if segment.expression not in persona.avatar.expressions.categories:
                errors.append(
                    f"Persona '{persona.name}' doesn't support expression '{segment.expression}'. "
                    f"Available: {persona.avatar.expressions.categories}"
                )

        return errors

    def validate_gestures(self, script_segments: List[ScriptSegment]) -> List[str]:
        """
        Validate that gestures used in script are supported by personas.

        Args:
            script_segments: List of script segments to validate

        Returns:
            List of error messages for invalid gestures (empty if all valid)

        Raises:
            RuntimeError: If personas haven't been loaded
        """
        if not self._loaded:
            raise RuntimeError("Personas must be loaded before validation. Call load_personas() first.")

        errors = []
        for segment in script_segments:
            if not segment.gesture:
                continue

            persona = self.get_persona(segment.persona)
            if not persona:
                continue  # Already handled by validate_personas

            if not persona.avatar.gestures.enabled:
                errors.append(
                    f"Persona '{persona.name}' has gestures disabled but script uses gesture '{segment.gesture}'"
                )
                continue

            if segment.gesture not in persona.avatar.gestures.library:
                errors.append(
                    f"Persona '{persona.name}' doesn't support gesture '{segment.gesture}'. "
                    f"Available: {persona.avatar.gestures.library}"
                )

        return errors

    def validate_script(self, parsed_script: ParsedScript) -> List[str]:
        """
        Validate entire script against persona configurations.

        Args:
            parsed_script: Parsed script to validate

        Returns:
            List of all validation error messages (empty if valid)

        Raises:
            RuntimeError: If personas haven't been loaded
        """
        errors = []
        errors.extend(self.validate_personas(parsed_script.segments))
        errors.extend(self.validate_expressions(parsed_script.segments))
        errors.extend(self.validate_gestures(parsed_script.segments))
        return errors

    def is_loaded(self) -> bool:
        """Check if personas have been loaded."""
        return self._loaded

