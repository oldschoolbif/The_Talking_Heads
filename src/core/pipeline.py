"""
Main Pipeline for The Talking Heads

Orchestrates the complete podcast generation workflow.
"""

import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import yaml

from src.core.script_parser import ScriptParser, ParsedScript, ScriptSegment
from src.core.persona_engine import PersonaEngine, Persona
from src.core.tts_engine import TTSEngine, AudioSegment
from src.core.audio_mixer import AudioMixer
from src.core.avatar_generator import AvatarGenerator, AvatarVideo
from src.core.scene_manager import SceneManager, Scene
from src.core.video_composer import VideoComposer, VideoComposition
from src.core.webhook_server import get_webhook_server


class Pipeline:
    """Main pipeline for orchestrating podcast generation."""

    def __init__(self, config: Dict[str, Any], project_root: Optional[Path] = None):
        """
        Initialize pipeline with configuration.

        Args:
            config: Configuration dictionary
            project_root: Root directory of the project (for resolving paths)
        """
        self.config = config
        self.project_root = project_root or Path.cwd()

        # Initialize components
        self.script_parser = ScriptParser()
        self.persona_engine = PersonaEngine()
        self.tts_engine = TTSEngine(config, cache_dir=Path(config.get("storage", {}).get("cache_dir", ".cache")) / "tts")
        self.audio_mixer = AudioMixer(output_dir=Path(config.get("storage", {}).get("temp_dir", ".cache/temp")))
        self.avatar_generator = AvatarGenerator(config, output_dir=Path(config.get("storage", {}).get("temp_dir", ".cache/temp")) / "avatars")
        self.scene_manager = SceneManager(project_root=self.project_root)
        self.video_composer = VideoComposer(config, output_dir=Path(config.get("storage", {}).get("outputs_dir", "outputs")))

        # Progress callback
        self.progress_callback: Optional[Callable[[str, float], None]] = None

        # Track temporary files for cleanup
        self.temp_files: List[Path] = []
        
        # Track pipeline start time for elapsed time reporting
        self.pipeline_start_time: Optional[float] = None
        
        # Webhook server for real-time API callbacks
        self.webhook_server = None
        self._init_webhook_server()

    def _init_webhook_server(self):
        """Initialize webhook server for API callbacks."""
        try:
            # Try to start webhook server
            webhook_config = self.config.get("webhook", {})
            if webhook_config.get("enabled", True):
                port = webhook_config.get("port", 5000)
                self.webhook_server = get_webhook_server(port=port)
                
                # Start Flask server if not already running
                if not self.webhook_server._running:
                    try:
                        self.webhook_server.start_flask_server()
                        self._report_progress("Webhook server started", 0.0)
                    except Exception as e:
                        print(f"[WARN] Could not start webhook server: {e}")
                        print("[WARN] Will use polling fallback for API status")
                        self.webhook_server = None
        except Exception as e:
            print(f"[WARN] Webhook server initialization failed: {e}")
            self.webhook_server = None
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """
        Set progress callback function.

        Args:
            callback: Function that takes (message: str, progress: float) where progress is 0.0-1.0
        """
        self.progress_callback = callback

    def _report_progress(self, message: str, progress: float):
        """Report progress if callback is set, including elapsed time."""
        if self.progress_callback:
            # Add elapsed time to message if pipeline has started
            if self.pipeline_start_time is not None:
                elapsed = time.time() - self.pipeline_start_time
                elapsed_str = f"{int(elapsed)}s elapsed"
                # Only add if not already present in message
                if "elapsed" not in message.lower():
                    message = f"{message} ({elapsed_str})"
            self.progress_callback(message, progress)

    def create_podcast(
        self,
        script_path: Optional[Path] = None,
        script_file: Optional[Path] = None,
        scene_name: str = "studio",
        layout: Optional[str] = None,
        output_name: Optional[str] = None,
        output_dir: Optional[Path] = None,
        cleanup_temp: bool = True,
    ) -> Path:
        """
        Create a complete podcast from script.

        Args:
            script_path: Path to script file
            scene_name: Name of scene to use (default: "studio")
            layout: Layout mode (default: from config)
            output_name: Output video filename (default: script name + .mp4)
            cleanup_temp: Whether to clean up temporary files (default: True)

        Returns:
            Path to final video file

        Raises:
            FileNotFoundError: If script file doesn't exist
            ValueError: If script or personas are invalid
            RuntimeError: If any step in the pipeline fails
        """
        try:
            # Handle script_path/script_file parameter
            if script_file is None:
                script_file = script_path
            if script_file is None:
                raise ValueError("Either script_path or script_file must be provided")
            
            # Track pipeline start time
            self.pipeline_start_time = time.time()
            
            # Step 1: Parse script
            self._report_progress("Step 1/7: Parsing script...", 0.0)
            parsed_script = self.script_parser.parse_file(script_file)
            self._report_progress(f"Step 1/7: Parsed {len(parsed_script.segments)} segments", 0.1)

            # Step 2: Load personas
            self._report_progress("Step 2/7: Loading personas...", 0.15)
            personas_config_path = self.project_root / self.config.get("personas_config", "config/personas.yaml")
            self.persona_engine.load_personas(personas_config_path)

            # Validate personas in script
            validation_errors = self.persona_engine.validate_script(parsed_script)
            if validation_errors:
                error_msg = "Script validation failed:\n" + "\n".join(validation_errors)
                raise ValueError(error_msg)

            # Build personas dictionary
            personas_dict = {}
            for persona_name in parsed_script.personas:
                persona = self.persona_engine.get_persona(persona_name)
                if persona:
                    personas_dict[persona_name] = persona

            self._report_progress(f"Step 2/7: Loaded {len(personas_dict)} personas", 0.2)

            # Step 3: Generate TTS audio
            self._report_progress("Step 3/7: Generating TTS audio...", 0.25)
            
            # Set progress callback on TTS engine so providers can report progress
            if self.progress_callback:
                self.tts_engine.set_progress_callback(self.progress_callback)
            
            total_segments = len(parsed_script.segments)
            audio_segments = []
            
            for idx, segment in enumerate(parsed_script.segments):
                progress = 0.25 + (idx / total_segments) * 0.25  # 25% to 50%
                persona_name = segment.persona.upper()
                self._report_progress(
                    f"Step 3/7: Generating audio {idx + 1}/{total_segments} for {persona_name}...",
                    progress
                )
                
                persona = personas_dict.get(persona_name)
                if not persona:
                    raise ValueError(f"Persona '{persona_name}' not found")
                
                audio_seg = self.tts_engine.generate_persona_audio(persona, segment.text)
                audio_segments.append(audio_seg)
            
            self._report_progress(f"Step 3/7: Generated {len(audio_segments)} audio segments", 0.5)

            # Track temp files
            for audio_seg in audio_segments:
                self.temp_files.append(audio_seg.audio_path)

            # Step 4: Mix audio tracks
            self._report_progress("Step 4/7: Mixing audio tracks...", 0.55)
            mixed_audio_path = self.audio_mixer.mix_persona_tracks(
                audio_segments, output_filename="mixed_audio.mp3", output_dir=self.audio_mixer.output_dir
            )
            self._report_progress("Step 4/7: Audio mixing complete", 0.6)
            self.temp_files.append(mixed_audio_path)

            # Step 5: Generate avatars with webhook support
            self._report_progress("Step 5/7: Generating avatars...", 0.65)
            
            # Set up webhook callbacks for avatar generation
            if self.webhook_server:
                base_url = self.webhook_server.get_base_url()
                print(f"[INFO] Using webhook server at {base_url}")
            
            # Set progress callback on avatar generator with progress mapping
            # Avatar generation progress (0.0-1.0) maps to pipeline progress (0.65-0.85)
            # CRITICAL: Don't map 0.0 to 0.65 immediately - start from actual progress
            if self.progress_callback:
                def mapped_progress_callback(message, progress):
                    # Map avatar generator progress (0.0-1.0) to pipeline progress (0.65-0.85)
                    if progress is None:
                        progress = 0.0
                    try:
                        avatar_progress = max(0.0, min(1.0, float(progress)))
                    except (ValueError, TypeError):
                        avatar_progress = 0.0
                    # Map: 0.0 -> 0.65 (start of avatar generation), 1.0 -> 0.85 (end)
                    # Only map if progress > 0, otherwise keep at 0.65
                    if avatar_progress > 0:
                        pipeline_progress = 0.65 + (avatar_progress * 0.20)
                    else:
                        pipeline_progress = 0.65  # Start of avatar generation step
                    self.progress_callback(message, pipeline_progress)
                
                self.avatar_generator.set_progress_callback(mapped_progress_callback)
            
            avatar_videos = self._generate_avatars_with_progress(
                parsed_script.segments, audio_segments, personas_dict, self.webhook_server
            )
            self._report_progress(f"Step 5/7: Generated {len(avatar_videos)} avatar videos", 0.85)

            # Track temp files
            for avatar_video in avatar_videos:
                self.temp_files.append(avatar_video.video_path)

            # Step 6: Load scene
            self._report_progress(f"Step 6/7: Loading scene '{scene_name}'...", 0.87)
            scenes_config_path = self.project_root / self.config.get("scenes_config", "config/scenes.yaml")
            self.scene_manager.load_scenes(scenes_config_path)
            scene = self.scene_manager.get_scene(scene_name)
            if not scene:
                raise ValueError(f"Scene '{scene_name}' not found")
            self._report_progress(f"Step 6/7: Scene '{scene_name}' loaded", 0.88)

            # Step 7: Compose final video
            self._report_progress("Step 7/7: Composing final video...", 0.9)
            if not output_name:
                output_name = f"{script_file.stem}_podcast.mp4"

            composition = self.video_composer.compose(
                mixed_audio_path, avatar_videos, scene=scene, layout=layout, output_filename=output_name
            )
            self._report_progress(f"Step 7/7: Video composition complete! Output: {composition.video_path}", 1.0)

            # Cleanup temporary files
            if cleanup_temp:
                self._cleanup_temp_files()

            return composition.video_path

        except Exception as e:
            # Cleanup on error
            if cleanup_temp:
                self._cleanup_temp_files()
            raise

    def _cleanup_temp_files(self):
        """Clean up temporary files."""
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    if temp_file.is_file():
                        temp_file.unlink()
                    elif temp_file.is_dir():
                        shutil.rmtree(temp_file)
            except Exception:
                pass  # Ignore cleanup errors

        self.temp_files.clear()

    def _generate_avatars_with_progress(
        self,
        segments: List[ScriptSegment],
        audio_segments: List[AudioSegment],
        personas: Dict[str, Persona],
        webhook_server=None,
    ) -> List[AvatarVideo]:
        """
        Generate avatars with progress tracking and webhook support.
        
        Args:
            segments: Script segments
            audio_segments: Audio segments
            personas: Persona dictionary
            webhook_server: Webhook server instance for API callbacks
            
        Returns:
            List of AvatarVideo objects
        """
        total_segments = len(segments)
        avatar_videos = []
        
        # Generate avatars one at a time to show progress
        for idx, (segment, audio_seg) in enumerate(zip(segments, audio_segments)):
            persona_name = segment.persona.upper()
            persona = personas.get(persona_name)
            
            if not persona:
                raise ValueError(f"Persona '{persona_name}' not found")
            
            progress = 0.65 + (idx / total_segments) * 0.20  # 65% to 85%
            self._report_progress(
                f"Step 5/7: Generating avatar {idx + 1}/{total_segments} for {persona_name}...",
                progress
            )
            
            try:
                avatar_video = self.avatar_generator.generate_persona_avatar(
                    persona,
                    audio_seg.audio_path,
                    expression=segment.expression,
                    gesture=segment.gesture,
                    text=segment.text,
                    webhook_server=webhook_server,
                )
                
                avatar_video.segment = segment
                avatar_videos.append(avatar_video)
                
                self._report_progress(
                    f"Step 5/7: Completed avatar {idx + 1}/{total_segments}",
                    progress + (0.20 / total_segments)
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to generate avatar for {persona_name} (segment {idx + 1}): {e}"
                ) from e
        
        return avatar_videos

    def validate_setup(self) -> List[str]:
        """
        Validate that pipeline is properly configured.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Check config files exist
        personas_config = self.project_root / self.config.get("personas_config", "config/personas.yaml")
        if not personas_config.exists():
            errors.append(f"Personas config not found: {personas_config}")

        scenes_config = self.project_root / self.config.get("scenes_config", "config/scenes.yaml")
        if not scenes_config.exists():
            errors.append(f"Scenes config not found: {scenes_config}")

        # Check TTS engine availability
        try:
            if not self.tts_engine.active_provider.is_available():
                errors.append("TTS engine is not available (check API keys and dependencies)")
        except Exception as e:
            errors.append(f"TTS engine error: {e}")

        # Check avatar generator availability
        try:
            provider = self.avatar_generator._get_provider(self.avatar_generator.engine)
            if not provider.is_available():
                errors.append("Avatar generator is not available (check API keys and dependencies)")
        except Exception as e:
            errors.append(f"Avatar generator error: {e}")

        return errors

