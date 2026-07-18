"""
Configuration loader for The Talking Heads

Loads configuration from YAML files with environment variable overrides.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def load_config(config_path: Path, project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable overrides.

    Args:
        config_path: Path to config.yaml file
        project_root: Root directory of the project (for resolving relative paths)

    Returns:
        Configuration dictionary with environment variable overrides applied

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    # Load .env file if available
    if DOTENV_AVAILABLE:
        if project_root:
            env_path = project_root / ".env"
        else:
            env_path = Path(".env")
        
        if env_path.exists():
            load_dotenv(env_path)
    
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config: {e}") from e
    except Exception as e:
        raise ValueError(f"Error reading config: {e}") from e

    if not config:
        config = {}

    # Override with environment variables
    _apply_env_overrides(config)

    return config


def _apply_env_overrides(config: Dict[str, Any]):
    """
    Apply environment variable overrides to config.

    Args:
        config: Configuration dictionary to modify in-place
    """
    # Override API keys
    if "api" in config:
        api_config = config["api"]

        # HeyGen
        if "heygen" in api_config:
            heygen_key = os.getenv("HEYGEN_API_KEY")
            if heygen_key:
                api_config["heygen"]["api_key"] = heygen_key

        # D-ID
        if "did" in api_config:
            did_key = os.getenv("DID_API_KEY")
            if did_key:
                api_config["did"]["api_key"] = did_key

        # ElevenLabs
        if "elevenlabs" in api_config:
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            if elevenlabs_key:
                api_config["elevenlabs"]["api_key"] = elevenlabs_key

        # Azure Speech
        if "azure" in api_config:
            azure_key = os.getenv("AZURE_SPEECH_KEY")
            if azure_key:
                api_config["azure"]["speech_key"] = azure_key
            azure_region = os.getenv("AZURE_SPEECH_REGION")
            if azure_region:
                api_config["azure"]["speech_region"] = azure_region

