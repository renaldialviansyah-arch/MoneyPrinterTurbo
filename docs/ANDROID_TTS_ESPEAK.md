# Offline Narration Engine
Uses eSpeak/eSpeak NG locally with no API key or internet access. This produces WAV audio, suitable as pipeline narration input; voice quality is synthetic/robotic and multilingual voice availability depends on installation.
Usage:
```
python scripts/android_tts_espeak.py --text narration.txt --output voice.wav --voice en-us --speed 150
```
For Indonesian, try `--voice id` if installed; confirm available voices with `espeak --voices` or `espeak-ng --voices`. This is a free offline fallback, not neural-quality TTS.
