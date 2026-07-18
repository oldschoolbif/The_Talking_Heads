"""
Script Parser for The Talking Heads

Parses podcast scripts with persona assignments, expressions, and gestures.
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class ScriptSegment:
    """Represents a single segment of dialogue in a script."""

    persona: str
    text: str
    expression: Optional[str] = None
    gesture: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0
    line_number: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert segment to dictionary."""
        return {
            "persona": self.persona,
            "text": self.text,
            "expression": self.expression,
            "gesture": self.gesture,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "line_number": self.line_number,
        }


@dataclass
class ParsedScript:
    """Represents a fully parsed script with metadata."""

    title: str
    segments: List[ScriptSegment]
    personas: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert parsed script to dictionary."""
        return {
            "title": self.title,
            "segments": [seg.to_dict() for seg in self.segments],
            "personas": self.personas,
        }


class ScriptParser:
    """Parses podcast scripts with persona assignments and annotations."""

    # Regex patterns
    PERSONA_PATTERN = re.compile(r"^([A-Za-z][A-Za-z0-9_]+):\s*(.*)$", re.MULTILINE)
    EXPRESSION_PATTERN = re.compile(r"\[EXPRESSION:([^\]]+)\]", re.IGNORECASE)
    GESTURE_PATTERN = re.compile(r"\[GESTURE:([^\]]+)\]", re.IGNORECASE)
    TITLE_PATTERN = re.compile(r"^#\s*(.+)$", re.MULTILINE)

    def __init__(self):
        """Initialize the script parser."""
        pass

    def parse(self, script_text: str) -> ParsedScript:
        """
        Parse a script text into structured segments.

        Args:
            script_text: The script text to parse

        Returns:
            ParsedScript object with title, segments, and personas

        Raises:
            ValueError: If script is empty or invalid
        """
        if not script_text or not script_text.strip():
            raise ValueError("Script text cannot be empty")

        # Extract title (first line starting with #)
        title = self._extract_title(script_text)

        # Parse segments
        segments = self._parse_segments(script_text)

        # Extract unique personas
        personas = sorted(list(set(seg.persona for seg in segments)))

        return ParsedScript(title=title, segments=segments, personas=personas)

    def parse_file(self, script_path: Path) -> ParsedScript:
        """
        Parse a script file.

        Args:
            script_path: Path to the script file

        Returns:
            ParsedScript object

        Raises:
            FileNotFoundError: If script file doesn't exist
            ValueError: If script is empty or invalid
        """
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script file not found: {script_path}")

        try:
            script_text = script_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Try with error handling
            script_text = script_path.read_text(encoding="utf-8", errors="replace")

        return self.parse(script_text)

    def _extract_title(self, script_text: str) -> str:
        """Extract title from script (first line starting with #)."""
        match = self.TITLE_PATTERN.search(script_text)
        if match:
            return match.group(1).strip()
        return "Untitled Episode"

    def _parse_segments(self, script_text: str) -> List[ScriptSegment]:
        """Parse script into segments with persona assignments."""
        segments = []
        lines = script_text.split("\n")
        current_persona = None
        current_text_lines = []
        line_number = 0

        for i, line in enumerate(lines, start=1):
            line = line.rstrip()
            line_number = i

            # Check if line is a persona tag
            persona_match = self.PERSONA_PATTERN.match(line)
            if persona_match:
                # Save previous segment if exists
                if current_persona and current_text_lines:
                    segment = self._create_segment(
                        current_persona, "\n".join(current_text_lines), line_number - len(current_text_lines)
                    )
                    segments.append(segment)

                # Start new segment
                current_persona = persona_match.group(1).upper()
                current_text_lines = [persona_match.group(2).strip()]
            elif current_persona and line.strip():
                # Continuation of current persona's dialogue
                current_text_lines.append(line.strip())
            elif current_persona and not line.strip():
                # Empty line - end current segment
                if current_text_lines:
                    segment = self._create_segment(
                        current_persona, "\n".join(current_text_lines), line_number - len(current_text_lines)
                    )
                    segments.append(segment)
                    current_text_lines = []
                    current_persona = None

        # Handle last segment
        if current_persona and current_text_lines:
            segment = self._create_segment(
                current_persona, "\n".join(current_text_lines), line_number - len(current_text_lines) + 1
            )
            segments.append(segment)

        # Calculate timing (rough estimate: 150 words per minute)
        self._calculate_timing(segments)

        return segments

    def _create_segment(self, persona: str, text: str, line_number: int) -> ScriptSegment:
        """Create a ScriptSegment from persona and text, extracting annotations."""
        # Extract and remove expressions
        expression = None
        expression_match = self.EXPRESSION_PATTERN.search(text)
        if expression_match:
            expression = expression_match.group(1).strip().lower()
            text = self.EXPRESSION_PATTERN.sub("", text).strip()

        # Extract and remove gestures
        gesture = None
        gesture_match = self.GESTURE_PATTERN.search(text)
        if gesture_match:
            gesture = gesture_match.group(1).strip().lower()
            text = self.GESTURE_PATTERN.sub("", text).strip()

        # Clean up text (remove extra whitespace)
        text = re.sub(r"\s+", " ", text).strip()

        return ScriptSegment(
            persona=persona,
            text=text,
            expression=expression,
            gesture=gesture,
            line_number=line_number,
        )

    def _calculate_timing(self, segments: List[ScriptSegment], words_per_minute: float = 150.0) -> None:
        """
        Calculate start and end times for segments based on estimated speaking rate.

        Args:
            segments: List of segments to calculate timing for
            words_per_minute: Average speaking rate (default 150 WPM)
        """
        current_time = 0.0
        seconds_per_word = 60.0 / words_per_minute

        for segment in segments:
            # Count words in text
            word_count = len(segment.text.split()) if segment.text else 0
            duration = word_count * seconds_per_word

            segment.start_time = current_time
            segment.end_time = current_time + duration

            current_time = segment.end_time

