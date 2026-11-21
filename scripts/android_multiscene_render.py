#!/usr/bin/env python3
"""Render a scene-plan JSON into a portrait MP4 using FFmpeg.

Requires FFmpeg with libx264 and AAC. Each scene asset is a still image or video.
This helper does not generate visuals or audio; it assembles supplied assets.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path

IMAGE_EXTS={".jpg",".jpeg",".png",".webp",".bmp"}
VIDEO_EXTS={".mp4",".mov",".mkv",".webm"}

def run(cmd:list[str])->None:
    print("+"," ".join(cmd),flush=True)
    result=subprocess.run(cmd)
    if result.returncode:
        raise RuntimeError(f"FFmpeg failed with exit code {result.returncode}")

def load_json(path:Path):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e: raise ValueError(f"Cannot read JSON {path}: {e}")

def resolve(base:Path,value:str)->Path:
    p=Path(value).expanduser()
    return p.resolve() if p.is_absolute() else (base/p).resolve()

def build_segments(plan:dict, assets:list, work:Path, ffmpeg:str, width:int,height:int,fps:int):
    scenes=plan.get("scenes")
    if not isinstance(scenes,list) or not scenes: raise ValueError("Scene plan must contain a non-empty scenes list.")
    if len(assets)!=len(scenes): raise ValueError(f"Need exactly one asset per scene ({len(scenes)} scenes, {len(assets)} assets).")
    segments=[]
    for i,(scene,asset) in enumerate(zip(scenes,assets),1):
        duration=float(scene.get("duration_seconds",0))
        if duration<=0: raise ValueError(f"Scene {i}: duration_seconds must be positive.")
        src=Path(asset)
        if not src.is_file(): raise ValueError(f"Scene {i}: asset not found: {src}")
        out=work/f"scene_{i:04d}.mp4"
        scale=f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps={fps}"
        if src.suffix.lower() in IMAGE_EXTS:
            cmd=[ffmpeg,"-y","-hide_banner","-loop","1","-i",str(src),"-t",str(duration),"-vf",scale,"-an","-c:v","libx264","-preset","ultrafast","-crf","28","-pix_fmt","yuv420p",str(out)]
        elif src.suffix.lower() in VIDEO_EXTS:
            cmd=[ffmpeg,"-y","-hide_banner","-i",str(src),"-t",str(duration),"-vf",scale,"-an","-c:v","libx264","-preset","ultrafast","-crf","28","-pix_fmt","yuv420p","-r",str(fps),str(out)]
        else: raise ValueError(f"Scene {i}: unsupported asset extension {src.suffix}")
        run(cmd); segments.append(out)
    return segments

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan",required=True,help="Scene-plan JSON")
    p.add_argument("--assets",required=True,help="JSON array of image/video paths, in scene order")
    p.add_argument("--audio",required=True,help="Narration/audio file")
    p.add_argument("--subtitle",help="Optional SRT subtitle file")
    p.add_argument("--output",default="final_video.mp4")
    p.add_argument("--width",type=int,default=720);p.add_argument("--height",type=int,default=1280);p.add_argument("--fps",type=int,default=24)
    p.add_argument("--work-dir",default="render_work")
    a=p.parse_args()
    ffmpeg=shutil.which("ffmpeg")
    if not ffmpeg: print("ERROR: ffmpeg not found",file=sys.stderr);return 2
    plan_path=Path(a.plan).expanduser().resolve(); assets_path=Path(a.assets).expanduser().resolve()
    plan=load_json(plan_path); asset_list=load_json(assets_path)
    if not isinstance(asset_list,list): print("ERROR: --assets must contain a JSON array",file=sys.stderr);return 2
    assets=[resolve(assets_path.parent,str(x)) for x in asset_list]
    audio=Path(a.audio).expanduser().resolve()
    subtitle=Path(a.subtitle).expanduser().resolve() if a.subtitle else None
    if not audio.is_file(): print(f"ERROR: audio not found: {audio}",file=sys.stderr);return 2
    if subtitle and not subtitle.is_file(): print(f"ERROR: subtitle not found: {subtitle}",file=sys.stderr);return 2
    if min(a.width,a.height,a.fps)<=0: print("ERROR: width, height and fps must be positive",file=sys.stderr);return 2
    work=Path(a.work_dir).expanduser().resolve();work.mkdir(parents=True,exist_ok=True)
    output=Path(a.output).expanduser().resolve();output.parent.mkdir(parents=True,exist_ok=True)
    try:
        segments=build_segments(plan,assets,work,ffmpeg,a.width,a.height,a.fps)
        concat=work/"concat.txt"
        concat.write_text("".join("file '"+str(s).replace("'","'\\''")+"\\n" for s in segments),encoding="utf-8")
        joined=work/"joined.mp4"
        run([ffmpeg,"-y","-hide_banner","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(joined)])
        cmd=[ffmpeg,"-y","-hide_banner","-i",str(joined),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","128k","-shortest"]
        if subtitle:
            # Use soft subtitles for broad compatibility; hard burn-in is a separate optional workflow.
            cmd.extend(["-i",str(subtitle),"-c:s","mov_text"])
        cmd.extend(["-movflags","+faststart",str(output)])
        run(cmd)
        print(f"Render complete: {output}")
        print("Check playback, audio synchronization, and subtitle rendering on-device.")
    except Exception as e:
        print(f"ERROR: {e}",file=sys.stderr);return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
