# Visual Asset Engine tests

Run from repository root:

```bash
python -m unittest discover -s tests -p 'test_android_visual_asset_engine.py'
```

Coverage: plan-order mapping, metadata, missing scene, duplicate scene, and extra entries. Tests use placeholder local files and validate resolver behavior only; they do not exercise FFmpeg or Android playback.
