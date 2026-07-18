"""Check system capabilities for pipeline_capabilities.json generation."""
import sys
import json
import subprocess
from pathlib import Path

capabilities = {
    "audio_tools": {},
    "alignment_tools": {},
    "model_runtimes": {},
    "video_tools": {},
    "image_tools": {},
    "file_system": {},
    "scripting": {},
    "repo_structure": {},
    "environment_variables": {},
    "known_paths": {},
    "capabilities": {}
}

# Check Python packages
def check_package(name, import_name=None):
    """Check if a Python package is available."""
    if import_name is None:
        import_name = name
    try:
        mod = __import__(import_name)
        version = getattr(mod, '__version__', 'unknown')
        return {"available": True, "version": version}
    except ImportError:
        return {"available": False, "version": None}

# Audio tools
capabilities["audio_tools"]["bark_tts"] = check_package("bark")
capabilities["audio_tools"]["pydub"] = check_package("pydub")
capabilities["audio_tools"]["ffmpeg"] = {"available": False, "version": None}
try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        capabilities["audio_tools"]["ffmpeg"] = {"available": True, "version": version_line.split()[2] if len(version_line.split()) > 2 else "unknown"}
except:
    pass

# Model runtimes
torch_info = check_package("torch")
capabilities["model_runtimes"]["pytorch"] = torch_info
if torch_info["available"]:
    try:
        import torch
        capabilities["model_runtimes"]["pytorch"]["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            capabilities["model_runtimes"]["pytorch"]["cuda_version"] = torch.version.cuda
            capabilities["model_runtimes"]["pytorch"]["gpu_count"] = torch.cuda.device_count()
            capabilities["model_runtimes"]["pytorch"]["gpu_name"] = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else None
    except:
        pass

capabilities["model_runtimes"]["onnx_runtime"] = check_package("onnxruntime")
capabilities["model_runtimes"]["whisper"] = check_package("whisper")

# Image/Video tools
capabilities["image_tools"]["opencv"] = check_package("cv2", "cv2")
capabilities["image_tools"]["pillow"] = check_package("PIL", "PIL")

# Alignment tools (check if available)
capabilities["alignment_tools"]["gentle"] = {"available": False, "note": "Not checked"}
capabilities["alignment_tools"]["mfa"] = {"available": False, "note": "Not checked"}
capabilities["alignment_tools"]["coqui_align"] = {"available": False, "note": "Not checked"}
capabilities["alignment_tools"]["wav2vec"] = {"available": False, "note": "Not checked"}

# Video tools
capabilities["video_tools"]["ffmpeg"] = capabilities["audio_tools"]["ffmpeg"]
capabilities["video_tools"]["ffmpeg_features"] = {
    "concat": True,
    "mix": True,
    "overlay": True,
    "render": True,
    "cuda_acceleration": True  # Based on ffmpeg build
}

# File system
capabilities["file_system"]["wsl2"] = {"available": False}
try:
    result = subprocess.run(["wsl", "--list", "--verbose"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        capabilities["file_system"]["wsl2"] = {"available": True, "distributions": result.stdout.strip().split('\n')[1:]}
except:
    pass

capabilities["file_system"]["bash"] = {"available": False}
try:
    result = subprocess.run(["bash", "--version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        capabilities["file_system"]["bash"] = {"available": True}
except:
    pass

capabilities["file_system"]["powershell"] = {"available": True, "version": sys.version}

# Scripting
capabilities["scripting"]["python"] = {
    "available": True,
    "version": sys.version.split()[0],
    "executable": sys.executable
}
capabilities["scripting"]["bash"] = capabilities["file_system"]["bash"]
capabilities["scripting"]["powershell"] = capabilities["file_system"]["powershell"]

# Repo structure
repo_root = Path(__file__).parent.parent
capabilities["repo_structure"]["root"] = str(repo_root)
capabilities["repo_structure"]["has_src"] = (repo_root / "src").exists()
capabilities["repo_structure"]["has_scripts"] = (repo_root / "scripts").exists()
capabilities["repo_structure"]["has_config"] = (repo_root / "config").exists()
capabilities["repo_structure"]["has_examples"] = (repo_root / "examples").exists()

# Environment variables
import os
capabilities["environment_variables"]["python_path"] = os.environ.get("PYTHONPATH", "")
capabilities["environment_variables"]["cuda_visible_devices"] = os.environ.get("CUDA_VISIBLE_DEVICES", "")

# Known paths
capabilities["known_paths"]["python_executable"] = sys.executable
capabilities["known_paths"]["working_directory"] = str(Path.cwd())
capabilities["known_paths"]["repo_root"] = str(repo_root)

# Capabilities
capabilities["capabilities"]["can_run_python"] = True
capabilities["capabilities"]["can_run_bash"] = capabilities["file_system"]["bash"]["available"]
capabilities["capabilities"]["can_run_powershell"] = True
capabilities["capabilities"]["can_install_python_packages"] = True
capabilities["capabilities"]["can_accept_user_files"] = True
capabilities["capabilities"]["can_write_files"] = True
capabilities["capabilities"]["can_generate_scripts"] = True
capabilities["capabilities"]["can_orchestrate_pipelines"] = True

# Print JSON
print(json.dumps(capabilities, indent=2))

