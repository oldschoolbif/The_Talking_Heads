# Script Format Guide
## The Talking Heads

## Overview

The Talking Heads uses a simple markdown-based script format with persona assignments. Each line that starts with a persona name followed by a colon (`:`) is treated as dialogue for that persona.

## Basic Format

```markdown
# Episode Title

PERSONA_NAME: Dialogue text here
ANOTHER_PERSONA: More dialogue here
```

## Example

```markdown
# Welcome to The Talking Heads

ALICE: Hello everyone, and welcome to The Talking Heads!
BOB: Thanks for joining us!
ALICE: Today we're excited to have Charlie as our guest.
CHARLIE: Thanks for having me!
```

## Persona Names

- **Case-insensitive:** `ALICE`, `alice`, `Alice` all work
- **Must be defined:** Personas must be configured in `config/personas.yaml`
- **Max 5 personas:** The system supports 1-5 personas per episode

## Advanced Features (Future)

### Expression Annotations

```markdown
ALICE: [EXPRESSION:happy] I'm so excited about this!
BOB: [EXPRESSION:concerned] But what about the challenges?
```

Supported expressions:
- `happy`
- `sad`
- `surprised`
- `concerned`
- `neutral`
- `thinking`
- `excited`

### Gesture Annotations

```markdown
ALICE: [GESTURE:point] Let me explain this concept.
BOB: [GESTURE:wave] Welcome everyone!
```

Supported gestures:
- `point`
- `wave`
- `emphasize`
- `thinking`
- `welcome`
- `excited`

### Music Cues (Future)

```markdown
ALICE: Now let's move on to the next segment.
[MUSIC: upbeat background]
BOB: The music really sets the mood!
```

## Tips

1. **Clear persona names:** Use consistent, recognizable names
2. **Natural dialogue:** Write conversationally, as people actually speak
3. **One line per utterance:** Keep each persona line to a single statement
4. **Title format:** Start with `# Title` for episode title

## Limitations

- Maximum 5 personas per episode
- Personas must be configured in `config/personas.yaml`
- Each persona needs voice and avatar configuration
- Scripts should be under 10,000 words for optimal performance

## Examples

See `examples/scripts/` for complete example scripts.

