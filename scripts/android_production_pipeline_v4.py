#!/usr/bin/env python3
"""Production pipeline v4: neural Piper TTS preferred; optional eSpeak fallback."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(label,cmd):
 print("== "+label+" ==",flush=True);r=subprocess.run(list(map(str,cmd)))
 if r.returncode:raise RuntimeError(label+" failed: "+str(r.returncode))
def main():
 p=argparse.ArgumentParser();p.add_argument('--script',required=True);p.add_argument('--manifest',required=True);p.add_argument('--audio');p.add_argument('--subtitle');p.add_argument('--tts-engine',choices=['piper','espeak'],default='piper');p.add_argument('--model');p.add_argument('--output',default='production/final.mp4');p.add_argument('--work-dir',default='production/work');p.add_argument('--speed',type=int,default=150);p.add_argument('--wpm',type=int,default=145);p.add_argument('--width',type=int,default=720);p.add_argument('--height',type=int,default=1280);p.add_argument('--fps',type=int,default=24);a=p.parse_args()
 script=Path(a.script).resolve();manifest=Path(a.manifest).resolve()
 if not script.is_file() or not manifest.is_file():p.error('Script/manifest missing')
 w=Path(a.work_dir).resolve();w.mkdir(parents=True,exist_ok=True);o=Path(a.output).resolve();o.parent.mkdir(parents=True,exist_ok=True);plan=w/'plan.json';assets=w/'assets.json';meta=w/'metadata.json';srt=Path(a.subtitle).resolve() if a.subtitle else w/'subtitles.srt';audio=Path(a.audio).resolve() if a.audio else w/'narration.wav';qc=w/'qc.json'
 try:
  if not a.audio:
   if a.tts_engine=='piper':
    if not a.model:p.error('Piper selected: --model voice.onnx required')
    run('Neural narration',[sys.executable,ROOT/'scripts/android_tts_piper.py','--text',script,'--model',a.model,'--output',audio])
   else:run('eSpeak narration',[sys.executable,ROOT/'scripts/android_tts_espeak.py','--text',script,'--output',audio,'--speed',a.speed])
  elif not audio.is_file():p.error('Audio input not found')
  run('Planning',[sys.executable,ROOT/'scripts/android_scene_planner.py',script,'--out',plan,'--wpm',a.wpm])
  if not a.subtitle:run('Subtitle',[sys.executable,ROOT/'scripts/android_subtitle_generator.py','--plan',plan,'--out',srt])
  run('Resolve assets',[sys.executable,ROOT/'scripts/android_visual_asset_engine.py','--plan',plan,'--manifest',manifest,'--assets-out',assets,'--metadata-out',meta])
  run('Render',[sys.executable,ROOT/'scripts/android_multiscene_render_v4.py','--plan',plan,'--assets',assets,'--audio',audio,'--subtitle',srt,'--output',o,'--work-dir',w/'render','--width',a.width,'--height',a.height,'--fps',a.fps])
  total=sum(float(s['duration_seconds']) for s in json.loads(plan.read_text())['scenes']);run('QC',[sys.executable,ROOT/'scripts/android_video_qc.py',o,'--expected-duration',total,'--report',qc]);r={'status':'success','output':str(o),'qc':str(qc),'audio':str(audio),'subtitle':str(srt),'plan':str(plan)};(w/'pipeline_report.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));return 0
 except Exception as e:print('ERROR:',e,file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
