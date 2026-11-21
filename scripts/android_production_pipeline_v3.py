#!/usr/bin/env python3
"""Pipeline v3: optional offline eSpeak narration, planning, subtitles, render, QC."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(label,cmd):
 print("== "+label+" ==",flush=True);r=subprocess.run(list(map(str,cmd)))
 if r.returncode:raise RuntimeError(label+" failed (exit "+str(r.returncode)+")")
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--script",required=True);p.add_argument("--manifest",required=True);p.add_argument("--audio");p.add_argument("--subtitle");p.add_argument("--output",default="production/final.mp4");p.add_argument("--work-dir",default="production/work");p.add_argument("--voice",default="en-us");p.add_argument("--speed",type=int,default=150);p.add_argument("--wpm",type=int,default=145);p.add_argument("--width",type=int,default=720);p.add_argument("--height",type=int,default=1280);p.add_argument("--fps",type=int,default=24);a=p.parse_args()
 script=Path(a.script).resolve();manifest=Path(a.manifest).resolve()
 if not script.is_file() or not manifest.is_file():p.error("Script or manifest missing")
 w=Path(a.work_dir).resolve();w.mkdir(parents=True,exist_ok=True);o=Path(a.output).resolve();o.parent.mkdir(parents=True,exist_ok=True);plan=w/"plan.json";assets=w/"assets.json";meta=w/"metadata.json";srt=Path(a.subtitle).resolve() if a.subtitle else w/"subtitles.srt";audio=Path(a.audio).resolve() if a.audio else w/"narration.wav";qc=w/"qc.json"
 try:
  if not a.audio:run("Offline narration",[sys.executable,ROOT/"scripts/android_tts_espeak.py","--text",script,"--output",audio,"--voice",a.voice,"--speed",a.speed])
  elif not audio.is_file():p.error("Audio file missing: "+str(audio))
  run("Planning",[sys.executable,ROOT/"scripts/android_scene_planner.py",script,"--out",plan,"--wpm",a.wpm])
  if not a.subtitle:run("Subtitle",[sys.executable,ROOT/"scripts/android_subtitle_generator.py","--plan",plan,"--out",srt])
  run("Resolve visuals",[sys.executable,ROOT/"scripts/android_visual_asset_engine.py","--plan",plan,"--manifest",manifest,"--assets-out",assets,"--metadata-out",meta])
  run("Render",[sys.executable,ROOT/"scripts/android_multiscene_render_v4.py","--plan",plan,"--assets",assets,"--audio",audio,"--subtitle",srt,"--output",o,"--work-dir",w/"render","--width",a.width,"--height",a.height,"--fps",a.fps])
  total=sum(float(z["duration_seconds"]) for z in json.loads(plan.read_text())["scenes"]);run("QC",[sys.executable,ROOT/"scripts/android_video_qc.py",o,"--expected-duration",total,"--report",qc]);report={"status":"success","output":str(o),"qc":str(qc),"plan":str(plan),"audio":str(audio),"subtitle":str(srt)};(w/"pipeline_report.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return 0
 except Exception as e:print("PIPELINE ERROR:",e,file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
