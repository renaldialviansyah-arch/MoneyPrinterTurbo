# Android Storyboard Builder

The dependency-free `scripts/android_storyboard_builder.py` converts a user-provided narration text file into:
- a JSON storyboard, one sentence per scene, with narration and a starter visual prompt;
- an SRT subtitle draft with approximate timing.

## Usage
```bash
python scripts/android_storyboard_builder.py narration.txt --out output/storyboard --seconds 5.5
```
Creates `output/storyboard.json` and `output/storyboard.srt`. Ensure the output directory exists first.

This tool does not generate narration, AI imagery, or video footage. Timing is estimated per sentence; revise timings and scene prompts before production. Experimental; not yet tested on Android.
