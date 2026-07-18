# The Talking Heads Podcast Creator — Vision & Roadmap

## Mission
Create scalable, high-quality, AI-driven video podcasts from scripts.

## What THPC Is
- Multi-persona video generation from structured scripts  
- Avatar-agnostic — supports cloud avatars now; 3D avatars later  
- Full audio + music + overlay pipeline for polished output  
- Config-driven persona, scene, layout, language, voice  

## What THPC Is **Not** (Yet)
- Traditional film-level cinematics  
- Human-actor-level realism (until Phase 3 complete)  

## Roadmap
- Phase 1: MVP — cloud avatars, audio engine, basic mixing  
- Phase 2: Polished product — overlays, scene/layout presets, publishable episodes  
- Phase 3: 3D-driven avatars + full USD/Omniverse pipeline  

## Why This Makes Sense
1. Low barrier to entry + fast iteration  
2. Audio-first, storytelling-first: clean, simple visuals don’t compete with content  
3. Modular architecture for long-term flexibility  
4. Realistic path to future growth and sophistication  

## Getting Started
1. `config/personas.yaml` — define personas (voice, avatar settings)  
2. `config/scenes.yaml` — define backgrounds/layouts  
3. Write script with persona tags and optional cues (music, scene changes, overlays)  
4. Run `thpc build --script myscript.md` → outputs MP4 + assets  

## Phase 2 Goal
Create consistent, high-quality “episodes” — reliable output, minimal manual labor, scalable production.
