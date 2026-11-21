#!/usr/bin/env python3
"""Resolve scene visuals from a local manifest. Offline; does not scrape or download."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

SUPPORTED={".jpg",".jpeg",".png",".webp",".bmp",".mp4",".mov",".mkv",".webm"}

def resolve(base, value):
 p=Path(value).expanduser()
 return (p if p.is_absolute() else base/p).resolve()

def build(plan_path, manifest_path):
 plan=json.loads(plan_path.read_text(encoding="utf-8"))
 manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
 scenes=plan.get("scenes")
 entries=manifest.get("assets") if isinstance(manifest,dict) else None
 if not isinstance(scenes,list) or not scenes: raise ValueError("Scene plan must contain a non-empty scenes list")
 if not isinstance(entries,list): raise ValueError("Manifest must contain an assets list")
 by_scene={}
 for item in entries:
  if not isinstance(item,dict) or "scene" not in item or "path" not in item: raise ValueError("Each asset entry requires scene and path")
  n=int(item["scene"])
  if n in by_scene: raise ValueError(f"Duplicate asset entry for scene {n}")
  by_scene[n]=item
 base=manifest_path.parent; out=[];meta=[];missing=[]
 for idx,scene in enumerate(scenes,1):
  entry=by_scene.get(idx)
  if not entry: missing.append(idx);continue
  src=resolve(base,str(entry["path"]))
  if not src.is_file(): missing.append(idx);continue
  if src.suffix.lower() not in SUPPORTED: raise ValueError(f"Unsupported asset file for scene {idx}: {src.suffix}")
  out.append(str(src));meta.append({"scene":idx,"narration":scene.get("narration",""),"asset_path":str(src),"asset_type":"video" if src.suffix.lower() in {".mp4",".mov",".mkv",".webm"} else "image","source":entry.get("source","local file"),"license":entry.get("license","unspecified"),"notes":entry.get("notes","")})
 if missing: raise ValueError("Missing or invalid assets for scene(s): "+", ".join(map(str,missing)))
 extras=sorted(set(by_scene)-set(range(1,len(scenes)+1)))
 return out,meta,extras

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--plan",required=True);p.add_argument("--manifest",required=True);p.add_argument("--assets-out",default="assets_resolved.json");p.add_argument("--metadata-out",default="assets_metadata.json");a=p.parse_args()
 pp=Path(a.plan).expanduser().resolve();mp=Path(a.manifest).expanduser().resolve()
 try:
  out,meta,extras=build(pp,mp)
  Path(a.assets_out).write_text(json.dumps(out,indent=2),encoding="utf-8")
  Path(a.metadata_out).write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
  print(f"Resolved {len(out)} scene assets. Renderer list: {a.assets_out}; source metadata: {a.metadata_out}")
  if extras: print("Ignored extra manifest scenes:",extras)
 except Exception as e: print("ERROR:",e,file=sys.stderr);return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
