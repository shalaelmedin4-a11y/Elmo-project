#!/usr/bin/env python3
"""Narration + timeline for 'Ein Tag als Profifußballer … mit Halbo!'.

Every scene has a minimum length (from the brief). The phrases of a scene are
placed one after another with relaxed pauses; if they need more room the scene
gets longer. Result (build/fb_timeline.json) drives picture, lip-sync and music.

Phrases live in fussball/voice/cue_XX.wav. Missing ones are generated with a
neural German voice; record your own takes with the same names to replace them.
"""
import json
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "cartoon"))
import voice as V  # noqa: E402  (TTS + loading helpers)

V.VOICE = "de-DE-FlorianMultilingualNeural"   # young male voice
VDIR = os.path.join(HERE, "voice")
SR, FPS = V.SR, 12

# scene: (name, minimum length, clock, [(text, rate, pitch, breath)])
# scene: (name, minimum length, clock, [(text, rate, pitch, breath[, fixed local start])])
SCENES = [
    ("intro", 4.0, None, [("Ein Tag als Profifußballer …", "+2%", "+6Hz", False),
                          ("mit Halbo!", "+0%", "+10Hz", False)]),
    ("wake", 5.0, "06:30", [("Halb sieben.", "-4%", "+2Hz", True),
                            ("Der Wecker klingelt.", "-2%", "+2Hz", False)]),
    ("breakfast", 5.5, "07:30", [("Frühstück: Haferflocken, Obst, Eier.", "+0%", "+2Hz", True),
                                 ("Und ein Kaffee.", "-4%", "+2Hz", False)]),
    ("training", 5.5, "09:30", [("Training.", "+0%", "+4Hz", True),
                                ("Sprints, Flanken, Zweikämpfe.", "+2%", "+4Hz", False)]),
    ("canteen", 5.0, "12:00", [("Mittag in der Kantine.", "+0%", "+2Hz", True),
                               ("Reis, Hähnchen, Gemüse.", "+0%", "+2Hz", False)]),
    ("home", 5.0, "14:00", [("Mittagsruhe.", "-4%", "+0Hz", True),
                            ("Kurz zocken, dann schlafen.", "-2%", "+2Hz", False)]),
    ("drive", 5.0, "17:00", [("Ab ins Stadion.", "+2%", "+4Hz", True),
                             ("Kopfhörer auf, Fokus an.", "+0%", "+2Hz", False)]),
    ("match", 13.0, "19:30", [("Anpfiff!", "+0%", "+6Hz", False, 0.3),
                              ("Toooor!", "-35%", "+30Hz", True, 9.4)]),
    ("night", 6.0, "22:30", [("Eisbad. Kalt, aber es hilft.", "-4%", "+0Hz", True),
                             ("Gute Nacht.", "-8%", "+0Hz", False)]),
]
LEAD, GAP, TAIL = 0.35, 0.4, 0.5
INTRO_STARTS = [0.3, 2.6]          # intro phrases are tied to the signs


def main():
    force = "--tts" in sys.argv
    os.makedirs(VDIR, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    clips, i = [], 0
    for name, _, _, lines in SCENES:
        for text, rate, pitch, br, *_ in lines:
            wav = os.path.join(VDIR, f"cue_{i:02d}.wav")
            if force or not os.path.exists(wav):
                mp3 = os.path.join(ROOT, "build", f"fb_cue_{i:02d}.mp3")
                print(f"TTS {i:02d}: {text}")
                V.tts(text, rate, pitch, mp3)
                import subprocess
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", str(SR), "-ac", "1", wav], check=True)
            x = V.load(wav)
            clips.append((name, text, br, x / (np.max(np.abs(x)) + 1e-9) * 0.8))
            i += 1
    # layout
    scenes, cues, t, k = [], [], 0.0, 0
    for name, min_len, clock, lines in SCENES:
        start = t
        cur = start + LEAD
        local = []
        for j in range(len(lines)):
            _, text, br, x = clips[k]
            if name == "intro":
                cur = max(cur, INTRO_STARTS[j])
            if len(lines[j]) > 4:
                cur = start + lines[j][4]
            d = len(x) / SR
            cues.append(dict(start=round(cur, 3), end=round(cur + d, 3), text=text, scene=name, breath=br, idx=k))
            local.append([round(cur - start, 3), round(cur + d - start, 3)])
            cur += d + GAP
            k += 1
        end = max(start + min_len, cur - GAP + TAIL)
        scenes.append(dict(name=name, start=round(start, 3), end=round(end, 3), clock=clock, cues=local))
        t = end
    dur = round(t, 3)
    track = np.zeros(int(dur * SR) + SR, np.float32)
    rng = np.random.default_rng(9)
    for cu in cues:
        x = clips[cu["idx"]][3]
        a = int(cu["start"] * SR)
        if cu["breath"]:
            b = V.breath(rng) * 0.04
            s0 = max(0, a - len(b) - int(0.05 * SR))
            track[s0:s0 + len(b)] += b
        track[a:a + len(x)] += x
    track = track[: int(dur * SR)]
    hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(track[f * hop:(f + 1) * hop] ** 2)) for f in range(int(dur * FPS))])
    lvl = np.clip(rms / (np.percentile(rms[rms > 1e-3], 90) + 1e-9), 0, 1)
    with open(os.path.join(ROOT, "build", "fb_timeline.json"), "w") as fh:
        json.dump(dict(dur=dur, fps=FPS, scenes=scenes, cues=cues, level=[round(float(v), 3) for v in lvl]), fh, indent=1)
    with wave.open(os.path.join(ROOT, "build", "fb_voice_track.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype("<i2").tobytes())
    for s in scenes:
        print(f"{s['name']:9s} {s['start']:6.2f}-{s['end']:6.2f} ({s['end'] - s['start']:.1f}s)  cues {s['cues']}")
    print("total", dur, "s")


if __name__ == "__main__":
    main()
