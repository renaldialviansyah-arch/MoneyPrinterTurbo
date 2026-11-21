#!/usr/bin/env python3
"""Validate and summarize a simple JSON asset manifest for the mobile render workflow.

No third-party Python packages are required. This tool does not download assets.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

SUPPORTED_VISUAL_EXTS={".mp4",".mov",".mkv",".webm",".jpg",".jpeg",".png",".webp"}
SUPPORTED_AUDIO_EXTS={".mp3",".wav",".m4a",".aac",".ogg"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest",help="JSON manifest file")
    p.add_argument("--check-files",action="store_true",help="Check that local referenced files exist")
    args=p.parse_args()
    mpath=Path(args.manifest).expanduser().resolve()
    data=json.loads(mpath.read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise SystemExit("Manifest root must be an object")
    assets=data.get("assets",[])
    if not isinstance(assets,list): raise SystemExit("'assets' must be a list")
    errors=[]
    for i,item in enumerate(assets):
        if not isinstance(item,dict):
            errors.append(f"assets[{i}]: expected object");continue
        role=item.get("role")
        path=item.get("path")
        if role not in {"visual","audio","subtitle"}:
            errors.append(f"assets[{i}]: unsupported role {role!r}")
        if not isinstance(path,str) or not path.strip():
            errors.append(f"assets[{i}]: missing path");continue
        ext=Path(path).suffix.lower()
        if role=="visual" and ext not in SUPPORTED_VISUAL_EXTS: errors.append(f"assets[{i}]: unsupported visual extension {ext}")
        if role=="audio" and ext not in SUPPORTED_AUDIO_EXTS: errors.append(f"assets[{i}]: unsupported audio extension {ext}")
        if role=="subtitle" and ext not in {".srt",".vtt"}: errors.append(f"assets[{i}]: unsupported subtitle extension {ext}")
        if args.check_files:
            candidate=(mpath.parent/path).resolve()
            if not candidate.is_file(): errors.append(f"assets[{i}]: file not found: {candidate}")
        print(f"{i+1}. {role}: {path}"+(f" | source={item.get('source','unspecified')}" if item.get("source") else ""))
    print(f"Assets: {len(assets)}")
    if errors:
        print("Validation errors:")
        for e in errors: print("- "+e)
        return 1
    print("Manifest structure valid.")
    return 0
if __name__=="__main__": raise SystemExit(main())
