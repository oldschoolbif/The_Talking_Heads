"""
Generate a persona template for easy addition to personas.yaml.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def generate_persona_template(
    name: str,
    description: str = "",
    voice_style: str = "conversational",
    voice_rate: float = 1.0,
    voice_pitch: float = 1.0,
    avatar_style: str = "cartoon",
    default_expression: str = "neutral",
    gesture_frequency: str = "moderate",
) -> str:
    """
    Generate a persona YAML template.
    
    Args:
        name: Persona name (e.g., "Alice")
        description: Persona description
        voice_style: Voice style (conversational, professional, energetic)
        voice_rate: Voice rate multiplier (0.8-1.2)
        voice_pitch: Voice pitch multiplier (0.8-1.2)
        avatar_style: Avatar style (cartoon, realistic)
        default_expression: Default expression (neutral, happy, etc.)
        gesture_frequency: Gesture frequency (low, moderate, high)
    
    Returns:
        YAML string for the persona
    """
    key = name.lower()
    
    template = f"""  {key}:
    name: "{name}"
    description: "{description}"
    voice:
      engine: "elevenlabs"
      voice_id: "TODO_REPLACE_WITH_ELEVENLABS_VOICE_ID"  # TODO: Replace with actual ElevenLabs voice ID
      style: "{voice_style}"
      rate: {voice_rate}
      pitch: {voice_pitch}
    avatar:
      engine: "heygen"
      avatar_id: "{name}_{voice_style}_2024112501"  # TODO: Replace with actual HeyGen avatar ID
      style: "{avatar_style}"
      expressions:
        enabled: true
        default: "{default_expression}"
        categories:
          - "{default_expression}"
          - "neutral"
          - "happy"
          - "surprised"
      gestures:
        enabled: true
        frequency: "{gesture_frequency}"  # Options: "low", "moderate", "high"
        library:
          - "point"
          - "emphasize"
          - "wave"
"""
    return template


def main():
    """Generate persona template interactively or from command line."""
    print("=" * 60)
    print("Persona Template Generator")
    print("=" * 60)
    print()
    
    # Get persona details
    if len(sys.argv) > 1:
        # Command line mode
        name = sys.argv[1]
        description = sys.argv[2] if len(sys.argv) > 2 else ""
        voice_style = sys.argv[3] if len(sys.argv) > 3 else "conversational"
        voice_rate = 1.0
        voice_pitch = 1.0
        default_expression = "neutral"
        gesture_frequency = "moderate"
    else:
        # Interactive mode
        name = input("Persona name (e.g., Alice): ").strip()
        if not name:
            print("Error: Persona name required")
            sys.exit(1)
        description = input("Description (e.g., Main host, friendly): ").strip()
        voice_style = input("Voice style (conversational/professional/energetic) [conversational]: ").strip() or "conversational"
        voice_rate_str = input("Voice rate (0.8-1.2) [1.0]: ").strip()
        voice_rate = float(voice_rate_str) if voice_rate_str else 1.0
        voice_pitch_str = input("Voice pitch (0.8-1.2) [1.0]: ").strip()
        voice_pitch = float(voice_pitch_str) if voice_pitch_str else 1.0
        default_expression = input("Default expression (neutral/happy) [neutral]: ").strip() or "neutral"
        gesture_frequency = input("Gesture frequency (low/moderate/high) [moderate]: ").strip() or "moderate"
    
    template = generate_persona_template(
        name=name,
        description=description,
        voice_style=voice_style,
        voice_rate=voice_rate,
        voice_pitch=voice_pitch,
        default_expression=default_expression,
        gesture_frequency=gesture_frequency,
    )
    
    print()
    print("Generated Persona Template:")
    print("=" * 60)
    print(template)
    print("=" * 60)
    print()
    print("Copy this template and add it to config/personas.yaml")
    print("Don't forget to replace the TODO voice_id and avatar_id with real IDs!")
    
    # Optionally write to a file (interactive mode only)
    if len(sys.argv) == 1:
        save = input("\nSave to file? (y/n) [n]: ").strip().lower()
        if save == 'y':
            output_file = project_root / "examples" / f"persona_{name.lower()}_template.yaml"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"\nTemplate saved to: {output_file}")


if __name__ == "__main__":
    main()

