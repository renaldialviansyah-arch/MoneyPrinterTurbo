#!/usr/bin/env python3
"""Discover candidate media on Wikimedia Commons for scene plans. No downloading."""
from __future__ import annotations
import argparse,json,sys,urllib.parse,urllib.request
API="https://commons.wikimedia.org/w/api.php"
UA="AndroidMobileVideoWorkflow/0.1 (scene-media-discovery; educational use)"
def api(query):
 params={"action":"query","generator":"search","gsrsearch":query,"gsrnamespace":6,"gsrlimit":5,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1280,"format":"json"}
 url=API+"?"+urllib.parse.urlencode(params)
 req=urllib.request.Request(url,headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=20) as r:return json.loads(r.read().decode("utf-8"))
def clean_meta(v):
 return (v or {}).get("value","").replace("<p>"," ").replace("</p>"," ").strip()
def discover(plan):
 scenes=plan.get("scenes")
 if not isinstance(scenes,list) or not scenes:raise ValueError("Plan has no scenes")
 results=[]
 for n,s in enumerate(scenes,1):
  q=s.get("search_terms") or s.get("visual_prompt") or s.get("narration") or ""
  q=" ".join(str(q).split()[:18])
  try:
   data=api(q);pages=(data.get("query",{}).get("pages") or {})
   items=[]
   for page in pages.values():
    ii=(page.get("imageinfo") or [{}])[0];meta=ii.get("extmetadata") or {}
    items.append({"scene":n,"query":q,"title":page.get("title",""),"url":ii.get("url",""),"thumbnail":ii.get("thumburl",""),"page_url":ii.get("descriptionurl",""),"license":clean_meta(meta.get("LicenseShortName")),"license_url":clean_meta(meta.get("LicenseUrl")),"artist":clean_meta(meta.get("Artist")),"credit":clean_meta(meta.get("Credit")),"candidates_note":"Review the source page and license before use."})
   results.append({"scene":n,"query":q,"candidates":items})
  except Exception as e:results.append({"scene":n,"query":q,"error":str(e),"candidates":[]})
 return results
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--plan",required=True);p.add_argument("--out",default="visual_candidates.json");p.add_argument("--manifest-out",default="visual_urls_review.json");a=p.parse_args()
 try:
  plan=json.loads(open(a.plan,encoding="utf-8").read());results=discover(plan)
  with open(a.out,"w",encoding="utf-8") as f:json.dump(results,f,indent=2,ensure_ascii=False)
  # Convenience manifest: first candidate per scene. Must review before downloading.
  manifest=[]
  for row in results:
   if row.get("candidates"):
    c=row["candidates"][0];manifest.append({"scene":row["scene"],"url":c["url"],"source":c["page_url"],"license":c["license"] or "unknown","notes":"AUTO-CANDIDATE: review before use"})
  with open(a.manifest_out,"w",encoding="utf-8") as f:json.dump({"assets":manifest},f,indent=2,ensure_ascii=False)
  print(f"Saved candidate research to {a.out}; review manifest to {a.manifest_out}. No files downloaded.")
 except Exception as e:print("ERROR:",e,file=sys.stderr);return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
