#!/usr/bin/env python3
"""Standalone FFmpeg-first render test for Android/Termux.

This is an isolated proof-of-concept helper. It does not import MoneyPrinterTurbo
or Python media libraries. It requires a working FFmpeg executable.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    result = subprocess.run(cmd, check=False)
    if result.returncode:
        raise RuntimeError(f"Command failed (exit {result.returncode})")


def escape_filter_path(path: Path) -> str:
    # FFmpeg filter syntax has special characters; use a conservative absolute path.
    value = str(path.resolve()).replace("\\", "/")
    for char in (":", "'", ",", "[", "]", ";"):
        value = value.replace(char, "\\" + char)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--visual", required=True, help="Input MP4 or image")
    parser.add_argument("--audio", required=True, help="Narration/audio file")
    parser.add_argument("--subtitle", help="Optional SRT subtitle file")
    parser.add_argument("--output", default="android_render_test.mp4")
    parser.add_argument("--duration", type=float, default=15.0, help="Image visual duration in seconds")
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    parser.add_argument("--fps", type=int, default=24)
    args = parser.parse_args()

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ERROR: ffmpeg not found in PATH.", file=sys.stderr)
        return 2

    visual = Path(args.visual).expanduser().resolve()
    audio = Path(args.audio).expanduser().resolve()
    subtitle = Path(args.subtitle).expanduser().resolve() if args.subtitle else None
    output = Path(args.output).expanduser().resolve()

    for item in (visual, audio):
        if not item.is_file():
            print(f"ERROR: input file does not exist: {item}", file=sys.stderr)
            return 2
    if subtitle and not subtitle.is_file():
        print(f"ERROR: subtitle file does not exist: {subtitle}", file=sys.stderr)
        return 2
    if args.width <= 0 or args.height <= 0 or args.fps <= 0 or args.duration <= 0:
        print("ERROR: width, height, fps, and duration must be positive.", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    is_image = visual.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    cmd = [ffmpeg, "-y", "-hide_banner"]

    if is_image:
        cmd += ["-loop", "1", "-framerate", str(args.fps), "-i", str(visual)]
    else:
        cmd += ["-i", str(visual)]
    cmd += ["-i", str(audio)]

    scale_crop = (
        f"scale={args.width}:{args.height}:force_original_aspect_ratio=increase,"
        f"crop={args.width}:{args.height},setsar=1"
    )
    if subtitle:
        subtitle_filter = f"subtitles='{escape_filter_path(subtitle)}'"
        video_filter = scale_crop + "," + subtitle_filter
    else:
        video_filter = scale_crop

    cmd += ["-vf", video_filter, "-r", str(args.fps), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest"]
    if is_image:
        cmd += ["-t", str(args.duration)]
    cmd += ["-movflags", "+faststart", str(output)]

    try:
        run(cmd)
    except Exception as exc:
        print(f"ERROR: render failed: {exc}", file=sys.stderr)
        return 1

    print(f"Render command completed. Output: {output}")
    print("Playback/quality verification must be performed separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
