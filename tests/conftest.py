"""
Pytest configuration and fixtures for The Talking Heads
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import yaml


@pytest.fixture
def test_config(tmp_path: Path) -> Dict[str, Any]:
    """Provide a test configuration dictionary."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "api": {
            "heygen": {
                "api_key": "test_heygen_key",
                "base_url": "https://api.heygen.com/v1"
            },
            "did": {
                "api_key": "test_did_key",
                "base_url": "https://api.d-id.com"
            },
            "elevenlabs": {
                "api_key": "test_elevenlabs_key",
                "base_url": "https://api.elevenlabs.io/v1"
            }
        },
        "avatar": {
            "engine": "heygen",
            "style": "cartoon",
            "default_expression": "neutral",
            "fps": 30,
            "resolution": {
                "width": 1920,
                "height": 1080
            }
        },
        "tts": {
            "engine": "elevenlabs",
            "default_voice": None,
            "rate": 1.0,
            "pitch": 1.0
        },
        "video": {
            "resolution": {
                "width": 1920,
                "height": 1080
            },
            "fps": 30,
            "quality": "high",
            "format": "mp4",
            "codec": "h264"
        },
        "layout": {
            "mode": "switching",
            "max_avatars_visible": 2,
            "transition": {
                "type": "fade",
                "duration": 0.5
            }
        },
        "storage": {
            "outputs_dir": str(outputs_dir),
            "cache_dir": str(cache_dir),
            "temp_dir": str(cache_dir / "temp")
        },
        "personas_config": "config/personas.yaml",
        "scenes_config": "config/scenes.yaml"
    }


@pytest.fixture
def example_script(tmp_path: Path) -> Path:
    """Create an example script file for testing."""
    script_path = tmp_path / "example_script.txt"
    script_content = """# Test Episode

ALICE: Hello everyone, welcome to The Talking Heads!
BOB: Thanks for having us!
ALICE: Today we'll discuss AI.
BOB: That sounds great!
"""
    script_path.write_text(script_content, encoding="utf-8")
    return script_path


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

