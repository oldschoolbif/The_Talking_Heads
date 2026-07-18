"""
Unit tests for scene manager.
"""

import pytest
import yaml
from pathlib import Path
from src.core.scene_manager import SceneManager, Scene


class TestSceneManager:
    """Test cases for SceneManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = SceneManager()

    def test_load_scenes_from_file(self, tmp_path):
        """Test loading scenes from a YAML file."""
        config_file = tmp_path / "scenes.yaml"
        config_content = """
scenes:
  studio:
    name: "Podcast Studio"
    description: "Professional recording studio"
    background_url: "assets/scenes/studio.jpg"
    style: "professional"
    lighting: "warm"
    layout_hint: "centered"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.manager.load_scenes(config_file)

        assert self.manager.is_loaded()
        assert len(self.manager.get_all_scenes()) == 1

        studio = self.manager.get_scene("studio")
        assert studio is not None
        assert studio.name == "Podcast Studio"
        assert studio.key == "studio"
        assert studio.style == "professional"
        assert studio.lighting == "warm"

    def test_load_scenes_case_insensitive(self, tmp_path):
        """Test that scene lookup is case-insensitive."""
        config_file = tmp_path / "scenes.yaml"
        config_content = """
scenes:
  studio:
    name: "Podcast Studio"
    background_url: "assets/scenes/studio.jpg"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.manager.load_scenes(config_file)

        # All these should return the same scene
        assert self.manager.get_scene("studio") is not None
        assert self.manager.get_scene("STUDIO") is not None
        assert self.manager.get_scene("Studio") is not None
        assert self.manager.get_scene("STUDIO") == self.manager.get_scene("studio")

    def test_load_scenes_file_not_found(self, tmp_path):
        """Test that loading non-existent file raises FileNotFoundError."""
        config_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            self.manager.load_scenes(config_file)

    def test_load_scenes_invalid_yaml(self, tmp_path):
        """Test that invalid YAML raises ValueError."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid YAML"):
            self.manager.load_scenes(config_file)

    def test_load_scenes_missing_scenes_key(self, tmp_path):
        """Test that missing 'scenes' key raises ValueError."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("other_key: value", encoding="utf-8")

        with pytest.raises(ValueError, match="must contain 'scenes' key"):
            self.manager.load_scenes(config_file)

    def test_load_scenes_missing_required_fields(self, tmp_path):
        """Test that missing required fields raises ValueError."""
        config_file = tmp_path / "scenes.yaml"
        config_content = """
scenes:
  studio:
    # Missing name
    background_url: "assets/scenes/studio.jpg"
"""
        config_file.write_text(config_content, encoding="utf-8")

        with pytest.raises(ValueError, match="must have 'name' field"):
            self.manager.load_scenes(config_file)

    def test_get_scene_not_loaded(self):
        """Test that getting scene before loading raises RuntimeError."""
        with pytest.raises(RuntimeError, match="must be loaded"):
            self.manager.get_scene("studio")

    def test_get_scene_not_found(self, tmp_path):
        """Test that getting non-existent scene returns None."""
        config_file = tmp_path / "scenes.yaml"
        config_content = """
