# Unified Production Pipeline (offline/local assets)
This command-line orchestrator runs three existing project modules in sequence:
1. Scene planning from a narration/script text file.
2. Local scene asset resolution from a reviewed manifest.
3. Portrait MP4 rendering with renderer v4.

## Inputs
- script text file
- audio file
- reviewed JSON asset manifest with one local path per scene, e.g.:
```json
{"assets":[{"scene":1,"path":"../media/scene1.jpg","source":"source page","license":"reviewed license"},{"scene":2,"path":"../media/scene2.jpg","source":"source page","license":"reviewed license"}]}
```
Paths in the manifest are relative to the manifest file. Scene numbers must cover the generated scene plan.
Optional SRT subtitle.

## Run
```bash
python scripts/android_production_pipeline.py --script examples/narration.txt --manifest examples/assets_manifest.json --audio narration.mp3 --subtitle subtitles.srt --output output/final.mp4
```
Options: `--wpm`, `--width`, `--height`, `--fps`, `--work-dir`.

## Output artifacts
The work directory retains scene plan, resolved assets list, asset metadata, render segments, and pipeline report.
The manifest must use local paths. Discovery results are candidates only; review the source and licensing before downloading or using media. This orchestrator does not fetch URLs or synthesize narration.

## Failure behavior
A failed stage stops the pipeline and reports the stage. Intermediate files remain for debugging. This orchestrator checks final output existence and size, not perceptual quality; manually review the MP4.
