# Pipeline v5 — Neural voice and audio alignment

Use this pipeline for end-to-end rendering. Piper neural narration is preferred; eSpeak is optional fallback; supplied audio bypasses TTS. The pipeline aligns planned scene durations to the actual narration WAV duration before caption timing and render, reducing the risk of cut-off narration or mismatched captions.

Requirements: Python, FFmpeg/ffprobe, Piper CLI and an ONNX voice model (unless supplying audio), local visual assets mapped in a manifest.

Example:
`python scripts/android_production_pipeline_v5.py --script narration.txt --manifest assets.json --model voices/en_US-lessac-medium.onnx --output production/final.mp4`

Asset manifest must map every planned scene to a local asset path, e.g. `{"assets":[{"scene":1,"path":"visuals/scene1.jpg","source":"...","license":"..."}]}`. Paths are relative to the manifest file. Pipeline writes working files and a report to work-dir.
