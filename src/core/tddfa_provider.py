"""
3DDFA-based avatar generation provider.

Uses 3DDFA_V2 to reconstruct 3D faces from 2D images.
This provider processes the image and creates an enhanced version.
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import time

from src.core.avatar_provider_base import AvatarProvider


class TDDFAProvider(AvatarProvider):
    """3DDFA provider for 3D face reconstruction from 2D images."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize 3DDFA provider."""
        super().__init__(config)
        
        # 3DDFA installation path
        self.tddfa_path = Path(config.get("tddfa_path", "d:/dev/3DDFA_V2"))
        if not self.tddfa_path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            self.tddfa_path = project_root / self.tddfa_path
        
        # Python executable
        self.python_exec = config.get("python_exec", "python")
        
        # Config file
        self.config_file = self.tddfa_path / config.get("config_file", "configs/mb1_120x120.yml")
        
        # Output directory
        self.result_dir = Path(config.get("result_dir", self.tddfa_path / "examples" / "results"))
        self.result_dir.mkdir(parents=True, exist_ok=True)
        
        # Default source image
        self.default_source_image = config.get("default_source_image")

    def is_available(self) -> bool:
        """Check if 3DDFA is available."""
        # Check if 3DDFA directory exists
        if not self.tddfa_path.exists():
            return False
        
        # Check if demo script exists
        demo_script = self.tddfa_path / "demo.py"
        if not demo_script.exists():
            return False
        
        # Check if config file exists
        if not self.config_file.exists():
            return False
        
        # Check if Python can import required packages
        try:
            result = subprocess.run(
                [self.python_exec, "-c", "import torch; import cv2; import numpy"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

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
        Generate avatar video using 3DDFA processing.
        
        Note: 3DDFA reconstructs 3D faces but doesn't animate them directly.
        This implementation processes the image and creates an enhanced version.
        
        Args:
            audio_path: Path to audio file (used for duration)
            avatar_id: Can be a path to source image or identifier
            expression: Not directly used (3DDFA reconstructs neutral face)
            gesture: Not used
            text: Optional text (for logging)
            source_image: Path to source headshot image (overrides avatar_id)
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (video_path, duration_seconds)
        """
        if not self.is_available():
            raise RuntimeError("3DDFA is not available. Please check installation.")
        
        # Determine source image path
        if source_image:
            img_path = Path(source_image)
        elif avatar_id and Path(avatar_id).exists():
            img_path = Path(avatar_id)
        elif self.default_source_image and Path(self.default_source_image).exists():
            img_path = Path(self.default_source_image)
        else:
            raise ValueError(
                f"Source image not found. Provide source_image parameter, "
                f"set avatar_id to image path, or configure default_source_image."
            )
        
        if not img_path.exists():
            raise FileNotFoundError(f"Source image not found: {img_path}")
        
        # Get audio duration
        try:
            import librosa
            audio_data, sr = librosa.load(str(audio_path), sr=None)
            duration = len(audio_data) / sr
        except Exception:
            duration = 5.0  # Default estimate
        
        # Report progress
        self._report_progress("3DDFA: Processing image for 3D reconstruction...", 0.1)
        
        # Copy image to 3DDFA's input directory to avoid path issues
        # 3DDFA has issues with absolute Windows paths in output filenames
        tddfa_input_dir = self.tddfa_path / "examples" / "inputs"
        tddfa_input_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy image to input directory with simple name
        img_name = img_path.stem
        input_image = tddfa_input_dir / f"{img_name}.{img_path.suffix.lstrip('.')}"
        if not input_image.exists() or input_image.stat().st_mtime < img_path.stat().st_mtime:
            import shutil
            shutil.copy2(img_path, input_image)
        
        # Prepare demo command
        demo_script = self.tddfa_path / "demo.py"
        
        # Build command - use PLY output for mesh generation
        # 3DDFA can output: 2d_sparse, 2d_dense, 3d, depth, pncc, uv_tex, pose, ply, obj
        output_option = kwargs.get("output_option", "ply")  # PLY mesh for USD conversion
        
        # Use relative path from 3DDFA directory
        relative_img_path = f"examples/inputs/{input_image.name}"
        
        cmd = [
            self.python_exec,
            str(demo_script),
            "-c", str(self.config_file.relative_to(self.tddfa_path) if self.config_file.is_relative_to(self.tddfa_path) else str(self.config_file)),
            "-f", relative_img_path,
            "-m", "gpu",  # Use GPU if available
            "-o", output_option,
            "--show_flag", "false"  # Don't show, just save
        ]
        
        self._report_progress("3DDFA: Running 3D face reconstruction...", 0.2)
        
        # Run 3DDFA
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.tddfa_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                encoding='utf-8',
                errors='replace'
            )
            
            # Check return code - 0 means success (warnings in stderr are OK)
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                # Filter out warnings - they're not actual errors
                if "FutureWarning" in error_msg or "Warning" in error_msg:
                    # Check if there's actual error content beyond warnings
                    lines = error_msg.split('\n')
                    error_lines = [l for l in lines if 'Error' in l or 'error' in l or 'Traceback' in l or 'Exception' in l]
                    if not error_lines:
                        # Only warnings, not actual errors - treat as success
                        pass
                    else:
                        raise RuntimeError(f"3DDFA processing failed: {error_msg[:500]}")
                else:
                    raise RuntimeError(f"3DDFA processing failed: {error_msg[:500]}")
            # If returncode is 0, warnings in stderr are OK - continue
            
            # Find output file
            # 3DDFA outputs to: examples/results/{image_name}_{option}.{ext}
            # For PLY: {image_name}_ply.ply, for 3D: {image_name}_3d.jpg, etc.
            # Use the image name we copied (without full path)
            img_name = input_image.stem
            
            # Check 3DDFA's default output directory first
            tddfa_result_dir = self.tddfa_path / "examples" / "results"
            
            # Determine expected output file based on option
            if output_option in ["ply", "obj"]:
                # Mesh files: .ply or .obj
                output_file = tddfa_result_dir / f"{img_name}_{output_option}.{output_option}"
                # Also check our result_dir
                alt_output_file = self.result_dir / f"{img_name}_{output_option}.{output_option}"
            else:
                # Image files: .jpg
                output_file = tddfa_result_dir / f"{img_name}_{output_option}.jpg"
                alt_output_file = self.result_dir / f"{img_name}_{output_option}.jpg"
            
            # Try 3DDFA's default location first
            if not output_file.exists():
                # Try alternative location
                if alt_output_file.exists():
                    output_file = alt_output_file
                else:
                    # Try to find any matching file
                    all_outputs = list(tddfa_result_dir.glob(f"{img_name}_*"))
                    if not all_outputs:
                        all_outputs = list(self.result_dir.glob(f"{img_name}_*"))
                    
                    if all_outputs:
                        # Find the one matching our output_option
                        matching = [f for f in all_outputs if output_option in f.name]
                        if matching:
                            output_file = matching[0]
                        else:
                            output_file = all_outputs[0]  # Use first match
                    else:
                        raise FileNotFoundError(
                            f"3DDFA output not found. Checked: {tddfa_result_dir} and {self.result_dir}. "
                            f"Command output: {result.stdout[-500:]}"
                        )
            
            self._report_progress("3DDFA: 3D reconstruction complete!", 0.5)
            
            # Now we need to create a video from the processed image
            # Since 3DDFA doesn't animate, we'll create a simple video with the processed image
            # In a full implementation, this would be passed to an animation tool
            
            # Create a simple video by duplicating the frame for the duration
            import cv2
            import numpy as np
            
            self._report_progress("3DDFA: Creating video from processed image...", 0.6)
            
            # For PLY/OBJ output, return the mesh file directly (no video needed)
            if output_option in ["ply", "obj"]:
                # Return the mesh file path
                # Copy to our result directory for consistency
                final_output = self.result_dir / output_file.name
                if output_file != final_output:
                    import shutil
                    final_output.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(output_file, final_output)
                
                self._report_progress(f"3DDFA: PLY mesh generated: {final_output}", 0.9)
                return final_output, duration
            
            # For image outputs, create a video
            # Read the processed image
            img = cv2.imread(str(output_file))
            if img is None:
                raise RuntimeError(f"Could not read processed image: {output_file}")
            
            height, width = img.shape[:2]
            fps = 30
            
            # Generate unique output name
            import hashlib
            audio_hash = hashlib.md5(audio_path.read_bytes()).hexdigest()[:8]
            img_hash = hashlib.md5(img_path.read_bytes()).hexdigest()[:8]
            output_name = f"tddfa_{img_hash}_{audio_hash}"
            
            # Create output video path
            output_video = Path(self.config.get("output_dir", tempfile.gettempdir())) / f"{output_name}.mp4"
            output_video.parent.mkdir(parents=True, exist_ok=True)
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(str(output_video), fourcc, fps, (width, height))
            
            # Write frames for the duration
            num_frames = int(duration * fps)
            for _ in range(num_frames):
                video_writer.write(img)
            
            video_writer.release()
            
            if not output_video.exists():
                raise RuntimeError(f"Failed to create video: {output_video}")
            
            self._report_progress("3DDFA: Video generation complete!", 1.0)
            
            return output_video, duration
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("3DDFA processing timed out after 5 minutes")
        except Exception as e:
            raise RuntimeError(f"3DDFA generation failed: {str(e)}")