scenes:
  studio:
    name: "Podcast Studio"
    background_url: "assets/scenes/studio.jpg"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.manager.load_scenes(config_file)

        assert self.manager.get_scene("classroom") is None
        assert self.manager.get_scene("nonexistent") is None

    def test_get_all_scenes_not_loaded(self):
        """Test that getting all scenes before loading raises RuntimeError."""
        with pytest.raises(RuntimeError, match="must be loaded"):
            self.manager.get_all_scenes()

    def test_get_background_path_absolute(self, tmp_path):
        """Test getting background path for absolute path."""
        scene = Scene(
            key="studio",
            name="Studio",
            background_url=str(tmp_path / "background.jpg"),
        )

        # Create the file
        (tmp_path / "background.jpg").write_bytes(b"fake_image_data")

        path = self.manager.get_background_path(scene)
        assert path.is_absolute()
        assert path.exists()

    def test_get_background_path_relative(self, tmp_path):
        """Test getting background path for relative path."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        assets_dir = project_root / "assets" / "scenes"
        assets_dir.mkdir(parents=True)

        background_file = assets_dir / "studio.jpg"
        background_file.write_bytes(b"fake_image_data")

        manager = SceneManager(project_root=project_root)
        scene = Scene(
            key="studio",
            name="Studio",
            background_url="assets/scenes/studio.jpg",
        )

        path = manager.get_background_path(scene)
        assert path == background_file
        assert path.exists()

    def test_get_background_path_no_url(self):
        """Test getting background path when scene has no background_url."""
        scene = Scene(key="studio", name="Studio", background_url="")

        with pytest.raises(ValueError, match="has no background_url"):
            self.manager.get_background_path(scene)

    def test_validate_scene_valid(self, tmp_path):
        """Test validation when scene exists and has valid background."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        assets_dir = project_root / "assets" / "scenes"
        assets_dir.mkdir(parents=True)

        background_file = assets_dir / "studio.jpg"
        background_file.write_bytes(b"fake_image_data")

        config_file = tmp_path / "scenes.yaml"
        config_content = f"""
scenes:
  studio:
    name: "Podcast Studio"
    background_url: "assets/scenes/studio.jpg"
"""
        config_file.write_text(config_content, encoding="utf-8")

        manager = SceneManager(project_root=project_root)
        manager.load_scenes(config_file)

        errors = manager.validate_scene("studio")
        assert len(errors) == 0

    def test_validate_scene_not_found(self, tmp_path):
        """Test validation when scene doesn't exist."""
        config_file = tmp_path / "scenes.yaml"
        config_content = """
scenes:
  studio:
    name: "Podcast Studio"
    background_url: "assets/scenes/studio.jpg"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.manager.load_scenes(config_file)

        errors = self.manager.validate_scene("classroom")
        assert len(errors) == 1
        assert "not found" in errors[0]

    def test_validate_scene_missing_background(self, tmp_path):
        """Test validation when background image doesn't exist."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        config_file = tmp_path / "scenes.yaml"
        config_content = """
scenes:
  studio:
    name: "Podcast Studio"
    background_url: "assets/scenes/nonexistent.jpg"
"""
        config_file.write_text(config_content, encoding="utf-8")

        manager = SceneManager(project_root=project_root)
        manager.load_scenes(config_file)

        errors = manager.validate_scene("studio")
        assert len(errors) == 1
        assert "not found" in errors[0]

    def test_validate_scene_not_loaded(self):
        """Test that validation before loading raises RuntimeError."""
        with pytest.raises(RuntimeError, match="must be loaded"):
            self.manager.validate_scene("studio")

    def test_load_scenes_default_values(self, tmp_path):
        """Test that default values are used when optional fields are missing."""
        config_file = tmp_path / "scenes.yaml"
        config_content = """
scenes:
  studio:
    name: "Podcast Studio"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.manager.load_scenes(config_file)

        studio = self.manager.get_scene("studio")
        assert studio.description == ""
        assert studio.style == "professional"
        assert studio.lighting == "neutral"
        assert studio.layout_hint == "centered"

    def test_scene_to_dict(self, tmp_path):
        """Test scene to_dict conversion."""
        config_file = tmp_path / "scenes.yaml"
        config_content = """
scenes:
  studio:
    name: "Podcast Studio"
    description: "Test scene"
    background_url: "assets/scenes/studio.jpg"
    style: "professional"
    lighting: "warm"
    layout_hint: "centered"
"""
        config_file.write_text(config_content, encoding="utf-8")

        self.manager.load_scenes(config_file)

        studio = self.manager.get_scene("studio")
        scene_dict = studio.to_dict()

        assert scene_dict["key"] == "studio"
        assert scene_dict["name"] == "Podcast Studio"
        assert scene_dict["description"] == "Test scene"
        assert scene_dict["style"] == "professional"
        assert scene_dict["lighting"] == "warm"
        assert scene_dict["layout_hint"] == "centered"

    def test_load_real_scenes_config(self):
        """Test loading the actual scenes.yaml config file."""
        config_path = Path("config/scenes.yaml")
        if not config_path.exists():
            pytest.skip("config/scenes.yaml not found")

        manager = SceneManager(project_root=Path.cwd())
        manager.load_scenes(config_path)

        assert manager.is_loaded()
        scenes = manager.get_all_scenes()
        assert len(scenes) >= 5  # Should have studio, classroom, living_room, office, outdoors

        # Test getting each scene
        studio = manager.get_scene("studio")
        assert studio is not None
        assert studio.name == "Podcast Studio"

        classroom = manager.get_scene("classroom")
        assert classroom is not None
        assert classroom.name == "Classroom"

