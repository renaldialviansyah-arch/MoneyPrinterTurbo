#!/usr/bin/env python3
"""Basic MP4 QC with optional subtitle and resolution requirements."""
import argparse,json,subprocess,sys
from pathlib import Path

def probe(path):
 r=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stderr.strip() or 'ffprobe failed')
 return json.loads(r.stdout)

def inspect(path,expected_duration=None,require_subtitles=False,min_width=0,min_height=0):
 p=probe(path);streams=p.get('streams',[]);v=[x for x in streams if x.get('codec_type')=='video'];a=[x for x in streams if x.get('codec_type')=='audio'];s=[x for x in streams if x.get('codec_type')=='subtitle'];issues=[]
 if not v:issues.append('video stream missing')
 if not a:issues.append('audio stream missing')
 if require_subtitles and not s:issues.append('subtitle stream missing')
 if v:
  width=int(v[0].get('width',0));height=int(v[0].get('height',0))
  if width<=0 or height<=0:issues.append('invalid video dimensions')
  if width<min_width:issues.append(f'video width below minimum: {width} < {min_width}')
  if height<min_height:issues.append(f'video height below minimum: {height} < {min_height}')
 dur=float(p.get('format',{}).get('duration') or 0)
 if dur<=0:issues.append('duration missing or zero')
 if expected_duration is not None and abs(dur-expected_duration)>0.25:issues.append(f'duration mismatch: {dur:.3f} vs expected {expected_duration:.3f}')
 audio_durations=[float(x.get('duration') or 0) for x in a if x.get('duration')]
 if audio_durations and dur and max(audio_durations)<dur-0.5:issues.append(f'audio appears shorter than video: {max(audio_durations):.3f}s vs {dur:.3f}s')
 return {'file':str(path),'bytes':Path(path).stat().st_size,'duration_seconds':dur,'video_streams':len(v),'audio_streams':len(a),'subtitle_streams':len(s),'resolution':f"{v[0].get('width')}x{v[0].get('height')}" if v else None,'video_codec':v[0].get('codec_name') if v else None,'audio_codec':a[0].get('codec_name') if a else None,'subtitle_codec':s[0].get('codec_name') if s else None,'requirements':{'subtitles_required':require_subtitles,'minimum_width':min_width,'minimum_height':min_height},'issues':issues,'status':'PASS' if not issues else 'FAIL'}

def main():
 p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--expected-duration',type=float);p.add_argument('--report',default='qc_report.json');p.add_argument('--require-subtitles',action='store_true');p.add_argument('--min-width',type=int,default=0);p.add_argument('--min-height',type=int,default=0);a=p.parse_args()
 try:
  r=inspect(Path(a.video),a.expected_duration,a.require_subtitles,a.min_width,a.min_height);Path(a.report).write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2));return 0 if r['status']=='PASS' else 1
 except Exception as e:print('QC ERROR:',e,file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
