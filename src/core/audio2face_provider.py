"""
NVIDIA Audio2Face provider for avatar generation.

Audio2Face is part of NVIDIA Omniverse and provides high-quality facial animation
from audio input. This provider integrates with Audio2Face via Omniverse Python API.
"""

import os
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Optional, Any

from src.core.avatar_provider_base import AvatarProvider


class Audio2FaceProvider(AvatarProvider):
    """NVIDIA Audio2Face provider for avatar generation via Omniverse."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Audio2Face provider."""
        super().__init__(config)
        
        # Get Audio2Face-specific config
        a2f_config = config.get("audio2face", {})
        
        # Audio2Face installation path (for py-audio2face)
        # This can be:
        # 1. Omniverse Audio2Face extension path
        # 2. Audio2Face-3D-SDK build path  
        # 3. Audio2Face standalone installation
        self.a2f_install_path = a2f_config.get("a2f_install_path")
        if not self.a2f_install_path:
            # Try to detect default locations
            if os.name == 'nt':  # Windows
                appdata = os.getenv('LOCALAPPDATA', '')
                if appdata:
                    # Check Omniverse location for Audio2Face extension
                    ov_path = Path(appdata) / "ov" / "pkg"
                    if ov_path.exists():
                        # Look for Audio2Face in Omniverse packages (common names)
                        for pkg_dir in ov_path.iterdir():
                            if pkg_dir.is_dir():
                                pkg_name_lower = pkg_dir.name.lower()
                                if any(term in pkg_name_lower for term in ["audio2face", "a2f", "omni.audio2face"]):
                                    self.a2f_install_path = str(pkg_dir)
                                    break
                                # Also check subdirectories
                                try:
                                    for subdir in pkg_dir.iterdir():
                                        if subdir.is_dir() and "audio2face" in subdir.name.lower():
                                            self.a2f_install_path = str(subdir)
                                            break
                                    if self.a2f_install_path:
                                        break
                                except (PermissionError, OSError):
                                    pass
                    # Check Audio2Face-3D-SDK location (fallback)
                    if not self.a2f_install_path:
                        sdk_paths = [
                            Path("d:/dev/Audio2Face-3D-SDK"),
                            Path.home() / "dev" / "Audio2Face-3D-SDK",
                            Path.cwd().parent / "Audio2Face-3D-SDK"
                        ]
                        for sdk_path in sdk_paths:
                            if sdk_path.exists():
                                self.a2f_install_path = str(sdk_path)
                                break
        
        # Omniverse installation path (for fallback methods)
        omniverse_path = a2f_config.get("omniverse_path")
        if omniverse_path:
            self.omniverse_path = Path(omniverse_path).expanduser()
        else:
            # Try to detect default location
            if os.name == 'nt':  # Windows
                appdata = os.getenv('LOCALAPPDATA', '')
                self.omniverse_path = Path(appdata) / "ov" / "pkg" if appdata else None
            else:  # Linux/Mac
                self.omniverse_path = Path.home() / ".nvidia-omniverse" / "pkg"
        
        # Audio2Face extension path (if custom)
        self.a2f_extension_path = a2f_config.get("extension_path")
        
        # Character USD file path (required)
        # Can be set per persona or globally
        self.default_character_usd = a2f_config.get("default_character_usd")
        
        # Output directory for results
        output_dir = a2f_config.get("output_dir", ".cache/audio2face_outputs")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Python executable for Omniverse (usually comes with Omniverse)
        self.python_exec = a2f_config.get("python_exec", "python")
        
        # Audio2Face settings
        self.fps = a2f_config.get("fps", 60.0)
        self.quality = a2f_config.get("quality", "high")  # low, medium, high
        
        # Check if we can use Audio2Face Python API
        self.use_api = a2f_config.get("use_api", True)
        
    def is_available(self) -> bool:
        """Check if Audio2Face is available (multiple methods)."""
        try:
            # Method 1: Check py_audio2face (preferred)
            try:
                from py_audio2face import Audio2Face
                # Package is available - Audio2Face can work with Omniverse or SDK
                return True
            except ImportError:
                pass  # py_audio2face not installed, try other methods
            
            # Method 2: Check Omniverse installation
            if self.omniverse_path and self.omniverse_path.exists():
                # Check if Audio2Face extension exists
                if self._check_a2f_application():
                    return True
                
                # Try importing Omniverse API
                try:
                    import sys
                    omniverse_python_paths = [
                        str(self.omniverse_path / "omni.audio2face" / "exts" / "omni.audio2face"),
                        str(self.omniverse_path / "omni.audio2face"),
                    ]
                    for path in omniverse_python_paths:
                        if Path(path).exists() and path not in sys.path:
                            sys.path.insert(0, path)
                    
                    try:
                        import omni.audio2face as a2f
                        return True
                    except ImportError:
                        pass
                except Exception:
                    pass
            
            # Method 3: Check if Audio2Face application exists
            return self._check_a2f_application()
                
        except Exception:
            return False
    
    def _check_a2f_application(self) -> bool:
        """Check if Audio2Face application/extension is available."""
        # Check for Audio2Face extension in Omniverse
        if self.omniverse_path and self.omniverse_path.exists():
            # Look for Audio2Face extension
            a2f_ext_paths = [
                self.omniverse_path / "omni.audio2face",
                self.omniverse_path / "exts" / "omni.audio2face",
            ]
            for path in a2f_ext_paths:
                if path.exists():
                    return True
        return False

    def generate(
        self, audio_path: Path, avatar_id: str, expression: Optional[str] = None, gesture: Optional[str] = None, text: Optional[str] = None, **kwargs
    ) -> tuple[Path, float]:
        """
        Generate avatar video using Audio2Face.

        Args:
            audio_path: Path to audio file (WAV format preferred)
            avatar_id: Character USD file path or character name
            expression: Expression to apply (optional, Audio2Face handles this automatically)
            gesture: Gesture to apply (optional, not directly supported)
            text: Text to speak (optional, not used - we use audio_path)
            **kwargs: Additional parameters
                - character_usd: Override character USD path
                - output_usd: Output USD animation file path
                - export_video: Whether to export to video (default: True)

        Returns:
            Tuple of (video_path, duration_seconds)

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If generation fails
        """
        if not self.is_available():
            raise RuntimeError(
                "Audio2Face is not available. Ensure NVIDIA Omniverse is installed and Audio2Face extension is available.\n"
                f"Omniverse path: {self.omniverse_path}\n"
                "Install from: https://www.nvidia.com/en-us/omniverse/"
            )

        if not audio_path or not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        # Get character USD path
        character_usd = kwargs.get("character_usd") or avatar_id or self.default_character_usd
        if not character_usd:
            raise ValueError(
                "Character USD file is required. Provide 'character_usd' in kwargs, "
                "set 'avatar_id' to USD path, or configure 'default_character_usd' in config."
            )
        
        character_usd_path = Path(character_usd)
        if not character_usd_path.exists():
            raise ValueError(f"Character USD file not found: {character_usd_path}")

        # Get audio duration
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(audio_path))
            duration = len(audio) / 1000.0  # Convert to seconds
        except Exception:
            # Fallback: estimate duration
            duration = 5.0

        # Ensure audio is in WAV format (Audio2Face prefers WAV)
        audio_wav_path = self._ensure_wav_format(audio_path)

        # Generate output paths
        output_name = kwargs.get("output_filename") or f"a2f_{audio_path.stem}"
        output_usd = kwargs.get("output_usd") or (self.output_dir / f"{output_name}.usd")
        output_video = self.output_dir / f"{output_name}.mp4"

        # Generate animation using Audio2Face
        self._report_progress("Audio2Face: Generating facial animation...", 0.2)
        
        try:
            if self.use_api:
                # Use Audio2Face Python API
                animation_usd = self._generate_via_api(
                    audio_wav_path, character_usd_path, output_usd, **kwargs
                )
            else:
                # Use Audio2Face extension/application
                animation_usd = self._generate_via_extension(
                    audio_wav_path, character_usd_path, output_usd, **kwargs
                )
            
            self._report_progress("Audio2Face: Animation generated, exporting video...", 0.8)
            
            # Export to video if requested
            export_video = kwargs.get("export_video", True)
            if export_video:
                video_path = self._export_to_video(animation_usd, output_video, duration, **kwargs)
            else:
                # Return USD file as "video" (can be converted later)
                video_path = animation_usd
            
            self._report_progress("Audio2Face: Video generation complete!", 1.0)
            
            return video_path, duration
            
        except Exception as e:
            raise RuntimeError(f"Audio2Face generation failed: {str(e)}") from e

    def _ensure_wav_format(self, audio_path: Path) -> Path:
        """Convert audio to WAV format if needed."""
        if audio_path.suffix.lower() == '.wav':
            return audio_path
        
        # Convert to WAV
        wav_path = self.output_dir / f"{audio_path.stem}.wav"
        try:
            import subprocess
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(audio_path),
                    "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1",
                    str(wav_path)
                ],
                capture_output=True,
                check=True,
                timeout=30
            )
            return wav_path
        except Exception as e:
            # Fallback: try pydub
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(str(audio_path))
                audio.export(str(wav_path), format="wav")
                return wav_path
            except Exception:
                # If conversion fails, try original file
                return audio_path

    def _generate_via_api(
        self, audio_path: Path, character_usd: Path, output_usd: Path, **kwargs
    ) -> Path:
        """Generate animation using Audio2Face Python API (py_audio2face)."""
        try:
            # Try py_audio2face first (recommended method)
            try:
                from py_audio2face import Audio2Face
                
                # Get server URL from config or use default (Audio2Face uses 8011 by default)
                api_url = kwargs.get("api_url") or self.config.get("audio2face", {}).get("server_url", "http://localhost:8011")
                
                # Get Audio2Face install path (for Omniverse installation)
                a2f_install_path = kwargs.get("a2f_install_path") or self.config.get("audio2face", {}).get("a2f_install_path")
                
                self._report_progress(f"Audio2Face: Initializing Audio2Face (API: {api_url})...", 0.3)
                
                # Create Audio2Face instance
                # Use detected install path if not provided
                install_path = a2f_install_path or self.a2f_install_path
                a2f = Audio2Face(
                    api_url=api_url,
                    a2f_install_path=install_path,
                    output_dir=str(self.output_dir)
                )
                
                # Initialize Audio2Face (starts headless server if needed)
                self._report_progress("Audio2Face: Starting Audio2Face server...", 0.4)
                a2f.init_a2f(streaming=False)
                
                # Generate animation
                self._report_progress("Audio2Face: Generating animation...", 0.5)
                output_path = a2f.audio2face_single(
                    audio_file_path=str(audio_path),
                    output_path=str(output_usd),
                    fps=int(self.fps),
                    emotion_auto_detect=True
                )
                
                if output_path and Path(output_path).exists():
                    self._report_progress("Audio2Face: Animation generated successfully", 0.9)
                    return Path(output_path)
                else:
                    raise RuntimeError(f"Audio2Face output file not found: {output_path}")
                    
            except ImportError:
                # py_audio2face not installed, try Omniverse Python API
                self._report_progress("Audio2Face: py_audio2face not found, trying Omniverse API...", 0.3)
                return self._generate_via_omniverse_api(audio_path, character_usd, output_usd, **kwargs)
                
        except Exception as e:
            # If API fails, fall back to extension method
            self._report_progress(f"Audio2Face: API method failed ({str(e)}), trying extension method...", 0.3)
            return self._generate_via_extension(audio_path, character_usd, output_usd, **kwargs)
    
    def _generate_via_omniverse_api(
        self, audio_path: Path, character_usd: Path, output_usd: Path, **kwargs
    ) -> Path:
        """Generate animation using Omniverse Python API (if available)."""
        try:
            # Try to import Omniverse modules
            import sys
            
            # Add Omniverse Python paths
            if self.omniverse_path and self.omniverse_path.exists():
                omniverse_python_paths = [
                    str(self.omniverse_path / "omni.audio2face" / "exts" / "omni.audio2face"),
                    str(self.omniverse_path / "omni.audio2face"),
                    str(self.omniverse_path),
                ]
                for path in omniverse_python_paths:
                    if Path(path).exists() and path not in sys.path:
                        sys.path.insert(0, path)
            
            # Try importing Audio2Face modules
            try:
                import omni.audio2face as a2f
                from pxr import Usd
                
                # Initialize Audio2Face
                a2f.initialize()
                
                # Load character
                a2f.load_character(str(character_usd))
                
                # Generate animation from audio
                a2f.generate_animation(
                    audio_file=str(audio_path),
                    output_file=str(output_usd),
                    fps=self.fps,
                    quality=self.quality
                )
                
                return output_usd
                
            except ImportError as e:
                raise RuntimeError(
                    f"Omniverse Audio2Face API not available: {str(e)}\n"
                    f"Install py_audio2face: pip install py-audio2face\n"
                    f"Or ensure Omniverse Audio2Face extension is installed."
                ) from e
                
        except Exception as e:
            raise RuntimeError(f"Omniverse API error: {str(e)}") from e

    def _generate_via_extension(
        self, audio_path: Path, character_usd: Path, output_usd: Path, **kwargs
    ) -> Path:
        """Generate animation using Audio2Face extension/application."""
        # Audio2Face can be used via Omniverse Kit scripting
        # We'll create a Python script that uses the Audio2Face extension
        
        script_content = f"""
import sys
import os
from pathlib import Path

# Add Omniverse paths
sys.path.insert(0, r"{self.omniverse_path}")

try:
    import omni.audio2face as a2f
    from pxr import Usd
    
    # Initialize Audio2Face
    a2f.initialize()
    
    # Load character
    character_path = r"{character_usd}"
    a2f.load_character(character_path)
    
    # Generate animation
    audio_path = r"{audio_path}"
    output_path = r"{output_usd}"
    
    a2f.generate_animation(
        audio_file=audio_path,
        output_file=output_path,
        fps={self.fps},
        quality="{self.quality}"
    )
    
    print(f"Audio2Face: Animation saved to {{output_path}}")
    
except Exception as e:
    print(f"Error: {{e}}")
    sys.exit(1)
"""
        
        # Write script to temp file
        script_path = self.output_dir / "a2f_generate.py"
        script_path.write_text(script_content)
        
        # Run script via Omniverse Python
        try:
            # Try to find Omniverse Python executable
            omniverse_python = self._find_omniverse_python()
            
            result = subprocess.run(
                [omniverse_python, str(script_path)],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes max
                cwd=str(self.output_dir)
            )
            
            if result.returncode != 0:
                raise RuntimeError(
                    f"Audio2Face script failed: {result.stderr}\n{result.stdout}"
                )
            
            if not output_usd.exists():
                raise RuntimeError(f"Audio2Face output file not created: {output_usd}")
            
            return output_usd
            
        except FileNotFoundError:
            raise RuntimeError(
                "Omniverse Python executable not found. "
                "Ensure NVIDIA Omniverse is installed and Audio2Face extension is available."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio2Face generation timed out (10 minutes)")

    def _find_omniverse_python(self) -> str:
        """Find Omniverse Python executable."""
        # Common locations for Omniverse Python
        if os.name == 'nt':  # Windows
            appdata = os.getenv('LOCALAPPDATA', '')
            if appdata:
                python_paths = [
                    Path(appdata) / "ov" / "pkg" / "omni.audio2face" / "python.exe",
                    Path(appdata) / "ov" / "pkg" / "python.exe",
                ]
        else:  # Linux
            python_paths = [
                Path.home() / ".nvidia-omniverse" / "pkg" / "omni.audio2face" / "python",
                Path.home() / ".nvidia-omniverse" / "pkg" / "python",
            ]
        
        for path in python_paths:
            if Path(path).exists():
                return str(path)
        
        # Fallback to system Python (may not work, but worth trying)
        return self.python_exec

    def _export_to_video(
        self, usd_path: Path, output_video: Path, duration: float, **kwargs
    ) -> Path:
        """Export USD animation to video."""
        # Audio2Face typically outputs USD files, not videos directly
        # We need to render the USD to video
        
        # Try using py_audio2face export if available
        try:
            from py_audio2face import Audio2Face
            api_url = kwargs.get("api_url") or self.config.get("audio2face", {}).get("server_url", "http://localhost:8011")
            a2f_install_path = kwargs.get("a2f_install_path") or self.config.get("audio2face", {}).get("a2f_install_path")
            a2f = Audio2Face(api_url=api_url, a2f_install_path=a2f_install_path, output_dir=str(self.output_dir))
            
            # Try to export USD to video using Audio2Face export method
            # Note: py_audio2face may have export methods - check available methods
            if hasattr(a2f, 'export'):
                result = a2f.export(
                    usd_file=str(usd_path),
                    output_path=str(output_video)
                )
                if output_video.exists():
                    return output_video
        except Exception as e:
            print(f"[WARN] Audio2Face export failed: {e}, trying alternative methods...")
            pass  # Fall through to alternative methods
        
        # Alternative: Use Omniverse Kit/Create to render
        # This requires Omniverse to be running
        try:
            return self._render_usd_to_video(usd_path, output_video, duration, **kwargs)
        except Exception:
            pass
        
        # Fallback: Return USD file and note that video export needs manual step
        # Or use FFmpeg if we can extract frames somehow
        self._report_progress(
            "Audio2Face: Video export not available, returning USD file. "
            "Use Omniverse Create to render USD to video, or configure video export.",
            0.9
        )
        
        # For now, return USD - user can render manually or we'll add rendering later
        return usd_path
    
    def _render_usd_to_video(
        self, usd_path: Path, output_video: Path, duration: float, **kwargs
    ) -> Path:
        """Render USD to video using Omniverse (if available)."""
        # This is a placeholder - actual implementation would use Omniverse rendering
        # For now, we'll need to handle this differently
        
        # Option 1: Use Omniverse Kit command line rendering (if available)
        # Option 2: Use py_audio2face export functionality
        # Option 3: Return USD and let user render manually
        
        raise NotImplementedError(
            "USD to video rendering not yet implemented. "
            "Audio2Face outputs USD files - use Omniverse Create to render to video, "
            "or configure py_audio2face export functionality."
        )

