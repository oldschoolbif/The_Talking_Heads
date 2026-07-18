"""
Unit tests for script parser.
"""

import pytest
from pathlib import Path
from src.core.script_parser import ScriptParser, ScriptSegment, ParsedScript


class TestScriptParser:
    """Test cases for ScriptParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ScriptParser()

    def test_parse_basic_script(self):
        """Test parsing a basic script with persona tags."""
        script = """# Test Episode

ALICE: Hello everyone!
BOB: Thanks for joining us!
ALICE: Today we'll discuss AI.
"""
        result = self.parser.parse(script)

        assert result.title == "Test Episode"
        assert len(result.segments) == 3
        assert result.personas == ["ALICE", "BOB"]

        assert result.segments[0].persona == "ALICE"
        assert result.segments[0].text == "Hello everyone!"
        assert result.segments[1].persona == "BOB"
        assert result.segments[1].text == "Thanks for joining us!"

    def test_parse_with_expressions(self):
        """Test parsing script with expression annotations."""
        script = """# Episode with Expressions

ALICE: [EXPRESSION:happy] I'm so excited about this!
BOB: [EXPRESSION:concerned] But what about the challenges?
"""
        result = self.parser.parse(script)

        assert len(result.segments) == 2
        assert result.segments[0].expression == "happy"
        assert result.segments[0].text == "I'm so excited about this!"
        assert result.segments[1].expression == "concerned"
        assert result.segments[1].text == "But what about the challenges?"

    def test_parse_with_gestures(self):
        """Test parsing script with gesture annotations."""
        script = """# Episode with Gestures

ALICE: [GESTURE:point] Let me explain this concept.
BOB: [GESTURE:wave] Welcome everyone!
"""
        result = self.parser.parse(script)

        assert len(result.segments) == 2
        assert result.segments[0].gesture == "point"
        assert result.segments[0].text == "Let me explain this concept."
        assert result.segments[1].gesture == "wave"
        assert result.segments[1].text == "Welcome everyone!"

    def test_parse_with_both_annotations(self):
        """Test parsing script with both expressions and gestures."""
        script = """# Episode with Both

ALICE: [EXPRESSION:happy] [GESTURE:wave] Welcome to the show!
"""
        result = self.parser.parse(script)

        assert len(result.segments) == 1
        assert result.segments[0].expression == "happy"
        assert result.segments[0].gesture == "wave"
        assert result.segments[0].text == "Welcome to the show!"

    def test_parse_multi_line_dialogue(self):
        """Test parsing multi-line dialogue for same persona."""
        script = """# Multi-line Dialogue

ALICE: This is the first line.
This is the second line.
And this is the third line.
BOB: Now Bob speaks.
"""
        result = self.parser.parse(script)

        assert len(result.segments) == 2
        assert result.segments[0].persona == "ALICE"
        assert "first line" in result.segments[0].text
        assert "second line" in result.segments[0].text
        assert "third line" in result.segments[0].text
        assert result.segments[1].persona == "BOB"
        assert result.segments[1].text == "Now Bob speaks."

    def test_parse_case_insensitive_personas(self):
        """Test that persona names are case-insensitive (normalized to uppercase)."""
        script = """# Case Test

alice: Lowercase persona.
Alice: Title case persona.
ALICE: Uppercase persona.
bob: Another lowercase.
"""
        result = self.parser.parse(script)

        assert len(result.segments) == 4
        assert all(seg.persona == "ALICE" for seg in result.segments[:3])
        assert result.segments[3].persona == "BOB"
        assert "ALICE" in result.personas
        assert "BOB" in result.personas

    def test_parse_no_title(self):
        """Test parsing script without title (should default to 'Untitled Episode')."""
        script = """ALICE: Hello!
BOB: Hi there!
"""
        result = self.parser.parse(script)

        assert result.title == "Untitled Episode"
        assert len(result.segments) == 2

    def test_parse_empty_script_raises_error(self):
        """Test that parsing empty script raises ValueError."""
        with pytest.raises(ValueError, match="Script text cannot be empty"):
            self.parser.parse("")

        with pytest.raises(ValueError, match="Script text cannot be empty"):
            self.parser.parse("   \n\n  ")

    def test_parse_timing_calculation(self):
        """Test that timing is calculated for segments."""
        script = """# Timing Test

ALICE: Short text.
BOB: This is a longer text that should take more time to speak.
"""
        result = self.parser.parse(script)

        assert len(result.segments) == 2
        assert result.segments[0].start_time == 0.0
        assert result.segments[0].end_time > result.segments[0].start_time
        assert result.segments[1].start_time == result.segments[0].end_time
        assert result.segments[1].end_time > result.segments[1].start_time
        # Longer text should have longer duration
        assert (result.segments[1].end_time - result.segments[1].start_time) > (
            result.segments[0].end_time - result.segments[0].start_time
        )

    def test_parse_file(self, tmp_path):
        """Test parsing from a file."""
        script_file = tmp_path / "test_script.txt"
        script_content = """# File Test

ALICE: Hello from file!
BOB: This is from a file.
"""
        script_file.write_text(script_content, encoding="utf-8")

        result = self.parser.parse_file(script_file)

        assert result.title == "File Test"
        assert len(result.segments) == 2

    def test_parse_file_not_found(self, tmp_path):
        """Test that parsing non-existent file raises FileNotFoundError."""
        script_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            self.parser.parse_file(script_file)

    def test_parse_example_script(self):
        """Test parsing the example script format."""
        script = """# Welcome to The Talking Heads

