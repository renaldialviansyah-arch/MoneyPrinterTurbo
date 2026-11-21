# Pipeline v4 (Neural narration)
Piper neural TTS is the default and requires a downloaded voice model. Specify --model voice.onnx. eSpeak is available via --tts-engine espeak as a fallback. User-supplied audio bypasses synthesis. Remaining steps are planning, subtitle generation, reviewed asset resolution, rendering, and structural QC.
Example: `python scripts/android_production_pipeline_v4.py --script narration.txt --manifest assets.json --model voices/en_US-lessac-medium.onnx --output final.mp4`
