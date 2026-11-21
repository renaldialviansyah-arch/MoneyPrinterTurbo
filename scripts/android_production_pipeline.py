#!/usr/bin/env python3
"""Run scene planning, local asset resolution, and FFmpeg rendering as one pipeline."""
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLANNER=ROOT/"scripts/android_scene_planner.py"
RESOLVER=ROOT/"scripts/android_visual_asset_engine.py"
RENDERER=ROOT/"scripts/android_multiscene_render_v4.py"
def run_stage(label,cmd):
 print("\\n=== "+label+" ===",flush=True);print("+"," ".join(map(str,cmd)),flush=True)
 r=subprocess.run(list(map(str,cmd)))
 if r.returncode:raise RuntimeError(f"{label} failed (exit {r.returncode})")
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--script",required=True);p.add_argument("--manifest",required=True);p.add_argument("--audio",required=True);p.add_argument("--subtitle")
 p.add_argument("--output",default="production/final_video.mp4");p.add_argument("--work-dir",default="production/work")
 p.add_argument("--wpm",type=int,default=145);p.add_argument("--width",type=int,default=720);p.add_argument("--height",type=int,default=1280);p.add_argument("--fps",type=int,default=24)
 a=p.parse_args();script=Path(a.script).expanduser().resolve();manifest=Path(a.manifest).expanduser().resolve();audio=Path(a.audio).expanduser().resolve();sub=Path(a.subtitle).expanduser().resolve() if a.subtitle else None
 for label,path in [("script",script),("manifest",manifest),("audio",audio)]+([("subtitle",sub)] if sub else []):
  if not path.is_file():p.error(f"{label} file not found: {path}")
 if not 40<=a.wpm<=400:p.error("--wpm must be between 40 and 400")
 if min(a.width,a.height,a.fps)<=0:p.error("width, height and fps must be positive")
 work=Path(a.work_dir).expanduser().resolve();work.mkdir(parents=True,exist_ok=True);out=Path(a.output).expanduser().resolve();out.parent.mkdir(parents=True,exist_ok=True)
 plan=work/"scene_plan.json";assetlist=work/"assets_resolved.json";meta=work/"assets_metadata.json"
 try:
  run_stage("Scene planning",[sys.executable,PLANNER,script,"--out",plan,"--wpm",a.wpm])
  run_stage("Asset resolution",[sys.executable,RESOLVER,"--plan",plan,"--manifest",manifest,"--assets-out",assetlist,"--metadata-out",meta])
  cmd=[sys.executable,RENDERER,"--plan",plan,"--assets",assetlist,"--audio",audio,"--output",out,"--work-dir",work/"render","--width",a.width,"--height",a.height,"--fps",a.fps]
  if sub:cmd.extend(["--subtitle",sub])
  run_stage("Final render",cmd)
  if not out.is_file() or out.stat().st_size<1024:raise RuntimeError("Render output missing or suspiciously small")
  summary={"status":"success","output":str(out),"bytes":out.stat().st_size,"scene_plan":str(plan),"resolved_assets":str(assetlist),"metadata":str(meta)}
  report=work/"pipeline_report.json";report.write_text(json.dumps(summary,indent=2),encoding="utf-8")
  print("\\nPIPELINE COMPLETE\\n"+json.dumps(summary,indent=2));return 0
 except Exception as e:print(f"PIPELINE ERROR: {e}",file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
