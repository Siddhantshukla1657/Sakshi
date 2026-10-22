"""Generate each scene's narration with word timings: audio/<id>.wav and audio/<id>.json.

    python tts.py                # every scene
    python tts.py e1_end         # only these
"""
import asyncio
import json
import subprocess
import sys
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg

from script import RATE, SCENES, VOICE

OUT = Path(__file__).parent / "audio"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


async def stream(text):
    """The voice for text, as mp3 bytes, plus when each word is spoken."""
    audio, words = bytearray(), []
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
        elif chunk["type"] == "WordBoundary":  # offsets are in 100 ns units
            words.append({"text": chunk["text"], "start": chunk["offset"] / 1e7,
                          "end": (chunk["offset"] + chunk["duration"]) / 1e7})
    return bytes(audio), words


def synth(scene):
    audio, words = asyncio.run(stream(scene["say"]))
    mp3, wav = OUT / f"{scene['id']}.mp3", OUT / f"{scene['id']}.wav"
    mp3.write_bytes(audio)
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "48000", "-ac", "2", str(wav)], check=True)
    with wave.open(str(wav)) as w:
        duration = w.getnframes() / w.getframerate()
    (OUT / f"{scene['id']}.json").write_text(json.dumps({"duration": duration, "words": words}, indent=1), encoding="utf8")
    return duration, len(words)


def main(wanted):
    OUT.mkdir(exist_ok=True)
    total = 0
    for scene in SCENES:
        if wanted and scene["id"] not in wanted:
            continue
        duration, n = synth(scene)
        total += duration
        print(f"{scene['id']:12s} {duration:5.1f} s  {n} words")
    print(f"total voice {total:.1f} s")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
