# Android Multi-Scene Render v2

This helper assembles scene-plan JSON and supplied scene media into a portrait MP4.

## Inputs
- `--plan`: output from the Android scene planner (scene durations included).
- `--assets`: JSON array with exactly one image/video path per scene, ordered to match the plan.
- `--audio`: narration/audio file.
- `--subtitle`: optional SRT subtitle file (mapped as soft MP4 text track).
- `--output`: destination MP4.

## Example
Create `scene_assets.json`:
```json
[
  "visuals/scene_001.jpg",
  "visuals/scene_002.mp4",
  "visuals/scene_003.jpg"
]
```

Run:
```sh
python scripts/android_multiscene_render_v2.py --plan scene_plan.json --assets scene_assets.json --audio narration.mp3 --subtitle subtitles.srt --output final.mp4
```

The number of entries in the asset list must exactly match the plan's scenes.
Paths are resolved relative to the assets JSON file. Scene files are normalized
to portrait resolution and H.264, then joined, with narration encoded as AAC.
The optional subtitle is included as a soft subtitle track. It may not appear
automatically in all Android players; use a burn-in workflow for hard subtitles.

## Limitations / validation
This is an assembly helper, not an image/video generator or audio transcription
system. It requires FFmpeg including libx264 and MP4 muxing support. On-device
render, concat behavior, audio timing, and subtitle playback still need testing.
