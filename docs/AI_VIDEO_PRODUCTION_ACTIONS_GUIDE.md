# AI Video Production via GitHub Actions

This guide runs the v8 video pipeline from GitHub Actions without Termux.

## Start a production run

1. Open the repository Actions page: https://github.com/renaldialviansyah-arch/MoneyPrinterTurbo/actions
2. Select **AI Video Production (Manual Trigger)** in the workflow list.
3. Choose **Run workflow** and branch **android-mobile-work**.
4. Paste your narration script into the script field.
5. Supply direct HTTPS links to a Piper ONNX voice model and its matching JSON config.
   - The model and config must be a matching pair and the model should support the language of your script.
   - Do not use untrusted model download links.
6. Set a simple output name ending in `.mp4` (for example `final.mp4`).
7. Run the workflow. Follow its job log for errors.
8. When complete, open the successful run and download the **AI-video-output** artifact.

## Production defaults

- Portrait: 720 x 1280
- 24 FPS
- Subtle camera motion
- Scene planning and narration alignment
- Automatic Wikimedia Commons visual acquisition
- Piper neural narration
- Subtitle generation
- FFmpeg render and QC
- MP4 plus QC and asset-source reports packaged as an artifact

## Important limitations

- This workflow has not yet been proven end-to-end with a real voice model and real Wikimedia downloads. A successful synthetic smoke test is not equivalent to full production validation.
- Wikimedia images have attribution/license obligations depending on the individual file. Review the asset-source report and licenses before publishing.
- Public GitHub Actions runners have time and storage limits; large voice models or long scripts may need shorter content.
- Artifacts are retained for seven days by this workflow.

## Troubleshooting

- If voice synthesis fails, verify the model and config URLs are direct, accessible HTTPS links, and are a matching Piper pair.
- If visual acquisition fails, check the Commons search/download step logs.
- If render or QC fails, inspect `production/work/qc.json`, `pipeline_report.json`, and the Actions log.
