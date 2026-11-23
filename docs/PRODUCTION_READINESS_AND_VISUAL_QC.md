# Production readiness: visual acquisition and QC

## Recent hardening
- Commons visual acquisition runs several scene queries, filters to an allowlist of licenses, filters out tiny files, scores candidate relevance, and validates downloaded media.
- Normal production mode does not substitute geometric fallback cards when acquisition fails; the job fails and reports missing scene assets.
- Final video QC checks streams, subtitle presence, resolution, duration, and the external-source manifest.
- Assets must have an HTTP source URL and must not be marked as fallback/generated graphics.

## Run the readiness test
1. Open GitHub Actions in the repository.
2. Select **Production Readiness Test (Visual + Render + QC)** on the main branch.
3. Select Run workflow.
4. Inspect the job result and download the `production-readiness-result` artifact if it is created.

The readiness test uses a short English script, eSpeak, Wikimedia Commons retrieval, FFmpeg rendering, and final QC. It is a diagnostic end-to-end test; a pass does not guarantee all subjects or languages will retrieve equally relevant imagery.

## Production workflow
The AI Video Production workflow checks out the `android-mobile-work` branch. Production videos are only considered successful if all pipeline stages and final QC pass. Review asset attribution and license terms before publication.
