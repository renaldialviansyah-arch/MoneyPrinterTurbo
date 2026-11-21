#!/usr/bin/env python3
"""Generate natural neural narration with Piper CLI (not eSpeak)."""
import argparse,subprocess,sys
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--text",required=True);p.add_argument("--model",required=True,help="Piper .onnx voice model");p.add_argument("--output",required=True);p.add_argument("--length-scale",type=float,default=1.0);p.add_argument("--noise-scale",type=float,default=0.667);p.add_argument("--noise-w",type=float,default=0.8);p.add_argument("--sentence-silence",type=float,default=0.2);p.add_argument("--piper",default="piper");a=p.parse_args()
 t=Path(a.text);text=t.read_text(encoding="utf-8") if t.is_file() else a.text
 model=Path(a.model).expanduser().resolve()
 if not model.is_file():p.error("Model file not found: "+str(model))
 if not text.strip():p.error("Text empty")
 out=Path(a.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
 cmd=[a.piper,"--model",str(model),"--output_file",str(out),"--length_scale",str(a.length_scale),"--noise_scale",str(a.noise_scale),"--noise_w",str(a.noise_w),"--sentence_silence",str(a.sentence_silence)]
 try:subprocess.run(cmd,input=text,text=True,check=True)
 except FileNotFoundError:print("Piper CLI missing; install piper-tts and use its CLI",file=sys.stderr);return 2
 except subprocess.CalledProcessError as e:return e.returncode
 if not out.exists() or out.stat().st_size<1000:print("Output WAV missing or invalid",file=sys.stderr);return 1
 print("Natural neural WAV created:",out,"bytes",out.stat().st_size);return 0
if __name__=="__main__":raise SystemExit(main())
