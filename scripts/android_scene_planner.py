#!/usr/bin/env python3
"""Turn narration/script text into a practical scene plan. Offline and dependency-free."""
import argparse, json, re
from pathlib import Path

def split_sentences(text):
    text=re.sub(r"\s+"," ",text.strip())
    if not text:return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+",text) if s.strip()]

def estimate_duration(sentence, words_per_minute=145, minimum=4.0, maximum=12.0):
    words=len(re.findall(r"\b\w+\b",sentence))
    return round(max(minimum,min(maximum,words*60/max(words_per_minute,1))),2)

def build_plan(text, words_per_minute=145):
    scenes=[]
    for idx,sentence in enumerate(split_sentences(text),1):
        duration=estimate_duration(sentence,words_per_minute)
        scenes.append({
          "scene":idx,"narration":sentence,"duration_seconds":duration,
          "shot_type":["wide establishing shot","medium cinematic shot","close-up detail shot","dynamic tracking shot"][ (idx-1)%4],
          "visual_prompt":"Cinematic documentary visual illustrating: "+sentence+" Natural realistic lighting, coherent composition, high detail, no text, no logos.",
          "motion_prompt":["slow push-in","subtle lateral camera movement","slow pan","gentle parallax"][ (idx-1)%4],
          "transition":"cut" if idx==1 else "match-cut or short dissolve",
          "subtitle_text":sentence
        })
    total=round(sum(x["duration_seconds"] for x in scenes),2)
    return {"format":"android-mobile-scene-plan-v1","estimated_duration_seconds":total,"scene_count":len(scenes),"scenes":scenes}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("script",help="Script/narration text file")
    p.add_argument("--out",default="scene_plan.json")
    p.add_argument("--wpm",type=int,default=145)
    a=p.parse_args()
    if a.wpm<40 or a.wpm>400:p.error("--wpm must be between 40 and 400")
    plan=build_plan(Path(a.script).read_text(encoding="utf-8"),a.wpm)
    Path(a.out).write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Saved {a.out}: {plan['scene_count']} scenes, estimated {plan['estimated_duration_seconds']} seconds")
if __name__=="__main__":main()
