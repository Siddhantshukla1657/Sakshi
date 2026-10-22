"""Generate each scene's narration with word timings: audio/<id>.wav and audio/<id>.json."""
import asyncio
import json
import subprocess
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg

from script import RATE, SCENES, VOICE

OUT = Path(__file__).parent / "audio"
OUT.mkdir(exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


async def synth(scene):
    mp3, words = OUT / f"{scene['id']}.mp3", []
    comm = edge_tts.Communicate(scene["say"], VOICE, rate=RATE, boundary="WordBoundary")
    with open(mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":  # offsets are in 100 ns units
                words.append({"text": chunk["text"], "start": chunk["offset"] / 1e7,
                              "end": (chunk["offset"] + chunk["duration"]) / 1e7})
    wav = OUT / f"{scene['id']}.wav"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "48000", "-ac", "2", str(wav)], check=True)
    with wave.open(str(wav)) as w:
        duration = w.getnframes() / w.getframerate()
    (OUT / f"{scene['id']}.json").write_text(json.dumps({"duration": duration, "words": words}, indent=1), encoding="utf8")
    return scene["id"], duration, len(words)


async def main():
    total = 0
    import sys
    wanted = set(sys.argv[1:])
    for scene in SCENES:
        if wanted and scene["id"] not in wanted:
            continue
        sid, dur, n = await synth(scene)
        total += dur
        print(f"{sid:12s} {dur:5.1f} s  {n} words")
    print(f"total voice {total:.1f} s")


asyncio.run(main())
