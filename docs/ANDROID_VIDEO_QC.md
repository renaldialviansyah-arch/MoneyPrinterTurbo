# Video QC
Run ffprobe-based structural checks on an MP4: streams, basic dimensions, duration and optional duration tolerance. Usage: `python scripts/android_video_qc.py output.mp4 --expected-duration 8 --report qc_report.json`. It does not assess visual quality, audio loudness, or caption readability; those require separate review.
