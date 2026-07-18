"""
Unit tests for persona engine.
"""

import pytest
import yaml
from pathlib import Path
from src.core.persona_engine import (
    PersonaEngine,
    Persona,
    VoiceConfig,
    AvatarConfig,
    ExpressionConfig,
    GestureConfig,
)
from src.core.script_parser import ScriptParser, ScriptSegment, ParsedScript


class TestPersonaEngine:
    """Test cases for PersonaEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = PersonaEngine()

    def test_load_personas_from_file(self, tmp_path):
        """Test loading personas from a YAML file."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    description: "Test persona"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
      style: "conversational"
      rate: 1.0
      pitch: 1.0
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      style: "cartoon"
      expressions:
        enabled: true
        default: "neutral"
        categories:
          - "happy"
          - "neutral"
      gestures:
        enabled: true
        frequency: "moderate"
        library:
          - "point"
          - "wave"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.engine.load_personas(config_file)

        assert self.engine.is_loaded()
        assert len(self.engine.get_all_personas()) == 1

        alice = self.engine.get_persona("alice")
        assert alice is not None
        assert alice.name == "Alice"
        assert alice.key == "alice"
        assert alice.voice.engine == "elevenlabs"
        assert alice.voice.voice_id == "voice_123"
        assert alice.avatar.engine == "heygen"
        assert alice.avatar.avatar_id == "avatar_123"

    def test_load_personas_case_insensitive(self, tmp_path):
        """Test that persona lookup is case-insensitive."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.engine.load_personas(config_file)

        # All these should return the same persona
        assert self.engine.get_persona("alice") is not None
        assert self.engine.get_persona("ALICE") is not None
        assert self.engine.get_persona("Alice") is not None
        assert self.engine.get_persona("ALICE") == self.engine.get_persona("alice")

    def test_load_personas_file_not_found(self, tmp_path):
        """Test that loading non-existent file raises FileNotFoundError."""
        config_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            self.engine.load_personas(config_file)

    def test_load_personas_invalid_yaml(self, tmp_path):
        """Test that invalid YAML raises ValueError."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid YAML"):
            self.engine.load_personas(config_file)

    def test_load_personas_missing_personas_key(self, tmp_path):
        """Test that missing 'personas' key raises ValueError."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("other_key: value", encoding="utf-8")

        with pytest.raises(ValueError, match="must contain 'personas' key"):
            self.engine.load_personas(config_file)

    def test_load_personas_missing_required_fields(self, tmp_path):
        """Test that missing required fields raises ValueError."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    # Missing voice and avatar
"""
        config_file.write_text(config_content, encoding="utf-8")

        with pytest.raises(ValueError, match="must have 'voice'"):
            self.engine.load_personas(config_file)

    def test_get_persona_not_loaded(self):
        """Test that getting persona before loading raises RuntimeError."""
        with pytest.raises(RuntimeError, match="must be loaded"):
            self.engine.get_persona("alice")

    def test_get_persona_not_found(self, tmp_path):
        """Test that getting non-existent persona returns None."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.engine.load_personas(config_file)

        assert self.engine.get_persona("bob") is None
        assert self.engine.get_persona("nonexistent") is None

    def test_validate_personas_all_valid(self, tmp_path):
        """Test validation when all personas in script are configured."""
        # Setup personas
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
  bob:
    name: "Bob"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_456"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_456"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        # Create script segments
        segments = [
            ScriptSegment(persona="ALICE", text="Hello!"),
            ScriptSegment(persona="BOB", text="Hi there!"),
        ]

        errors = self.engine.validate_personas(segments)
        assert len(errors) == 0

    def test_validate_personas_missing_persona(self, tmp_path):
        """Test validation when script uses unconfigured persona."""
        # Setup personas (only alice)
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        # Create script segments with unconfigured persona
        segments = [
            ScriptSegment(persona="ALICE", text="Hello!"),
            ScriptSegment(persona="BOB", text="Hi there!"),  # Not configured
            ScriptSegment(persona="CHARLIE", text="Hey!"),  # Not configured
        ]

        errors = self.engine.validate_personas(segments)
        assert len(errors) == 2
        assert any("BOB" in error for error in errors)
        assert any("CHARLIE" in error for error in errors)

    def test_validate_personas_not_loaded(self):
        """Test that validation before loading raises RuntimeError."""
        segments = [ScriptSegment(persona="ALICE", text="Hello!")]

        with pytest.raises(RuntimeError, match="must be loaded"):
            self.engine.validate_personas(segments)

    def test_validate_expressions_valid(self, tmp_path):
        """Test expression validation when all expressions are valid."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      expressions:
        enabled: true
        categories:
          - "happy"
          - "neutral"
          - "surprised"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        segments = [
            ScriptSegment(persona="ALICE", text="Hello!", expression="happy"),
            ScriptSegment(persona="ALICE", text="Wow!", expression="surprised"),
        ]

        errors = self.engine.validate_expressions(segments)
        assert len(errors) == 0

    def test_validate_expressions_invalid(self, tmp_path):
        """Test expression validation when expression is not supported."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      expressions:
        enabled: true
        categories:
          - "happy"
          - "neutral"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        segments = [
            ScriptSegment(persona="ALICE", text="Hello!", expression="sad"),  # Not in categories
        ]

        errors = self.engine.validate_expressions(segments)
        assert len(errors) == 1
        assert "sad" in errors[0]
        assert "happy" in errors[0] or "neutral" in errors[0]  # Should mention available

    def test_validate_expressions_disabled(self, tmp_path):
        """Test expression validation when expressions are disabled for persona."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      expressions:
        enabled: false
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        segments = [
            ScriptSegment(persona="ALICE", text="Hello!", expression="happy"),
        ]

        errors = self.engine.validate_expressions(segments)
        assert len(errors) == 1
        assert "disabled" in errors[0].lower()

    def test_validate_gestures_valid(self, tmp_path):
        """Test gesture validation when all gestures are valid."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      gestures:
        enabled: true
        library:
          - "point"
          - "wave"
          - "emphasize"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        segments = [
            ScriptSegment(persona="ALICE", text="Hello!", gesture="point"),
            ScriptSegment(persona="ALICE", text="Wow!", gesture="wave"),
        ]

        errors = self.engine.validate_gestures(segments)
        assert len(errors) == 0

    def test_validate_gestures_invalid(self, tmp_path):
        """Test gesture validation when gesture is not supported."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      gestures:
        enabled: true
        library:
          - "point"
          - "wave"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        segments = [
            ScriptSegment(persona="ALICE", text="Hello!", gesture="dance"),  # Not in library
        ]

        errors = self.engine.validate_gestures(segments)
        assert len(errors) == 1
        assert "dance" in errors[0]
        assert "point" in errors[0] or "wave" in errors[0]  # Should mention available

    def test_validate_gestures_disabled(self, tmp_path):
        """Test gesture validation when gestures are disabled for persona."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      gestures:
        enabled: false
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        segments = [
            ScriptSegment(persona="ALICE", text="Hello!", gesture="point"),
        ]

        errors = self.engine.validate_gestures(segments)
        assert len(errors) == 1
        assert "disabled" in errors[0].lower()

    def test_validate_script_comprehensive(self, tmp_path):
        """Test comprehensive script validation."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      expressions:
        enabled: true
        categories:
          - "happy"
      gestures:
        enabled: true
        library:
          - "point"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        # Create parsed script with various issues
        parser = ScriptParser()
        script_text = """# Test Script

