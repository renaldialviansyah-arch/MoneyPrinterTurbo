#!/usr/bin/env python3
"""Offline narration generator using eSpeak/eSpeak NG; outputs WAV."""
import argparse,shutil,subprocess,sys
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--text",required=True);p.add_argument("--output",required=True);p.add_argument("--voice",default="en-us");p.add_argument("--speed",type=int,default=150);p.add_argument("--pitch",type=int,default=50);p.add_argument("--volume",type=int,default=100);a=p.parse_args()
 exe=shutil.which("espeak-ng") or shutil.which("espeak")
 if not exe:print("ERROR: install espeak or espeak-ng",file=sys.stderr);return 2
 src=Path(a.text)
 text=src.read_text(encoding="utf-8") if src.is_file() else a.text
 if not text.strip():p.error("Text is empty")
 if not 80<=a.speed<=450:p.error("Speed must be 80..450")
 if not 0<=a.pitch<=99:p.error("Pitch must be 0..99")
 if not 0<=a.volume<=200:p.error("Volume must be 0..200")
 out=Path(a.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 cmd=[exe,"-v",a.voice,"-s",str(a.speed),"-p",str(a.pitch),"-a",str(a.volume),"-w",str(out),text]
 try:subprocess.run(cmd,check=True)
 except subprocess.CalledProcessError as e:print("TTS failed:",e,file=sys.stderr);return e.returncode
 if not out.exists() or out.stat().st_size<1000:print("ERROR: output missing/invalid",file=sys.stderr);return 1
 print("Generated WAV:",out,"bytes:",out.stat().st_size);return 0
if __name__=="__main__":raise SystemExit(main())
