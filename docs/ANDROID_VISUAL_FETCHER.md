# Android Visual Acquisition (explicit URL fetcher)

This helper downloads scene assets only from URLs explicitly provided by the user in a JSON manifest. It does not search, scrape websites, or follow redirects.

## Manifest
```json
{ "assets": [
 { "scene": 1, "url": "https://example.org/image.jpg", "source": "provider/page", "license": "check license", "notes": "" }
] }
```

## Run
```bash
python scripts/android_visual_fetcher.py --manifest visual_urls.json --out-dir visuals --metadata-out downloaded_visuals.json
```
Then make a resolver manifest using downloaded file paths. URLs must be HTTPS unless `--allow-http` is explicitly supplied. The tool blocks local hostnames/private/non-public IPs, embedded credentials, redirects, unsupported extensions/content types, and files over 30 MB. Network validation is best-effort and not a substitute for careful trusted sources. Confirm rights and terms; license fields are metadata only. Downloaded visuals should be inspected before rendering.
