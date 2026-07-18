"""
DreamTalk local avatar generation provider.

DreamTalk is a high-quality local talking head generation model that runs on GPU.
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import time

from src.core.avatar_provider_base import AvatarProvider


class DreamTalkProvider(AvatarProvider):
    """DreamTalk local GPU-based provider for avatar generation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize DreamTalk provider."""
        super().__init__(config)
        
        # DreamTalk installation path (can be absolute or relative to project root)
        self.dreamtalk_path = Path(config.get("dreamtalk_path", "~/dreamtalk")).expanduser()
        
        # Check if path is relative and resolve it
        if not self.dreamtalk_path.is_absolute():
            # Try to find project root (go up from src/core)
            project_root = Path(__file__).parent.parent.parent
            self.dreamtalk_path = project_root / self.dreamtalk_path
        
        # Python executable (use venv if available, otherwise system Python)
        self.python_exec = config.get("python_exec", "python")
        if (self.dreamtalk_path / "venv" / "bin" / "python").exists():
            self.python_exec = str(self.dreamtalk_path / "venv" / "bin" / "python")
        elif (self.dreamtalk_path / "venv" / "Scripts" / "python.exe").exists():
            self.python_exec = str(self.dreamtalk_path / "venv" / "Scripts" / "python.exe")
        
        # Checkpoints path
        self.checkpoints_path = self.dreamtalk_path / "checkpoints"
        
        # Output directory for DreamTalk results
        self.result_dir = Path(config.get("result_dir", tempfile.mkdtemp(prefix="dreamtalk_")))
        self.result_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        """Check if DreamTalk is available."""
        # Check if DreamTalk directory exists
        if not self.dreamtalk_path.exists():
            return False
        
        # Check if inference script exists (try multiple possible names)
        inference_scripts = [
            self.dreamtalk_path / "inference.py",
            self.dreamtalk_path / "inference_for_demo_video.py",
            self.dreamtalk_path / "demo.py",
        ]
        inference_script = None
        for script in inference_scripts:
            if script.exists():
                inference_script = script
                break
        
        if not inference_script:
            return False
        
        # Check if Python is available
        try:
            result = subprocess.run(
                [self.python_exec, "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        
        # Check for required checkpoints
        checkpoints_dir = self.dreamtalk_path / "checkpoints"
        denoising_checkpoint = checkpoints_dir / "denoising_network.pth"
        renderer_checkpoint = checkpoints_dir / "renderer.pt"
        
        if not denoising_checkpoint.exists() or not renderer_checkpoint.exists():
            return False
        
        # Check if CUDA/GPU is available (optional but recommended)
        try:
            result = subprocess.run(
                [self.python_exec, "-c", "import torch; print(torch.cuda.is_available())"],
                capture_output=True,
                timeout=10,
                cwd=str(self.dreamtalk_path)
            )
            # GPU check is optional - DreamTalk can work on CPU (slowly)
        except Exception:
            pass  # Continue anyway
        
        return True

    def generate(
        self,
        audio_path: Path,
        avatar_id: str,
        expression: Optional[str] = None,
        gesture: Optional[str] = None,
        **kwargs
    ) -> tuple[Path, float]:
        """
        Generate avatar video using DreamTalk.

        Args:
            audio_path: Path to audio file
            avatar_id: Avatar identifier (can be image path or persona name)
            expression: Expression to apply (optional)
            gesture: Gesture to apply (optional)
            **kwargs: Additional parameters:
                - output_path: Output video path
                - image_path: Source image path (if avatar_id is not a path)
                - duration: Expected video duration
                - emotion: Emotion type (happy, sad, angry, etc.)

        Returns:
            Tuple of (video_path, duration_seconds)

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If generation fails
        """
        # Validate inputs
        if not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")
        
        # Get source image path
        image_path = kwargs.get("image_path")
        if not image_path:
            # Try to resolve avatar_id as image path
            if Path(avatar_id).exists():
                image_path = Path(avatar_id)
            else:
                # Try to find image in personas or default location
                # For now, raise error - user must provide image_path
                raise ValueError(
                    f"DreamTalk requires 'image_path' parameter. "
                    f"avatar_id '{avatar_id}' is not a valid file path. "
                    f"Please provide image_path in kwargs."
                )
        
        if not Path(image_path).exists():
            raise ValueError(f"Source image not found: {image_path}")
        
        # Get output path
        output_path = kwargs.get("output_path")
        if not output_path:
            # Generate output filename
            output_filename = f"dreamtalk_{avatar_id}_{audio_path.stem}.mp4"
            output_path = self.result_dir / output_filename
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Report progress
        self._report_progress("DreamTalk: Starting video generation...", 0.1)
        
        # Build DreamTalk command
        # DreamTalk inference.py typically takes:
        # --driven_audio: Audio file path
        # --source_image: Source image path
        # --ref_eyeblink: Reference eye blink video (optional)
        # --ref_pose: Reference pose video (optional)
        # --result_dir: Output directory
        # --enhancer: Enhancer type (gfpgan, etc.)
        
        # Find inference script (try multiple possible names)
        inference_scripts = [
            self.dreamtalk_path / "inference.py",
            self.dreamtalk_path / "inference_for_demo_video.py",
            self.dreamtalk_path / "demo.py",
        ]
        inference_script = None
        for script in inference_scripts:
            if script.exists():
                inference_script = script
                break
        
        if not inference_script:
            raise RuntimeError(
                f"DreamTalk inference script not found. Checked: {[str(s) for s in inference_scripts]}. "
                f"Please ensure DreamTalk is properly installed."
            )
        
        cmd = [
            self.python_exec,
            str(inference_script),
            "--wav_path", str(audio_path.absolute()),
            "--image_path", str(Path(image_path).absolute()),
            "--output_name", str(output_path.stem),
        ]
        
        # Add optional parameters (DreamTalk doesn't use enhancer, ref_eyeblink, ref_pose, or emotion)
        # These are for other avatar providers, not DreamTalk
        if kwargs.get("style_clip_path"):
            cmd.extend(["--style_clip_path", str(kwargs["style_clip_path"])])
        
        if kwargs.get("pose_path"):
            cmd.extend(["--pose_path", str(kwargs["pose_path"])])
        
        if kwargs.get("max_gen_len"):
            cmd.extend(["--max_gen_len", str(kwargs["max_gen_len"])])
        
        if kwargs.get("cfg_scale"):
            cmd.extend(["--cfg_scale", str(kwargs["cfg_scale"])])
        
        if kwargs.get("device"):
            cmd.extend(["--device", str(kwargs["device"])])
        
        # Report progress
        self._report_progress("DreamTalk: Running inference...", 0.2)
        
        # Run DreamTalk
        start_time = time.time()
        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.dreamtalk_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output for progress updates
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
                    # Report progress periodically
                    if "step" in output.lower() or "epoch" in output.lower():
                        # Estimate progress from output
                        self._report_progress(f"DreamTalk: {output.strip()}", 0.3)
            
            # Wait for completion
            return_code = process.wait()
            
            if return_code != 0:
                stderr_output = process.stderr.read()
                error_msg = f"DreamTalk generation failed with return code {return_code}"
                if stderr_output:
                    error_msg += f"\nError output: {stderr_output[:500]}"
                raise RuntimeError(error_msg)
            
        except FileNotFoundError:
            raise RuntimeError(
                f"DreamTalk Python executable not found: {self.python_exec}. "
                f"Please ensure DreamTalk is installed and Python is available."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("DreamTalk generation timed out")
        except Exception as e:
            raise RuntimeError(f"DreamTalk generation failed: {e}")
        
        elapsed_time = time.time() - start_time
        self._report_progress("DreamTalk: Processing complete, locating output...", 0.9)
        
        # Find output video file
        # DreamTalk outputs to output_video/{output_name}.mp4 in the DreamTalk directory
        dreamtalk_output_dir = self.dreamtalk_path / "output_video"
        expected_output = dreamtalk_output_dir / f"{output_path.stem}.mp4"
        
        # Also check our result_dir
        output_dir = output_path.parent
        video_files = []
        
        # Check DreamTalk's output directory first
        if expected_output.exists():
            generated_video = expected_output
        else:
            # Check DreamTalk output directory for any matching files
            if dreamtalk_output_dir.exists():
                dreamtalk_videos = list(dreamtalk_output_dir.glob(f"*{output_path.stem}*.mp4"))
                if dreamtalk_videos:
                    generated_video = max(dreamtalk_videos, key=lambda p: p.stat().st_mtime)
                else:
                    # Get most recently modified video file from DreamTalk output
                    dreamtalk_videos = list(dreamtalk_output_dir.glob("*.mp4"))
                    if dreamtalk_videos:
                        generated_video = max(dreamtalk_videos, key=lambda p: p.stat().st_mtime)
                    else:
                        generated_video = None
            else:
                generated_video = None
            
            # Fallback to our result_dir
            if not generated_video:
                video_files = list(output_dir.glob("*.mp4"))
                if not video_files:
                    video_files = list(output_dir.glob("*.avi")) + list(output_dir.glob("*.mov"))
                if video_files:
                    generated_video = max(video_files, key=lambda p: p.stat().st_mtime)
        
        if not generated_video or not generated_video.exists():
            raise RuntimeError(
                f"DreamTalk did not generate output video. "
                f"Checked: {expected_output}, {dreamtalk_output_dir}, {output_dir}. "
                f"Check DreamTalk logs for errors."
            )
        
        # Copy to desired output path if different
        if generated_video != output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(generated_video, output_path)
        
        # Get video duration
        duration = kwargs.get("duration", 0.0)
        if duration == 0.0:
            try:
                from pydub import AudioSegment as PydubAudioSegment
                audio_file = PydubAudioSegment.from_file(str(audio_path))
                duration = len(audio_file) / 1000.0
            except Exception:
                # Estimate from file size or use elapsed time
                duration = elapsed_time
        
        self._report_progress(f"DreamTalk: Video generated successfully! ({duration:.1f}s)", 1.0)
        
        return output_path, duration

