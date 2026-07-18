"""
VALL-E X local TTS provider.

VALL-E X is a high-quality zero-shot voice cloning TTS model.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import time

from src.core.tts_provider_base import TTSProvider


class VALLEProvider(TTSProvider):
    """VALL-E X local GPU-based TTS provider."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize VALL-E provider."""
        super().__init__(config)
        
        # VALL-E installation path
        self.valle_path = Path(config.get("valle_path", "~/valle")).expanduser()
        
        # Check if path is relative and resolve it
        if not self.valle_path.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            self.valle_path = project_root / self.valle_path
        
        # Python executable
        self.python_exec = config.get("python_exec", "python")
        if (self.valle_path / "venv" / "bin" / "python").exists():
            self.python_exec = str(self.valle_path / "venv" / "bin" / "python")
        elif (self.valle_path / "venv" / "Scripts" / "python.exe").exists():
            self.python_exec = str(self.valle_path / "venv" / "Scripts" / "python.exe")
        
        # Output directory
        self.output_dir = Path(config.get("output_dir", tempfile.mkdtemp(prefix="valle_")))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        """Check if VALL-E is available."""
        # Check if VALL-E is installed
        # VALL-E X (Plachtaa) uses utils.generation module
        try:
            # Check if directory exists
            if not self.valle_path.exists():
                return False
            
            # Check for key VALL-E files
            key_files = [
                self.valle_path / "utils" / "generation.py",  # Main generation module
                self.valle_path / "requirements.txt",  # Dependencies file
            ]
            
            # At least utils/generation.py should exist
            if (self.valle_path / "utils" / "generation.py").exists():
                # Verify it can be imported (CRITICAL: must change directory first due to relative paths)
                result = subprocess.run(
                    [self.python_exec, "-c", "import sys; import os; os.chdir(r'{}'); sys.path.insert(0, r'{}'); from utils.generation import generate_audio; print('OK')".format(str(self.valle_path), str(self.valle_path))],
                    capture_output=True,
                    timeout=10,
                    cwd=str(self.valle_path)
                )
                if result.returncode == 0:
                    return True
                else:
                    # Debug: show error if import fails
                    if result.stderr:
                        print(f"[DEBUG] VALL-E import error: {result.stderr.decode('utf-8', errors='ignore')[:200]}")
            
            # Fallback: check for inference scripts
            inference_scripts = [
                self.valle_path / "inference.py",
                self.valle_path / "demo.py",
            ]
            
            for inference_script in inference_scripts:
                if inference_script.exists():
                    return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return False

    def generate(self, text: str, voice_id: str, **kwargs) -> tuple[bytes, float]:
        """
        Generate audio using VALL-E X.

        Args:
            text: Text to convert to speech
            voice_id: Voice identifier (reference audio path or speaker name)
            **kwargs: Additional parameters:
                - reference_audio: Path to reference audio for voice cloning
                - output_path: Output audio path
                - language: Language code

        Returns:
            Tuple of (audio_bytes, duration_seconds)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Get reference audio for voice cloning (optional - VALL-E can work without it)
        reference_audio = kwargs.get("reference_audio")
        if not reference_audio:
            if voice_id and Path(voice_id).exists():
                reference_audio = Path(voice_id)
            # VALL-E can work without prompt (uses default voice)
            # Only require reference_audio if voice_id is explicitly a file path
            elif voice_id and voice_id != "default":
                # Try to resolve as file path, but don't require it
                reference_audio = None
        
        # Get output path
        output_path = kwargs.get("output_path")
        if not output_path:
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            output_filename = f"valle_{text_hash}.wav"
            output_path = self.output_dir / output_filename
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # VALL-E X (Plachtaa) uses utils.generation module
        # Must run from VALL-E directory due to relative paths
        try:
            import subprocess
            import json
            import tempfile
            
            self._report_progress("VALL-E: Initializing generation...", 0.0)
            
            # Create a Python script to run VALL-E generation
            # CRITICAL: Must run from VALL-E directory due to relative paths in generation.py
            script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
            valle_path_abs = str(self.valle_path.absolute())
            output_path_abs = str(output_path.absolute())
            text_escaped = json.dumps(text)
            language_escaped = json.dumps(kwargs.get("language", "auto"))
            
            script_content = f"""import sys
