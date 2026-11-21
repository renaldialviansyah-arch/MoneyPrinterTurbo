#!/usr/bin/env python3
"""Convert fetcher metadata into the resolver manifest format."""
import argparse,json
from pathlib import Path
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("metadata");p.add_argument("--out",default="visual_manifest_resolved.json");a=p.parse_args()
 src=Path(a.metadata).expanduser().resolve();data=json.loads(src.read_text(encoding="utf-8"))
 if not isinstance(data,list) or not data: p.error("Metadata must be a non-empty list")
 assets=[]
 for x in data:
  assets.append({"scene":int(x["scene"]),"path":str(Path(x["path"]).resolve()),"source":x.get("source",x.get("url","downloaded URL")),"license":x.get("license","unspecified"),"notes":x.get("notes","")})
 out=Path(a.out).expanduser().resolve();out.write_text(json.dumps({"assets":assets},indent=2,ensure_ascii=False),encoding="utf-8")
 print("Resolver manifest:",out)
if __name__=="__main__":main()
