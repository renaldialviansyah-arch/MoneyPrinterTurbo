#!/usr/bin/env python3
"""Wikimedia licensed image retrieval with original generated-card fallback."""
import argparse,json,re,urllib.parse,urllib.request,subprocess,shutil,unicodedata,time
from pathlib import Path
API="https://commons.wikimedia.org/w/api.php";UA="MoneyPrinterTurboProduction/3.0"
PERMITTED={"CC0","Public domain","Public Domain","CC BY 4.0","CC BY 3.0","CC BY 2.0","CC BY-SA 4.0","CC BY-SA 3.0","CC BY-SA 2.0"}
STOP={"the","and","but","with","that","this","from","into","when","where","what","how","why","are","was","were","have","has","had","for","not","you","your","they","them","their","about","over","under","then","than","its","yang","dan","atau","dari","pada","untuk","dengan","ini","itu","dalam","akan","telah","sudah","belum","bisa","dapat","adalah","oleh","karena","mereka","kita","kami","saya","dia","sebagai","lebih","saat","juga","tidak","ada","jadi","ke","di","an"}
def norm(s):
 s=unicodedata.normalize("NFKD",s or "").encode("ascii","ignore").decode().lower();return set(re.findall(r"[a-z0-9]{3,}",s))-STOP
def request(q):
 last=None
 for attempt in range(4):
  try:
   params={"action":"query","generator":"search","gsrsearch":q,"gsrnamespace":6,"gsrlimit":30,"prop":"imageinfo","iiprop":"url|extmetadata|size","format":"json"}
   req=urllib.request.Request(API+"?"+urllib.parse.urlencode(params),headers={"User-Agent":UA+" (github.com/renaldialviansyah-arch/MoneyPrinterTurbo)"})
   with urllib.request.urlopen(req,timeout=25) as r:return json.loads(r.read().decode())
  except Exception as e:
   last=e;time.sleep(1+attempt*2)
 raise last
def plain(x):return re.sub(r"<[^>]+>"," ",(x or {}).get("value","")).strip()
def candidates(q):
 pages=request(q).get("query",{}).get("pages",{}) or {};out=[];qw=norm(q)
 for page in pages.values():
  info=(page.get("imageinfo") or [{}])[0];m=info.get("extmetadata") or {};lic=plain(m.get("LicenseShortName"));url=info.get("url","")
  lic_norm=lic.strip().lower().replace(" ","")
  permitted=lic in PERMITTED or lic_norm in {"ccby4.0","ccby3.0","ccby2.0","ccby-sa4.0","ccby-sa3.0","ccby-sa2.0","cc0","publicdomain","publicdomainmark"}
  if not permitted or not url:continue
  ext=Path(urllib.parse.urlparse(url).path).suffix.lower()
  if ext not in (".jpg",".jpeg",".png",".webp") or int(info.get("size",0))<12000:continue
  title=page.get("title","");score=len(qw&norm(title))
  if score:out.append({"title":title,"url":url,"source":info.get("descriptionurl",""),"license":lic,"license_url":plain(m.get("LicenseUrl")),"artist":plain(m.get("Artist")),"credit":plain(m.get("Credit")),"attribution":plain(m.get("Attribution")),"ext":ext,"score":score,"size":int(info.get("size",0))})
 return sorted(out,key=lambda x:(x["score"],x["size"]),reverse=True)
def download(c,t):
 req=urllib.request.Request(c["url"],headers={"User-Agent":UA})
 with urllib.request.urlopen(req,timeout=40) as r:data=r.read()
 if len(data)<1200:raise ValueError("Download too small")
 t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(data);ff=shutil.which("ffmpeg")
 if ff:
  z=subprocess.run([ff,"-v","error","-i",str(t),"-frames:v","1","-f","null","-"],capture_output=True,text=True,timeout=30)
  if z.returncode:raise ValueError("Image validation: "+z.stderr[-300:])
 return len(data)
