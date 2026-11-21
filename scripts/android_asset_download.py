#!/usr/bin/env python3
"""Download explicitly listed HTTPS assets from a manifest with size limits.

No scraping or search is performed. URLs must be supplied by the user.
"""
from __future__ import annotations
import argparse, json, mimetypes, urllib.parse, urllib.request, urllib.error
from pathlib import Path

MAX_DEFAULT_MB=100
EXTS={
 "visual":{".mp4",".mov",".mkv",".webm",".jpg",".jpeg",".png",".webp"},
 "audio":{".mp3",".wav",".m4a",".aac",".ogg"},
 "subtitle":{".srt",".vtt"},
}

def validate_url(url:str)->str:
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!="https" or not parsed.hostname:
        raise ValueError("Only valid HTTPS URLs are accepted.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are rejected.")
    return url

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest")
    p.add_argument("--output-dir",default="assets_downloaded")
    p.add_argument("--max-mb",type=int,default=MAX_DEFAULT_MB)
    args=p.parse_args()
    if args.max_mb<=0: p.error("--max-mb must be positive")
    manifest=Path(args.manifest).expanduser().resolve()
    data=json.loads(manifest.read_text(encoding="utf-8"))
    assets=data.get("assets",[])
    outdir=Path(args.output_dir).expanduser().resolve()
    outdir.mkdir(parents=True,exist_ok=True)
    limit=args.max_mb*1024*1024
    downloaded=[]
    for i,item in enumerate(assets):
        url=item.get("url")
        role=item.get("role")
        if not url: continue
        if role not in EXTS: raise ValueError(f"Asset {i}: invalid role")
        validate_url(url)
        parsed=urllib.parse.urlparse(url)
        ext=Path(parsed.path).suffix.lower()
        if ext not in EXTS[role]:
            raise ValueError(f"Asset {i}: URL extension {ext!r} not allowed for {role}")
        filename=item.get("filename") or f"asset_{i+1}{ext}"
        dest=outdir/filename
        if dest.parent!=outdir:
            raise ValueError("filename must not contain directories")
        req=urllib.request.Request(url,headers={"User-Agent":"MoneyPrinterTurbo-MobileAsset/0.1"})
        with urllib.request.urlopen(req,timeout=20) as response:
            final_url=response.geturl()
            validate_url(final_url)
            content_length=response.headers.get("Content-Length")
            if content_length and int(content_length)>limit:
                raise ValueError(f"Asset {i}: exceeds maximum size")
            content_type=response.headers.get("Content-Type","").split(";")[0].lower()
            if content_type.startswith("text/html"):
                raise ValueError(f"Asset {i}: received HTML, not media")
            total=0
            with dest.open("wb") as f:
                while True:
                    chunk=response.read(1024*1024)
                    if not chunk: break
                    total+=len(chunk)
                    if total>limit:
                        f.close()
                        dest.unlink(missing_ok=True)
                        raise ValueError(f"Asset {i}: download exceeds size limit")
                    f.write(chunk)
        downloaded.append({"role":role,"url":url,"path":str(dest),"bytes":total})
        print(f"Downloaded {role}: {dest} ({total} bytes)")
    print(json.dumps({"downloaded":downloaded},indent=2))
if __name__=="__main__": main()
