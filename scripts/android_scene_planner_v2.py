#!/usr/bin/env python3
"""Cinematic scene planner v2: specific visuals, search terms, shot and continuity metadata."""
import argparse,json,re
from pathlib import Path
def sentences(text):
 text=re.sub(r"\s+"," ",text.strip())
 return [s.strip() for s in re.split(r"(?<=[.!?])\s+",text) if s.strip()]
def keywords(s):
 stop={"the","and","but","with","that","this","from","into","when","where","what","how","why","are","was","were","have","has","had","for","not","you","your","they","them","their","about","over","under","then","than","its"}
 words=re.findall(r"[A-Za-z0-9'-]+",s.lower())
 useful=[w for w in words if w not in stop and len(w)>2]
 return " ".join(useful[:12]) or s[:100]
def plan(text,wpm=145):
 scenes=[];shots=["wide establishing shot","medium shot","close-up detail","over-the-shoulder","low-angle cinematic shot","aerial or overhead shot"];camera=["slow push-in","subtle lateral drift","gentle pull-back","slow pan left","slow pan right","steady framing"]
 for i,s in enumerate(sentences(text),1):
  n=len(re.findall(r"\b\w+\b",s));dur=max(4,min(12,round(n*60/max(wpm,1),2)));k=keywords(s)
  scenes.append({"scene":i,"narration":s,"subtitle_text":s,"duration_seconds":dur,"shot_type":shots[(i-1)%len(shots)],"camera_movement":camera[(i-1)%len(camera)],"search_terms":k+" documentary cinematic photograph","visual_prompt":"Specific documentary visual of "+s+" | shot: "+shots[(i-1)%len(shots)]+" | composition: clear subject, foreground/midground/background layers, realistic lighting, cinematic color, no text or logos.","motion_prompt":camera[(i-1)%len(camera)],"transition":"cut" if i==1 else "continuity cut or brief dissolve","visual_group":i,"continuity_note":"Maintain documentary realism and coherent visual style across scenes."})
 return {"format":"android-mobile-scene-plan-v2","scene_count":len(scenes),"estimated_duration_seconds":round(sum(x["duration_seconds"] for x in scenes),2),"scenes":scenes}
def main():
 p=argparse.ArgumentParser();p.add_argument("script");p.add_argument("--out",default="scene_plan.json");p.add_argument("--wpm",type=int,default=145);a=p.parse_args()
 if not 40<=a.wpm<=400:p.error("WPM must be 40-400")
 d=plan(Path(a.script).read_text(encoding="utf-8"),a.wpm);Path(a.out).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");print(f"Planned {d['scene_count']} scenes with cinematic metadata.")
if __name__=="__main__":main()
