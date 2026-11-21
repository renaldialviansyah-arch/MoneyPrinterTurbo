# Android Scene Planner

Dependency-free script-to-scene planning helper. It creates a JSON plan with narration, estimated duration, shot type, visual prompt, camera motion prompt, transition hint, and subtitle text.

```sh
python scripts/android_scene_planner.py narration.txt --out project/scene_plan.json
```

Duration is a rough word-rate estimate, not audio timing. Visual prompts are drafts; this module does not generate or download media.
