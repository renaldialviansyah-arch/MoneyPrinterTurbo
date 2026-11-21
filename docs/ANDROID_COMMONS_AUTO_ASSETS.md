# Automatic Commons visual acquisition

This helper searches Wikimedia Commons for each scene, filters candidates to a defined license allow-list, attempts bounded downloads via the validated downloader, and writes a local asset manifest plus attribution/source report. It does not guarantee image relevance or license suitability; review source pages and attribution before publishing.

Example: `python scripts/android_commons_auto_assets.py --plan production/work/plan_aligned.json --out-dir production/visuals --manifest production/work/assets_local.json --report production/work/asset_sources.json`

Requires internet access. The Commons search API and image hosts may fail; unresolved scenes are reported and the script exits nonzero. Only a subset of common licenses is allow-listed. License metadata may be incomplete or inconsistent and needs review.
