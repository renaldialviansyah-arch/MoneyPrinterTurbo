#!/usr/bin/env python3
"""Render scenes with subtle Ken Burns motion on still images, then assemble narration/subtitles."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
IMG={".jpg",".jpeg",".png",".webp",".bmp"};VID={".mp4",".mov",".mkv",".webm"}
def run(cmd):
 print("+"," ".join(map(str,cmd)),flush=True);r=subprocess.run(list(map(str,cmd)))
 if r.returncode:raise RuntimeError("FFmpeg error "+str(r.returncode))
def read(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def resolve(base,s):
 p=Path(s).expanduser();return p.resolve() if p.is_absolute() else (base/p).resolve()
def main():
 p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--assets",required=True);p.add_argument("--audio",required=True);p.add_argument("--subtitle");p.add_argument("--output",default="final.mp4");p.add_argument("--width",type=int,default=720);p.add_argument("--height",type=int,default=1280);p.add_argument("--fps",type=int,default=24);p.add_argument("--work-dir",default="render_work");p.add_argument("--motion",choices=["subtle","dynamic","none"],default="subtle");a=p.parse_args()
 ff=shutil.which("ffmpeg")
 if not ff:p.error("FFmpeg unavailable")
 plan=read(a.plan);assets=read(a.assets);sc=plan.get("scenes")
 if not isinstance(sc,list) or not sc or len(sc)!=len(assets):p.error("Plan and asset list must match")
 audio=Path(a.audio).resolve();sub=Path(a.subtitle).resolve() if a.subtitle else None
 if not audio.is_file() or (sub and not sub.is_file()):p.error("Missing audio/subtitle")
 work=Path(a.work_dir).resolve();work.mkdir(parents=True,exist_ok=True);out=Path(a.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 # Alternating camera motion patterns, using expressions for a slow drift.
 patterns=[("1","0","0"),("1","iw-iw/zoom","ih-ih/zoom"),("1","iw/2-iw/zoom/2","0"),("1","0","ih-ih/zoom"),("1","iw-iw/zoom","0")]
 try:
  segs=[]
  for i,(scene,item) in enumerate(zip(sc,assets)):
   dur=float(scene.get("duration_seconds",0));src=resolve(Path(a.assets).resolve().parent,str(item))
   if dur<=0 or not src.is_file():raise ValueError("Invalid/missing media at scene "+str(i+1))
   ext=src.suffix.lower();dst=work/f"scene_{i+1:04}.mp4";frames=max(1,int(round(dur*a.fps)))
   if ext not in IMG|VID:raise ValueError("Unsupported extension: "+ext)
   base=f"scale={a.width}:{a.height}:force_original_aspect_ratio=increase,crop={a.width}:{a.height},setsar=1"
   if ext in IMG and a.motion!="none":
    zmax="1.08" if a.motion=="subtle" else "1.16"
    xexpr=["0","iw-iw/zoom","iw/2-iw/zoom/2","0","iw-iw/zoom"][i%5]
    yexpr=["0","ih-ih/zoom","0","ih-ih/zoom","ih/2-ih/zoom/2"][i%5]
    vf=f"{base},zoompan=z='min(zoom+0.0008,{zmax})':x='{xexpr}':y='{yexpr}':d={frames}:s={a.width}x{a.height}:fps={a.fps}"
    cmd=[ff,"-y","-hide_banner","-loop","1","-i",str(src),"-vf",vf,"-t",str(dur),"-an","-c:v","libx264","-preset","ultrafast","-crf","25","-pix_fmt","yuv420p",str(dst)]
   else:
    cmd=[ff,"-y","-hide_banner"]
    cmd+=["-loop","1","-i",str(src)] if ext in IMG else ["-stream_loop","-1","-i",str(src)]
    cmd+=["-t",str(dur),"-vf",base+",fps="+str(a.fps),"-an","-c:v","libx264","-preset","ultrafast","-crf","25","-pix_fmt","yuv420p",str(dst)]
   run(cmd);segs.append(dst)
  concat=work/"concat.txt";concat.write_text("\n".join("file '"+str(x).replace("'","'\\''")+"'" for x in segs)+"\n",encoding="utf-8")
  merged=work/"video_only.mp4";run([ff,"-y","-hide_banner","-f","concat","-safe","0","-i",str(concat),"-c:v","libx264","-preset","ultrafast","-crf","25","-pix_fmt","yuv420p","-r",str(a.fps),str(merged)])
  total=sum(float(x["duration_seconds"]) for x in sc);cmd=[ff,"-y","-hide_banner","-i",str(merged),"-i",str(audio)]
  if sub:cmd+=["-i",str(sub)]
  cmd+=["-map","0:v:0","-map","1:a:0","-c:v","copy","-af","apad,atrim=0:"+str(total),"-c:a","aac","-b:a","160k","-t",str(total)]
  if sub:cmd+=["-map","2:s:0","-c:s","mov_text"]
  cmd+=["-movflags","+faststart",str(out)];run(cmd);print("Finished:",out)
 except Exception as e:print("ERROR:",e,file=sys.stderr);return 1
 return 0
if __name__=="__main__":raise SystemExit(main())
