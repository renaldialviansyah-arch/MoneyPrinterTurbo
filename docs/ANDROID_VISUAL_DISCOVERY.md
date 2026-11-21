# Wikimedia Commons Scene Discovery

Searches Wikimedia Commons using each scene's `search_terms`, then visual prompt or narration as a fallback. It produces candidate records with source pages and license/credit metadata; it does not download anything.

## Usage
```bash
python scripts/android_visual_discovery.py --plan scene_plan.json --out visual_candidates.json --manifest-out visual_urls_review.json
```

Review each candidate, source page, image and license. The generated manifest uses the first result as a convenience draft and is explicitly marked for review. It is not a vetted selection. No automated license clearance is provided. After reviewing and editing, pass the manifest to the fetcher. Some Wikimedia URLs may redirect or may not be accepted by the current fetcher; direct download compatibility remains to be tested.
