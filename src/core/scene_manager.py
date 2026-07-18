"""
Scene Manager for The Talking Heads

Manages background scenes for podcast videos.
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class Scene:
    """Represents a scene configuration."""

    key: str  # The key in the YAML (e.g., "studio")
    name: str  # Display name (e.g., "Podcast Studio")
    description: str = ""
    background_url: str = ""
    style: str = "professional"
    lighting: str = "neutral"
    layout_hint: str = "centered"  # How avatars should be positioned

    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to dictionary."""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "background_url": self.background_url,
            "style": self.style,
            "lighting": self.lighting,
            "layout_hint": self.layout_hint,
        }


class SceneManager:
    """Manages scene configurations and background images."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize scene manager.

        Args:
            project_root: Root directory of the project (for resolving relative paths)
        """
        self._scenes: Dict[str, Scene] = {}
        self._loaded: bool = False
        self.project_root = project_root or Path.cwd()

    def load_scenes(self, config_path: Path) -> None:
        """
        Load scene configurations from YAML file.

        Args:
            config_path: Path to scenes.yaml configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid or missing required fields
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Scene config file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in scene config: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading scene config: {e}") from e

        if not config or "scenes" not in config:
            raise ValueError("Scene config must contain 'scenes' key")

        scenes_dict = config["scenes"]
        if not isinstance(scenes_dict, dict):
            raise ValueError("'scenes' must be a dictionary")

        self._scenes = {}
        for key, scene_data in scenes_dict.items():
            try:
                scene = self._parse_scene(key, scene_data)
                self._scenes[key.lower()] = scene
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(f"Invalid scene configuration for '{key}': {e}") from e

        self._loaded = True

    def _parse_scene(self, key: str, data: Dict[str, Any]) -> Scene:
        """Parse a single scene from configuration data."""
        if "name" not in data:
            raise ValueError("Scene must have 'name' field")

        return Scene(
            key=key.lower(),
            name=data["name"],
            description=data.get("description", ""),
            background_url=data.get("background_url", ""),
            style=data.get("style", "professional"),
            lighting=data.get("lighting", "neutral"),
            layout_hint=data.get("layout_hint", "centered"),
        )

    def get_scene(self, name: str) -> Optional[Scene]:
        """
        Get scene by name (case-insensitive).

        Args:
            name: Scene name (e.g., "studio", "STUDIO", "Studio")

        Returns:
            Scene object if found, None otherwise

        Raises:
            RuntimeError: If scenes haven't been loaded
        """
        if not self._loaded:
            raise RuntimeError("Scenes must be loaded before use. Call load_scenes() first.")

        return self._scenes.get(name.lower())

    def get_all_scenes(self) -> List[Scene]:
        """
        Get all loaded scenes.

        Returns:
            List of all Scene objects

        Raises:
            RuntimeError: If scenes haven't been loaded
        """
        if not self._loaded:
            raise RuntimeError("Scenes must be loaded before use. Call load_scenes() first.")

        return list(self._scenes.values())

    def get_background_path(self, scene: Scene) -> Path:
        """
        Get resolved path to background image for a scene.

        Args:
            scene: Scene object

        Returns:
            Path to background image file

        Raises:
            ValueError: If scene has no background_url
        """
        if not scene.background_url:
            raise ValueError(f"Scene '{scene.name}' has no background_url configured")

        background_path = Path(scene.background_url)

        # If absolute path, return as-is
        if background_path.is_absolute():
            return background_path

        # If relative path, resolve from project root
        # First try relative to config file location, then project root
        resolved_path = (self.project_root / background_path).resolve()

        return resolved_path

    def validate_scene(self, scene_name: str) -> List[str]:
        """
        Validate that a scene exists and has required resources.

        Args:
            scene_name: Name of scene to validate

        Returns:
            List of error messages (empty if valid)

        Raises:
            RuntimeError: If scenes haven't been loaded
        """
        if not self._loaded:
            raise RuntimeError("Scenes must be loaded before validation. Call load_scenes() first.")

        errors = []

        scene = self.get_scene(scene_name)
        if not scene:
            errors.append(f"Scene '{scene_name}' not found in scenes.yaml")
            return errors

        # Check if background image exists
        if scene.background_url:
            try:
                background_path = self.get_background_path(scene)
                if not background_path.exists():
                    errors.append(f"Background image not found: {background_path}")
            except ValueError:
                errors.append(f"Scene '{scene_name}' has invalid background_url: {scene.background_url}")

        return errors

    def is_loaded(self) -> bool:
        """Check if scenes have been loaded."""
        return self._loaded

