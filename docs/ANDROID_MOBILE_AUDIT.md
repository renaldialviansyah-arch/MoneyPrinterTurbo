# Android / Termux Compatibility Audit

**Repository:** `renaldialviansyah-arch/MoneyPrinterTurbo`  
**Audit branch:** `android-mobile-work`  
**Upstream version observed:** 1.3.10  
**Audit status:** Static repository review only; no Android runtime or dependency installation tests performed.

## Executive assessment

MoneyPrinterTurbo is a relatively mature, multi-entry-point Python application for automated short-video production. It is not currently an Android/Termux-ready package. A mobile port should be treated as a separate runtime profile, with selective dependencies and an adapted rendering pipeline, rather than attempting to install the full upstream stack on Android.

## Architecture

- **Web UI:** Streamlit in `webui/Main.py`; large, feature-rich UI.
- **API:** FastAPI/ASGI in `app/asgi.py`, routes/controllers in `app/router.py` and `app/controllers/v1`.
- **Task orchestration:** `app/services/task.py`; task/state/progress and publishing orchestration.
- **Media acquisition:** `app/services/material.py` plus provider modules for stock footage and generated media.
- **Voice/audio:** `app/services/voice.py`, background music modules and provider integrations.
- **Subtitles:** `app/services/subtitle.py`, subtitle reader/writer/shaping utilities.
- **Rendering:** `app/services/video.py`, MoviePy and subprocess/FFmpeg paths.
- **Configuration/storage:** `app/config/config.py`, `app/paths.py`, configuration template and persistent storage paths.
- **Interfaces:** WebUI, API and CLI (`cli.py`, launcher).
- **Cross-posting:** task orchestration and platform publishing integrations.

## Video pipeline (static code review)

The task service coordinates multiple stages and providers. The CLI describes stages as script, terms, audio, subtitle, materials, and video; local-material workflows can bypass term generation. Rendering in the video service uses MoviePy clips/compositing, Pillow for image/subtitle handling, NumPy, and FFmpeg subprocess operations. The renderer supports video/image materials, transitions/effects, audio mixing, subtitle overlays and output encoding. Code also contains codec fallback/runtime-disable logic and heartbeat/timeout behavior around FFmpeg work.

## Audio and narration

The voice module supports multiple provider integrations, including Edge TTS and configured API-based providers. Audio handling and conversion may invoke FFmpeg. The default Edge TTS path depends on remote network access and should not be represented as offline. An Android profile should initially support either a simple remote TTS path or user-supplied narration, not every provider.

Background music supports built-in/custom and provider-generated paths. Uploaded music is persisted under storage. Audio mixing and format conversion require compatible FFmpeg binaries/codecs.

## Subtitle pipeline

Subtitle generation may use Faster-Whisper with a configurable model/device/compute type. Model loading and inference are significant resource operations. Subtitle rendering also involves Pillow, shaping libraries and MoviePy. Word-level timing and visual animation add CPU and memory cost. For mobile, use pre-generated SRT/VTT or cloud speech recognition as an initial profile; local Whisper should be optional and independently tested.

## Dependencies and runtime assumptions

Declared project dependencies include Python 3.11+, MoviePy 2.2.1, Streamlit, FastAPI, Uvicorn, OpenAI SDK, Faster-Whisper, PyAV constrained below 19, imageio-ffmpeg, Pillow override, Pydub, Edge TTS, Redis, LiteLLM, Google GenAI, Azure Speech SDK, Dashscope, Khatt video shaping, and other utilities.

Some packages include native binaries, compiled extensions or platform-specific wheels. Android/Termux availability cannot be inferred from the Linux/Windows/macOS packaging or Docker setup.

## Android/Termux compatibility risks

### High risk / blockers to investigate
1. **Python/native wheels:** PyAV, CTranslate2/Faster-Whisper, Pillow, audioop compatibility, shaping libraries, and SDKs may not have compatible Android wheels; source builds can be complex.
2. **FFmpeg:** Android FFmpeg availability, codec build options, executable path discovery, and MoviePy subprocess behavior must be tested. imageio-ffmpeg bundled binaries may not be Android-compatible.
3. **Docker:** The upstream Dockerfile uses Debian apt installation and container assumptions. Docker is not a typical Android/Termux runtime.
4. **Redis:** Task manager/config may depend on Redis. Redis server availability and process/service behavior in Android need evaluation; an initial mobile profile should avoid it if possible.
5. **Whisper:** Faster-Whisper/CTranslate2 model loading and inference may be impractical on constrained ARM Android devices; model download/storage and RAM pressure are major concerns.
6. **Background execution:** Android may suspend/kill long-running Termux processes, especially when app is backgrounded, battery optimization is active or device is thermally constrained.
7. **RAM/thermal:** Rendering multiple clips, MoviePy frame arrays, subtitle layers, image decoding and Whisper can create peaks in memory/CPU usage.
8. **Filesystem permissions:** Storage paths and access to shared Android storage need explicit handling and permission setup.
9. **Provider integrations:** API credentials, provider SDKs, network reliability, usage costs and rate limits remain external dependencies.
10. **UI/network:** Streamlit local hosting and browser access on localhost need testing; binding to network interfaces should be carefully controlled.

## Recommended mobile adaptation

### Phase 0 — Do not port the full application
Maintain the upstream fork and isolate mobile-specific changes. Do not make broad changes to the production pipeline until a minimal path is proven.

### Phase 1 — Minimal mobile profile
- CLI-first workflow; avoid full WebUI at first.
- No Redis dependency for single-user jobs; replace or isolate task management if feasible.
- Use local input media or one compatible media-search provider.
- Use remote TTS or uploaded narration.
- Use pre-generated subtitles initially; optional transcription later.
- Keep MoviePy/FFmpeg rendering as the first major compatibility experiment.
- Disable cross-posting, advanced generated-media providers, GPU features and Whisper by default.
- One rendering worker and conservative resolution/bitrate presets.

### Phase 2 — Rendering proof of concept
Test, on actual Android/Termux:
- FFmpeg binary and codec availability.
- Python import/installation viability for MoviePy, NumPy and Pillow.
- A tiny local clip + image + audio + subtitle composition.
- H.264/AAC MP4 output, portrait dimensions and audio/video duration alignment.
- File paths and output storage.
- Memory/time/thermal behavior.

### Phase 3 — Mobile user interface
Only after the render test passes, consider a lightweight local WebUI or browser UI. Streamlit is not automatically ruled out, but it is not the first compatibility target.

### Phase 4 — Gradual feature additions
Add material providers, TTS provider selection, subtitles, music, and automation incrementally, each with isolated tests and clear API/cost disclosure.

## Suggested first technical experiment

A standalone minimal render test—not the entire MoneyPrinterTurbo stack—should use:
1. One local MP4 clip or static image.
2. One short local WAV/MP3 narration.
3. One SRT subtitle.
4. FFmpeg and MoviePy/Pillow only as needed.
5. Output: 720x1280 or lower, H.264/AAC MP4.

Record install outcome, runtime, peak memory if measurable, output playback and errors. This test is a prerequisite before committing to a full Android port.

## Audit limitations

This audit is based on static inspection of repository files and configuration. No packages were installed, no unit tests were run, no Android device runtime was exercised, no rendering output was produced, and compatibility claims remain unverified.