import os
from pathlib import Path

# CRITICAL: Change to VALL-E directory FIRST (before any imports)
os.chdir(r"{valle_path_abs}")
sys.path.insert(0, r"{valle_path_abs}")

from utils.generation import generate_audio, SAMPLE_RATE, preload_models
from scipy.io.wavfile import write as write_wav

print("PROGRESS:0.1:Preloading models...")
preload_models()

print("PROGRESS:0.5:Generating audio...")
text = {text_escaped}
language = {language_escaped}
prompt_path = None

audio_array = generate_audio(text, prompt=prompt_path, language=language)

print("PROGRESS:0.9:Saving audio...")
output_path = r"{output_path_abs}"
write_wav(output_path, SAMPLE_RATE, audio_array)
print("SUCCESS:" + str(output_path))
"""
            script_file.write(script_content)
            script_file.close()
            
            self._report_progress("VALL-E: Starting generation process...", 0.1)
            
            # Run script from VALL-E directory with real-time output parsing
            process = subprocess.Popen(
                [self.python_exec, script_file.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr into stdout
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True,
                cwd=str(self.valle_path)
            )
            
            # Read output line by line to capture progress
            stdout_lines = []
            stderr_lines = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    stdout_lines.append(line)
                    # Parse progress messages (format: "PROGRESS:0.5:message")
                    if line.startswith("PROGRESS:"):
                        try:
                            parts = line.strip().split(":", 2)
                            if len(parts) == 3:
                                progress = float(parts[1])
                                message = parts[2]
                                self._report_progress(f"VALL-E: {message}", progress)
                        except:
                            pass
            
            # Get remaining output
            remaining_stdout, remaining_stderr = process.communicate(timeout=1)
            if remaining_stdout:
                stdout_lines.append(remaining_stdout)
            if remaining_stderr:
                stderr_lines.append(remaining_stderr)
            
            stdout = ''.join(stdout_lines)
            stderr = ''.join(stderr_lines)
            
            # Clean up script file
            import os
            try:
                os.unlink(script_file.name)
            except:
                pass
            
            if process.returncode != 0:
                error_msg = f"VALL-E generation failed with return code {process.returncode}"
                if stderr:
                    stderr_str = stderr if isinstance(stderr, str) else stderr.decode('utf-8', errors='ignore')
                    error_msg += f"\nError output: {stderr_str[:2000]}"
                if stdout:
                    stdout_str = stdout if isinstance(stdout, str) else stdout.decode('utf-8', errors='ignore')
                    error_msg += f"\nStdout: {stdout_str[:500]}"
                self._report_progress(f"VALL-E: Error - {error_msg[:100]}", 1.0)
                raise RuntimeError(error_msg)
            
            if not output_path.exists():
                self._report_progress("VALL-E: Output file not found", 1.0)
                raise RuntimeError(f"VALL-E did not generate output file: {output_path}")
            
            self._report_progress("VALL-E: Reading audio file...", 0.95)
            
            # Read audio file
            with open(output_path, "rb") as f:
                audio_bytes = f.read()
            
            # Get duration
            try:
                from pydub import AudioSegment
                audio_file = AudioSegment.from_file(str(output_path))
                duration = len(audio_file) / 1000.0
            except Exception:
                words = len(text.split())
                duration = (words / 150.0) * 60.0
            
            self._report_progress(f"VALL-E: Generation complete ({duration:.2f}s)", 1.0)
            
            return audio_bytes, duration
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("VALL-E generation timed out (10 minutes)")
        except FileNotFoundError:
            raise RuntimeError(
                f"VALL-E Python executable not found: {self.python_exec}. "
                f"Please ensure VALL-E is installed and configured."
            )
        except Exception as e:
            raise RuntimeError(f"VALL-E generation failed: {e}")

