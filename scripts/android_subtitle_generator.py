#!/usr/bin/env python3
"""Generate scene-timed SRT captions from a scene plan."""
import argparse,json
from pathlib import Path
def stamp(sec):
 ms=max(0,round(sec*1000));h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def generate(plan,max_chars=90):
 scenes=plan.get('scenes')
 if not isinstance(scenes,list) or not scenes:raise ValueError('Scene plan requires non-empty scenes')
 rows=[];start=0.0
 for i,sc in enumerate(scenes,1):
  dur=float(sc.get('duration_seconds',0));text=str(sc.get('subtitle_text') or sc.get('narration') or '').strip()
  if dur<=0 or not text:raise ValueError(f'Invalid duration or text for scene {i}')
  lines=[]
  while len(text)>max_chars:
   cut=text.rfind(' ',0,max_chars);cut=cut if cut>0 else max_chars;lines.append(text[:cut].strip());text=text[cut:].strip()
  if text:lines.append(text)
  rows.append(f'{i}\n{stamp(start)} --> {stamp(start+dur)}\n'+'\n'.join(lines)+'\n');start+=dur
 return '\n'.join(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument('--plan',required=True);p.add_argument('--out',default='subtitles.srt');p.add_argument('--max-chars',type=int,default=90);a=p.parse_args()
 Path(a.out).write_text(generate(json.loads(Path(a.plan).read_text(encoding='utf-8')),a.max_chars),encoding='utf-8');print('Saved',a.out)
if __name__=='__main__':main()
