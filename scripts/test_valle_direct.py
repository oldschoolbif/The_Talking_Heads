"""Test VALL-E directly to debug subprocess issues."""
import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path

valle_path = Path("C:/Users/dpipe/valle")
output_path = Path(".cache/smoke_tests/valle_direct_test.wav")
output_path.parent.mkdir(parents=True, exist_ok=True)

script_content = f"""
import sys
import os
from pathlib import Path

# CRITICAL: Change to VALL-E directory FIRST (before any imports)
os.chdir(r"{valle_path}")
sys.path.insert(0, r"{valle_path}")

from utils.generation import generate_audio, SAMPLE_RATE, preload_models
from scipy.io.wavfile import write as write_wav

print("Preloading models...")
preload_models()

print("Generating audio...")
text = "Hello, this is a test of VALL-E X text to speech."
language = "auto"
prompt_path = None

audio_array = generate_audio(text, prompt=prompt_path, language=language)

print("Saving audio...")
output_path = r"{output_path.absolute()}"
write_wav(output_path, SAMPLE_RATE, audio_array)
print("SUCCESS:" + str(output_path))
"""

script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
script_file.write(script_content)
script_file.close()

print(f"Running script: {script_file.name}")
print(f"Working directory: {valle_path}")

result = subprocess.run(
    ['python', script_file.name],
    capture_output=True,
    text=True,
    timeout=120,
    cwd=str(valle_path)
)

print(f"\nReturn code: {result.returncode}")
print(f"\nStdout:\n{result.stdout}")
if result.stderr:
    print(f"\nStderr:\n{result.stderr[-1000:]}")

os.unlink(script_file.name)

if result.returncode == 0 and output_path.exists():
    print(f"\n[OK] SUCCESS! Output: {output_path}")
else:
    print(f"\n[FAIL] FAILED")

