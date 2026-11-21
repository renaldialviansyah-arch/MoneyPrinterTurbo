# Explicit HTTPS Asset Downloader (Experimental)

This downloader only retrieves assets explicitly listed with a `url` in the JSON manifest. It does not search the web, scrape sites, bypass restrictions or infer permission to reuse media.

## Manifest example
```json
{
  "topic": "Sample",
  "assets": [
    {"role": "visual", "url": "https://example.org/clip.mp4", "filename": "clip.mp4"},
    {"role": "audio", "url": "https://example.org/voice.mp3"},
    {"role": "subtitle", "url": "https://example.org/captions.srt"}
  ]
}
```

## Usage
```bash
python scripts/android_asset_download.py assets.json --output-dir assets --max-mb 100
```

- HTTPS only; URL credentials rejected.
- File extensions checked against asset role.
- HTML content rejected.
- Download size capped (default 100 MB per asset).
- Redirect destination is checked for HTTPS.
- Files are downloaded to a specified output folder.
- This does not validate copyright, provider terms, file integrity, or actual media decoding. Use sources that permit download and reuse.

This is experimental and not tested on Android.
