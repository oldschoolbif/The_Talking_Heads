from pxr import Usd, Sdf
import omni.usd
import json
import os
from typing import Dict, List

"""
C-2: JSON viseme timeline -> per-viseme float attributes on a character prim.

Use from the Kit Script Editor:

    from kit_tools.visemes_from_json import bake_visemes_from_json
    bake_visemes_from_json(
        json_path=r"C:\Path\To\episode_visemes.json",
        prim_path="/World/Char",
        default_fps=60.0,
    )
"""

def _ensure_float_attr(prim: Usd.Prim, name: str):
    attr = prim.GetAttribute(name)
    if not attr:
        attr = prim.CreateAttribute(name, Sdf.ValueTypeNames.Float)
    return attr


def bake_visemes_from_json(
    json_path: str,
    prim_path: str,
    default_fps: float = 60.0,
    hold_between_keys: bool = True,
) -> None:
    if not os.path.isfile(json_path):
        raise RuntimeError(f"Viseme JSON not found: {json_path}")

    ctx = omni.usd.get_context()
    stage = ctx.get_stage()
    if not stage:
        raise RuntimeError("No USD stage is open")

    prim = stage.GetPrimAtPath(prim_path)
    if not prim:
        raise RuntimeError(f"Prim not found at {prim_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    visemes = data.get("visemes", [])
    if not visemes:
        raise RuntimeError("No visemes found in JSON")

    fps = float(data.get("meta", {}).get("fps", default_fps))

    labels = sorted({v["label"] for v in visemes})
    attrs = {label: _ensure_float_attr(prim, label) for label in labels}

    max_end = max(v["end"] for v in visemes)
    total_frames = int(max_end * fps) + 1

    stage.SetTimeCodesPerSecond(fps)
    stage.SetStartTimeCode(0)
    stage.SetEndTimeCode(total_frames)

    for label, attr in attrs.items():
        attr.Clear()

    for v in visemes:
        start_sec = float(v["start"])
        end_sec = float(v["end"])
        label = v["label"]
        attr = attrs[label]

        start_frame = int(round(start_sec * fps))
        end_frame = int(round(end_sec * fps))

        if hold_between_keys:
            if start_frame > 0:
                attr.Set(0.0, start_frame - 1)
            attr.Set(1.0, start_frame)
            attr.Set(1.0, end_frame)
            attr.Set(0.0, end_frame + 1)
        else:
            attr.Set(1.0, start_frame)
            attr.Set(0.0, end_frame)

    print(f"[visemes_from_json] Baked visemes for labels: {', '.join(labels)}")
    print(f"[visemes_from_json] Time range 0..{total_frames} @ {fps} fps")
