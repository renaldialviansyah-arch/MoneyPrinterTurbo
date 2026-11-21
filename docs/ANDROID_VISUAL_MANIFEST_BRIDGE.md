# Fetcher-to-resolver bridge

After downloading assets with `android_visual_fetcher.py`, convert its metadata into the resolver manifest:

```bash
python scripts/android_visual_manifest_bridge.py downloaded_visuals.json --out visual_manifest.json
python scripts/android_visual_asset_engine.py --plan scene_plan.json --manifest visual_manifest.json --assets-out assets_resolved.json --metadata-out assets_metadata.json
``

This bridge retains scene numbering, source, license and notes, and converts paths to absolute paths. It does not validate licensing or media integrity beyond metadata structure.
