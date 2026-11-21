# Renderer v4: scene-plan duration control

## Change
Renderer v3 used `-shortest` in its final mux. In testing, an SRT ending at 4.8 seconds caused the MP4 to end at 4.8 seconds although the scene plan and audio were 5.0 seconds. A short subtitle stream could therefore truncate the final output.

Renderer v4 removes `-shortest`, applies audio padding, and explicitly sets the output duration to the sum of the scene-plan durations. The video duration is therefore controlled by the scene plan; audio is padded if short and trimmed if longer.

## Verified real render test
- Two synthetic still images, each 2.5 seconds, portrait 720x1280
- 24 fps H.264 video
- AAC test tone audio
- SRT subtitle converted to MP4 mov_text
- FFmpeg v7.1.5 runtime
- Output: 5.000 seconds; streams verified as H.264, AAC, mov_text
- Test output size: 82,693 bytes

The test used a local reconstructed copy of the GitHub renderer v3/v4 code. Renderer v4 was committed separately and readback/runtime testing of the committed file is pending.

## Limitations
This was a synthetic technical test, not a finished content video. Wikimedia discovery and downloader network integration, real narration, and visual review remain unvalidated.