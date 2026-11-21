# Android Minimal Profile (Experimental)

This profile is a staged adaptation plan for Android/Termux and is deliberately isolated from MoneyPrinterTurbo's production pipeline.

## Principles
- Keep upstream code and defaults intact while compatibility is uncertain.
- Prefer a single-user, CLI-first execution path.
- Do not require Redis for the first proof of concept.
- Start with user-provided assets, narration, and subtitle files.
- Use FFmpeg for the first render experiment; add MoviePy only after direct FFmpeg capability is established.
- Disable optional local transcription, GPU paths, cross-posting, and advanced providers in the first experiment.
- Use one render worker and low-resolution output to reduce memory and thermal risk.

## Phase 0: Diagnostics
Run the dependency-free diagnostic script:

```bash
python scripts/android_compat_probe.py
```

It reports Python/platform information, FFmpeg presence and a small encoder check, optional module availability, and writable working/home directories. It does not install or change anything.

## Phase 1: FFmpeg proof of concept
On the Android/Termux device, separately verify that the local FFmpeg build can combine a small input video/image, a short audio file and an SRT subtitle into a portrait MP4. Keep test assets small and target 480p/720p initially. Record command output and playback results. Do not infer success from the probe alone.

## Phase 2: Python media subset
Only after FFmpeg output is verified, test imports and minimal use of NumPy, Pillow and MoviePy individually. PyAV, Faster-Whisper/CTranslate2, Redis, Streamlit and provider SDKs are not prerequisites for the initial render proof.

## Phase 3: Incremental integration
Add a mobile-specific launcher/configuration as a separate layer. The mobile profile should not silently change upstream behavior. Add one feature at a time, with reproducible validation.

## Limitations
Android/Termux compatibility is experimental. This document and the probe do not certify installation or rendering. Device-specific results are required.
