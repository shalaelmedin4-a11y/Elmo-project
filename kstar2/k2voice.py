#!/usr/bin/env python3
"""Narration + timeline for 'Ein Tag als K-Pop-Star' (version 2).

Every scene has a minimum length (from the brief). The phrases of a scene are
placed one after another with relaxed pauses; if they need more room the scene
gets longer. Result (build/k2_timeline.json) drives picture, lip-sync and music.

Phrases live in kstar2/voice/cue_XX.wav. Missing ones are generated with a
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

V.VOICE = "de-DE-SeraphinaMultilingualNeural"
VDIR = os.path.join(HERE, "voice")
SR, FPS = V.SR, 12

# scene: (name, minimum length, clock, [(text, rate, pitch, breath)])
R, P = "-16%", "+2Hz"     # slow, calm, very clear
SCENES = [
    ("bed", 6.0, "05:00", [("Fünf Uhr.", R, "+4Hz", True),
                           ("Ich hab nur drei Stunden geschlafen.", R, P, False)]),
    ("kitchen", 6.0, "06:00", [("Frühstück.", R, "+4Hz", True),
                               ("Nur ein Salat.", R, P, False),
                               ("Ich darf nicht zunehmen.", R, "+0Hz", False)]),
    ("makeup", 6.0, "08:00", [("Drei Stunden Make-up.", R, "+2Hz", True),
                              ("Jeden Tag.", R, "+0Hz", False)]),
    ("dance", 6.0, "11:00", [("Tanztraining.", R, "+2Hz", True),
                             ("Immer und immer wieder.", R, "+0Hz", False)]),
    ("studio", 6.0, "13:00", [("Aufnahme im Studio.", R, "+2Hz", True),
                              ("Es muss perfekt sein.", R, "+0Hz", False)]),
    ("fans", 6.0, "16:00", [("Fan-Treffen.", R, "+6Hz", True),
                            ("Immer lächeln.", R, "+4Hz", False),
                            ("Auch wenn ich müde bin.", "-18%", "-2Hz", False)]),
    ("concert", 6.0, "19:00", [("Das Konzert.", R, "+6Hz", True),
                               ("Das ist der schönste Moment.", R, "+6Hz", False)]),
    ("office", 7.0, "23:00", [("Danach Gespräch mit dem Manager.", R, "+0Hz", True),
                              ("Ich hab Schulden bei der Firma.", "-18%", "-2Hz", False),
                              ("Und Dating ist verboten.", "-18%", "-4Hz", False)]),
    ("night", 6.0, "01:00", [("Ein Uhr nachts.", "-18%", "-2Hz", True),
                             ("Morgen geht alles wieder von vorne los.", "-18%", "-2Hz", False),
                             ("Folg mir für Tag zwei.", R, "+4Hz", True)]),
]
LEAD, GAP, TAIL = 0.4, 0.65, 0.6


def main():
    force = "--tts" in sys.argv
    os.makedirs(VDIR, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    clips, i = [], 0
    for name, _, _, lines in SCENES:
        for text, rate, pitch, br in lines:
            wav = os.path.join(VDIR, f"cue_{i:02d}.wav")
            if force or not os.path.exists(wav):
                mp3 = os.path.join(ROOT, "build", f"k2_cue_{i:02d}.mp3")
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
    with open(os.path.join(ROOT, "build", "k2_timeline.json"), "w") as fh:
        json.dump(dict(dur=dur, fps=FPS, scenes=scenes, cues=cues, level=[round(float(v), 3) for v in lvl]), fh, indent=1)
    with wave.open(os.path.join(ROOT, "build", "k2_voice_track.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype("<i2").tobytes())
    for s in scenes:
        print(f"{s['name']:9s} {s['start']:6.2f}-{s['end']:6.2f} ({s['end'] - s['start']:.1f}s)  cues {s['cues']}")
    print("total", dur, "s")


if __name__ == "__main__":
    main()