def fallback(s,t):
 from PIL import Image,ImageDraw,ImageFont
 t.parent.mkdir(parents=True,exist_ok=True);im=Image.new("RGB",(720,1280),(12,20,36));d=ImageDraw.Draw(im)
 for y in range(1280):
  k=y/1280;d.line((0,y,720,y),fill=(int(12+30*k),int(20+24*k),int(36+38*k)))
 d.ellipse((430,-100,900,380),fill=(48,68,100));d.ellipse((-240,750,500,1500),fill=(25,52,78))
 try:f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",32);sm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
 except Exception:f=sm=ImageFont.load_default()
 txt=re.sub(r"[^A-Za-z0-9 ,.:!?'-]","",str(s.get("visual_prompt") or s.get("narration") or s.get("search_terms") or "Visual scene"))[:150];lines=[]
 for w in txt.split():
  if not lines or len(lines[-1])+len(w)+1>28:lines.append(w)
  else:lines[-1]+=" "+w
 d.text((50,510),"VISUAL SCENE",font=sm,fill=(160,190,220))
 for i,l in enumerate(lines[:5]):d.text((50,570+i*50),l,font=f,fill=(245,248,255))
 d.text((50,1120),"Generated fallback • not a sourced photograph",font=sm,fill=(170,185,205));im.save(t,quality=90);return t.stat().st_size
def main():
 p=argparse.ArgumentParser();p.add_argument("--plan",required=True);p.add_argument("--out-dir",default="visuals");p.add_argument("--manifest",default="assets_local.json");p.add_argument("--report",default="asset_sources.json");p.add_argument("--max-attempts",type=int,default=15);p.add_argument("--allow-fallback",action="store_true");a=p.parse_args()
 scenes=json.loads(Path(a.plan).read_text(encoding="utf-8")).get("scenes")
 if not isinstance(scenes,list) or not scenes:p.error("Scene plan must contain scenes")
 out=Path(a.out_dir);assets=[];sources=[];fails=[];used=set();fc=0
 for n,s in enumerate(scenes,1):
  qs=[]
  for raw in [s.get("search_terms"),s.get("visual_prompt"),s.get("narration")]:
   q=str(raw or "").strip();q=re.sub(r"\\|.*$","",q).strip();q=re.sub(r"\\b(documentary cinematic photograph|specific documentary visual of)\\b","",q,flags=re.I).strip()
   if q and q not in qs:qs.append(q[:140])
  rawtext=str(s.get("search_terms") or s.get("visual_prompt") or s.get("narration") or "")
  words=[x for x in re.findall(r"[A-Za-z0-9]{3,}",rawtext) if x.lower() not in STOP]
  if words:
   qs.append(" ".join(words[:6]))
   if len(words)>=3:qs.append(" ".join(words[:3]))
  qs=list(dict.fromkeys(qs))[:6]
  opts=[]
  for q in qs[:5]:
   try:
    for c in candidates(q):
     if c["url"] not in used and all(x["url"]!=c["url"] for x in opts):opts.append(c)
   except Exception as e:fails.append({"scene":n,"query":q,"error":str(e)})
  opts.sort(key=lambda x:(x["score"],x["size"]),reverse=True);chosen=None
  for c in opts[:a.max_attempts]:
   t=out/f"scene{n:03}{c['ext']}"
   try:
    sz=download(c,t);used.add(c["url"]);chosen=c;notes="Attribution: "+(c["artist"] or c["credit"] or c["attribution"] or "not supplied")+" | "+c["license_url"]
    assets.append({"scene":n,"path":str(t.resolve()),"source":c["source"],"license":c["license"],"notes":notes,"title":c["title"],"bytes":sz});sources.append({"scene":n,**c,"download_bytes":sz});print("Selected",c["title"]);break
   except Exception as e:
    if t.exists():t.unlink()
    fails.append({"scene":n,"title":c["title"],"error":str(e)})
  if not chosen:
   fails.append({"scene":n,"error":"No matching permitted image","queries":qs})
   if a.allow_fallback:
    t=out/f"scene{n:03}_fallback.jpg";sz=fallback(s,t);fc+=1;assets.append({"scene":n,"path":str(t.resolve()),"source":"generated fallback graphic","license":"original generated graphic","notes":"Fallback card, not a photograph","title":"Generated scene card","bytes":sz})
  Path(a.manifest).parent.mkdir(parents=True,exist_ok=True);Path(a.manifest).write_text(json.dumps({"assets":assets},indent=2,ensure_ascii=False))
 status="PASS" if len(assets)==len(scenes) and fc==0 else ("DEGRADED" if a.allow_fallback and len(assets)==len(scenes) else "FAIL")
 Path(a.report).write_text(json.dumps({"sources":sources,"failures":fails,"scene_count":len(scenes),"asset_count":len(assets),"fallback_count":fc,"status":status,"notice":"Fallback cards are original graphics, not photos. Review sources/licenses."},indent=2,ensure_ascii=False))
 print(f"Scene assets: {len(assets)}/{len(scenes)}; fallback {fc}; {status}")
 return 0 if len(assets)==len(scenes) and (fc==0 or a.allow_fallback) else 2
if __name__=="__main__":raise SystemExit(main())
