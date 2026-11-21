# Android Render Test Engine (Experimental)

This helper is an isolated FFmpeg-first proof-of-concept and does not import the main MoneyPrinterTurbo application.

## Inputs
- One image or MP4 visual source.
- One audio/narration file.
- Optional SRT subtitle.
- Output defaults to portrait 720x1280, 24 fps.

## Usage

Image input (default image duration 15 seconds):

```bash
python scripts/android_render_test.py --visual image.jpg --audio narration.mp3 --subtitle captions.srt --output test.mp4
```

Video input:

```bash
python scripts/android_render_test.py --visual source.mp4 --audio narration.mp3 --subtitle captions.srt --output test.mp4
```

For a smaller device test:

```bash
python scripts/android_render_test.py --visual image.jpg --audio narration.mp3 --output test.mp4 --width 480 --height 854 --fps 20 --duration 8
```

## Requirements
- FFmpeg executable available in PATH.
- Input files readable and output folder writable.
- For subtitle burn-in, FFmpeg must be built with the subtitles/libass filter. The helper will fail visibly if that filter is unavailable.

## Behavior and limitations
- Image sources are looped for the requested duration.
- Video sources are scaled and center-cropped to the target portrait size.
- The provided audio is muxed and the render ends at the shortest relevant stream due to `-shortest`.
- Uses libx264 and AAC; these encoder names may not be available in every Android FFmpeg build.
- Uses an ultrafast preset and high CRF to keep the first experiment conservative.
- No validation of output playback is performed automatically.
- No files in the main MoneyPrinterTurbo pipeline are modified.
