#!/usr/bin/env python3
"""Production visual acquisition from Wikimedia Commons with relevance filtering and fail-closed QC."""
import argparse,json,re,urllib.parse,urllib.request,subprocess,shutil,unicodedata
from pathlib import Path
API="https://commons.wikimedia.org/w/api.php"
UA="MoneyPrinterTurboProduction/3.0 (licensed media downloader)"
PERMITTED={"CC0","Public domain","Public Domain","CC BY 4.0","CC BY 3.0","CC BY 2.0","CC BY-SA 4.0","CC BY-SA 3.0","CC BY-SA 2.0"}
STOP={"the","and","but","with","that","this","from","into","when","where","what","how","why","are","was","were","have","has","had","for","not","you","your","they","them","their","about","over","under","then","than","its","yang","dan","atau","dari","pada","untuk","dengan","ini","itu","dalam","akan","telah","sudah","belum","bisa","dapat","adalah","oleh","karena","mereka","kita","kami","saya","dia","sebagai","lebih","saat","juga","tidak","ada","jadi","ke","di","an"}
def norm(s):
 s=unicodedata.normalize("NFKD",s or "").encode("ascii","ignore").decode().lower()
 return set(re.findall(r"[a-z0-9]{3,}",s))-STOP
def request(q):
 params={"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":6,"gsrlimit":30,"prop":"imageinfo","iiprop":"url|extmetadata|size","format":"json"}
 req=urllib.request.Request(API+"?"+urllib.parse.urlencode(params),headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=30) as r:return json.loads(r.read().decode())
def plain(x):return re.sub(r"<[^>]+>"," ",(x or {}).get("value","")).strip()
def candidates(q):
 pages=request(q).get("query",{}).get("pages",{}) or {};out=[]
 qwords=norm(q)
 for page in pages.values():
  info=(page.get("imageinfo") or [{}])[0];m=info.get("extmetadata") or {};lic=plain(m.get("LicenseShortName"));url=info.get("url","")
  if lic not in PERMITTED or not url:continue
  ext=Path(urllib.parse.urlparse(url).path).suffix.lower()
  if ext not in (".jpg",".jpeg",".png",".webp"):continue
  if int(info.get("size",0))<40000:continue
  title=page.get("title","");score=len(qwords & norm(title))
  if score==0:continue
  out.append({"title":title,"url":url,"source":info.get("descriptionurl",""),"license":lic,"license_url":plain(m.get("LicenseUrl")),"artist":plain(m.get("Artist")),"credit":plain(m.get("Credit")),"attribution":plain(m.get("Attribution")),"ext":ext,"score":score,"size":int(info.get("size",0))})
 return sorted(out,key=lambda x:(x["score"],x["size"]),reverse=True)
def download(c,target):
 req=urllib.request.Request(c["url"],headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=40) as r:data=r.read()
 if len(data)<1200:raise ValueError("Downloaded file too small")
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 ff=shutil.which("ffmpeg")
 if ff:
  p=subprocess.run([ff,"-v","error","-i",str(target),"-frames:v","1","-f","null","-"],capture_output=True,text=True,timeout=30)
  if p.returncode:raise ValueError("FFmpeg image validation failed: "+p.stderr[-400:])
 else:
  sig=data[:12]
  if not (sig.startswith(bytes.fromhex("ffd8ff")) or sig.startswith(bytes.fromhex("89504e47")) or b"WEBP" in sig):raise ValueError("Unrecognized image signature")
 return len(data)
def main():
 p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--out-dir",default="visuals");p.add_argument("--manifest",default="assets_local.json");p.add_argument("--report",default="asset_sources.json");p.add_argument("--max-attempts",type=int,default=15);p.add_argument("--allow-fallback",action="store_true",help="Not recommended for production");a=p.parse_args()
 plan=json.loads(Path(a.plan).read_text(encoding="utf-8"));scenes=plan.get("scenes")
 if not isinstance(scenes,list) or not scenes:p.error("Scene plan must contain scenes")
 outdir=Path(a.out_dir);downloaded=[];sources=[];failed=[];used=set()
 for n,s in enumerate(scenes,1):
  rawlist=[s.get("search_terms"),s.get("visual_prompt"),s.get("narration")]
  queries=[]
  for raw in rawlist:
   q=str(raw or "").strip()
   q=re.sub(r"\|.*$","",q).strip()
   q=re.sub(r"\b(documentary cinematic photograph|specific documentary visual of)\b","",q,flags=re.I).strip()
   if q and q not in queries:queries.append(q[:180])
  # Generate compact subject query from title-like scene keywords.
  subject=" ".join(sorted(norm(str(s.get("narration") or s.get("search_terms") or ""))))
  if subject:queries.append(subject[:160])
  opts=[]
  for q in queries[:5]:
   try:
    for c in candidates(q):
     if c["url"] not in used and all(x["url"]!=c["url"] for x in opts):opts.append(c)
   except Exception as e:failed.append({"scene":n,"query":q,"error":"Search error: "+str(e)})
  opts.sort(key=lambda x:(x["score"],x["size"]),reverse=True)
  chosen=None
  for c in opts[:a.max_attempts]:
   target=outdir/f"scene{n:03}{c['ext']}"
   try:
    size=download(c,target);used.add(c["url"]);chosen=c
    notes="Attribution: "+(c["artist"] or c["credit"] or c["attribution"] or "not supplied")+" | "+c["license_url"]
    downloaded.append({"scene":n,"path":str(target.resolve()),"source":c["source"],"license":c["license"],"notes":notes,"title":c["title"],"bytes":size})
    sources.append({"scene":n,**c,"download_bytes":size});print(f"Scene {n}: selected {c['title']} (score {c['score']})");break
   except Exception as e:
    if target.exists():target.unlink()
    failed.append({"scene":n,"title":c["title"],"error":"Download/validation: "+str(e)})
  if not chosen:
   failed.append({"scene":n,"queries":queries,"error":"No relevant licensed image passed filtering"})
   if a.allow_fallback:
    # Deliberately visible fallback; never silently substitute.
    target=outdir/f"scene{n:03}_fallback.jpg";target.parent.mkdir(parents=True,exist_ok=True)
    from PIL import Image,ImageDraw
    im=Image.new("RGB",(720,1280),(30,30,40));d=ImageDraw.Draw(im);d.text((40,600),"VISUAL ACQUISITION FAILED",fill="white");im.save(target)
    downloaded.append({"scene":n,"path":str(target.resolve()),"source":"explicit fallback","license":"generated graphic","notes":"Clearly marked diagnostic fallback","title":"Visual acquisition failed","bytes":target.stat().st_size})
  Path(a.manifest).parent.mkdir(parents=True,exist_ok=True)
  Path(a.manifest).write_text(json.dumps({"assets":downloaded},indent=2,ensure_ascii=False),encoding="utf-8")
 Path(a.report).parent.mkdir(parents=True,exist_ok=True)
 Path(a.report).write_text(json.dumps({"sources":sources,"failures":failed,"license_allowlist":sorted(PERMITTED),"scene_count":len(scenes),"asset_count":len(downloaded),"status":"PASS" if len(downloaded)==len(scenes) and not any(x.get("error","").startswith("No relevant") for x in failed) else "FAIL","notice":"Review relevance, attribution, and license conditions before publication."},indent=2,ensure_ascii=False),encoding="utf-8")
 print(f"Relevant licensed assets: {len(downloaded)}/{len(scenes)}")
 return 0 if len(downloaded)==len(scenes) and not any(x.get("error","").startswith("No relevant") for x in failed) else 2
if __name__=="__main__":raise SystemExit(main())
