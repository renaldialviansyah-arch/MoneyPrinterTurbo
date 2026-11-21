# Piper Neural TTS
Piper is a VITS-based local neural speech synthesizer and typically sounds more natural than classic formant synthesis (such as eSpeak), though voice quality varies by model. It is offline after install/model download.
Install: `pip install piper-tts` (environment compatibility varies). Download a voice model `.onnx` and matching `.onnx.json` from an official voice repository; inspect the model's license.
Usage: `python scripts/android_tts_piper.py --text narration.txt --model voices/en_US-lessac-medium.onnx --output voice.wav`
Adjust length scale, noise scale, noise width, and sentence silence. Test voices before production; model size, platform, and quality are voice-specific.
