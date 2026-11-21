# Android Visual Asset Engine

A dependency-free, offline manifest validator/resolver for scene-plan visuals. It intentionally does not scrape, generate images, or download arbitrary URLs.

## Files
- `scripts/android_visual_asset_engine.py`: checks each scene's asset and produces renderer-compatible ordered JSON paths plus provenance metadata.
- `examples/android_visual_manifest.example.json`: manifest example.

## Use
```bash
python scripts/android_visual_asset_engine.py --plan scene_plan.json --manifest visual_manifest.json --assets-out assets_resolved.json --metadata-out assets_metadata.json
```
Then hand `assets_resolved.json` to `android_multiscene_render_v3.py` as its `--assets` argument.

Paths in the manifest are resolved relative to the manifest file. Each scene number (1-based) must be present exactly once, and each asset must exist and have a supported image/video extension. The output order follows the scene plan, not manifest ordering. Missing assets cause a failure rather than a silent placeholder. Extra scene entries are reported and ignored.

The metadata file records path, image/video type, source, license and notes. License defaults to `unspecified`; confirm usage rights yourself. The tool does not certify licensing.

## Manifest schema (minimal)
```json
{ "assets": [ { "scene": 1, "path": "visuals/scene01.jpg", "source": "local file", "license": "unspecified", "notes": "" } ] }
```
