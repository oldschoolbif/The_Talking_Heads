"""
Test 3DDFA -> USD conversion workflow.

This tests:
1. 3DDFA reconstruction (if PLY doesn't exist)
2. PLY -> USD conversion using USD Python API
"""

import sys
import os
from pathlib import Path

# FIX UNICODE FIRST - MUST BE BEFORE ANY OTHER IMPORTS
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.mesh_to_usd import convert_ply_to_usd_pxr
from src.core.tddfa_provider import TDDFAProvider
import yaml

def main():
    print("=== Testing 3DDFA -> USD Conversion ===\n")
    
    # Load config
    config_path = project_root / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Test image
    source_image = Path.home() / "Downloads" / "blonde.png"
    if not source_image.exists():
        print(f"[ERROR] Source image not found: {source_image}")
        print("Please ensure blonde.png is in your Downloads folder.")
        return 1
    
    print(f"[OK] Source image: {source_image}\n")
    
    # Check if PLY already exists
    result_dir = Path(config.get("tddfa", {}).get("result_dir", "examples/results"))
    result_dir.mkdir(parents=True, exist_ok=True)
    
    img_name = source_image.stem
    ply_file = result_dir / f"{img_name}_ply.ply"
    
    # Step 1: Run 3DDFA if PLY doesn't exist
    if not ply_file.exists():
        print("Step 1: Running 3DDFA reconstruction...")
        print(f"  This will create: {ply_file}\n")
        
        tddfa_config = config.get("tddfa", {})
        tddfa_provider = TDDFAProvider(tddfa_config)
        
        if not tddfa_provider.is_available():
            print("[ERROR] 3DDFA is not available")
            print("Please ensure 3DDFA is set up correctly.")
            return 1
        
        # Create temporary audio (3DDFA needs audio but we only need mesh)
        import tempfile
        import numpy as np
        import soundfile as sf
        
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_audio.close()
        temp_audio_path = Path(temp_audio.name)
        
        # Create 1-second silent audio
        sample_rate = 16000
        duration = 1.0
        silent_audio = np.zeros(int(sample_rate * duration), dtype=np.float32)
        sf.write(str(temp_audio_path), silent_audio, sample_rate)
        
        try:
            # Run 3DDFA
            video_path, duration = tddfa_provider.generate(
                audio_path=temp_audio_path,
                avatar_id=str(source_image),
                source_image=source_image
            )
            
            # Find PLY output
            if not ply_file.exists():
                # Try to find any PLY file with this name
                ply_files = list(result_dir.glob(f"{img_name}_*.ply"))
                if ply_files:
                    ply_file = ply_files[0]
                    print(f"[INFO] Found PLY: {ply_file}")
                else:
                    print(f"[ERROR] 3DDFA did not generate PLY file")
                    print(f"  Expected: {ply_file}")
                    print(f"  Checked: {result_dir}")
                    return 1
            
            print(f"[OK] 3DDFA reconstruction complete: {ply_file}\n")
            
        finally:
            # Cleanup temp audio
            if temp_audio_path.exists():
                temp_audio_path.unlink()
    else:
        print(f"[OK] PLY file already exists: {ply_file}\n")
    
    # Step 2: Convert PLY to USD
    print("Step 2: Converting PLY to USD...")
    usd_file = result_dir / f"{img_name}_mesh.usd"
    
    try:
        convert_ply_to_usd_pxr(ply_file, usd_file)
        print(f"[OK] USD conversion complete: {usd_file}\n")
        
        # Verify USD file
        if usd_file.exists():
            size_kb = usd_file.stat().st_size / 1024
            print(f"[OK] USD file created successfully")
            print(f"  Size: {size_kb:.2f} KB")
            print(f"  Location: {usd_file}")
            return 0
        else:
            print(f"[ERROR] USD file was not created")
            return 1
            
    except ImportError as e:
        print(f"[ERROR] USD Python API (pxr) not available")
        print(f"  Error: {e}")
        print("\nTo fix:")
        print("  1. Install usd-core: pip install usd-core")
        print("  2. Or install Omniverse for USD Python API")
        return 1
    except Exception as e:
        print(f"[ERROR] USD conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

