"""
Utilities for converting PLY/OBJ meshes to USD format.

Supports multiple conversion methods:
1. USD Python API (pxr) - preferred
2. Omniverse Create - via command line
3. Blender Python API - alternative
"""

from pathlib import Path
from typing import Optional
import subprocess
import tempfile


def convert_ply_to_usd_pxr(ply_path: Path, usd_path: Path) -> Path:
    """
    Convert PLY to USD using USD Python API (pxr).
    
    Args:
        ply_path: Path to PLY file
        usd_path: Path for output USD file
    
    Returns:
        Path to created USD file
    
    Raises:
        ImportError: If pxr is not available
        RuntimeError: If conversion fails
    """
    try:
        from pxr import Usd, UsdGeom, Gf, Sdf
    except ImportError:
        raise ImportError(
            "USD Python API (pxr) not available. "
            "Install via Omniverse or build from source."
        )
    
    # Read PLY file
    vertices = []
    faces = []
    
    with open(ply_path, 'r') as f:
        lines = f.readlines()
        
        # Parse header
        header_end = 0
        num_vertices = 0
        num_faces = 0
        
        for i, line in enumerate(lines):
            if line.startswith('element vertex'):
                num_vertices = int(line.split()[2])
            elif line.startswith('element face'):
                num_faces = int(line.split()[2])
            elif line.startswith('end_header'):
                header_end = i + 1
                break
        
        # Parse vertices
        for i in range(header_end, header_end + num_vertices):
            parts = lines[i].strip().split()
            if len(parts) >= 3:
                x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                vertices.append((x, y, z))
        
        # Parse faces
        for i in range(header_end + num_vertices, header_end + num_vertices + num_faces):
            parts = lines[i].strip().split()
            if len(parts) >= 4:
                # PLY format: "3 v1 v2 v3" for triangle
                num_verts = int(parts[0])
                if num_verts == 3:
                    v1, v2, v3 = int(parts[1]), int(parts[2]), int(parts[3])
                    faces.append((v1, v2, v3))
    
    # Create USD stage
    stage = Usd.Stage.CreateNew(str(usd_path))
    
    # Create mesh prim
    mesh_prim = UsdGeom.Mesh.Define(stage, '/FaceMesh')
    
    # Set vertices
    points = [Gf.Vec3f(v[0], v[1], v[2]) for v in vertices]
    mesh_prim.GetPointsAttr().Set(points)
    
    # Set face vertex indices
    face_vertex_counts = [3] * len(faces)  # All triangles
    face_vertex_indices = []
    for face in faces:
        face_vertex_indices.extend(face)
    
    mesh_prim.GetFaceVertexCountsAttr().Set(face_vertex_counts)
    mesh_prim.GetFaceVertexIndicesAttr().Set(face_vertex_indices)
    
    # Set extent (bounding box) - compute from points
    if points:
        from pxr import Vt
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        z_coords = [p[2] for p in points]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        min_z, max_z = min(z_coords), max(z_coords)
        extent = Vt.Vec3fArray([Gf.Vec3f(min_x, min_y, min_z), Gf.Vec3f(max_x, max_y, max_z)])
        mesh_prim.GetExtentAttr().Set(extent)
    
    # Save stage
    stage.Save()
    
    return usd_path


def convert_ply_to_usd_omniverse(ply_path: Path, usd_path: Path, omniverse_path: Optional[Path] = None) -> Path:
    """
    Convert PLY to USD using Omniverse Create (command line).
    
    This requires Omniverse Create to be installed and accessible.
    
    Args:
        ply_path: Path to PLY file
        usd_path: Path for output USD file
        omniverse_path: Path to Omniverse installation (optional)
    
    Returns:
        Path to created USD file
    
    Raises:
        RuntimeError: If conversion fails
    """
    # This would use Omniverse Create's command-line tools
    # For now, raise NotImplementedError as this requires specific Omniverse setup
    raise NotImplementedError(
        "Omniverse command-line conversion not yet implemented. "
        "Use Omniverse Create GUI to import PLY and export as USD, "
        "or use USD Python API (pxr) method."
    )


def convert_ply_to_usd(ply_path: Path, usd_path: Path, method: str = "auto") -> Path:
    """
    Convert PLY mesh to USD format.
    
    Args:
        ply_path: Path to PLY file
        usd_path: Path for output USD file
        method: Conversion method ("auto", "pxr", "omniverse", "blender")
    
    Returns:
        Path to created USD file
    
    Raises:
        RuntimeError: If conversion fails
    """
    if not ply_path.exists():
        raise FileNotFoundError(f"PLY file not found: {ply_path}")
    
    usd_path.parent.mkdir(parents=True, exist_ok=True)
    
    if method == "auto":
        # Try pxr first, then fall back to other methods
        try:
            return convert_ply_to_usd_pxr(ply_path, usd_path)
        except ImportError:
            # Try other methods
            try:
                return convert_ply_to_usd_omniverse(ply_path, usd_path)
            except NotImplementedError:
                raise RuntimeError(
                    "No USD conversion method available. "
                    "Install USD Python API (pxr) or use Omniverse Create manually."
                )
    elif method == "pxr":
        return convert_ply_to_usd_pxr(ply_path, usd_path)
    elif method == "omniverse":
        return convert_ply_to_usd_omniverse(ply_path, usd_path)
    else:
        raise ValueError(f"Unknown conversion method: {method}")

