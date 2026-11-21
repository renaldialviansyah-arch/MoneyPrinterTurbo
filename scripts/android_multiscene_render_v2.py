#!/usr/bin/env python3
"""Multi-scene FFmpeg assembly for Android portrait video.

Scene-plan JSON supplies durations. --assets JSON array supplies one image/video
path per scene, in order. This tool assembles provided media; it does not fetch
or generate media assets. Requires FFmpeg with libx264 and AAC.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path

IMAGE_EXTS={".jpg",".jpeg",".png",".webp",".bmp"}
VIDEO_EXTS={".mp4",".mov",".mkv",".webm"}

def run(cmd:list[str])->None:
    print("+"," ".join(cmd),flush=True)
    result=subprocess.run(cmd)
    if result.returncode: raise RuntimeError(f"Command failed ({result.returncode})")

def load(path:Path):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: raise ValueError(f"Invalid JSON {path}: {exc}")

def resolve(base:Path,value:str)->Path:
    p=Path(value).expanduser()
    return p.resolve() if p.is_absolute() else (base/p).resolve()

def segment(scene,source:Path,out:Path,ffmpeg:str,duration:float,w:int,h:int,fps:int):
    vf=f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps}"
    if source.suffix.lower() in IMAGE_EXTS:
        cmd=[ffmpeg,"-y","-hide_banner","-loop","1","-i",str(source),"-t",str(duration),"-vf",vf,"-an","-c:v","libx264","-preset","ultrafast","-crf","28","-pix_fmt","yuv420p"]
    elif source.suffix.lower() in VIDEO_EXTS:
        cmd=[ffmpeg,"-y","-hide_banner","-i",str(source),"-t",str(duration),"-vf",vf,"-an","-c:v","libx264","-preset","ultrafast","-crf","28","-pix_fmt","yuv420p"]
    else: raise ValueError(f"Unsupported scene file: {source}")
    cmd.append(str(out));run(cmd)

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan",required=True);p.add_argument("--assets",required=True,help="JSON array of scene media paths")
    p.add_argument("--audio",required=True);p.add_argument("--subtitle");p.add_argument("--output",default="final_video.mp4")
    p.add_argument("--width",type=int,default=720);p.add_argument("--height",type=int,default=1280);p.add_argument("--fps",type=int,default=24);p.add_argument("--work-dir",default="render_work")
    a=p.parse_args();ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg: print("FFmpeg not found",file=sys.stderr);return 2
    planpath=Path(a.plan).expanduser().resolve();assetspath=Path(a.assets).expanduser().resolve()
    plan=load(planpath);items=load(assetspath);scenes=plan.get("scenes")
    if not isinstance(scenes,list) or not scenes: print("Plan has no scenes",file=sys.stderr);return 2
    if not isinstance(items,list) or len(items)!=len(scenes): print("Assets list must have one path per scene",file=sys.stderr);return 2
    audio=Path(a.audio).expanduser().resolve();sub=Path(a.subtitle).expanduser().resolve() if a.subtitle else None
    if not audio.is_file(): print(f"Audio missing: {audio}",file=sys.stderr);return 2
    if sub and not sub.is_file(): print(f"Subtitle missing: {sub}",file=sys.stderr);return 2
    if min(a.width,a.height,a.fps)<=0: print("Width/height/FPS must be positive",file=sys.stderr);return 2
    work=Path(a.work_dir).expanduser().resolve();work.mkdir(parents=True,exist_ok=True)
    out=Path(a.output).expanduser().resolve();out.parent.mkdir(parents=True,exist_ok=True)
    try:
        parts=[]
        for i,(sc,item) in enumerate(zip(scenes,items),1):
            d=float(sc.get("duration_seconds",0))
            if d<=0: raise ValueError(f"Scene {i}: invalid duration")
            src=resolve(assetspath.parent,str(item))
            if not src.is_file(): raise ValueError(f"Scene {i}: file not found: {src}")
            part=work/f"scene_{i:04d}.mp4";segment(sc,src,part,ffmpeg,d,a.width,a.height,a.fps);parts.append(part)
        concat=work/"concat.txt"
        # FFmpeg concat demuxer paths are quoted; escape single quotes conservatively.
        lines=[]
        for part in parts:
            path=str(part).replace("'","'\\''")
            lines.append("file '"+path+"'")
        concat.write_text("\n".join(lines)+"\n",encoding="utf-8")
        joined=work/"joined.mp4"
        run([ffmpeg,"-y","-hide_banner","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(joined)])
        cmd=[ffmpeg,"-y","-hide_banner","-i",str(joined),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-shortest"]
        if sub:
            cmd.extend(["-i",str(sub),"-map","2:s:0","-c:s","mov_text"])
        cmd.extend(["-movflags","+faststart",str(out)])
        run(cmd);print("Render complete:",out)
    except Exception as exc: print("ERROR:",exc,file=sys.stderr);return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
