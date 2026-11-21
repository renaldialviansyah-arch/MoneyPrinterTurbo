import json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(c):subprocess.run(c,check=True)
def main():
 with tempfile.TemporaryDirectory() as d:
  w=Path(d); imgs=[]
  for i,c in enumerate(['blue','red']):
   p=w/f'i{i}.png';run(['ffmpeg','-y','-hide_banner','-f','lavfi','-i',f'color=c={c}:s=360x640:d=1','-frames:v','1',str(p)]);imgs.append(p)
  au=w/'a.wav';run(['ffmpeg','-y','-hide_banner','-f','lavfi','-i','sine=frequency=440:duration=4','-c:a','pcm_s16le',str(au)])
  pl=w/'p.json';pl.write_text(json.dumps({'scenes':[{'duration_seconds':2},{'duration_seconds':2}]}));ap=w/'a.json';ap.write_text(json.dumps([str(x) for x in imgs]));s=w/'s.srt';s.write_text('1\n00:00:00,000 --> 00:00:02,000\nTest one\n\n2\n00:00:02,000 --> 00:00:04,000\nTest two\n')
  out=w/'out.mp4';run(['python',str(ROOT/'scripts/android_multiscene_render_v5.py'),'--plan',str(pl),'--assets',str(ap),'--audio',str(au),'--subtitle',str(s),'--output',str(out),'--work-dir',str(w/'r'),'--width','360','--height','640','--fps','12','--motion','subtle']);run(['python',str(ROOT/'scripts/android_video_qc.py'),str(out),'--expected-duration','4','--report',str(w/'qc.json')]);q=json.loads((w/'qc.json').read_text());assert q['status']=='PASS' and q['subtitle_streams']>=1,q;print('SMOKE PASS')
if __name__=='__main__':main()
