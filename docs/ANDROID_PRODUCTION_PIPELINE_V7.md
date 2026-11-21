# Pipeline v7 — dynamic visual motion

Adds subtle or dynamic Ken Burns zoom/pan motion to still image scenes. `--motion subtle` default, `dynamic` stronger zoom, `none` disables zoom/pan. Pipeline retains neural TTS, audio alignment, automatic Commons sourcing (optional), subtitles, rendering, and QC.

Example: `python scripts/android_production_pipeline_v7.py --script narration.txt --auto-visuals --model voices/en_US-lessac-medium.onnx --motion subtle --output production/final.mp4`

Motion is applied to still images only; video sources are normalized and rendered without this image zoom effect. Visual quality and transitions still require human review.
