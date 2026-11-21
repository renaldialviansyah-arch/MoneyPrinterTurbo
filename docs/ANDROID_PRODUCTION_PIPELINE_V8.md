# Android Production Pipeline v8

Pipeline v8 builds on v7 and uses the cinematic scene planner v2.

## New planning metadata
- Scene-specific search_terms for visual discovery
- Shot type and camera-movement descriptions
- Composition guidance (subject clarity, depth layers, lighting)
- Continuity notes to preserve documentary style

## Run
Use the same inputs as v7, but run:
```
python scripts/android_production_pipeline_v8.py --script script.txt --auto-visuals --model /path/to/voice.onnx --output production/final.mp4
```
Or supply `--manifest` for local assets. Piper voice generation, audio duration alignment, subtitle generation, rendering, and QC remain integrated.

## Limitations
This remains an automated planning system, not a semantic image-generation model. Search results can be irrelevant; inspect the visual source/license report. Full end-to-end production has not yet been tested on-device. Requires FFmpeg/ffprobe, Piper CLI/model (unless audio is supplied), and network access for automatic Commons assets.


## Rendering reliability update

- Video assets are looped during scene rendering so a short source clip can fill the scene duration instead of leaving a truncated segment.
- Final narration is padded when needed and trimmed to the computed video duration, reducing audio/video duration drift.
- These renderer changes have been committed but still require a real production run for end-to-end validation.
