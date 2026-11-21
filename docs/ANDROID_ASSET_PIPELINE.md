# Android Asset Pipeline (Experimental)

This is a manifest-first asset workflow. It intentionally does not fetch media from websites yet; it defines, validates and tracks input assets so later retrieval/download functionality can be added safely and legally.

## Manifest example
Save as `assets.json`:

```json
{
  "topic": "A short documentary about urban farming",
  "assets": [
    {"role": "visual", "path": "visual.mp4", "source": "user-provided"},
    {"role": "audio", "path": "narration.mp3", "source": "user-provided"},
    {"role": "subtitle", "path": "captions.srt", "source": "user-provided"}
  ]
}
```

## Validate
```bash
python scripts/android_asset_manifest.py assets.json
python scripts/android_asset_manifest.py assets.json --check-files
```

The second command checks local files relative to the manifest directory.

## Supported extensions
- Visual: MP4, MOV, MKV, WEBM, JPG, JPEG, PNG, WEBP
- Audio: MP3, WAV, M4A, AAC, OGG
- Subtitle: SRT, VTT

## Workflow design
1. Specify a topic and asset list in a JSON manifest.
2. Keep source and license/attribution notes in the manifest metadata where applicable.
3. Validate asset roles and file types before rendering.
4. Check local file presence before invoking the render helper.
5. Keep asset acquisition/download as a separate future module.

## Limitation
This module validates a manifest only. It does not search, download, scrape, or render media.
