from pxr import Usd, Sdf
import omni.usd
import wave
import audioop
import os

"""
C-1: Audio amplitude -> single jawOpen animation channel for Omniverse Kit.
Use from the Kit Script Editor:

    from kit_tools.jaw_from_audio import bake_jaw_from_wav
    bake_jaw_from_wav(
        wav_path=r"C:\Path\To\episode.wav",
        prim_path="/World/Char",
        attr_name="jawOpen",
        target_fps=60.0,
    )
"""

def bake_jaw_from_wav(
    wav_path: str,
    prim_path: str,
    attr_name: str = "jawOpen",
    target_fps: float = 60.0,
    gamma: float = 0.7,
) -> None:
    if not os.path.isfile(wav_path):
        raise RuntimeError(f"WAV file not found: {wav_path}")

    ctx = omni.usd.get_context()
    stage = ctx.get_stage()
    if not stage:
        raise RuntimeError("No USD stage is open")

    prim = stage.GetPrimAtPath(prim_path)
    if not prim:
        raise RuntimeError(f"Prim not found at {prim_path}")

    attr = prim.GetAttribute(attr_name)
    if not attr:
        attr = prim.CreateAttribute(attr_name, Sdf.ValueTypeNames.Float)

    with wave.open(wav_path, 'rb') as w:
        n_channels = w.getnchannels()
        sample_width = w.getsampwidth()
        framerate = w.getframerate()
        n_frames = w.getnframes()

        duration_sec = n_frames / float(framerate)
        print(f"[jaw_from_audio] {os.path.basename(wav_path)}: "
              f"{duration_sec:.2f}s, {framerate}Hz, {n_channels}ch")

        frames_per_step = max(1, int(framerate / target_fps))
        rms_values = []

        while True:
            data = w.readframes(frames_per_step)
            if not data:
                break

            if n_channels > 1:
                data = audioop.tomono(data, sample_width, 0.5, 0.5)

            rms = audioop.rms(data, sample_width)
            rms_values.append(rms)

    if not rms_values:
        raise RuntimeError("No audio data read (empty WAV or incompatible format?)")

    max_rms = max(rms_values) or 1.0
    normalized = [float(v) / max_rms for v in rms_values]
    normalized = [pow(v, gamma) for v in normalized]

    stage.SetTimeCodesPerSecond(target_fps)
    start_frame = 0
    end_frame = start_frame + len(normalized) - 1
    stage.SetStartTimeCode(start_frame)
    stage.SetEndTimeCode(end_frame)

    for i, value in enumerate(normalized):
        t = start_frame + i
        attr.Set(value, t)

    print(f"[jaw_from_audio] Baked {len(normalized)} frames "
          f"to {prim_path}.{attr_name} [{start_frame}, {end_frame}] @ {target_fps}fps")
