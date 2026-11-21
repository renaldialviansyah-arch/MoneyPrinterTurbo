#!/usr/bin/env python3
"""Fetch explicitly supplied scene asset URLs. No scraping; redirects blocked."""
from __future__ import annotations
import argparse,json,ipaddress,socket,sys,urllib.request,urllib.parse
from pathlib import Path
MAX_BYTES=30*1024*1024
EXT={".jpg",".jpeg",".png",".webp",".bmp",".mp4",".mov",".mkv",".webm"}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl): return None
def safe_url(url,allow_http=False):
 u=urllib.parse.urlparse(url)
 if u.scheme not in ({"https","http"} if allow_http else {"https"}): raise ValueError("Only HTTPS URLs are allowed (HTTP requires --allow-http)")
 if not u.hostname or u.username or u.password: raise ValueError("URL must have a host and no embedded credentials")
 host=u.hostname.lower()
 if host in {"localhost","localhost.localdomain"} or host.endswith(".local"): raise ValueError("Local hostnames are blocked")
 try:
  ips=[ipaddress.ip_address(x[4][0]) for x in socket.getaddrinfo(host,None)]
  if not ips or any(not ip.is_global for ip in ips): raise ValueError("Non-public IP address blocked")
 except socket.gaierror as e: raise ValueError("Host resolution failed") from e
 return u
def fetch(url,dest,allow_http=False):
 u=safe_url(url,allow_http)
 req=urllib.request.Request(url,headers={"User-Agent":"AndroidVisualAssetFetcher/1.0"})
 opener=urllib.request.build_opener(NoRedirect())
 with opener.open(req,timeout=20) as res:
  typ=res.headers.get("Content-Type","").split(";")[0].lower()
  if typ not in {"image/jpeg","image/png","image/webp","image/bmp","video/mp4","video/quicktime","video/x-matroska","video/webm","application/octet-stream"}: raise ValueError("Unexpected content type: "+typ)
  data=res.read(MAX_BYTES+1)
  if len(data)>MAX_BYTES: raise ValueError("Asset exceeds 30 MB limit")
  if len(data)<128: raise ValueError("Downloaded asset is suspiciously small")
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 return {"url":url,"path":str(dest),"content_type":typ,"bytes":len(data)}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--manifest",required=True);p.add_argument("--out-dir",default="visuals");p.add_argument("--metadata-out",default="downloaded_visuals.json");p.add_argument("--allow-http",action="store_true");a=p.parse_args()
 mp=Path(a.manifest).resolve();m=json.loads(mp.read_text(encoding="utf-8"));entries=m.get("assets") if isinstance(m,dict) else None
 if not isinstance(entries,list) or not entries: print("Manifest must have a non-empty assets list",file=sys.stderr);return 2
 out=Path(a.out_dir).expanduser().resolve();records=[];seen=set()
 try:
  for e in entries:
   n=int(e["scene"]);url=str(e["url"]);ext=Path(urllib.parse.urlparse(url).path).suffix.lower()
   if n<1 or n in seen: raise ValueError("Scene numbers must be positive and unique")
   if ext not in EXT: raise ValueError("URL path extension unsupported for scene "+str(n))
   seen.add(n);dest=out/f"scene{n:03}{ext}"
   records.append({"scene":n,**fetch(url,dest,a.allow_http),"source":e.get("source",url),"license":e.get("license","unspecified"),"notes":e.get("notes","")})
  records.sort(key=lambda x:x["scene"])
  Path(a.metadata_out).write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding="utf-8")
  print("Downloaded",len(records),"assets. Metadata:",a.metadata_out)
 except Exception as e: print("ERROR:",e,file=sys.stderr);return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
