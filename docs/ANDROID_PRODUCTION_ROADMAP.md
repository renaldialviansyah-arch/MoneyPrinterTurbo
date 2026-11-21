# Android Mobile Video Production Roadmap

Branch: `android-mobile-work` only. Keep upstream/main unchanged.

## Current experimental building blocks
1. Asset manifest validation and explicit-URL download.
2. FFmpeg-first portrait render helper.
3. Mobile workflow orchestrator for manifest/download/render.
4. Storyboard and SRT draft builder from a supplied script.
5. Compatibility probe.

## Next integration phases
- **Phase A — Offline smoke tests:** add tests for storyboard timing, empty text, manifest validation, URL safety and render command construction; test syntax and behavior on a desktop runner where available.
- **Phase B — Script input and scene plan:** make one project directory layout; normalize outputs and generated JSON/SRT.
- **Phase C — Visual acquisition:** connect scene prompts to an approved provider or explicit user assets; preserve source URL and licensing notes; no scraping by default.
- **Phase D — Narration:** implement selectable TTS providers behind an interface; keep credentials out of the repo; fail gracefully when no provider is configured.
- **Phase E — Timing alignment:** derive subtitle durations from audio where possible, not fixed sentence estimates.
- **Phase F — Render integration:** create one workflow command that accepts project config and produces MP4; test codecs and filter support on Android.
- **Phase G — Device validation:** execute probe, render a short test clip, playback and inspect sound/subtitles, then produce a longer clip.

## Status / limitations
Modules in this branch are experimental. They have not yet been run in Termux or validated on-device. A working video production system cannot be claimed until device tests and a full output playback are successful.