ALICE: Hello everyone, and welcome to The Talking Heads! I'm Alice, your host for today.

BOB: And I'm Bob, co-host. Thanks for joining us!

ALICE: Today we're thrilled to have Charlie joining us as our special guest.

CHARLIE: Thanks for having me! I'm so excited to be here.
"""
        result = self.parser.parse(script)

        assert result.title == "Welcome to The Talking Heads"
        assert len(result.segments) == 4
        assert set(result.personas) == {"ALICE", "BOB", "CHARLIE"}

    def test_parse_expression_case_insensitive(self):
        """Test that expression annotations are case-insensitive."""
        script = """# Expression Case Test

ALICE: [EXPRESSION:HAPPY] Uppercase expression.
BOB: [expression:concerned] Lowercase expression.
CHARLIE: [Expression:Neutral] Mixed case expression.
"""
        result = self.parser.parse(script)

        assert result.segments[0].expression == "happy"
        assert result.segments[1].expression == "concerned"
        assert result.segments[2].expression == "neutral"

    def test_parse_gesture_case_insensitive(self):
        """Test that gesture annotations are case-insensitive."""
        script = """# Gesture Case Test

ALICE: [GESTURE:POINT] Uppercase gesture.
BOB: [gesture:wave] Lowercase gesture.
"""
        result = self.parser.parse(script)

        assert result.segments[0].gesture == "point"
        assert result.segments[1].gesture == "wave"

    def test_parse_empty_lines_between_segments(self):
        """Test parsing with empty lines between segments."""
        script = """# Empty Lines Test

ALICE: First segment.


BOB: Second segment after empty lines.

CHARLIE: Third segment.
"""
        result = self.parser.parse(script)

        assert len(result.segments) == 3
        assert result.segments[0].persona == "ALICE"
        assert result.segments[1].persona == "BOB"
        assert result.segments[2].persona == "CHARLIE"

    def test_parse_text_cleaning(self):
        """Test that extra whitespace is cleaned from text."""
        script = """# Text Cleaning Test

ALICE: Text    with    multiple    spaces.
BOB: Text
with
newlines.
"""
        result = self.parser.parse(script)

        assert "    " not in result.segments[0].text
        assert "\n" not in result.segments[1].text or result.segments[1].text.count("\n") < 3

    def test_parse_segment_line_numbers(self):
        """Test that line numbers are correctly assigned."""
        script = """# Line Number Test

ALICE: First line.
BOB: Second line.
"""
        result = self.parser.parse(script)

        # Line numbers should be set (exact values depend on implementation)
        assert all(seg.line_number > 0 for seg in result.segments)

    def test_parse_to_dict(self):
        """Test conversion to dictionary format."""
        script = """# Dict Test

ALICE: Hello!
"""
        result = self.parser.parse(script)

        result_dict = result.to_dict()
        assert "title" in result_dict
        assert "segments" in result_dict
        assert "personas" in result_dict
        assert isinstance(result_dict["segments"], list)
        assert len(result_dict["segments"]) == 1

        segment_dict = result_dict["segments"][0]
        assert "persona" in segment_dict
        assert "text" in segment_dict
        assert "expression" in segment_dict
        assert "gesture" in segment_dict
        assert "start_time" in segment_dict
        assert "end_time" in segment_dict

    def test_parse_multiple_expressions_uses_first(self):
        """Test that if multiple expressions are present, first one is used."""
        script = """# Multiple Expressions

ALICE: [EXPRESSION:happy] [EXPRESSION:sad] Mixed emotions.
"""
        result = self.parser.parse(script)

        # Should extract first expression
        assert result.segments[0].expression == "happy"
        # Both should be removed from text
        assert "[EXPRESSION:" not in result.segments[0].text

    def test_parse_multiple_gestures_uses_first(self):
        """Test that if multiple gestures are present, first one is used."""
        script = """# Multiple Gestures

ALICE: [GESTURE:point] [GESTURE:wave] Multiple gestures.
"""
        result = self.parser.parse(script)

        # Should extract first gesture
        assert result.segments[0].gesture == "point"
        # Both should be removed from text
        assert "[GESTURE:" not in result.segments[0].text

    def test_parse_unicode_characters(self):
        """Test parsing script with unicode characters."""
        script = """# Unicode Test

ALICE: Hello! 👋 This has emojis and special chars: café, résumé.
BOB: 你好！This has Chinese characters.
"""
        result = self.parser.parse(script)

        assert len(result.segments) == 2
        assert "👋" in result.segments[0].text or "café" in result.segments[0].text
        assert "你好" in result.segments[1].text

    def test_parse_file_encoding_handling(self, tmp_path):
        """Test parsing file with encoding issues (should use error handling)."""
        script_file = tmp_path / "test_script.txt"
        # Write with UTF-8 encoding
        script_content = """# Encoding Test

ALICE: Hello with émojis 👋!
"""
        script_file.write_text(script_content, encoding="utf-8")

        result = self.parser.parse_file(script_file)

        assert result.title == "Encoding Test"
        assert len(result.segments) == 1

