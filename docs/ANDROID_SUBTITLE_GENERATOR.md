# Subtitle Generator
Creates an SRT from a scene plan, using each scene's duration and subtitle text/narration. Output captions are scene-timed and wrapped to a configurable character limit. Usage: `python scripts/android_subtitle_generator.py --plan scene_plan.json --out subtitles.srt`. This is timing-by-scene, not word-level alignment.
