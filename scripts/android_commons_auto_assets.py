#!/usr/bin/env python3
"""Discover and download Commons images with explicit license allow-list and attribution metadata."""
import argparse,json,re,subprocess,sys,urllib.parse,urllib.request
from pathlib import Path
API="https://commons.wikimedia.org/w/api.php"
UA="AndroidMobileVideoWorkflow/1.0 (automated asset pipeline)"
# Permit public domain and common Creative Commons reuse licenses; retain attribution details.
PERMITTED={"CC0","Public domain","Public Domain","CC BY 4.0","CC BY 3.0","CC BY 2.0","CC BY-SA 4.0","CC BY-SA 3.0","CC BY-SA 2.0"}
def request(q):
 params={"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":6,"gsrlimit":8,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1200,"format":"json"}
 url=API+"?"+urllib.parse.urlencode(params)
 req=urllib.request.Request(url,headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=25) as r:return json.loads(r.read().decode())
def plain(x):
 return re.sub(r"<[^>]+>"," ",(x or {}).get("value","")).strip()
def candidates(q):
 data=request(q);pages=(data.get("query",{}).get("pages") or {})
 out=[]
 for page in pages.values():
  info=(page.get("imageinfo") or [{}])[0];m=info.get("extmetadata") or {}
  license=plain(m.get("LicenseShortName"));url=info.get("url","")
  if license not in PERMITTED or not url.lower().split("?")[0].endswith((".jpg",".jpeg",".png",".webp")):continue
  out.append({"title":page.get("title",""),"url":url,"source":info.get("descriptionurl",""),"license":license,"license_url":plain(m.get("LicenseUrl")),"artist":plain(m.get("Artist")),"credit":plain(m.get("Credit")),"attribution":plain(m.get("Attribution"))})
 return out
def main():
 p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--out-dir",default="visuals");p.add_argument("--manifest",default="assets_local.json");p.add_argument("--report",default="asset_sources.json");p.add_argument("--fetcher",default="scripts/android_visual_fetcher_v2.py");p.add_argument("--max-attempts",type=int,default=5);a=p.parse_args()
 plan=json.loads(Path(a.plan).read_text(encoding="utf-8"));scenes=plan.get("scenes")
 if not isinstance(scenes,list) or not scenes:p.error("Scene plan must contain scenes")
 downloaded=[];sources=[];failed=[];used_urls=set()
 for n,s in enumerate(scenes,1):
  queries=[]
  for raw in (s.get("search_terms"),s.get("narration"),s.get("visual_prompt")):
   q=str(raw or "").strip()[:220]
   if q and q not in queries:queries.append(q)
  opts=[];chosen=None
  for q in queries:
   try:
    for cand in candidates(q):
     if cand["url"] not in used_urls and all(x["url"]!=cand["url"] for x in opts):opts.append(cand)
   except Exception as e:failed.append({"scene":n,"query":q,"error":"Search: "+str(e)})
   if len(opts)>=a.max_attempts:break
  for c in opts[:a.max_attempts]:
   ext=Path(urllib.parse.urlparse(c["url"]).path).suffix.lower()
   target=Path(a.out_dir)/f"scene{n:03}{ext}"
   one={"assets":[{"scene":n,"url":c["url"],"path":str(target.resolve()),"source":c["source"],"license":c["license"],"notes":"Attribution: "+(c["artist"] or c["credit"] or "not supplied")+" | "+c["license_url"]}]}
   temp=Path(a.out_dir)/f".download_manifest_{n}.json";temp.parent.mkdir(parents=True,exist_ok=True);temp.write_text(json.dumps(one),encoding="utf-8")
   try:
    subprocess.run([sys.executable,a.fetcher,"--manifest",str(temp),"--out-dir",a.out_dir,"--metadata-out",str(Path(a.out_dir)/f".downloadmeta_{n}.json")],check=True,capture_output=True,text=True)
    chosen=c;used_urls.add(c["url"]);downloaded.append({"scene":n,"path":str(target),"source":c["source"],"license":c["license"]});sources.append({"scene":n,**c});break
   except Exception as e:failed.append({"scene":n,"title":c["title"],"error":str(e)})
  if not chosen:failed.append({"scene":n,"queries":queries,"error":"No successfully downloaded unique candidate under allow-list"})
 Path(a.manifest).write_text(json.dumps({"assets":downloaded},indent=2,ensure_ascii=False),encoding="utf-8")
 Path(a.report).write_text(json.dumps({"sources":sources,"failures":failed,"license_allowlist":sorted(PERMITTED),"notice":"Review each source page, image relevance, and license terms before publishing."},indent=2,ensure_ascii=False),encoding="utf-8")
 print(f"Assets downloaded: {len(downloaded)}/{len(scenes)}. Manifest: {a.manifest}. Source report: {a.report}")
 if len(downloaded)!=len(scenes):return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
