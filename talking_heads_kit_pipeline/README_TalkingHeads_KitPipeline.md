# Talking Heads Kit Pipeline Starter

This zip contains the minimal Omniverse-side pieces for your
audio-driven talking-head pipeline (C-1, C-2, and a C-3 scaffold).

## Layout

- kit_tools/
  - jaw_from_audio.py
  - visemes_from_json.py
- scripts/
  - audio_to_dummy_visemes.py
- config/
  - viseme_map_template.json

## Typical Workflow

1. Generate or record audio (e.g., with Bark TTS or your podcast pipeline)
   and save as a mono 16-bit PCM WAV file, e.g. `episode.wav`.

2. Generate a viseme JSON (C-3 scaffold):

   ```bash
   python scripts/audio_to_dummy_visemes.py episode.wav visemes/episode_visemes.json
   ```

   This dummy script just chops the audio into evenly spaced
   segments and cycles through a small set of viseme labels so
   you can validate the Kit integration end-to-end.

   Later, you can replace the internals of `build_dummy_visemes`
   with a real ML-based viseme/phoneme model using PyTorch or ONNX.

3. In Omniverse Kit, open your stage and select the character prim,
   e.g. `/World/Char`.

4. From the Script Editor, run:

   ```python
   import sys
   sys.path.append(r"PATH_TO_THIS_FOLDER")  # e.g. D:\dev\The_Talking_Heads\talking_heads_kit_pipeline

   from kit_tools.jaw_from_audio import bake_jaw_from_wav
   from kit_tools.visemes_from_json import bake_visemes_from_json

   # C-1: amplitude -> jawOpen (optional)
   bake_jaw_from_wav(
       wav_path=r"D:\audio\episode.wav",
       prim_path="/World/Char",
       attr_name="jawOpen",
       target_fps=60.0,
   )

   # C-2: viseme JSON -> viseme_* attributes
   bake_visemes_from_json(
       json_path=r"D:\visemes\episode_visemes.json",
       prim_path="/World/Char",
       default_fps=60.0,
   )
   ```

5. Scrub the timeline: you should see `jawOpen` and `viseme_*`
   attributes animating on your character prim in the Properties panel.

## Next Steps (C-3 Real ML)

The dummy viseme generator is deliberately simple. Using your
environment (PyTorch + Bark + ffmpeg), you can plug in a real
model that:

- Generates phonemes or visemes from the WAV
- Uses `config/viseme_map_template.json` to map phonemes -> viseme labels
- Writes out the same JSON structure that `visemes_from_json.py` expects.

Once that is in place, your pipeline is:

`Text -> TTS (Bark) -> WAV -> Phonemes/Visemes (ML) -> JSON -> Omniverse animation`.
