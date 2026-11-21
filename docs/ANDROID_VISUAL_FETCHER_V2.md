# Safe Visual Fetcher v2
This version allows validated public HTTPS redirects (needed by some media hosts) while validating each redirect destination. It rejects embedded credentials, local names, non-public IP addresses, unexpected MIME types, files over 30 MB, and suspiciously small downloads. Redirect/DNS validation is best-effort and cannot eliminate DNS rebinding race conditions. Use only reviewed URLs and source/license metadata.
Usage: `python scripts/android_visual_fetcher_v2.py --manifest visual_urls_review.json --out-dir visuals --metadata-out downloaded_visuals.json`
