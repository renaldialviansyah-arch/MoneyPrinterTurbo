# Android Helper Smoke Tests

Run from the repository root:

```bash
python -m unittest discover -s tests -p 'test_android_mobile.py' -v
```

The current suite checks storyboard sentence segmentation, approximate SRT timing, timestamp formatting, extension constants, and a local manifest path fixture. Tests are dependency-free.

These tests have **not yet been executed** in an Android or remote environment. Passing them on a desktop Python runtime would not certify Termux, FFmpeg, codecs, media playback, or end-to-end rendering.
