# Pipeline v6 — automated visual sourcing

Use `--auto-visuals` to search Wikimedia Commons per scene, filter to a license allow-list, download candidate images, and generate a manifest/source report. Otherwise supply a reviewed local manifest with `--manifest`.

Example: `python scripts/android_production_pipeline_v6.py --script narration.txt --auto-visuals --model voices/en_US-lessac-medium.onnx --output production/final.mp4`

This requires network access for Commons, Piper CLI/model for narration, and FFmpeg/ffprobe. Automatically selected visuals are candidates; review imagery and licensing metadata before publication. Failed asset retrieval stops the run instead of silently producing an incomplete video.
