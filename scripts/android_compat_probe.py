#!/usr/bin/env python3
"""Lightweight, dependency-free Android/Termux compatibility probe.

This script intentionally does not install packages, change repository files,
or launch a render. It checks the local Python runtime, FFmpeg executable,
common optional imports, and storage writability.
"""
from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OPTIONAL_MODULES = (
    "moviepy",
    "numpy",
    "PIL",
    "av",
    "faster_whisper",
    "pydub",
    "streamlit",
    "fastapi",
)


def check_ffmpeg() -> dict[str, object]:
    executable = shutil.which("ffmpeg")
    if not executable:
        return {"available": False, "path": None, "version": None, "encoders": []}
    try:
        version_result = subprocess.run(
            [executable, "-version"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        version_line = (version_result.stdout or version_result.stderr).splitlines()
        version = version_line[0] if version_line else "version output unavailable"
    except Exception as exc:  # diagnostic script: capture and report
        version = f"version check failed: {type(exc).__name__}: {exc}"

    encoders: list[str] = []
    try:
        encoder_result = subprocess.run(
            [executable, "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        output = encoder_result.stdout or encoder_result.stderr
        for name in ("libx264", "h264", "mpeg4", "aac"):
            if name in output:
                encoders.append(name)
    except Exception as exc:
        encoders = [f"encoder check failed: {type(exc).__name__}"]

    return {"available": True, "path": executable, "version": version, "encoders": encoders}


def check_writable(path: Path) -> dict[str, object]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=".mpt_probe_", dir=path, delete=True) as f:
            f.write(b"probe")
        return {"path": str(path), "writable": True, "error": None}
    except Exception as exc:
        return {"path": str(path), "writable": False, "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    is_android = "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ
    report: dict[str, object] = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "android_environment_detected": is_android,
        "termux_environment_detected": "com.termux" in os.environ.get("PREFIX", ""),
        "ffmpeg": check_ffmpeg(),
        "optional_imports": {
            module: importlib.util.find_spec(module) is not None for module in OPTIONAL_MODULES
        },
        "storage_checks": [
            check_writable(Path.cwd()),
            check_writable(Path.home()),
        ],
        "note": "Probe only. No installation, configuration changes, or render test was performed.",
    }

    import json
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
