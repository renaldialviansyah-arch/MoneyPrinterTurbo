#!/usr/bin/env python3
"""Orchestrate the isolated mobile asset + FFmpeg render workflow."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST_TOOL=ROOT/"scripts/android_asset_manifest.py"
DOWNLOAD_TOOL=ROOT/"scripts/android_asset_download.py"
RENDER_TOOL=ROOT/"scripts/android_render_test.py"

def resolve_asset(base:Path,item:dict)->Path:
    path=Path(item["path"]).expanduser()
    return path.resolve() if path.is_absolute() else (base/path).resolve()

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest")
    p.add_argument("--download",action="store_true",help="Download URL assets listed in manifest")
    p.add_argument("--assets-dir",default="assets_downloaded")
    p.add_argument("--output",default="output.mp4")
    p.add_argument("--width",type=int,default=720)
    p.add_argument("--height",type=int,default=1280)
    p.add_argument("--fps",type=int,default=24)
    p.add_argument("--duration",type=float,default=15.0)
    p.add_argument("--max-mb",type=int,default=100)
    args=p.parse_args()
    manifest=Path(args.manifest).expanduser().resolve()
    if not manifest.is_file():
        print(f"ERROR: manifest not found: {manifest}",file=sys.stderr);return 2
    try: data=json.loads(manifest.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: cannot parse manifest: {e}",file=sys.stderr);return 2
    if not isinstance(data,dict) or not isinstance(data.get("assets"),list):
        print("ERROR: manifest must contain an assets list.",file=sys.stderr);return 2
    if args.download:
        cmd=[sys.executable,str(DOWNLOAD_TOOL),str(manifest),"--output-dir",str(Path(args.assets_dir).resolve()),"--max-mb",str(args.max_mb)]
        if subprocess.run(cmd).returncode: return 1
        # Update in-memory asset paths to downloaded output, preserving manifest on disk.
        downloaded_dir=Path(args.assets_dir).expanduser().resolve()
        for item in data["assets"]:
            if item.get("url") and item.get("filename"):
                item["path"]=str(downloaded_dir/item["filename"])
            elif item.get("url"):
                ext=Path(item["url"].split("?",1)[0]).suffix
                item["path"]=str(downloaded_dir/f"asset_{data['assets'].index(item)+1}{ext}")
    assets=data["assets"]
    visuals=[x for x in assets if x.get("role")=="visual" and x.get("path")]
    audios=[x for x in assets if x.get("role")=="audio" and x.get("path")]
    subs=[x for x in assets if x.get("role")=="subtitle" and x.get("path")]
    if not visuals or not audios:
        print("ERROR: manifest requires at least one visual and one audio path (or URL with --download).",file=sys.stderr);return 2
    base=manifest.parent
    visual=resolve_asset(base,visuals[0])
    audio=resolve_asset(base,audios[0])
    subtitle=resolve_asset(base,subs[0]) if subs else None
    for path in [visual,audio]+([subtitle] if subtitle else []):
        if not path.is_file():
            print(f"ERROR: asset missing: {path}",file=sys.stderr);return 2
    output=Path(args.output).expanduser().resolve()
    cmd=[sys.executable,str(RENDER_TOOL),"--visual",str(visual),"--audio",str(audio),"--output",str(output),"--width",str(args.width),"--height",str(args.height),"--fps",str(args.fps)]
    if subtitle: cmd.extend(["--subtitle",str(subtitle)])
    if visual.suffix.lower() in {".jpg",".jpeg",".png",".webp",".bmp"}: cmd.extend(["--duration",str(args.duration)])
    print("Starting render helper...")
    result=subprocess.run(cmd)
    if result.returncode==0:
        print(f"Render helper completed. Check playback manually: {output}")
    return result.returncode
if __name__=="__main__": raise SystemExit(main())
