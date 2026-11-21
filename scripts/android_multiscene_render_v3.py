#!/usr/bin/env python3
"""Multi-scene portrait MP4 assembler. Requires FFmpeg with libx264 and AAC."""
from __future__ import annotations
import argparse,json,shutil,subprocess,sys
from pathlib import Path
IMG={".jpg",".jpeg",".png",".webp",".bmp"};VID={".mp4",".mov",".mkv",".webm"}
def run(cmd):
 print("+"," ".join(cmd),flush=True);r=subprocess.run(cmd)
 if r.returncode:raise RuntimeError(f"FFmpeg returned {r.returncode}")
def read(p):
 return json.loads(p.read_text(encoding="utf-8"))
def resolve(base,s):
 p=Path(s).expanduser();return p.resolve() if p.is_absolute() else (base/p).resolve()
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--plan",required=True);ap.add_argument("--assets",required=True);ap.add_argument("--audio",required=True);ap.add_argument("--subtitle")
 ap.add_argument("--output",default="final_video.mp4");ap.add_argument("--width",type=int,default=720);ap.add_argument("--height",type=int,default=1280);ap.add_argument("--fps",type=int,default=24);ap.add_argument("--work-dir",default="render_work")
 a=ap.parse_args();ff=shutil.which("ffmpeg")
 if not ff:print("FFmpeg missing",file=sys.stderr);return 2
 pp=Path(a.plan).expanduser().resolve();aa=Path(a.assets).expanduser().resolve()
 plan=read(pp);assets=read(aa);sc=plan.get("scenes")
 if not isinstance(sc,list) or not sc or not isinstance(assets,list) or len(sc)!=len(assets):print("Plan and assets must have matching non-empty scene lists",file=sys.stderr);return 2
 audio=Path(a.audio).expanduser().resolve();sub=Path(a.subtitle).expanduser().resolve() if a.subtitle else None
 if not audio.is_file() or (sub and not sub.is_file()):print("Audio/subtitle input missing",file=sys.stderr);return 2
 if min(a.width,a.height,a.fps)<=0:print("Dimensions and FPS must be positive",file=sys.stderr);return 2
 work=Path(a.work_dir).expanduser().resolve();work.mkdir(parents=True,exist_ok=True);out=Path(a.output).expanduser().resolve();out.parent.mkdir(parents=True,exist_ok=True)
 try:
  segs=[]
  for i,(scene,item) in enumerate(zip(sc,assets),1):
   dur=float(scene.get("duration_seconds",0));src=resolve(aa.parent,str(item))
   if dur<=0 or not src.is_file():raise ValueError(f"Invalid duration or missing media for scene {i}")
   if src.suffix.lower() not in IMG|VID:raise ValueError(f"Unsupported media extension: {src.suffix}")
   dst=work/f"seg{i:04}.mp4";vf=f"scale={a.width}:{a.height}:force_original_aspect_ratio=increase,crop={a.width}:{a.height},setsar=1,fps={a.fps}"
   cmd=[ff,"-y","-hide_banner"]
   if src.suffix.lower() in IMG:cmd+=["-loop","1","-i",str(src)]
   else:cmd+=["-i",str(src)]
   cmd+=["-t",str(dur),"-vf",vf,"-an","-c:v","libx264","-preset","ultrafast","-crf","28","-pix_fmt","yuv420p","-r",str(a.fps),str(dst)]
   run(cmd);segs.append(dst)
  concat=work/"concat.txt";concat.write_text("\n".join("file '"+str(x).replace("'","'\\''")+"'" for x in segs)+"\n",encoding="utf-8")
  merged=work/"merged.mp4";run([ff,"-y","-hide_banner","-f","concat","-safe","0","-i",str(concat),"-c:v","libx264","-preset","ultrafast","-crf","28","-pix_fmt","yuv420p","-r",str(a.fps),str(merged)])
  cmd=[ff,"-y","-hide_banner","-i",str(merged),"-i",str(audio)]
  if sub:cmd+=["-i",str(sub)]
  cmd+=["-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-shortest"]
  if sub:cmd+=["-map","2:s:0","-c:s","mov_text"]
  cmd+=["-movflags","+faststart",str(out)];run(cmd)
  print("Finished:",out)
 except Exception as e:print("ERROR:",e,file=sys.stderr);return 1
 return 0
if __name__=="__main__":raise SystemExit(main())
