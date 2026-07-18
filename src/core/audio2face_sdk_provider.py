"""
Audio2Face SDK Provider - Direct integration with GitHub Audio2Face-3D-SDK.

This provider uses the Audio2Face SDK C++ library directly via subprocess calls
to a wrapper executable or via ctypes (future implementation).
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any

# Configure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from src.core.avatar_provider_base import AvatarProvider


class Audio2FaceSDKProvider(AvatarProvider):
    """
    Audio2Face SDK provider using the GitHub Audio2Face-3D-SDK.
    
    This provider uses the built SDK directly, without requiring Omniverse.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize Audio2Face SDK provider."""
        super().__init__(config)
        
        # Get SDK-specific config
        sdk_config = config.get("audio2face_sdk", {})
        
        # SDK build path (e.g., d:\dev\Audio2Face-3D-SDK\_build\release)
        self.sdk_build_path = Path(sdk_config.get("sdk_build_path", 
            "d:/dev/Audio2Face-3D-SDK/_build/release"))
        
        # SDK base path (for finding models and data)
        self.sdk_base_path = Path(sdk_config.get("sdk_base_path",
            "d:/dev/Audio2Face-3D-SDK"))
        
        # Model path (path to model.json)
        self.model_path = sdk_config.get("model_path")
        if not self.model_path:
            # Try default location
            default_model = self.sdk_base_path / "_data" / "generated" / "audio2face-sdk" / "samples" / "data" / "mark" / "model.json"
            if default_model.exists():
                self.model_path = str(default_model)
        
        # Wrapper executable path
        wrapper_exe = self.sdk_build_path / "audio2face-sdk" / "bin" / "a2f-wrapper.exe"
        self.wrapper_exe = wrapper_exe if wrapper_exe.exists() else None
        
        # Output directory
        output_dir = sdk_config.get("output_dir", ".cache/audio2face_sdk_outputs")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Settings
        self.fps = sdk_config.get("fps", 60.0)
        
        # Environment setup (CUDA, TensorRT paths)
        self.cuda_path = os.getenv("CUDA_PATH", "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v13.0")
        self.tensorrt_root = os.getenv("TENSORRT_ROOT_DIR", "D:\\dev\\TensorRT-10.14.1.48")

    def is_available(self) -> bool:
        """Check if Audio2Face SDK is available."""
        try:
            # Check if SDK build directory exists
            if not self.sdk_build_path.exists():
                return False
            
            # Check if audio2x.dll exists
            audio2x_dll = self.sdk_build_path / "audio2x-sdk" / "bin" / "audio2x.dll"
            if not audio2x_dll.exists():
                return False
            
            # Check if model exists (if specified)
            if self.model_path and not Path(self.model_path).exists():
                return False
            
            # Check if wrapper exists (optional - we can create one if needed)
            # For now, wrapper is optional
            
            return True
        except Exception:
            return False

    def _setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for SDK execution."""
        env = os.environ.copy()
        
        # Add SDK DLL to PATH
        audio2x_bin = self.sdk_build_path / "audio2x-sdk" / "bin"
        if audio2x_bin.exists():
            current_path = env.get("PATH", "")
            env["PATH"] = str(audio2x_bin) + os.pathsep + current_path
        
        # Add CUDA to PATH
        if Path(self.cuda_path).exists():
            cuda_bin = Path(self.cuda_path) / "bin"
            if cuda_bin.exists():
                current_path = env.get("PATH", "")
                env["PATH"] = str(cuda_bin) + os.pathsep + current_path
        
        # Add TensorRT to PATH
        if Path(self.tensorrt_root).exists():
            trt_lib = Path(self.tensorrt_root) / "lib"
            if trt_lib.exists():
                current_path = env.get("PATH", "")
                env["PATH"] = str(trt_lib) + os.pathsep + current_path
        
        # Set CUDA_PATH and TENSORRT_ROOT_DIR
        env["CUDA_PATH"] = self.cuda_path
        env["TENSORRT_ROOT_DIR"] = self.tensorrt_root
        
        return env

    def generate(
        self,
        audio_path: Path,
        avatar_id: str,
        expression: Optional[str] = None,
        gesture: Optional[str] = None,
        text: Optional[str] = None,
        source_image: Optional[Path] = None,
        **kwargs
    ) -> tuple[Path, float]:
        """
        Generate avatar video using Audio2Face SDK.
        
        Args:
            audio_path: Path to audio file (must be 16kHz WAV)
            avatar_id: Path to character USD file
            expression: Expression to apply (not yet supported)
            gesture: Gesture to apply (not yet supported)
            text: Optional text (for logging)
            source_image: Not used for SDK provider
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (video_path, duration_seconds)
        
        Raises:
            RuntimeError: If generation fails
        """
        if not self.is_available():
            raise RuntimeError(
                "Audio2Face SDK is not available. "
                "Ensure the SDK is built and model files are downloaded."
            )
        
        # Validate inputs
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        character_usd = Path(avatar_id)
        if not character_usd.exists():
            raise FileNotFoundError(f"Character USD file not found: {character_usd}")
        
        # Get audio duration
        try:
            import librosa
            audio_data, sr = librosa.load(str(audio_path), sr=None)
            duration = len(audio_data) / sr if sr > 0 else 5.0
        except Exception:
            duration = 5.0  # Default estimate
        
        # Report progress
        self._report_progress("Audio2Face SDK: Starting generation...", 0.1)
        
        # Create output USD path
        output_usd = self.output_dir / f"{audio_path.stem}_animated.usd"
        
        # Check if wrapper executable exists
        if self.wrapper_exe and self.wrapper_exe.exists():
            # Use wrapper executable
            self._report_progress("Audio2Face SDK: Using wrapper executable...", 0.2)
            return self._generate_via_wrapper(audio_path, character_usd, output_usd, duration)
        else:
            # Wrapper doesn't exist - need to build it or use alternative method
            raise RuntimeError(
                "Audio2Face SDK wrapper executable not found. "
                "The wrapper needs to be built first. "
                f"Expected location: {self.wrapper_exe}\n\n"
                "To build the wrapper:\n"
                "1. Add the wrapper source to the SDK build\n"
                "2. Rebuild the SDK\n"
                "3. Or implement direct DLL access via ctypes"
            )

    def _generate_via_wrapper(
        self,
        audio_path: Path,
        character_usd: Path,
        output_usd: Path,
        duration: float
    ) -> tuple[Path, float]:
        """Generate animation using wrapper executable."""
        self._report_progress("Audio2Face SDK: Running wrapper executable...", 0.3)
        
        # Prepare command
        cmd = [
            str(self.wrapper_exe),
            str(audio_path),
            str(character_usd),
            str(output_usd),
        ]
        
        # Add model path if specified
        if self.model_path:
            cmd.append(self.model_path)
        
        # Add FPS
        cmd.append(str(int(self.fps)))
        
        # Setup environment
        env = self._setup_environment()
        
        # Run wrapper
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.sdk_build_path),
                env=env,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                error_msg = result.stderr[:500] if result.stderr else result.stdout[-500:]
                raise RuntimeError(
                    f"Audio2Face SDK wrapper failed (exit code {result.returncode}):\n{error_msg}"
                )
            
            # Check if output was created
            if not output_usd.exists():
                raise RuntimeError(
                    f"Audio2Face SDK wrapper completed but output file not found: {output_usd}\n"
                    f"Wrapper output: {result.stdout[-1000:]}"
                )
            
            self._report_progress("Audio2Face SDK: Animation generated successfully", 0.9)
            
            # TODO: Convert USD to video
            # For now, return the USD file (video conversion needs to be implemented)
            # This would require USD rendering (e.g., using USD's renderer or Omniverse)
            
            raise RuntimeError(
                "Audio2Face SDK generated animation data, but video conversion is not yet implemented.\n"
                f"Animated USD file created at: {output_usd}\n"
                "To convert USD to video, you need:\n"
                "1. USD renderer (e.g., USD's renderer, Omniverse, or Blender)\n"
                "2. Or use the SDK's geometry output directly with a mesh renderer"
            )
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Audio2Face SDK wrapper timed out after 5 minutes")
        except Exception as e:
            raise RuntimeError(f"Audio2Face SDK wrapper execution failed: {e}") from e

