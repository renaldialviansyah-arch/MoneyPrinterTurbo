#!/usr/bin/env python3
"""Pipeline v8: cinematic scene metadata and v7 workflow."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(label,cmd):
 print("== "+label+" ==",flush=True);r=subprocess.run(list(map(str,cmd)))
 if r.returncode:raise RuntimeError(label+" failed ("+str(r.returncode)+")")
def main():
 p=argparse.ArgumentParser();p.add_argument("--script",required=True);p.add_argument("--manifest");p.add_argument("--auto-visuals",action="store_true");p.add_argument("--audio");p.add_argument("--subtitle");p.add_argument("--tts-engine",choices=["piper","espeak"],default="piper");p.add_argument("--model");p.add_argument("--output",default="production/final.mp4");p.add_argument("--work-dir",default="production/work");p.add_argument("--speed",type=int,default=150);p.add_argument("--wpm",type=int,default=145);p.add_argument("--width",type=int,default=720);p.add_argument("--height",type=int,default=1280);p.add_argument("--fps",type=int,default=24);p.add_argument("--motion",choices=["subtle","dynamic","none"],default="subtle");a=p.parse_args()
 script=Path(a.script).resolve()
 if not script.is_file():p.error("Script missing")
 if not a.auto_visuals and not a.manifest:p.error("Use --manifest or --auto-visuals")
 w=Path(a.work_dir).resolve();w.mkdir(parents=True,exist_ok=True);o=Path(a.output).resolve();o.parent.mkdir(parents=True,exist_ok=True);plan=w/"plan.json";aligned=w/"plan_aligned.json";manifest=Path(a.manifest).resolve() if a.manifest else w/"assets_local.json";assets=w/"assets_resolved.json";meta=w/"metadata.json";srt=Path(a.subtitle).resolve() if a.subtitle else w/"subtitles.srt";audio=Path(a.audio).resolve() if a.audio else w/"narration.wav";qc=w/"qc.json"
 try:
  if not a.audio:
   if a.tts_engine=="piper":
    if not a.model:p.error("Piper requires --model")
    run("Neural voice",[sys.executable,ROOT/"scripts/android_tts_piper.py","--text",script,"--model",a.model,"--output",audio])
   else:run("Fallback voice",[sys.executable,ROOT/"scripts/android_tts_espeak.py","--text",script,"--output",audio,"--speed",a.speed])
  elif not audio.is_file():p.error("Audio missing")
  run("Planning",[sys.executable,ROOT/"scripts/android_scene_planner_v2.py",script,"--out",plan,"--wpm",a.wpm])
  run("Audio align",[sys.executable,ROOT/"scripts/android_plan_audio_sync.py","--plan",plan,"--audio",audio,"--out",aligned])
  if a.auto_visuals:run("Automatic visual acquisition",[sys.executable,ROOT/"scripts/android_commons_auto_assets.py","--plan",aligned,"--out-dir",w/"visuals","--manifest",manifest,"--report",w/"asset_sources.json","--allow-fallback"])
  if not a.subtitle:run("Subtitles",[sys.executable,ROOT/"scripts/android_subtitle_generator.py","--plan",aligned,"--out",srt])
  run("Asset resolution",[sys.executable,ROOT/"scripts/android_visual_asset_engine.py","--plan",aligned,"--manifest",manifest,"--assets-out",assets,"--metadata-out",meta])
  run("Motion rendering",[sys.executable,ROOT/"scripts/android_multiscene_render_v5.py","--plan",aligned,"--assets",assets,"--audio",audio,"--subtitle",srt,"--output",o,"--work-dir",w/"render","--width",a.width,"--height",a.height,"--fps",a.fps,"--motion",a.motion])
  total=sum(float(x["duration_seconds"]) for x in json.loads(aligned.read_text(encoding="utf-8"))["scenes"]);run("QC",[sys.executable,ROOT/"scripts/android_video_qc.py",o,"--expected-duration",total,"--require-subtitles","--min-width",a.width,"--min-height",a.height,"--report",qc,"--asset-manifest",manifest])
  report={"status":"success","output":str(o),"audio":str(audio),"subtitle":str(srt),"asset_manifest":str(manifest),"qc":str(qc),"motion":a.motion};(w/"pipeline_report.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return 0
 except Exception as e:print("ERROR:",e,file=sys.stderr);return 1
if __name__=="__main__":raise SystemExit(main())
