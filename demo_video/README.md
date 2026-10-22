# Sakshi demo video

Watch it on YouTube: https://youtu.be/uOjglE-VGdg

| File | What it is |
|:---|:---|
| `Sakshi_demo.mp4` | The demo, 1920x1080, 4 min 48 s, captions burned in |
| `Sakshi_demo_clean.mp4` | The same video without captions |
| `Sakshi_demo.srt` | Captions as a separate file |
| `script.md` | The narration script, scene by scene |
| `youtube_description.txt` | YouTube description with chapter timestamps |

## How it was made

The video is generated from code, so it can be re-made after the app changes.

- `script.py` holds the scenes: narration, on-screen step label, and the cue words that build each slide.
- `tts.py` voices each scene with edge-tts (`en-US-AndrewMultilingualNeural`) and saves the word timings.
- `record.py` drives the running app with Playwright and records it through Chrome's screencast, timing every click and message to the narration. Slides come from `slides.html`.
- `edit.py` crossfades the scenes, lays the voice under them, and burns in captions (`captions.ass`) grouped from the word timings.

To rebuild:

```bash
pip install edge-tts playwright imageio-ffmpeg
python -m playwright install chromium
python tts.py
python record.py
python edit.py
```

Before `record.py`, start the backend fresh (the trace history lives in memory) and the frontend with
`VITE_API_BASE=http://127.0.0.1:8000`, so the live trace panel connects straight to the backend.
