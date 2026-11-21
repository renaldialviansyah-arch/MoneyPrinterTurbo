# Android Mobile Video Workflow — Experimental readiness

## Current workflow
This isolated workflow can validate a JSON manifest, optionally download assets with explicit HTTPS URLs, and invoke the FFmpeg render helper. It is not a full automatic text-to-video product: it does not generate scripts, narration, captions or find media automatically.

## Manifest
Paths are relative to the manifest file. Example:

```json
{
  "topic": "A short explainer",
  "assets": [
    {"role": "visual", "path": "visual.mp4", "source": "user-provided"},
    {"role": "audio", "path": "narration.mp3", "source": "user-provided"},
    {"role": "subtitle", "path": "captions.srt", "source": "user-provided"}
  ]
}
```

For explicit HTTPS downloads, use entries with `url` and optionally `filename`, and run with `--download`. Ensure source licensing and provider terms permit downloading and reuse.

## Run
```bash
python scripts/android_mobile_workflow.py assets.json --output final.mp4
```

For URL entries:
```bash
python scripts/android_mobile_workflow.py assets.json --download --assets-dir assets --output final.mp4
```

## Conservative settings
```bash
python scripts/android_mobile_workflow.py assets.json --output final.mp4 --width 480 --height 854 --fps 20 --duration 8
```

## Preparation checks
1. Run `python scripts/android_compat_probe.py`.
2. Verify the FFmpeg binary and required encoder/filter support.
3. Create a small manifest and assets.
4. Run the workflow with conservative resolution.
5. Manually play and verify the output; script completion alone does not certify video quality.

## What this does NOT yet provide
- AI script generation
- AI narration/TTS
- subtitle generation/transcription
- stock-media discovery
- automatic licensing verification
- video-quality inspection
- tested Android runtime support

The project remains experimental until actual device testing is performed.
