# Production Pipeline v2

Integrates scene planning, optional scene-timed SRT generation, local reviewed asset resolution, renderer v4, and FFprobe structural QC with target-duration tolerance. Requires script text, a reviewed local asset manifest, and audio. It does not download assets or synthesize narration. Usage: `python scripts/android_production_pipeline_v2.py --script narration.txt --manifest assets.json --audio voice.mp3 --output final.mp4`. Intermediate files and reports are retained. QC is structural and does not assess perceptual quality.
