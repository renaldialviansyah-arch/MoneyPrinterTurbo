#!/usr/bin/env python3
"""Discover and download reuse-licensed Wikimedia Commons image assets directly."""
import argparse,json,re,urllib.parse,urllib.request,subprocess,shutil
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
API="https://commons.wikimedia.org/w/api.php"
UA="AndroidMobileVideoWorkflow/2.0 (image downloader; contact via repository)"
PERMITTED={"CC0","Public domain","Public Domain","CC BY 4.0","CC BY 3.0","CC BY 2.0","CC BY-SA 4.0","CC BY-SA 3.0","CC BY-SA 2.0"}
def request(q):
 params={"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":6,"gsrlimit":12,"prop":"imageinfo","iiprop":"url|extmetadata","format":"json"}
 req=urllib.request.Request(API+"?"+urllib.parse.urlencode(params),headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=30) as r:return json.loads(r.read().decode())
def plain(x):return re.sub(r"<[^>]+>"," ",(x or {}).get("value","")).strip()
def candidates(q):
 pages=request(q).get("query",{}).get("pages",{}) or {};out=[]
 for page in pages.values():
  info=(page.get("imageinfo") or [{}])[0];m=info.get("extmetadata") or {};lic=plain(m.get("LicenseShortName"));url=info.get("url","")
  if lic not in PERMITTED or not url:continue
  ext=Path(urllib.parse.urlparse(url).path).suffix.lower()
  if ext not in (".jpg",".jpeg",".png",".webp"):continue
  out.append({"title":page.get("title",""),"url":url,"source":info.get("descriptionurl",""),"license":lic,"license_url":plain(m.get("LicenseUrl")),"artist":plain(m.get("Artist")),"credit":plain(m.get("Credit")),"attribution":plain(m.get("Attribution")),"ext":ext})
 return out
def download(c,target):
 req=urllib.request.Request(c["url"],headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=40) as r:
  data=r.read()
 if len(data)<1200:raise ValueError("Downloaded file too small")
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 # Decode-check with FFmpeg if present, otherwise check recognizable image signature.
 ff=shutil.which("ffmpeg")
 if ff:
  p=subprocess.run([ff,"-v","error","-i",str(target),"-frames:v","1","-f","null","-"],capture_output=True,text=True,timeout=30)
  if p.returncode:raise ValueError("FFmpeg image validation failed: "+p.stderr[-400:])
 else:
  sig=data[:12]
  if not (sig.startswith(b"\\xff\\xd8\\xff") or sig.startswith(b"\\x89PNG") or b"WEBP" in sig):raise ValueError("Unrecognized image signature")
 return len(data)
def main():
 p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--out-dir",default="visuals");p.add_argument("--manifest",default="assets_local.json");p.add_argument("--report",default="asset_sources.json");p.add_argument("--max-attempts",type=int,default=8);a=p.parse_args()
 plan=json.loads(Path(a.plan).read_text(encoding="utf-8"));scenes=plan.get("scenes")
 if not isinstance(scenes,list) or not scenes:p.error("Scene plan must contain scenes")
 outdir=Path(a.out_dir);downloaded=[];sources=[];failed=[];used=set()
 for n,s in enumerate(scenes,1):
  queries=[]
  for raw in (s.get("search_terms"),s.get("visual_prompt"),s.get("narration")):
   q=str(raw or "").strip()[:220]
   if q and q not in queries:queries.append(q)
  opts=[]
  for q in queries:
   try:
    for c in candidates(q):
     if c["url"] not in used and all(x["url"]!=c["url"] for x in opts):opts.append(c)
   except Exception as e:failed.append({"scene":n,"query":q,"error":"Search error: "+str(e)})
  chosen=None
  for c in opts[:a.max_attempts]:
   target=outdir/f"scene{n:03}{c['ext']}"
   try:
    size=download(c,target);used.add(c["url"]);chosen=c
    notes="Attribution: "+(c["artist"] or c["credit"] or c["attribution"] or "not supplied")+" | "+c["license_url"]
    item={"scene":n,"path":str(target.resolve()),"source":c["source"],"license":c["license"],"notes":notes,"title":c["title"],"bytes":size}
    downloaded.append(item);sources.append({"scene":n,**c,"download_bytes":size});break
   except Exception as e:
    if target.exists():target.unlink()
    failed.append({"scene":n,"title":c["title"],"error":"Download/validation: "+str(e)})
  if not chosen:
   target=outdir/f"scene{n:03}_fallback.jpg"
   try:
    target.parent.mkdir(parents=True,exist_ok=True)
    W,H=1080,1920;im=Image.new("RGB",(W,H));pix=im.load()
    seed=n*37;c1=(18+seed%35,25+(seed*2)%35,45+(seed*3)%45);c2=(100+seed%70,40+(seed*5)%70,20+seed%55)
    for y in range(H):
     t=y/(H-1);col=tuple(int(c1[k]*(1-t)+c2[k]*t) for k in range(3))
     for x in range(W):pix[x,y]=col
    d=ImageDraw.Draw(im,"RGBA")
    d.ellipse((W*.15,H*.12,W*.85,H*.58),fill=(255,180,80,22))
    d.polygon([(0,H*.72),(W*.28,H*.42),(W*.52,H*.78),(W*.78,H*.45),(W,H*.73),(W,H),(0,H)],fill=(0,0,0,110))
    d.rectangle((70,90,W-70,H-90),outline=(255,255,255,70),width=3)
    raw=str(s.get("narration") or s.get("visual_prompt") or s.get("search_terms") or f"Scene {n}")
    title=" ".join(re.sub(r"[^A-Za-z0-9À-ÿ ]"," ",raw).strip().split()[:14])[:100]
    try:font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",64)
    except Exception:font=ImageFont.load_default()
    lines=[];line=""
    for word in title.split():
     if len(line+" "+word)>22:lines.append(line);line=word
     else:line=(line+" "+word).strip()
    if line:lines.append(line)
    yy=int(H*.58)
    for line in lines[:5]:
     d.text((100,yy),line,font=font,fill=(255,255,255,235),stroke_width=2,stroke_fill=(0,0,0,130));yy+=90
    im.save(target,quality=90)
    item={"scene":n,"path":str(target.resolve()),"source":"generated local cinematic fallback","license":"Generated graphic (no external image)","notes":"Fallback generated locally because Wikimedia retrieval failed.","title":title,"bytes":target.stat().st_size}
    downloaded.append(item);sources.append({"scene":n,"title":title,"fallback":True,"download_bytes":target.stat().st_size})
    print(f"Scene {n}: fallback graphic created")
   except Exception as e:failed.append({"scene":n,"queries":queries,"error":"Fallback generation failed: "+str(e)})
 Path(a.manifest).parent.mkdir(parents=True,exist_ok=True)
 Path(a.manifest).write_text(json.dumps({"assets":downloaded},indent=2,ensure_ascii=False),encoding="utf-8")
 Path(a.report).parent.mkdir(parents=True,exist_ok=True)
 Path(a.report).write_text(json.dumps({"sources":sources,"failures":failed,"license_allowlist":sorted(PERMITTED),"notice":"Review relevance, attribution, and license conditions before publication."},indent=2,ensure_ascii=False),encoding="utf-8")
 print(f"Assets downloaded and validated: {len(downloaded)}/{len(scenes)}")
 return 0 if len(downloaded)==len(scenes) else 2
if __name__=="__main__":raise SystemExit(main())
