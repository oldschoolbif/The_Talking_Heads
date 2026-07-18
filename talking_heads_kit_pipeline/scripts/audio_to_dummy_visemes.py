import wave
import json
import os
from typing import List, Dict

"""
C-3 scaffold: audio -> dummy viseme JSON generator.

This does NOT do real ML-based phoneme recognition yet.
It just chops the audio duration into equal segments and
cycles through a small viseme set, so you can validate the
Kit-side JSON -> animation pipeline end-to-end.

Later, you can replace `build_dummy_visemes` with a Bark/Whisper/
wav2vec2-based phoneme/viseme model using PyTorch.
"""

VISEME_LABELS = [
    "viseme_sil",
    "viseme_PP",
    "viseme_FF",
    "viseme_AA",
    "viseme_EE",
    "viseme_OH",
]


def get_wav_duration(path: str) -> float:
    with wave.open(path, "rb") as w:
        frames = w.getnframes()
        rate = w.getframerate()
        return frames / float(rate)


def build_dummy_visemes(duration: float, segment_length: float = 0.12) -> Dict:
    visemes: List[Dict] = []
    t = 0.0
    idx = 0

    while t < duration:
        start = t
        end = min(t + segment_length, duration)
        label = VISEME_LABELS[idx % len(VISEME_LABELS)]
        visemes.append({"start": round(start, 4),
                        "end": round(end, 4),
                        "label": label})
        t = end
        idx += 1

    return {
        "visemes": visemes,
        "meta": {
            "duration": duration,
            "fps": 60.0,
            "note": "dummy evenly-spaced visemes for pipeline testing"
        }
    }


def main(wav_path: str, out_json: str) -> None:
    if not os.path.isfile(wav_path):
        raise SystemExit(f"WAV not found: {wav_path}")

    duration = get_wav_duration(wav_path)
    data = build_dummy_visemes(duration)

    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[audio_to_dummy_visemes] duration={duration:.2f}s -> {len(data['visemes'])} segments")
    print(f"[audio_to_dummy_visemes] wrote {out_json}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dummy audio -> visemes JSON generator")
    parser.add_argument("wav_path", help="Input WAV file (mono, 16-bit PCM)")
    parser.add_argument("out_json", help="Output JSON path")
    args = parser.parse_args()

    main(args.wav_path, args.out_json)
