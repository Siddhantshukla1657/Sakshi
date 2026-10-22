"""Assemble the demo: crossfaded scenes, the narration placed per scene, captions from the voice's word timings,
and step chips on the app scenes. The last scene (the end slide) holds for END_HOLD seconds.

    python edit.py      -> Sakshi_demo.mp4 (captions burned in), Sakshi_demo_clean.mp4 (no captions), Sakshi_demo.srt
"""
import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
from script import END_HOLD, LEAD_IN, SCENES, TAIL

HERE = Path(__file__).parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
XFADE = 0.4
NAME = "Sakshi_demo"


def stamp(t, srt=False):
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def align(spoken, tokens):
    """Pair each spoken word with the script token it came from, so captions keep the script's punctuation."""
    words, j = [], 0
    for w in spoken:
        target = norm(w["text"])
        # one spoken word covering several script tokens ("in 2033,")
        acc, m = "", j
        while m < len(tokens) and len(acc) < len(target):
            acc += norm(tokens[m])
            m += 1
        if m - j > 1 and acc == target:
            words.append({"shown": " ".join(tokens[j:m]), "start": w["start"], "end": w["end"]})
            j = m
            continue
        k = j
        while k < len(tokens) and target and target not in norm(tokens[k]):
            k += 1
        if k < len(tokens):
            j = k
        shown = tokens[j] if j < len(tokens) else w["text"]
        if words and words[-1]["shown"] is shown:
            words[-1]["end"] = w["end"]  # one script token spoken as several words
            continue
        words.append({"shown": shown, "start": w["start"], "end": w["end"]})
        j += 1
    return words


def text_of(line):
    return " ".join(x["shown"] for x in line)


def wrap(words):
    """Split at punctuation first (clauses), then wrap long clauses into balanced lines of up to ~42 characters."""
    clauses, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[.,:;?]$", w["shown"]):
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    lines = []
    for clause in clauses:
        parts = max(1, -(-len(text_of(clause)) // 42))
        size = -(-len(clause) // parts)
        lines += [clause[k:k + size] for k in range(0, len(clause), size)]
    return lines


def join_short(lines):
    """Join a short one- or two-word line to its neighbour when the result still fits on one line."""
    forward, held = [], None
    for k, line in enumerate(lines):
        if held is not None:
            forward.append(held + line)
            held = None
            continue
        nxt = lines[k + 1] if k + 1 < len(lines) else None
        if len(line) <= 2 and nxt and len(text_of(line + nxt)) <= 46:
            held = line
        else:
            forward.append(line)
    merged = []
    for line in forward:
        if merged and len(line) <= 2 and len(text_of(merged[-1] + line)) <= 46:
            merged[-1] = merged[-1] + line
        else:
            merged.append(line)
    return merged


def captions_for(scene, offset):
    """The scene's caption lines as (start, end, text), timed to the voice."""
    data = json.loads((HERE / "audio" / f"{scene['id']}.json").read_text(encoding="utf8"))
    lines = join_short(wrap(align(data["words"], scene["say"].split())))
    out = []
    for i, line in enumerate(lines):
        start = offset + line[0]["start"]
        nxt = offset + lines[i + 1][0]["start"] if i + 1 < len(lines) else offset + line[-1]["end"] + .35
        out.append((start, min(nxt, offset + line[-1]["end"] + .6), text_of(line)))
    return out


ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Segoe UI,44,&H00FFFFFF,&H00FFFFFF,&H140D0D0D,&H140D0D0D,-1,0,0,0,100,100,0,0,3,14,0,2,160,160,34,1
Style: Chip,Segoe UI,30,&H000D0D0D,&H000D0D0D,&H0097DC3D,&H0097DC3D,-1,0,0,0,100,100,1,0,3,11,0,9,40,90,92,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main():
    lengths, starts, t = [], [], 0.0
    for i, scene in enumerate(SCENES):
        voice = json.loads((HERE / "audio" / f"{scene['id']}.json").read_text(encoding="utf8"))["duration"]
        length = LEAD_IN + voice + TAIL + (END_HOLD if i == len(SCENES) - 1 else 0)
        starts.append(t)
        lengths.append(length)
        t += length - XFADE
    total = starts[-1] + lengths[-1]

    # captions + chips
    events, srt = [], []
    for scene, start in zip(SCENES, starts, strict=True):
        for a, b, text in captions_for(scene, start + LEAD_IN):
            events.append(f"Dialogue: 0,{stamp(a)},{stamp(b)},Caption,,0,0,0,,{{\\fad(120,120)}}{text}")
            srt.append((a, b, text))
        if scene["chip"]:
            end = start + LEAD_IN + json.loads((HERE / "audio" / f"{scene['id']}.json").read_text(encoding="utf8"))["duration"] + TAIL
            events.append(f"Dialogue: 1,{stamp(start + .25)},{stamp(end - .2)},Chip,,0,0,0,,{{\\fad(250,200)}}{scene['chip']}")
    (HERE / "captions.ass").write_text(ASS_HEAD + "\n".join(events) + "\n", encoding="utf8")
    (HERE / f"{NAME}.srt").write_text("\n".join(f"{i}\n{stamp(a, True)} --> {stamp(b, True)}\n{text}\n"
                                               for i, (a, b, text) in enumerate(srt, 1)), encoding="utf8")

    # video: crossfade the scene clips
    inputs, vf = [], []
    for scene in SCENES:
        inputs += ["-i", str(HERE / "clips" / f"{scene['id']}.mp4")]
    n = len(SCENES)
    norm = "fps=30,format=yuv420p,setsar=1,settb=AVTB"  # xfade needs identical rate, format and timebase
    for i in range(n):
        vf.append(f"[{i}:v]{norm}[c{i}]")
    prev = "c0"
    for i in range(1, n):
        vf.append(f"[{prev}][c{i}]xfade=transition=fade:duration={XFADE}:offset={starts[i]:.3f}[v{i}]")
        prev = f"v{i}"
    vf.append(f"[{prev}]null[video]")

    # audio: each scene's voice at its start + lead-in
    for scene in SCENES:
        inputs += ["-i", str(HERE / "audio" / f"{scene['id']}.wav")]
    mix = []
    for i, start in enumerate(starts):
        ms = int((start + LEAD_IN) * 1000)
        vf.append(f"[{n + i}:a]adelay={ms}|{ms}[a{i}]")
        mix.append(f"[a{i}]")
    vf.append(f"{''.join(mix)}amix=inputs={n}:normalize=0:dropout_transition=0,apad=whole_dur={total:.3f},"
              f"loudnorm=I=-16:TP=-1.5:LRA=11[audio]")

    clean = HERE / f"{NAME}_clean.mp4"
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", *inputs, "-filter_complex", ";".join(vf),
                    "-map", "[video]", "-map", "[audio]", "-t", f"{total:.3f}", "-r", "30",
                    "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(clean)],
                   check=True, cwd=HERE)
    final = HERE / f"{NAME}.mp4"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", clean.name, "-vf", "ass=captions.ass",
                    "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy",
                    "-movflags", "+faststart", final.name], check=True, cwd=HERE)
    print(f"{final.name}: {total:.1f} s, {final.stat().st_size / 1e6:.1f} MB; also {clean.name} and {NAME}.srt")


if __name__ == "__main__":
    main()
