#!/usr/bin/env python3
"""Build a simple scene storyboard and draft SRT from a supplied narration script.

Offline, dependency-free, experimental. This does not generate AI scripts or validate media.
"""
import argparse, json, re
from pathlib import Path

def split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    if not text: return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]

def ts(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def build(text, seconds_per_sentence=5.5):
    sentences = split_sentences(text)
    scenes, captions = [], []
    for i, sentence in enumerate(sentences, 1):
        start = (i-1) * seconds_per_sentence
        end = start + seconds_per_sentence
        scenes.append({"scene": i, "narration": sentence, "visual_prompt": f"Illustrate this narration as a cinematic supporting shot: {sentence}", "duration_seconds": seconds_per_sentence})
        captions.append(f"{i}\n{ts(start)} --> {ts(end)}\n{sentence}\n")
    return scenes, "\n".join(captions), len(sentences)*seconds_per_sentence

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("script", help="Narration text file")
    ap.add_argument("--out", default="android_storyboard", help="Output base path (without extension)")
    ap.add_argument("--seconds", type=float, default=5.5, help="Approximate seconds per sentence")
    args=ap.parse_args()
    if args.seconds <= 0: ap.error("--seconds must be positive")
    text=Path(args.script).read_text(encoding="utf-8")
    scenes,srt,duration=build(text,args.seconds)
    base=Path(args.out)
    base.with_suffix(".json").write_text(json.dumps({"duration_seconds":duration,"scenes":scenes},ensure_ascii=False,indent=2),encoding="utf-8")
    base.with_suffix(".srt").write_text(srt,encoding="utf-8")
    print(f"Created {base.with_suffix('.json')} and {base.with_suffix('.srt')} ({len(scenes)} scenes, ~{duration:.1f}s)")
if __name__=="__main__": main()
