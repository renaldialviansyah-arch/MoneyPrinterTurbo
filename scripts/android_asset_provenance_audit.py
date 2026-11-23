#!/usr/bin/env python3
"""Independent production asset audit with explicit PASS/DEGRADED/FAIL states."""
import argparse,json,sys,urllib.parse
from pathlib import Path
try:
 from PIL import Image
except Exception:
 Image=None

def audit(manifest,expected,require_external=False):
 m=json.loads(Path(manifest).read_text(encoding="utf-8"))
 entries=m.get("assets",[])
 issues=[];degraded=[];seen=set()
 if not isinstance(entries,list) or not entries:issues.append("empty or malformed asset list")
 if expected is not None and len(entries)!=expected:issues.append(f"asset count mismatch: {len(entries)} != {expected}")
 for i,e in enumerate(entries,1):
  path=Path(e.get("path",""))
  if not path.is_file():issues.append(f"scene {i}: missing asset file");continue
  if path.stat().st_size<1200:issues.append(f"scene {i}: file too small")
  source=str(e.get("source","")).strip();license=str(e.get("license","")).strip()
  if source.startswith("http"):
   u=urllib.parse.urlparse(source)
   if u.scheme not in ("http","https") or not u.netloc:issues.append(f"scene {i}: malformed source URL")
  else:degraded.append(f"scene {i}: no external source URL ({source or 'missing'})")
  if not license:degraded.append(f"scene {i}: license missing")
  if "fallback" in source.lower() or "generated graphic" in license.lower():degraded.append(f"scene {i}: fallback graphic")
  key=source or str(path.resolve())
  if key in seen:degraded.append(f"scene {i}: duplicated source")
  seen.add(key)
  if Image:
   try:
    with Image.open(path) as im:
     im.verify()
   except Exception as ex:issues.append(f"scene {i}: invalid image: {ex}")
 status="FAIL" if issues else ("DEGRADED" if degraded else "PASS")
 if require_external and degraded and status!="FAIL":status="FAIL"
 return {"status":status,"asset_count":len(entries),"expected_count":expected,"issues":issues,"degraded":degraded}
def main():
 p=argparse.ArgumentParser();p.add_argument("manifest");p.add_argument("--expected-scenes",type=int);p.add_argument("--require-external",action="store_true");p.add_argument("--report",default="asset_audit.json");a=p.parse_args()
 try:
  r=audit(a.manifest,a.expected_scenes,a.require_external);Path(a.report).write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8");print(json.dumps(r,indent=2,ensure_ascii=False));return 0 if r["status"]!="FAIL" else 1
 except Exception as e:print("AUDIT ERROR:",e,file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
