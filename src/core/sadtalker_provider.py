"""
SadTalker local avatar generation provider.

SadTalker animates 2D headshot images with audio to create talking videos.
Perfect for creating avatars from single photos.
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import time

from src.core.avatar_provider_base import AvatarProvider


class SadTalkerProvider(AvatarProvider):
    """SadTalker local GPU-based provider for 2D headshot animation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize SadTalker provider."""
        super().__init__(config)
        
        # SadTalker installation path
        self.sadtalker_path = Path(config.get("sadtalker_path", "d:/dev/SadTalker"))
        if not self.sadtalker_path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            self.sadtalker_path = project_root / self.sadtalker_path
        
        # Python executable
        self.python_exec = config.get("python_exec", "python")
        
        # Checkpoints path
        self.checkpoints_path = self.sadtalker_path / "checkpoints"
        
        # Output directory
        self.result_dir = Path(config.get("result_dir", self.sadtalker_path / "results"))
        self.result_dir.mkdir(parents=True, exist_ok=True)
        
        # Default source image (can be overridden per generation)
        self.default_source_image = config.get("default_source_image")

    def is_available(self) -> bool:
        """Check if SadTalker is available."""
        # Check if SadTalker directory exists
        if not self.sadtalker_path.exists():
            return False
        
        # Check if inference script exists
        inference_script = self.sadtalker_path / "inference.py"
        if not inference_script.exists():
            return False
        
        # Check if checkpoints exist
        if not self.checkpoints_path.exists():
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
        Generate talking avatar video using SadTalker.
        
        Args:
            audio_path: Path to audio file
            avatar_id: Can be a path to source image or identifier
            expression: Not used by SadTalker (audio-driven)
            gesture: Not used by SadTalker
            text: Optional text (for logging)
            source_image: Path to source headshot image (overrides avatar_id)
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (video_path, duration_seconds)
        """
        if not self.is_available():
            raise RuntimeError("SadTalker is not available. Please check installation.")
        
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
            # Fallback: estimate from file size
            duration = 5.0  # Default estimate
        
        # Generate unique output name
        import hashlib
        audio_hash = hashlib.md5(audio_path.read_bytes()).hexdigest()[:8]
        img_hash = hashlib.md5(img_path.read_bytes()).hexdigest()[:8]
        output_name = f"sadtalker_{img_hash}_{audio_hash}"
        
        # Report progress
        self._report_progress("SadTalker: Starting video generation...", 0.1)
        
        # Prepare inference command
        inference_script = self.sadtalker_path / "inference.py"
        if not inference_script.exists():
            # Try alternative script names
            for alt_name in ["inference_for_demo.py", "demo.py", "test.py"]:
                alt_script = self.sadtalker_path / alt_name
                if alt_script.exists():
                    inference_script = alt_script
                    break
        
        if not inference_script.exists():
            raise FileNotFoundError(f"SadTalker inference script not found in {self.sadtalker_path}")
        
        # Build command
        # SadTalker uses: python inference.py --driven_audio <audio> --source_image <image> --result_dir <output> --checkpoint_dir <checkpoints>
        cmd = [
            self.python_exec,
            str(inference_script),
            "--driven_audio", str(audio_path),
            "--source_image", str(img_path),
            "--result_dir", str(self.result_dir),
            "--checkpoint_dir", str(self.checkpoints_path),
        ]
        
        # Add optional parameters
        if "preprocess" in kwargs:
            cmd.extend(["--preprocess", str(kwargs["preprocess"])])
        else:
            cmd.extend(["--preprocess", "full"])  # Default to full preprocessing
        
        if "enhancer" in kwargs:
            cmd.extend(["--enhancer", str(kwargs["enhancer"])])
        
        if "still" in kwargs and kwargs["still"]:
            cmd.append("--still")
        
        self._report_progress("SadTalker: Running inference...", 0.2)
        
        # Run inference
        try:
            # Change to SadTalker directory for execution
            result = subprocess.run(
                cmd,
                cwd=str(self.sadtalker_path),
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"SadTalker inference failed: {error_msg[:500]}")
            
            # Parse output to find generated video
            # SadTalker outputs to: result_dir/YYYY_MM_DD_HH.MM.SS.mp4
            # Find the most recently created .mp4 file in result_dir
            import time
            time.sleep(1)  # Give it a moment to finish writing
            
            output_video = None
            
            # Find all .mp4 files in result_dir
            mp4_files = list(self.result_dir.glob("*.mp4"))
            
            if not mp4_files:
                # Check subdirectories (if verbose mode was used)
                mp4_files = list(self.result_dir.rglob("*.mp4"))
            
            if mp4_files:
                # Get the most recently modified file
                output_video = max(mp4_files, key=lambda p: p.stat().st_mtime)
            else:
                # Last resort: check stdout for the output path
                stdout_lines = result.stdout.split('\n')
                for line in stdout_lines:
                    if 'generated video is named' in line.lower() or '.mp4' in line:
                        # Try to extract path from line
                        import re
                        path_match = re.search(r'([^\s]+\.mp4)', line)
                        if path_match:
                            potential_path = Path(path_match.group(1))
                            if potential_path.exists():
                                output_video = potential_path
                                break
            
            if output_video is None or not output_video.exists():
                raise FileNotFoundError(
                    f"SadTalker output video not found. Checked: {self.result_dir}. "
                    f"Command output: {result.stdout[-1000:]}"
                )
            
            self._report_progress("SadTalker: Video generated successfully!", 1.0)
            
            return output_video, duration
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("SadTalker inference timed out after 10 minutes")
        except Exception as e:
            raise RuntimeError(f"SadTalker generation failed: {str(e)}")

