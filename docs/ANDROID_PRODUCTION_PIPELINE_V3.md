# Production Pipeline v3

Adds optional offline eSpeak/eSpeak NG narration to pipeline v2. When --audio is omitted, script text is synthesized to WAV using --voice and --speed. Then scene planning, SRT generation, reviewed local asset resolution, render, and structural QC run.

Example: `python scripts/android_production_pipeline_v3.py --script narration.txt --manifest assets.json --output final.mp4 --voice en-us --speed 150`

Reviewed visuals remain local. Voice quality is synthetic and durations may differ from planner estimates, so QC may fail on timing. Supply --audio to use external narration instead.