ALICE: [EXPRESSION:happy] Hello!
BOB: Hi there!  # Bob not configured
ALICE: [EXPRESSION:sad] I'm sad.  # Expression not supported
ALICE: [GESTURE:dance] Let's dance!  # Gesture not supported
"""
        parsed_script = parser.parse(script_text)

        errors = self.engine.validate_script(parsed_script)
        assert len(errors) >= 3  # Bob missing, sad expression, dance gesture

    def test_load_personas_default_values(self, tmp_path):
        """Test that default values are used when optional fields are missing."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        alice = self.engine.get_persona("alice")
        assert alice.voice.style == "conversational"
        assert alice.voice.rate == 1.0
        assert alice.voice.pitch == 1.0
        assert alice.avatar.style == "cartoon"
        assert alice.avatar.expressions.enabled is True
        assert alice.avatar.expressions.default == "neutral"
        assert alice.avatar.gestures.enabled is True
        assert alice.avatar.gestures.frequency == "moderate"

    def test_persona_to_dict(self, tmp_path):
        """Test persona to_dict conversion."""
        config_file = tmp_path / "personas.yaml"
        config_content = """
personas:
  alice:
    name: "Alice"
    description: "Test persona"
    voice:
      engine: "elevenlabs"
      voice_id: "voice_123"
      style: "conversational"
      rate: 1.0
      pitch: 1.0
    avatar:
      engine: "heygen"
      avatar_id: "avatar_123"
      style: "cartoon"
      expressions:
        enabled: true
        default: "neutral"
        categories:
          - "happy"
      gestures:
        enabled: true
        frequency: "moderate"
        library:
          - "point"
"""
        config_file.write_text(config_content, encoding="utf-8")
        self.engine.load_personas(config_file)

        alice = self.engine.get_persona("alice")
        persona_dict = alice.to_dict()

        assert persona_dict["key"] == "alice"
        assert persona_dict["name"] == "Alice"
        assert persona_dict["description"] == "Test persona"
        assert persona_dict["voice"]["engine"] == "elevenlabs"
        assert persona_dict["avatar"]["engine"] == "heygen"
        assert persona_dict["avatar"]["expressions"]["enabled"] is True
        assert persona_dict["avatar"]["gestures"]["enabled"] is True

    def test_load_real_personas_config(self):
        """Test loading the actual personas.yaml config file."""
        config_path = Path("config/personas.yaml")
        if not config_path.exists():
            pytest.skip("config/personas.yaml not found")

        self.engine.load_personas(config_path)

        assert self.engine.is_loaded()
        personas = self.engine.get_all_personas()
        assert len(personas) >= 3  # Should have alice, bob, charlie

        # Test getting each persona
        alice = self.engine.get_persona("alice")
        assert alice is not None
        assert alice.name == "Alice"

        bob = self.engine.get_persona("bob")
        assert bob is not None
        assert bob.name == "Bob"

        charlie = self.engine.get_persona("charlie")
        assert charlie is not None
        assert charlie.name == "Charlie"

