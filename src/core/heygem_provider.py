"""
HeyGem local avatar generation provider.

HeyGem is a local, GPU-based HeyGen alternative that runs via Docker.
It provides the same API interface as HeyGen but runs entirely locally.
"""

import os
import subprocess
import time
import json
import uuid
from pathlib import Path
from typing import Dict, Optional, Any
import requests

from src.core.avatar_provider_base import AvatarProvider


class HeyGemProvider(AvatarProvider):
    """HeyGem local GPU-based provider for avatar generation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize HeyGem provider."""
        super().__init__(config)
        
        # Get HeyGem-specific config
        heygem_config = config.get("heygem", {})
        
        # HeyGem API base URL (video generation service)
        self.base_url = heygem_config.get("base_url", "http://127.0.0.1:8383/easy")
        
        # HeyGem installation path (for Docker management)
        heygem_path = heygem_config.get("heygem_path", "./heygem")
        self.heygem_path = Path(heygem_path).expanduser()
        
        # Check if path is relative and resolve it
        if not self.heygem_path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            self.heygem_path = project_root / self.heygem_path
        
        # Docker container name
        self.container_name = heygem_config.get("container_name", "heygem-gen-video")
        
        # Data directory (where models and outputs are stored)
        # Default: D:/heygem_data/face2face (Windows) or ~/heygem_data/face2face (Linux)
        self.data_dir = Path(heygem_config.get("data_dir", "D:/heygem_data/face2face"))
        if not self.data_dir.is_absolute():
            # Try Windows default first
            win_default = Path("D:/heygem_data/face2face")
            if win_default.exists():
                self.data_dir = win_default
            else:
                # Fall back to home directory
                self.data_dir = Path.home() / "heygem_data" / "face2face"
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Output directory for our results
        output_dir = heygem_config.get("output_dir", ".cache/heygem_outputs")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        """Check if HeyGem is available (Docker container running)."""
        try:
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return False
            
            # Check if HeyGem container is running
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                timeout=5,
                text=True
            )
            if self.container_name not in result.stdout:
                return False
            
            # Try to connect to HeyGem API endpoint (simple query to check if service is up)
            try:
                # Use a test query to check if the service responds
                response = requests.get(f"{self.base_url}/query?code=test", timeout=5)
                # Even if it returns an error, if we get a response, the service is up
                return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                return False
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def generate(
        self, audio_path: Path, avatar_id: str, expression: Optional[str] = None, gesture: Optional[str] = None, text: Optional[str] = None, **kwargs
    ) -> tuple[Path, float]:
        """
        Generate avatar video using HeyGem (local GPU).

        Args:
            audio_path: Path to audio file
            avatar_id: Avatar identifier - should be a path to a video file (model video)
            expression: Expression to apply (optional, not used by HeyGem)
            gesture: Gesture to apply (optional, not used by HeyGem)
            text: Text to speak (optional, not used - we use audio_path)
            **kwargs: Additional parameters

        Returns:
            Tuple of (video_path, duration_seconds)

        Raises:
            ValueError: If inputs are invalid
            RuntimeError: If generation fails
        """
        if not self.is_available():
            raise RuntimeError(
                f"HeyGem is not available. Ensure Docker is running and HeyGem container '{self.container_name}' is started.\n"
                f"Start with: cd {self.heygem_path}/deploy && docker-compose up -d"
            )

        if not audio_path or not audio_path.exists():
            raise ValueError(f"Audio file not found: {audio_path}")

        # Validate avatar_id (should be a path to a video file)
        video_model_path = Path(avatar_id)
        if not video_model_path.exists():
            # Try relative to data directory
            video_model_path = self.data_dir / avatar_id
            if not video_model_path.exists():
                raise ValueError(
                    f"Avatar video model not found: {avatar_id}\n"
                    f"Expected at: {avatar_id} or {video_model_path}\n"
                    f"Please provide a valid path to a video file (the model video)."
                )

        # Get audio duration for progress tracking
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(str(audio_path))
            duration = len(audio) / 1000.0  # Convert to seconds
        except Exception:
            # Fallback: estimate duration (rough)
            duration = 5.0  # Default estimate

        # Copy audio file to data directory if needed (HeyGem expects files in its data directory)
        # The audio file needs to be accessible to the Docker container
        # Use FFmpeg directly for maximum compatibility with HeyGem's internal FFmpeg
        audio_in_data_dir = self.data_dir / "temp"
        audio_in_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate a simple filename (HeyGem may have issues with complex filenames)
        import uuid
        simple_filename = f"audio_{uuid.uuid4().hex[:8]}.wav"
        audio_in_data_dir = audio_in_data_dir / simple_filename
        
        # Use FFmpeg directly to convert to PCM 16-bit WAV (most compatible format)
        try:
            import subprocess
            # Convert to PCM 16-bit, mono, 22050 Hz WAV using FFmpeg
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # Overwrite output file
                '-i', str(audio_path),  # Input file
                '-acodec', 'pcm_s16le',  # 16-bit PCM codec
                '-ar', '22050',  # Sample rate 22050 Hz
                '-ac', '1',  # Mono channel
                '-f', 'wav',  # WAV format
                str(audio_in_data_dir)
            ]
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")
            
            # Ensure file is fully written
            import time
            import os
            if hasattr(os, 'sync'):
                os.sync()  # Force sync on Linux
            time.sleep(1.0)  # Wait for file to be fully accessible
            
            # Verify file exists and is readable
            if not audio_in_data_dir.exists():
                raise RuntimeError(f"Audio file was not created: {audio_in_data_dir}")
            
            if audio_in_data_dir.stat().st_size == 0:
                raise RuntimeError(f"Audio file is empty: {audio_in_data_dir}")
            
            # Verify with FFprobe (same way HeyGem does)
            verify_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams',
                str(audio_in_data_dir)
            ]
            verify_result = subprocess.run(
                verify_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if verify_result.returncode != 0:
                raise RuntimeError(f"FFprobe verification failed: {verify_result.stderr}")
            
            # Parse and verify JSON structure (same as HeyGem expects)
            import json
            verify_data = json.loads(verify_result.stdout)
            if 'streams' not in verify_data or len(verify_data['streams']) == 0:
                raise RuntimeError(f"FFprobe verification failed: no streams found")
            
            audio_filename = simple_filename
            self._report_progress(f"HeyGem: Converted audio to PCM 16-bit WAV via FFmpeg", 0.1)
        except Exception as e:
            # Fallback: try pydub conversion
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(str(audio_path))
                audio = audio.set_channels(1).set_frame_rate(22050).set_sample_width(2)
                audio.export(str(audio_in_data_dir), format="wav")
                import time
                time.sleep(1.0)
                audio_filename = simple_filename
                self._report_progress(f"HeyGem: Converted audio to WAV (pydub fallback)", 0.1)
            except Exception as e2:
                # Last resort: just copy the file
                import shutil
                audio_filename = f"audio_{uuid.uuid4().hex[:8]}.wav"
                audio_in_data_dir = self.data_dir / "temp" / audio_filename
                shutil.copy2(audio_path, audio_in_data_dir)
                self._report_progress(f"HeyGem: Copied audio (conversion failed: {e2})", 0.1)
        
        # Use relative paths from data directory (as HeyGem expects)
        audio_url = f"temp/{audio_filename}"
        video_url = str(video_model_path.relative_to(self.data_dir)) if video_model_path.is_relative_to(self.data_dir) else video_model_path.name

        # Generate unique task code
        task_code = str(uuid.uuid4())

        # Prepare payload according to HeyGem API
        payload = {
            "audio_url": audio_url,
            "video_url": video_url,
            "code": task_code,
            "chaofen": 0,  # Super resolution (0 = off)
            "watermark_switch": 0,  # Watermark (0 = off)
            "pn": 1  # Page number
        }

        self._report_progress(f"HeyGem: Submitting video generation task (code: {task_code[:8]}...)", 0.2)

        # Submit video generation task
        try:
            response = requests.post(
                f"{self.base_url}/submit",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Check response code (10000 = success)
            if result.get("code") != 10000:
                error_msg = result.get("msg", "Unknown error")
                raise RuntimeError(f"HeyGem API error: {error_msg}")

            self._report_progress(f"HeyGem: Task submitted successfully", 0.3)

            # Poll for completion
            output_file = self._poll_video_status(task_code, max_wait=600)  # 10 minutes max

            # Copy output file to our output directory
            output_path = self.output_dir / f"heygem_{task_code[:8]}.mp4"
            import shutil
            shutil.copy2(output_file, output_path)

            self._report_progress("HeyGem: Video generation complete!", 1.0)
            
            return output_path, duration

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"HeyGem API request failed: {str(e)}") from e
        except Exception as e:
            raise RuntimeError(f"HeyGem video generation failed: {str(e)}") from e

    def _poll_video_status(self, task_code: str, max_wait: int = 600, poll_interval: int = 2) -> Path:
        """
        Poll HeyGem API for video completion.

        Args:
            task_code: Task code to poll
            max_wait: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds

        Returns:
            Path to completed video file

        Raises:
            RuntimeError: If video fails or times out
        """
        start_time = time.time()
        task_code_short = task_code[:8] + "..." if len(task_code) > 8 else task_code

        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/query?code={task_code}",
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()
                    
                    # Check response code
                    if result.get("code") not in [10000]:
                        # Error codes: 9999, 10002, 10003 = failed
                        if result.get("code") in [9999, 10002, 10003]:
                            error_msg = result.get("msg", "Unknown error")
                            raise RuntimeError(f"HeyGem video generation failed: {error_msg}")
                        # Other codes might be temporary, continue polling
                    
                    data = result.get("data", {})
                    status = data.get("status")
                    
                    if status == 2:  # Completed
                        result_file = data.get("result")
                        if not result_file:
                            raise RuntimeError("HeyGem video completed but no result file provided")
                        
                        # Result file is relative to data directory
                        output_file = self.data_dir / result_file
                        if not output_file.exists():
                            raise RuntimeError(f"HeyGem output file not found: {output_file}")
                        
                        return output_file
                    
                    elif status == 3:  # Failed
                        error_msg = data.get("msg", "Unknown error")
                        raise RuntimeError(f"HeyGem video generation failed: {error_msg}")
                    
                    elif status == 1:  # Processing
                        elapsed = time.time() - start_time
                        progress_pct = min(0.3 + (elapsed / max_wait) * 0.6, 0.9)  # 30% to 90%
                        progress_msg = data.get("progress", "")
                        message = f"HeyGem: Processing... ({progress_msg}, {elapsed:.0f}s elapsed)"
                        self._report_progress(message, progress_pct)
                    
                    # Status 0 or other = pending/queued
                    else:
                        elapsed = time.time() - start_time
                        progress_pct = min(0.2 + (elapsed / max_wait) * 0.1, 0.3)  # 20% to 30%
                        message = f"HeyGem: Queued/Processing... (code: {task_code_short}, {elapsed:.0f}s elapsed)"
                        self._report_progress(message, progress_pct)

                else:
                    response.raise_for_status()

            except requests.exceptions.RequestException as e:
                # Network error - retry
                elapsed = time.time() - start_time
                if elapsed > 10:  # Only log after 10 seconds
                    self._report_progress(f"HeyGem: Connection error, retrying... ({elapsed:.0f}s elapsed)", 0.2)

            time.sleep(poll_interval)

        raise RuntimeError(
            f"HeyGem video generation timed out after {max_wait}s. "
            f"Task code: {task_code_short}"
        )
