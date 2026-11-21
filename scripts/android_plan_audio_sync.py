#!/usr/bin/env python3
"""Align planned scene durations to the actual narration duration using ffprobe."""
import argparse,json,subprocess
from pathlib import Path
def duration(audio):
 r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(audio)],capture_output=True,text=True,check=True)
 d=float(r.stdout.strip())
 if d<=0:raise ValueError("Audio duration must be positive")
 return d
def align(plan,audio,out):
 data=json.loads(Path(plan).read_text(encoding="utf-8"));sc=data.get("scenes")
 if not isinstance(sc,list) or not sc:raise ValueError("Plan has no scenes")
 total=duration(audio);old=sum(float(x["duration_seconds"]) for x in sc)
 if old<=0:raise ValueError("Plan duration must be positive")
 factor=total/old;acc=0
 for i,s in enumerate(sc):
  if i==len(sc)-1:s["duration_seconds"]=round(total-acc,3)
  else:s["duration_seconds"]=round(float(s["duration_seconds"])*factor,3);acc+=s["duration_seconds"]
 data["estimated_duration_seconds"]=round(total,3);data["audio_aligned"]=True
 Path(out).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
 print(f"Aligned {len(sc)} scenes: {old:.2f}s -> {total:.3f}s")
def main():
 p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--audio",required=True);p.add_argument("--out",required=True);a=p.parse_args();align(a.plan,a.audio,a.out)
if __name__=="__main__":main()
