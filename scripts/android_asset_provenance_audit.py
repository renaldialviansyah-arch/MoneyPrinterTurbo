#!/usr/bin/env python3
"""Independent production asset audit with explicit PASS/DEGRADED/FAIL states."""
import argparse
import json
import sys
import urllib.parse
from pathlib import Path

try:
    from PIL import Image
except Exception:
    Image = None


def audit(manifest, expected, require_external=False):
    issues, degraded, seen = [], [], set()
    try:
        data = json.loads(Path(manifest).read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "FAIL", "asset_count": 0, "expected_count": expected,
                "issues": [f"manifest unreadable or invalid JSON: {exc}"], "degraded": []}

    if not isinstance(data, dict):
        data = {}
        issues.append("manifest root is not an object")

    raw_entries = data.get("assets")
    if not isinstance(raw_entries, list):
        issues.append("assets field is not a list")
        entries = []
    else:
        entries = raw_entries

    if not entries:
        issues.append("empty asset list")
    if expected is not None and len(entries) != expected:
        issues.append(f"asset count mismatch: {len(entries)} != {expected}")

    for i, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            issues.append(f"scene {i}: asset entry is not an object")
            continue
        raw_path = entry.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            issues.append(f"scene {i}: missing or invalid path")
            continue
        path = Path(raw_path)
        if not path.is_file():
            issues.append(f"scene {i}: missing asset file")
            continue
        try:
            if path.stat().st_size < 1200:
                issues.append(f"scene {i}: file too small")
        except OSError as exc:
            issues.append(f"scene {i}: cannot stat asset: {exc}")
            continue

        source = str(entry.get("source") or "").strip()
        license_name = str(entry.get("license") or "").strip()
        if source.startswith(("http://", "https://")):
            parsed = urllib.parse.urlparse(source)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                issues.append(f"scene {i}: malformed source URL")
        else:
            degraded.append(f"scene {i}: no external source URL ({source or 'missing'})")
        if not license_name:
            degraded.append(f"scene {i}: license missing")
        if "fallback" in source.lower() or "generated graphic" in license_name.lower():
            degraded.append(f"scene {i}: fallback graphic")

        key = source or str(path.resolve())
        if key in seen:
            degraded.append(f"scene {i}: duplicated source")
        seen.add(key)

        if Image:
            try:
                with Image.open(path) as image:
                    image.verify()
            except Exception as exc:
                issues.append(f"scene {i}: invalid image: {exc}")

    status = "FAIL" if issues else ("DEGRADED" if degraded else "PASS")
    if require_external and degraded and status != "FAIL":
        status = "FAIL"
    return {"status": status, "asset_count": len(entries), "expected_count": expected,
            "issues": issues, "degraded": degraded}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--expected-scenes", type=int)
    parser.add_argument("--require-external", action="store_true")
    parser.add_argument("--report", default="asset_audit.json")
    args = parser.parse_args()
    try:
        result = audit(args.manifest, args.expected_scenes, args.require_external)
        Path(args.report).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] != "FAIL" else 1
    except Exception as exc:
        print("AUDIT ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
