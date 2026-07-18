"""
Combined 3DDFA + Audio2Face provider.

This provider:
1. Uses 3DDFA to reconstruct 3D face from 2D image
2. Converts the 3D mesh to USD format
3. Uses Audio2Face to animate the USD model with audio
"""

import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import time
import hashlib

from src.core.avatar_provider_base import AvatarProvider
from src.core.tddfa_provider import TDDFAProvider
from src.core.audio2face_provider import Audio2FaceProvider
from src.core.audio2face_sdk_provider import Audio2FaceSDKProvider


class TDDFA_A2FProvider(AvatarProvider):
    """
    Combined provider: 3DDFA reconstruction + Audio2Face animation.
    
    Workflow:
    1. 3DDFA reconstructs 3D face from 2D image -> PLY/OBJ mesh
    2. Convert mesh to USD format
    3. Audio2Face animates USD model with audio -> Video
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize combined 3DDFA + Audio2Face provider."""
        super().__init__(config)
        
        # Initialize sub-providers
        tddfa_config = config.get("tddfa", {})
        a2f_config = config.get("audio2face", {})
        a2f_sdk_config = config.get("audio2face_sdk", {})
        
        self.tddfa_provider = TDDFAProvider(tddfa_config)
        
        # Try SDK provider first (GitHub version), fallback to Omniverse provider
        if a2f_sdk_config:
            try:
                self.a2f_provider = Audio2FaceSDKProvider(a2f_sdk_config)
                if not self.a2f_provider.is_available():
                    # SDK not available, fallback to Omniverse provider
                    self.a2f_provider = Audio2FaceProvider(a2f_config)
            except Exception:
                # SDK provider failed, use Omniverse provider
                self.a2f_provider = Audio2FaceProvider(a2f_config)
        else:
            # No SDK config, use Omniverse provider
            self.a2f_provider = Audio2FaceProvider(a2f_config)
        
        # USD conversion cache directory
        self.usd_cache_dir = Path(config.get("usd_cache_dir", ".cache/usd_models"))
        self.usd_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Default source image
        self.default_source_image = config.get("default_source_image")

    def is_available(self) -> bool:
        """Check if both 3DDFA and Audio2Face are available."""
        tddfa_available = self.tddfa_provider.is_available()
        a2f_available = self.a2f_provider.is_available()
        
        if not tddfa_available:
            print("[WARN] 3DDFA is not available")
        if not a2f_available:
            print("[WARN] Audio2Face is not available")
        
        return tddfa_available and a2f_available

    def _convert_mesh_to_usd(self, mesh_path: Path, output_usd: Path) -> Path:
        """
        Convert PLY/OBJ mesh to USD format.
        
        Uses USD Python API (pxr) if available, otherwise raises error.
        
        Args:
            mesh_path: Path to PLY or OBJ file
            output_usd: Path for output USD file
        
        Returns:
            Path to created USD file
        
        Raises:
            RuntimeError: If conversion fails or USD API not available
        """
        from src.utils.mesh_to_usd import convert_ply_to_usd
        
        try:
            return convert_ply_to_usd(mesh_path, output_usd, method="auto")
        except Exception as e:
            raise RuntimeError(
                f"Failed to convert mesh to USD: {e}\n"
                f"Mesh file: {mesh_path}\n"
                f"Target USD: {output_usd}\n\n"
                "To fix:\n"
                "1. Install USD Python API (pxr) via Omniverse\n"
                "2. Or use Omniverse Create to manually convert PLY -> USD\n"
                "3. Or install usd-core: pip install usd-core"
            )

    def _get_or_create_usd_model(self, source_image: Path) -> Path:
        """
        Get or create USD model from source image.
        
        Checks cache first, then reconstructs if needed.
        
        Args:
            source_image: Path to 2D source image
        
        Returns:
            Path to USD model file
        """
        # Create cache key from image
        img_hash = hashlib.md5(source_image.read_bytes()).hexdigest()[:12]
        cached_usd = self.usd_cache_dir / f"face_{img_hash}.usd"
        
        # Check cache
        if cached_usd.exists():
            print(f"[INFO] Using cached USD model: {cached_usd}")
            return cached_usd
        
        # Need to create USD from image
        print(f"[INFO] Creating USD model from image: {source_image}")
        
        # Step 1: Use 3DDFA to reconstruct 3D face
        # We'll call 3DDFA directly to get PLY/OBJ output
        tddfa_path = self.tddfa_provider.tddfa_path
        demo_script = tddfa_path / "demo.py"
        config_file = self.tddfa_provider.config_file
        
        # Create temporary audio for 3DDFA call (it needs audio_path but we only need mesh)
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio.close()
        temp_audio_path = Path(temp_audio.name)
        
        # Generate PLY mesh
        import cv2
        import numpy as np
        # Create a 1-second silent audio file
        sample_rate = 16000
        duration = 1.0
        silent_audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
        import soundfile as sf
        sf.write(str(temp_audio_path), silent_audio, sample_rate)
        
        try:
            # Run 3DDFA to get PLY output
            cmd = [
                self.tddfa_provider.python_exec,
                str(demo_script),
                "-c", str(config_file),
                "-f", str(source_image),
                "-m", "gpu",
                "-o", "ply",  # Export as PLY
                "--show_flag", "false"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(tddfa_path),
                capture_output=True,
                text=True,
                timeout=300,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"3DDFA failed: {result.stderr[:500]}")
            
            # Find PLY output
            result_dir = self.tddfa_provider.result_dir
            img_name = source_image.stem
            ply_file = result_dir / f"{img_name}_ply.ply"
            
            if not ply_file.exists():
                # Try to find any PLY file
                ply_files = list(result_dir.glob(f"{img_name}_*.ply"))
                if ply_files:
                    ply_file = ply_files[0]
                else:
                    raise FileNotFoundError(f"3DDFA PLY output not found: {result_dir}")
            
            # Step 2: Convert PLY to USD
            print(f"[INFO] Converting PLY to USD: {ply_file} -> {cached_usd}")
            self._convert_mesh_to_usd(ply_file, cached_usd)
            
            return cached_usd
            
        finally:
            # Cleanup temp audio
            if temp_audio_path.exists():
                temp_audio_path.unlink()

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
        Generate avatar video using 3DDFA + Audio2Face.
        
        Args:
            audio_path: Path to audio file
            avatar_id: Can be a path to source image or identifier
            expression: Expression to apply
            gesture: Gesture to apply
            text: Optional text (for logging)
            source_image: Path to source headshot image (overrides avatar_id)
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (video_path, duration_seconds)
        """
        if not self.is_available():
            raise RuntimeError(
                "3DDFA + Audio2Face not available. "
                "Ensure both 3DDFA and Audio2Face are set up."
            )
        
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
        self._report_progress("3DDFA+A2F: Starting generation...", 0.1)
        
        # Step 1: Get or create USD model from image
        self._report_progress("3DDFA+A2F: Reconstructing 3D face and converting to USD...", 0.2)
        try:
            usd_model = self._get_or_create_usd_model(img_path)
        except NotImplementedError as e:
            # USD conversion not implemented yet
            raise RuntimeError(
                f"USD conversion not yet implemented. "
                f"Please convert the 3DDFA output manually:\n"
                f"1. Run 3DDFA to get PLY file\n"
                f"2. Use Omniverse Create to convert PLY -> USD\n"
                f"3. Set avatar_id to the USD file path\n"
                f"\nError: {e}"
            )
        
        # Step 2: Use Audio2Face to animate USD model
        self._report_progress("3DDFA+A2F: Animating USD model with Audio2Face...", 0.5)
        video_path, duration = self.a2f_provider.generate(
            audio_path=audio_path,
            avatar_id=str(usd_model),  # Pass USD file path as avatar_id
            expression=expression,
            gesture=gesture,
            text=text,
            **kwargs
        )
        
        self._report_progress("3DDFA+A2F: Generation complete!", 1.0)
        
        return video_path, duration

