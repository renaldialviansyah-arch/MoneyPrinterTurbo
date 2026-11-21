#!/usr/bin/env python3
"""Safe asset downloader with bounded, validated public HTTPS redirects."""
import argparse,json,ipaddress,socket,urllib.parse,urllib.request,sys
from pathlib import Path
MAX_BYTES=30*1024*1024
ALLOWED={"image/jpeg","image/png","image/webp","image/bmp","video/mp4","video/quicktime","video/x-matroska","video/webm","application/octet-stream"}
EXT={".jpg",".jpeg",".png",".webp",".bmp",".mp4",".mov",".mkv",".webm"}
def validate(url):
 u=urllib.parse.urlparse(url)
 if u.scheme!="https" or not u.hostname or u.username or u.password:raise ValueError("Only credential-free HTTPS URLs permitted")
 h=u.hostname.lower()
 if h=="localhost" or h.endswith(".local"):raise ValueError("Local hostnames blocked")
 ips=[ipaddress.ip_address(x[4][0]) for x in socket.getaddrinfo(h,None)]
 if not ips or any(not ip.is_global for ip in ips):raise ValueError("Non-public address blocked")
 return url
class SafeRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  validate(newurl)
  if code not in (301,302,303,307,308):return None
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def download(url,dest):
 validate(url);opener=urllib.request.build_opener(SafeRedirect())
 req=urllib.request.Request(url,headers={"User-Agent":"AndroidVisualFetchSafe/2.0"})
 with opener.open(req,timeout=25) as r:
  typ=r.headers.get("Content-Type","").split(";")[0].lower()
  if typ not in ALLOWED:raise ValueError("Unsupported media type: "+typ)
  data=r.read(MAX_BYTES+1)
 if len(data)>MAX_BYTES:raise ValueError("Over 30 MB limit")
 if len(data)<128:raise ValueError("Asset too small")
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 return {"url":url,"final_url":r.geturl(),"path":str(dest),"content_type":typ,"bytes":len(data)}
def main():
 p=argparse.ArgumentParser();p.add_argument("--manifest",required=True);p.add_argument("--out-dir",default="visuals");p.add_argument("--metadata-out",default="downloaded_visuals.json");a=p.parse_args()
 m=json.loads(Path(a.manifest).read_text(encoding="utf-8"));entries=m.get("assets") if isinstance(m,dict) else None
 if not isinstance(entries,list) or not entries:p.error("Manifest requires non-empty assets list")
 out=Path(a.out_dir).resolve();seen=set();records=[]
 try:
  for e in entries:
   n=int(e["scene"]);url=str(e["url"]);ext=Path(urllib.parse.urlparse(url).path).suffix.lower()
   if n<1 or n in seen:raise ValueError("Scene numbers must be positive and unique")
   if ext not in EXT:raise ValueError(f"Unsupported extension for scene {n}: {ext}")
   seen.add(n);dest=out/f"scene{n:03}{ext}"
   records.append({"scene":n,**download(url,dest),"source":e.get("source",url),"license":e.get("license","unknown"),"notes":e.get("notes","")})
  records.sort(key=lambda x:x["scene"]);Path(a.metadata_out).write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8");print("Downloaded",len(records),"assets")
 except Exception as e:print("ERROR:",e,file=sys.stderr);return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
